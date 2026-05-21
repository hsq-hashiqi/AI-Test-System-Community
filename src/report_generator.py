# src/report_generator.py
"""
测试报告生成器 - 支持HTML和JSON格式
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, report_dir: str = "reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_html(self, results: Dict[str, Any], suite_name: str) -> Path:
        """生成HTML报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.report_dir / f"{suite_name}_{timestamp}.html"
        
        # 统计信息
        total = results.get('total', 0)
        passed = results.get('passed', 0)
        failed = results.get('failed', 0)
        pass_rate = results.get('pass_rate', 0) * 100
        avg_latency = results.get('avg_latency_ms', 0)
        
        # 构建HTML
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI测试系统报告 - {suite_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .meta {{ opacity: 0.9; font-size: 14px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
        .summary-card .number {{ font-size: 36px; font-weight: bold; margin-bottom: 8px; }}
        .summary-card .label {{ color: #666; font-size: 14px; }}
        .summary-card.pass .number {{ color: #10b981; }}
        .summary-card.fail .number {{ color: #ef4444; }}
        .summary-card.rate .number {{ color: #3b82f6; }}
        .summary-card.time .number {{ color: #f59e0b; }}
        .results-table {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f8f9fa; padding: 12px 16px; text-align: left; font-weight: 600; border-bottom: 2px solid #e5e7eb; }}
        td {{ padding: 10px 16px; border-bottom: 1px solid #e5e7eb; }}
        .status-pass {{ color: #10b981; font-weight: 500; }}
        .status-fail {{ color: #ef4444; font-weight: 500; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
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
        </div>
        
        <div class="results-table">
            <table>
                <thead>
                    <tr><th>用例ID</th><th>用例名称</th><th>状态</th><th>耗时(ms)</th><th>响应预览</th></tr>
                </thead>
                <tbody>
'''
        
        for r in results.get('results', []):
            status_class = "status-pass" if r['passed'] else "status-fail"
            status_text = "✅ 通过" if r['passed'] else "❌ 失败"
            response_preview = r.get('response_preview', '')[:100]
            html_content += f'''
                    <tr>
                        <td>{r['id']}</td>
                        <td>{r['name']}</td>
                        <td class="{status_class}">{status_text}</td>
                        <td>{r['latency_ms']:.0f}</td>
                        <td style="max-width:300px; overflow:hidden; text-overflow:ellipsis;">{response_preview}</td>
                    </tr>
'''
        
        html_content += f'''
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>平均响应时间: {avg_latency:.0f}ms | 报告生成: AI测试系统 v3.0</p>
        </div>
    </div>
</body>
</html>
'''
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def generate_json(self, results: Dict[str, Any], suite_name: str) -> Path:
        """生成JSON报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.report_dir / f"{suite_name}_{timestamp}.json"
        
        report_data = {
            "suite_name": suite_name,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": results.get('total', 0),
                "passed": results.get('passed', 0),
                "failed": results.get('failed', 0),
                "pass_rate": results.get('pass_rate', 0),
                "avg_latency_ms": results.get('avg_latency_ms', 0)
            },
            "results": results.get('results', [])
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return filename
