## 股票投资跟踪系统实施计划

- [ ] 编写完整的 README.md（项目概览与使用说明）
- [ ] 搭建目录结构（notion_template/、scripts/、config/、data/、.github/workflows/）
- [ ] 创建配置文件：
  - [ ] config/indicators.yaml（技术指标参数）
  - [ ] config/stock_list.yaml（股票池/标的范围定义）
  - [ ] config/radar_rules.json（信号生成规则）
- [ ] 实现核心 Python 脚本：
  - [ ] scripts/calc_indicators.py（技术指标计算）
  - [ ] scripts/update_data.py（数据抓取与处理主流程）
  - [ ] scripts/push_to_notion.py（可选的 Notion API 集成）
  - [ ] scripts/archive_markdown.py（每日报告生成）
- [ ] 创建模板文件：
  - [ ] notion_template/tickers.csv（股票池模板）
  - [ ] notion_template/sectors.csv（板块/行业分类）
  - [ ] notion_template/daily_metrics.csv（输出模板，含表头）
- [ ] 配置自动化：
  - [ ] .github/workflows/daily_update.yml（GitHub Actions 工作流）
  - [ ] requirements.txt（Python 依赖）
  - [ ] .env.example（环境变量模板）
- [ ] 更新 .gitignore（适配 Python 项目）
- [ ] 测试系统功能：
  - [ ] 测试 update_data.py 脚本执行
  - [ ] 测试 archive_markdown.py 报告生成
  - [ ] 校验 GitHub Actions 工作流语法
- [ ] 人工核对输出结果与功能

—  
提示：你可以通过设置自定义指令、定制开发环境以及配置 MCP（Model Context Protocol）服务器，让 Copilot 更智能。文档参考：Copilot coding agent tips https://gh.io/copilot-coding-agent-tips