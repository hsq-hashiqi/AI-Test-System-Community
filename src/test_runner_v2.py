# src/test_runner_v2.py
"""测试运行器 v2 - 性能优化版"""

import time
import yaml
import requests
from typing import List, Dict, Any
from pathlib import Path
from functools import lru_cache

from src.config import Config
from src.hardware_adapter_v2 import hardware_v2


class TestRunnerV2:
    """测试运行器 v2"""
    
    def __init__(self):
        self.ollama_url = Config.get_ollama_url()
        self.default_model = hardware_v2.get_recommended_model()
        self.test_suites_path = Path("data/test_suites")
        self.test_suites_path.mkdir(parents=True, exist_ok=True)
        self._session = requests.Session()
    
    @lru_cache(maxsize=32)
    def load_test_suite(self, suite_name: str) -> Dict:
        """加载测试套件（带缓存）"""
        suite_file = self.test_suites_path / f"{suite_name}.yaml"
        if not suite_file.exists():
            return self._create_default_suite(suite_name)
        
        with open(suite_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _create_default_suite(self, suite_name: str) -> Dict:
        """创建默认测试套件"""
        default_suite = {
            'name': suite_name,
            'description': '默认测试套件',
            'model': self.default_model,
            'test_cases': [
                {'id': 'TC001', 'name': '基础测试', 'task': '你好',
                 'assertions': [{'type': 'not_empty'}]},
            ]
        }
        suite_file = self.test_suites_path / f"{suite_name}.yaml"
        with open(suite_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_suite, f, allow_unicode=True)
        return default_suite
    
    def _call_llm(self, prompt: str, model: str) -> tuple:
        """调用LLM"""
        if not prompt or not prompt.strip():
            return "", 0
        
        start_time = time.time()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 256,
                "num_ctx": 2048
            }
        }
        
        try:
            response = self._session.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', ''), latency
            return f"API Error: {response.status_code}", latency
        except Exception as e:
            return f"Error: {str(e)}", 0
    
    def _evaluate_assertions(self, response: str, assertions: List[Dict]) -> tuple:
        """评估断言"""
        if not assertions:
            return True, []
        
        for assertion in assertions:
            assert_type = assertion.get('type', 'contains')
            
            if assert_type == 'contains':
                patterns = assertion.get('patterns', [])
                if not all(p in response for p in patterns):
                    return False, assertion
            elif assert_type == 'not_empty':
                if len(response.strip()) == 0:
                    return False, assertion
        
        return True, []
    
    def run_suite(self, suite_name: str) -> Dict:
        """执行测试套件"""
        suite = self.load_test_suite(suite_name)
        model = suite.get('model', self.default_model)
        test_cases = suite.get('test_cases', [])
        
        results = []
        passed_count = 0
        total_latency = 0
        
        for tc in test_cases:
            task = tc.get('task', '')
            response, latency = self._call_llm(task, model)
            total_latency += latency
            passed, _ = self._evaluate_assertions(response, tc.get('assertions', []))
            
            if passed:
                passed_count += 1
            
            results.append({
                'id': tc.get('id', ''),
                'name': tc.get('name', ''),
                'passed': passed,
                'latency_ms': latency,
                'response_preview': response[:200]
            })
        
        total = len(test_cases)
        avg_latency = total_latency / total if total > 0 else 0
        
        return {
            'suite_name': suite_name,
            'model': model,
            'total': total,
            'passed': passed_count,
            'failed': total - passed_count,
            'pass_rate': passed_count / total if total > 0 else 0,
            'avg_latency_ms': avg_latency,
            'results': results
        }
