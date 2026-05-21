#!/usr/bin/env python
"""AI测试系统 - 主启动脚本（集成启动检测）"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def check_ollama():
    """检查Ollama服务是否运行"""
    try:
        import requests
        resp = requests.get("http://localhost:11434", timeout=3)
        return resp.status_code == 200
    except:
        return False


def check_model():
    """检查模型是否已下载"""
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    return "qwen2.5" in result.stdout


def download_model(model_name: str = "qwen2.5:0.5b"):
    """下载模型"""
    print(f"   正在下载 {model_name} 模型...")
    subprocess.run(["ollama", "pull", model_name])
    print(f"   {model_name} 模型下载完成")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                  AI测试系统 启动器 v3.0                       ║
    ║                         (集成自适应检测)                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # ========== 步骤1：硬件检测与自适应配置 ==========
    print("\n[步骤1] 执行硬件检测与自适应配置...")
    
    try:
        from src.startup_check import run_startup_check
        check_result = run_startup_check()
        
        if not check_result['passed']:
            # 错误已在 startup_check 中处理并退出
            return
        
        # 获取自适应配置
        adaptive_config = check_result['config'].get('adaptive', {})
        concurrency = adaptive_config.get('concurrency', 1)
        recommended_model = check_result['config'].get('recommended_model', 'qwen2.5:0.5b')
        
        print(f"\n✅ 自适应配置已应用:")
        print(f"   - 并发数: {concurrency}")
        print(f"   - 推荐模型: {recommended_model}")
        
    except ImportError as e:
        print(f"⚠️ 启动检测模块未找到: {e}")
        print("   跳过硬件检测，使用默认配置")
        concurrency = 1
        recommended_model = "qwen2.5:0.5b"
    except Exception as e:
        print(f"⚠️ 启动检测失败: {e}")
        print("   使用默认配置继续")
        concurrency = 1
        recommended_model = "qwen2.5:0.5b"
    
    # ========== 步骤2：检查Ollama服务 ==========
    print("\n[步骤2] 检查Ollama服务...")
    if not check_ollama():
        print("    ❌ Ollama未启动")
        print("    请在新终端运行: ollama serve")
        print("    然后重新运行本脚本")
        input("\n按回车键退出...")
        return
    print("    ✅ Ollama服务正常")
    
    # ========== 步骤3：检查模型 ==========
    print("\n[步骤3] 检查模型...")
    if not check_model():
        print(f"    ⚠️ 推荐模型 {recommended_model} 未下载")
        download_model(recommended_model)
    else:
        print(f"    ✅ 模型已就绪")
    
    # ========== 步骤4：创建必要目录 ==========
    print("\n[步骤4] 准备启动...")
    Path("logs").mkdir(exist_ok=True)
    Path("data/test_suites").mkdir(parents=True, exist_ok=True)
    print("    ✅ 目录准备完成")
    
    # ========== 步骤5：启动服务 ==========
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  服务已启动！                                                 ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  本地访问: http://localhost:8000                             ║
    ║  API文档: http://localhost:8000/docs                         ║
    ║  仪表板: http://localhost:8501 (需运行 streamlit)            ║
    ║                                                              ║
    ║  自适应配置:                                                 ║
    ║    - 并发数: {concurrency}                                   ║
    ║    - 推荐模型: {recommended_model}                           ║
    ║                                                              ║
    ║  按 Ctrl+C 停止服务                                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
