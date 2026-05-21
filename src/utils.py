# src/utils.py
"""公共工具模块 - 消除重复代码"""

import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


# ========== 打印工具 ==========
def print_header(title: str, width: int = 100, char: str = "="):
    """打印标题头"""
    print(f"\n{char * width}")
    print(f"{title.center(width)}")
    print(f"{char * width}")


def print_separator(width: int = 100, char: str = "-"):
    """打印分隔线"""
    print(f"{char * width}")


def print_table_row(cols, widths: List[int], align: str = "left"):
    """打印对齐表格行"""
    row = ""
    for i, col in enumerate(cols):
        col_str = str(col) if col is not None else ""
        if align == "left":
            row += f"{col_str:<{widths[i]}}"
        elif align == "right":
            row += f"{col_str:>{widths[i]}}"
        elif align == "center":
            row += f"{col_str:^{widths[i]}}"
        if i < len(cols) - 1:
            row += "  "
    print(row)


# ========== 文件工具 ==========
def ensure_dir(path: Path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(file_path: Path) -> Optional[Dict]:
    """读取JSON文件"""
    if not file_path.exists():
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def write_json(file_path: Path, data: Dict):
    """写入JSON文件"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ========== 时间工具 ==========
def get_timestamp() -> str:
    """获取时间戳字符串"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def get_datetime() -> str:
    """获取日期时间字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class Timer:
    """计时器上下文管理器"""
    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        elapsed = time.time() - self.start_time
        if self.name:
            print(f"⏱️ {self.name} 耗时: {elapsed:.2f}s")
    
    def elapsed(self) -> float:
        return time.time() - self.start_time if self.start_time else 0


# ========== API 工具 ==========
class APIClient:
    """API客户端 - 统一请求处理"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """统一请求方法"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method.upper() == 'GET':
                resp = self.session.get(url, timeout=30)
            elif method.upper() == 'POST':
                resp = self.session.post(url, json=data, timeout=300)
            else:
                return None
            
            if resp.status_code == 200:
                return resp.json()
            return None
        except:
            return None
    
    def health(self) -> Optional[Dict]:
        return self._request('GET', 'health')
    
    def get_suites(self) -> List[str]:
        result = self._request('GET', 'api/test/suites')
        return result.get('suites', []) if result else []
    
    def run_test(self, suite_name: str) -> Optional[Dict]:
        return self._request('POST', 'api/test/run', {'suite_name': suite_name})
    
    def get_status(self) -> Optional[Dict]:
        return self._request('GET', 'api/test/status')


# 全局实例
api_client = APIClient()
