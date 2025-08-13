# # 股票投资跟踪系统（GitHub + Notion + 自动化）

本项目将你的投资跟踪模板产品化：版本化、可协作、可扩展，并支持每日自动抓取数据、计算技术指标、生成信号、归档报告、同步到 Notion。

## 功能一览
- 日常数据抓取（yfinance 示例）与全套技术指标计算（pandas + pandas_ta）
- 复合信号生成（Radar/Tech/BUY）与可配置阈值
- Notion 数据库同步（可选）
- GitHub Actions 定时任务（每日自动更新）、归档 Markdown 报告
- CSV、Markdown 跨平台留存

## 目录结构
```
.
├─ notion_template/
│  ├─ tickers.csv              # 股票池模板
│  ├─ sectors.csv              # 板块/行业模板
│  └─ daily_metrics.csv        # 指标与信号（脚本生成/覆盖）
│
├─ scripts/
│  ├─ calc_indicators.py       # 指标计算模块（按 Ticker 分组）
│  ├─ update_data.py           # 抓取数据 + 计算指标 + 生成信号 + 导出CSV
│  ├─ push_to_notion.py        # 同步到 Notion（可选）
│  └─ archive_markdown.py      # 生成每日归档报告
│
├─ config/
│  ├─ indicators.yaml          # 指标参数
│  ├─ stock_list.yaml          # 股票池配置
│  └─ radar_rules.json         # 复合信号阈值
│
├─ data/
│  └─ .gitkeep                 # 归档目录（每日报告等）
│
├─ .github/workflows/
│  └─ daily_update.yml         # 定时任务：更新数据、归档、可选推 Notion
│
├─ requirements.txt
├─ .env.example                # 本地环境变量样例
└─ .gitignore
```

## 快速开始（本地）
1) 安装依赖
```
pip install -r requirements.txt
```

2) 配置
- 复制 .env.example 为 .env，若需推送 Notion，填写 NOTION_API_KEY 和 NOTION_DATABASE_ID
- 编辑 config/stock_list.yaml，设定你的股票池与基准
- 如需调整指标参数或信号阈值，编辑 config/indicators.yaml 与 config/radar_rules.json

3) 运行
```
python scripts/update_data.py --days 365
python scripts/archive_markdown.py
# 如需推送到 Notion（可选）
python scripts/push_to_notion.py --csv notion_template/daily_metrics.csv
```

运行后：
- notion_template/daily_metrics.csv 将被生成/覆盖（全量指标+信号）
- data/YYYY-MM-DD-report.md 生成当日归档报告

## GitHub Actions 自动化
1) 在仓库设置中添加 Secrets（可选）
- NOTION_API_KEY：你的 Notion Integration 秘钥
- NOTION_DATABASE_ID：目标数据库 ID（若使用 Notion 同步）
2) 工作流文件 .github/workflows/daily_update.yml 已就绪，默认每日执行并可手动触发

## Notion 配置指引（简要）
- 在 Notion 创建一个数据库，至少包含：
  - Ticker（Title）
  - Date（Date）
  - Close, EMA20, MACD, ADX, CMF, RSI14（Number）
  - Signal_BUY（Checkbox）
- 将数据库 ID 与 API Key 填入环境变量后，运行 push_to_notion.py 即可新增页面（默认"追加"模式，去重/更新可按 TODO 注释扩展）

## 字段说明（节选）
- 趋势类：MA/EMA(5/10/20/50/200), Bollinger_Mid/Upper/Lower, Ichimoku_*, ADX/DI+/DI-
- 动量类：MACD/MACD_Signal/MACD_Hist, Stochastic_K/D, RSI14, ROC, Relative_Strength（相对基准）
- 波动与风险：ATR, HV（历史波动率，log年化）, Gap, Max_Drawdown
- 量能：OBV, VWAP, CMF
- 复合信号：Golden_Cross, Death_Cross, Boll_Break_Up/Down, MACD_Break_Zero, ATR_Break
- 策略触发：Signal_Radar, Signal_Tech, Signal_BUY（来自 radar_rules.json 阈值）

提示：daily_metrics.csv 会自动填充、覆盖，无需手动编辑。

## 免责声明
本项目仅供学习研究，不构成任何投资建议。请自行承担风险。
