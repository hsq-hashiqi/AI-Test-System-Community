#!/usr/bin/env python
"""
AI测试系统 - 单套件测试执行器
支持执行指定测试套件并输出详细用例执行明细
自动生成HTML和JSON报告，测试完成后自动弹出报告页面
用法: python run_single.py <suite_name>
示例: python run_single.py fintech
"""

import requests
import sys
import time
import json
import argparse
import webbrowser
import os
from pathlib import Path
from datetime import datetime

# 配置
API_URL = "http://localhost:8000/api/test/run"
TEST_SUITES_DIR = Path("data/test_suites")
REPORT_DIR = Path("reports")


def ensure_report_dir():
    """确保报告目录存在"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 报告目录: {REPORT_DIR.absolute()}")


def print_header(title: str, width: int = 110):
    """打印标题头"""
    print(f"\n{'='*width}")
    print(f"{title.center(width)}")
    print(f"{'='*width}")


def print_separator(width: int = 110):
    """打印分隔线"""
    print(f"{'-'*width}")


def print_table_row(cols, widths, align="center"):
    """打印对齐的表格行"""
    row = ""
    for i, col in enumerate(cols):
        if align == "left":
            row += f"{col:<{widths[i]}}"
        elif align == "right":
            row += f"{col:>{widths[i]}}"
        elif align == "center":
            row += f"{col:^{widths[i]}}"
        else:
            row += f"{col:<{widths[i]}}"
        if i < len(cols) - 1:
            row += "  "
    print(row)


def get_all_suites():
    """获取所有可用测试套件"""
    if not TEST_SUITES_DIR.exists():
        return []
    yaml_files = list(TEST_SUITES_DIR.glob("*.yaml"))
    return sorted([f.stem for f in yaml_files])


def get_suite_details(suite_name):
    """获取测试套件详细用例信息"""
    import yaml
    suite_file = TEST_SUITES_DIR / f"{suite_name}.yaml"
    if not suite_file.exists():
        return []
    
    with open(suite_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    details = []
    for tc in data.get('test_cases', []):
        details.append({
            'id': tc.get('id', ''),
            'name': tc.get('name', ''),
            'task': tc.get('task', '')[:50],
            'priority': tc.get('priority', 'P1')
        })
    return details


def run_suite(suite_name):
    """执行单个测试套件，返回详细结果"""
    try:
        start = time.time()
        response = requests.post(
            API_URL,
            json={"suite_name": suite_name},
            timeout=300
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            
            # 提取详细用例结果
            case_results = []
            for r in data.get('results', []):
                case_results.append({
                    'id': r.get('id', ''),
                    'name': r.get('name', ''),
                    'passed': r.get('passed', False),
                    'latency_ms': r.get('latency_ms', 0),
                    'response_preview': r.get('response_preview', '')[:200]
                })
            
            return {
                'success': True,
                'total': data.get('total', 0),
                'passed': data.get('passed', 0),
                'failed': data.get('failed', 0),
                'pass_rate': data.get('pass_rate', 0) * 100,
                'avg_latency_ms': data.get('avg_latency_ms', 0),
                'time': elapsed,
                'case_results': case_results
            }
        else:
            return {'success': False, 'time': elapsed, 'error': f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'time': 0, 'error': "无法连接服务器"}
    except Exception as e:
        return {'success': False, 'time': 0, 'error': str(e)}


def generate_html_report(suite_name, result):
    """生成HTML报告"""
    ensure_report_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_file = REPORT_DIR / f"{suite_name}_{timestamp}.html"
    
    total = result['total']
    passed = result['passed']
    failed = result['failed']
    pass_rate = result['pass_rate']
    avg_latency = result.get('avg_latency_ms', 0)
    total_time = result['time']
    
    # 构建HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI测试系统报告 - {suite_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 28px;
            color: #333;
            margin-bottom: 10px;
        }}
        .header .meta {{
            color: #666;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .summary-card:hover {{
            transform: translateY(-5px);
        }}
        .summary-card .number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .summary-card .label {{
            color: #666;
            font-size: 14px;
        }}
        .summary-card.total .number {{ color: #3b82f6; }}
        .summary-card.pass .number {{ color: #10b981; }}
        .summary-card.fail .number {{ color: #ef4444; }}
        .summary-card.rate .number {{ color: #8b5cf6; }}
        .summary-card.time .number {{ color: #f59e0b; }}
        .results-table {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #e5e7eb;
        }}
        td {{
            padding: 10px 16px;
            border-bottom: 1px solid #e5e7eb;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .status-pass {{
            color: #10b981;
            font-weight: 500;
        }}
        .status-fail {{
            color: #ef4444;
            font-weight: 500;
        }}
        .priority-P0 {{
            background: #fee2e2;
            color: #dc2626;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            display: inline-block;
        }}
        .priority-P1 {{
            background: #fef3c7;
            color: #d97706;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            display: inline-block;
        }}
        .priority-P2 {{
            background: #dbeafe;
            color: #2563eb;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            display: inline-block;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: white;
            font-size: 12px;
        }}
        .success-badge {{
            background: #10b981;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            display: inline-block;
        }}
        .failed-badge {{
            background: #ef4444;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 AI测试系统 - 测试报告</h1>
            <div class="meta">套件名称: {suite_name} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <div class="number">{total}</div>
                <div class="label">总用例数</div>
            </div>
            <div class="summary-card pass">
                <div class="number">{passed}</div>
                <div class="label">通过</div>
            </div>
            <div class="summary-card fail">
                <div class="number">{failed}</div>
                <div class="label">失败</div>
            </div>
            <div class="summary-card rate">
                <div class="number">{pass_rate:.1f}%</div>
                <div class="label">通过率</div>
            </div>
            <div class="summary-card time">
                <div class="number">{total_time:.1f}s</div>
                <div class="label">总耗时</div>
            </div>
        </div>
        
        <div class="results-table">
            <table>
                <thead>
                    <tr>
                        <th>用例ID</th>
                        <th>用例名称</th>
                        <th>优先级</th>
                        <th>状态</th>
                        <th>耗时(ms)</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    for r in result.get('case_results', []):
        status_class = "status-pass" if r['passed'] else "status-fail"
        status_text = "✅ 通过" if r['passed'] else "❌ 失败"
        # 提取优先级
        priority = 'P1'
        if 'P0' in r['id']:
            priority = 'P0'
        elif 'P2' in r['id']:
            priority = 'P2'
        
        priority_display = f"<span class='priority-{priority}'>{priority}</span>"
        
        html_content += f'''
                    <tr>
                        <td>{r['id']}</td>
                        <td>{r['name']}</td>
                        <td>{priority_display}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{r['latency_ms']:.0f}</td>
                    </tr>
'''
    
    result_badge = "success-badge" if result['pass_rate'] == 100 else "failed-badge"
    result_text = "✅ 全部通过" if result['pass_rate'] == 100 else f"❌ 通过率: {result['pass_rate']:.1f}%"
    
    html_content += f'''
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p style="margin-bottom: 10px;">平均响应时间: {avg_latency:.0f}ms | 报告生成: AI测试系统 v3.0 (A级)</p>
            <p><span class="{result_badge}">{result_text}</span></p>
        </div>
    </div>
</body>
</html>
'''
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file


def generate_json_report(suite_name, result):
    """生成JSON报告"""
    ensure_report_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = REPORT_DIR / f"{suite_name}_{timestamp}.json"
    
    report_data = {
        "suite_name": suite_name,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": result['total'],
            "passed": result['passed'],
            "failed": result['failed'],
            "pass_rate": result['pass_rate'],
            "avg_latency_ms": result.get('avg_latency_ms', 0),
            "total_time_seconds": result['time']
        },
        "results": result.get('case_results', [])
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    return json_file


def open_report_in_browser(html_file):
    """在默认浏览器中打开报告"""
    if not html_file or not html_file.exists():
        print(f"❌ 报告文件不存在: {html_file}")
        return False
    
    # 转换为绝对路径的 file:// URL
    file_url = f"file:///{html_file.absolute().as_posix()}"
    # Windows 路径格式调整
    file_url = file_url.replace('\\', '/')
    
    try:
        webbrowser.open(file_url)
        return True
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        return False


def list_suites():
    """列出所有可用测试套件"""
    suites = get_all_suites()
    if not suites:
        print("❌ 未找到任何测试套件")
        return
    
    print_header("可用的测试套件列表", 80)
    print(f"\n共发现 {len(suites)} 个测试套件:\n")
    
    for i, suite in enumerate(suites, 1):
        details = get_suite_details(suite)
        print(f"  {i:3d}. {suite:<30} ({len(details)} 个用例)")
    
    print(f"\n{'='*80}")
    print(f"使用示例: python run_single.py <套件名称>")
    print(f"例如: python run_single.py fintech")


def print_case_details(suite_name, result):
    """打印详细用例执行明细"""
    case_results = result.get('case_results', [])
    if not case_results:
        return
    
    print(f"\n  📋 {suite_name} 详细用例执行明细:")
    print(f"  {'-'*100}")
    
    # 表头
    print(f"  {'序号':<6} {'用例ID':<20} {'用例名称':<30} {'状态':<8} {'耗时(ms)':<10}")
    print(f"  {'-'*100}")
    
    for idx, cr in enumerate(case_results, 1):
        status = "✅ 通过" if cr['passed'] else "❌ 失败"
        name_display = cr['name'][:28] + ".." if len(cr['name']) > 30 else cr['name']
        print(f"  {idx:<6} {cr['id']:<20} {name_display:<30} {status:<8} {cr['latency_ms']:<10.0f}")
    
    print(f"  {'-'*100}")


def run_single_suite(suite_name, save_report=True, auto_open=True):
    """执行单个测试套件并输出详细报告"""
    ensure_report_dir()
    
    # 检查服务
    try:
        resp = requests.get("http://localhost:8000/health", timeout=5)
        if resp.status_code != 200:
            print("❌ 服务未就绪，请先运行: python run.py")
            return 1
    except:
        print("❌ 无法连接到服务器，请先运行: python run.py")
        return 1
    
    # 检查套件是否存在
    all_suites = get_all_suites()
    if suite_name not in all_suites:
        print(f"❌ 测试套件 '{suite_name}' 不存在")
        print(f"可用套件: {', '.join(all_suites)}")
        return 1
    
    # 执行测试
    print_header(f"AI测试系统 - 单套件测试报告 [{suite_name}]", 110)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*110}")
    
    print(f"\n▶ 正在执行测试套件: {suite_name}")
    result = run_suite(suite_name)
    
    if not result['success']:
        print(f"❌ 执行失败: {result.get('error', '未知错误')}")
        return 1
    
    # 打印详细用例执行明细
    print_case_details(suite_name, result)
    
    # 执行统计
    print(f"\n  📊 执行统计:")
    print(f"    总用例数: {result['total']}")
    print(f"    通过数:   {result['passed']}")
    print(f"    失败数:   {result['failed']}")
    print(f"    通过率:   {result['pass_rate']:.1f}%")
    print(f"    总耗时:   {result['time']:.1f} 秒")
    print(f"    平均耗时: {result['time']/result['total']:.1f} 秒/用例" if result['total'] > 0 else "")
    
    print(f"{'='*110}\n")
    
    # 生成报告
    html_file = None
    json_file = None
    if save_report:
        html_file = generate_html_report(suite_name, result)
        json_file = generate_json_report(suite_name, result)
        print(f"📄 HTML报告: {html_file}")
        print(f"📋 JSON报告: {json_file}")
        print()
    
    # 最终结果
    if result['pass_rate'] == 100:
        print_header(f"✅ 测试套件 [{suite_name}] 全部通过！", 80)
    else:
        print_header(f"⚠️ 测试套件 [{suite_name}] 部分失败，通过率: {result['pass_rate']:.1f}%", 80)
    
    # 自动打开报告
    if auto_open and html_file and html_file.exists():
        print(f"\n🌐 正在打开测试报告页面...")
        if open_report_in_browser(html_file):
            print(f"   ✅ 报告已在浏览器中打开")
        else:
            print(f"   ❌ 自动打开失败，请手动打开: {html_file}")
    
    return 0 if result['pass_rate'] == 100 else 1


def main():
    parser = argparse.ArgumentParser(description='AI测试系统 - 单套件测试执行器')
    parser.add_argument('suite', nargs='?', help='要执行的测试套件名称')
    parser.add_argument('-l', '--list', action='store_true', help='列出所有可用测试套件')
    parser.add_argument('-nr', '--no-report', action='store_true', help='不生成报告文件')
    parser.add_argument('-no-open', '--no-open', action='store_true', help='不自动打开浏览器')
    
    args = parser.parse_args()
    
    if args.list:
        list_suites()
        return 0
    
    if not args.suite:
        print("❌ 请指定测试套件名称")
        print("用法: python run_single.py <suite_name>")
        print("示例: python run_single.py fintech")
        print("      python run_single.py --list  # 查看所有套件")
        return 1
    
    return run_single_suite(args.suite, save_report=not args.no_report, auto_open=not args.no_open)


if __name__ == "__main__":
    sys.exit(main())
