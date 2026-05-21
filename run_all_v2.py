#!/usr/bin/env python
"""AI测试系统 - 批量执行所有测试套件（简化版）"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import print_header, print_separator, print_table_row, api_client, Timer
from src.parallel_runner_v2 import ParallelTestRunnerV2


def main():
    print_header("AI测试系统 - 批量执行所有测试套件", 100)
    
    # 检查服务
    health = api_client.health()
    if not health:
        print("❌ 无法连接到服务器，请先运行: python run.py")
        return 1
    
    print(f"✅ 服务连接正常 - 版本: {health.get('version', 'unknown')}")
    
    # 获取套件列表
    suites = api_client.get_suites()
    if not suites:
        print("❌ 未找到任何测试套件")
        return 1
    
    print(f"\n📋 发现 {len(suites)} 个测试套件")
    
    # 并行执行
    with Timer("批量测试"):
        runner = ParallelTestRunnerV2()
        results = runner.run_parallel(suites)
        runner.print_summary(results)
    
    # 检查是否有失败
    failed = sum(1 for r in results if not r.get('success', False))
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
