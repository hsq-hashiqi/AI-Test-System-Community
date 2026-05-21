# src/startup_check.py - 优化超时配置版
"""AI测试系统 - 启动时硬件检测（优化超时配置）"""

import sys
import psutil
import subprocess
import re
import json
import time
from pathlib import Path
from datetime import datetime, timedelta


class StartupChecker:
    
    # 缓存文件路径
    CACHE_FILE = Path("data/hardware_cache.json")
    CACHE_TTL = 3600  # 缓存有效期1小时
    
    def __init__(self):
        self.memory_gb = 0
        self.gpu_memory_gb = 0
        self.disk_free_gb = 0
        self.has_gpu = False
        self.ollama_running = False
        self.available_models = []
        
        self.checks = []
        self.errors = []
        self.config = {}
        
        # 加载缓存
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """加载缓存"""
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE, 'r') as f:
                    data = json.load(f)
                    cache_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                    if datetime.now() - cache_time < timedelta(seconds=self.CACHE_TTL):
                        return data.get('data', {})
            except:
                pass
        return {}
    
    def _save_cache(self, data):
        """保存缓存"""
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.CACHE_FILE, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                }, f)
        except:
            pass
    
    def run(self):
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("🔧 AI测试系统 - 启动时硬件检测")
        print("=" * 60)
        
        # 快速检测（不耗时的项目）
        self._check_python()
        self._check_disk()
        
        # 使用缓存的检测
        self._check_memory_with_cache()
        self._check_gpu_with_cache()
        
        # 必须实时检测的项目
        self._check_ollama()
        self._check_models()
        
        self._generate_config()
        self._print_report()
        
        elapsed = time.time() - start_time
        print(f"\n⏱️ 检测耗时: {elapsed:.2f}秒")
        
        if self.errors:
            input("\n按回车键退出...")
            sys.exit(1)
        
        return self.config
    
    def _check_python(self):
        v = sys.version_info
        passed = v.major >= 3 and v.minor >= 9
        self.checks.append(f"{'✅' if passed else '❌'} Python: {v.major}.{v.minor}.{v.micro}")
        if not passed:
            self.errors.append("Python版本过低，需要3.9+")
    
    def _check_disk(self):
        disk = psutil.disk_usage(str(Path(__file__).parent.parent))
        self.disk_free_gb = disk.free / (1024**3)
        passed = self.disk_free_gb >= 10
        self.checks.append(f"{'✅' if passed else '❌'} 磁盘: {self.disk_free_gb:.0f}GB")
        if not passed:
            self.errors.append("磁盘空间不足")
    
    def _check_memory_with_cache(self):
        mem = psutil.virtual_memory()
        self.memory_gb = mem.total / (1024**3)
        passed = self.memory_gb >= 8
        self.checks.append(f"{'✅' if passed else '❌'} 内存: {self.memory_gb:.0f}GB")
        if not passed:
            self.errors.append("内存不足")
    
    def _check_gpu_with_cache(self):
        cached_gpu = self.cache.get('gpu')
        if cached_gpu:
            self.has_gpu = cached_gpu.get('has_gpu', False)
            self.gpu_memory_gb = cached_gpu.get('gpu_memory_gb', 0)
            self.checks.append(f"✅ GPU: {cached_gpu.get('name', 'Unknown')} ({self.gpu_memory_gb:.0f}GB) [缓存]")
            return
        
        try:
            start = time.time()
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                capture_output=True, text=True, timeout=5
            )
            print(f"    (GPU检测耗时: {time.time()-start:.2f}秒)")
            
            if result.returncode == 0:
                parts = [p.strip() for p in result.stdout.strip().split(',')]
                match = re.search(r'\d+', parts[1])
                mem = int(match.group()) / 1024 if match else 0
                self.has_gpu = True
                self.gpu_memory_gb = mem
                self.checks.append(f"✅ GPU: {parts[0]} ({mem:.0f}GB)")
                
                self._save_cache({
                    'gpu': {
                        'has_gpu': True,
                        'gpu_memory_gb': mem,
                        'name': parts[0]
                    }
                })
            else:
                self._no_gpu()
        except:
            self._no_gpu()
    
    def _no_gpu(self):
        self.has_gpu = False
        self.gpu_memory_gb = 0
        self.checks.append("ℹ️ GPU: 未检测到 (使用CPU模式)")
    
    def _check_ollama(self):
        import requests
        try:
            start = time.time()
            resp = requests.get("http://localhost:11434", timeout=3)
            print(f"    (Ollama检测耗时: {time.time()-start:.2f}秒)")
            self.ollama_running = resp.status_code == 200
            self.checks.append(f"{'✅' if self.ollama_running else '❌'} Ollama: {'运行中' if self.ollama_running else '未启动'}")
            if not self.ollama_running:
                self.errors.append("Ollama服务未启动")
        except:
            self.ollama_running = False
            self.checks.append("❌ Ollama: 未启动")
            self.errors.append("Ollama服务未启动")
    
    def _check_models(self):
        cached_models = self.cache.get('models')
        if cached_models:
            self.available_models = cached_models
            count = len(self.available_models)
            self.checks.append(f"✅ 模型: {count}个 [缓存]")
            return
        
        try:
            start = time.time()
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            print(f"    (模型列表检测耗时: {time.time()-start:.2f}秒)")
            
            lines = result.stdout.strip().split('\n')
            self.available_models = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if parts:
                        self.available_models.append(parts[0])
            
            count = len(self.available_models)
            self.checks.append(f"{'✅' if count > 0 else '⚠️'} 模型: {count}个")
            if count == 0:
                self.errors.append("未检测到模型")
            
            self._save_cache({'models': self.available_models})
        except:
            self.checks.append("❌ 模型: 检测失败")
            self.errors.append("模型检测失败")
    
    def _generate_config(self):
        """生成自适应配置 - 优化超时时间"""
        
        # ============================================
        # 根据 GPU 显存设置超时时间
        # ============================================
        # 参考标准:
        #   - 10GB+ 显存: 可流畅运行 7B 模型，响应快，超时 50 秒
        #   - 6-10GB 显存: 可运行 4B 模型，响应正常，超时 60 秒
        #   - 4-6GB 显存: 可运行 3B 模型，响应较慢，超时 90 秒
        #   - 无 GPU: CPU 模式，响应很慢，超时 120 秒
        # ============================================
        
        if self.gpu_memory_gb >= 10:
            concurrency = 4
            batch_size = 4
            timeout = 50      # 10GB+ 显存，响应快
            grade = "高性能"
        elif self.gpu_memory_gb >= 6:
            concurrency = 2
            batch_size = 2
            timeout = 60      # 6GB 显存（你的配置），标准响应
            grade = "标准"
        elif self.gpu_memory_gb >= 4:
            concurrency = 1
            batch_size = 1
            timeout = 90      # 4GB 显存，响应较慢
            grade = "基础"
        else:
            concurrency = 1
            batch_size = 1
            timeout = 120     # CPU 模式，响应很慢
            grade = "CPU模式"
        
        # 内存不足时降低并发
        if self.memory_gb < 8:
            concurrency = 1
            batch_size = 1
            timeout = 90
        
        # ============================================
        # 推荐模型
        # ============================================
        if self.gpu_memory_gb >= 8 and any('7b' in m for m in self.available_models):
            model = 'qwen2.5:7b'
        elif self.gpu_memory_gb >= 6 and any('4b' in m for m in self.available_models):
            model = 'qwen2.5:4b'
        elif any('0.5b' in m for m in self.available_models):
            model = 'qwen2.5:0.5b'
        elif self.available_models:
            model = self.available_models[0]
        else:
            model = 'qwen2.5:0.5b'
        
        self.config = {
            'concurrency': concurrency,
            'batch_size': batch_size,
            'timeout': timeout,
            'parallel_enabled': concurrency > 1,
            'recommended_model': model,
            'grade': grade,
            'gpu_memory_gb': self.gpu_memory_gb
        }
    
    def _print_report(self):
        print("\n" + "-" * 40)
        print("检测结果")
        print("-" * 40)
        for c in self.checks:
            print(f"  {c}")
        
        print("\n" + "-" * 40)
        print("自适应配置（已自动应用）")
        print("-" * 40)
        print(f"  📊 GPU等级: {self.config.get('grade', 'unknown')} ({self.config.get('gpu_memory_gb', 0):.0f}GB)")
        print(f"  🔧 并发数: {self.config.get('concurrency', 1)}")
        print(f"  📦 Batch Size: {self.config.get('batch_size', 1)}")
        print(f"  ⏱️ 超时时间: {self.config.get('timeout', 60)}秒")
        print(f"  🔄 并行执行: {'启用' if self.config.get('parallel_enabled', False) else '禁用'}")
        print(f"  🤖 推荐模型: {self.config.get('recommended_model', 'unknown')}")
        
        # 显示超时说明
        timeout = self.config.get('timeout', 60)
        print(f"\n  💡 超时说明: 单个测试用例最长等待 {timeout} 秒")
        if timeout <= 50:
            print(f"     你的硬件配置优秀，响应快速")
        elif timeout <= 60:
            print(f"     你的硬件配置标准，响应正常")
        elif timeout <= 90:
            print(f"     你的硬件配置基础，响应较慢")
        else:
            print(f"     CPU模式，响应较慢，建议升级显卡")
        
        print("=" * 60)


def run_startup_check():
    checker = StartupChecker()
    return checker.run()


if __name__ == "__main__":
    run_startup_check()
