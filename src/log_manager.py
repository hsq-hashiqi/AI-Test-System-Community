# src/log_manager.py
"""日志自动管理模块"""

import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict


class LogManager:
    """日志管理器 - 自动清理"""
    
    def __init__(self, log_dir: str = "logs", retention_days: int = 30):
        self.log_dir = Path(log_dir)
        self.retention_days = retention_days
        self._running = False
        self._thread = None
    
    def start(self):
        """启动自动清理"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._thread.start()
        print(f"✅ 日志管理器已启动 (保留 {self.retention_days} 天)")
    
    def stop(self):
        """停止自动清理"""
        self._running = False
    
    def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            time.sleep(86400)  # 每天检查一次
            self.cleanup()
    
    def cleanup(self) -> Dict:
        """清理过期日志"""
        if not self.log_dir.exists():
            return {"deleted": 0, "size_mb": 0}
        
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        deleted = 0
        size_saved = 0
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff:
                    size_saved += log_file.stat().st_size
                    log_file.unlink()
                    deleted += 1
            except:
                pass
        
        for log_file in self.log_dir.glob("*.log.*"):
            try:
                if log_file.stat().st_mtime < cutoff.timestamp():
                    size_saved += log_file.stat().st_size
                    log_file.unlink()
                    deleted += 1
            except:
                pass
        
        return {
            "deleted": deleted,
            "size_mb": round(size_saved / (1024 * 1024), 2)
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if not self.log_dir.exists():
            return {"total_files": 0, "total_size_mb": 0}
        
        files = list(self.log_dir.glob("*.log"))
        files.extend(self.log_dir.glob("*.log.*"))
        
        total_size = sum(f.stat().st_size for f in files) / (1024 * 1024)
        
        return {
            "total_files": len(files),
            "total_size_mb": round(total_size, 2),
            "retention_days": self.retention_days
        }


# 全局实例
log_manager = LogManager(retention_days=30)
