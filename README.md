# AI Testing System - Community Edition

> 从零开发的AI测试系统 | 支持Web/API/性能自动化测试 | 自动生成HTML/JSON报告

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 简介

**AI Testing System** 是一个基于本地LLM的AI测试系统，无需支付API费用，数据完全私有化部署。

我从零开发了这套系统，结合了7年软件测试经验和AI技术，旨在帮助企业降低测试成本、提升测试效率。

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🚀 **智能启动器** | 一键启动所有服务，自动清理缓存 |
| 🧪 **测试引擎** | YAML格式测试用例，支持多种断言类型 |
| 📊 **自动报告** | HTML + JSON双格式报告，自动打开浏览器 |
| 📋 **日志管理** | 自动轮转和清理，保留30天 |

---

## 🚀 快速开始

### 环境要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| Python | 3.9+ | 3.11 |
| 内存 | 8GB | 16GB |

### 安装

```bash
# 克隆项目
git clone https://github.com/yourname/AI-Test-System-Community.git
cd AI-Test-System-Community

# 安装依赖
pip install -r requirements.txt

# 生成配置
python generate_key.py

# 启动系统
python run.py
测试
bash
# 健康检查
curl http://localhost:8000/health

# 执行测试
curl -X POST http://localhost:8000/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"suite_name": "demo"}'
📁 项目结构
text
AI-Test-System-Community/
├── run.py                # API服务
├── run_single.py         # 单套件测试
├── run_all_v2.py         # 批量测试
├── src/                  # 源代码
├── data/test_suites/     # 测试套件
├── logs/                 # 日志目录
└── reports/              # 报告目录
📄 许可证
MIT License

📧 联系方式
作者：Saxon Wang

邮箱：635630645@qq.com

Made with ❤️ by Saxon Wang
