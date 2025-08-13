# Indicators Pipeline (AkShare + GitHub Actions)

## What you get
- AkShare data fetchers for A-shares (tickers and benchmark)
- Daily scheduled workflow at 16:30 Beijing time (08:30 UTC)
- Full technical indicators + composite signals
- CSV outputs uploaded as workflow artifacts for manual Notion import

## Quick start (local)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/fetch_akshare.py --tickers config/tickers.csv --out data/prices.csv --start 2019-01-01
python scripts/fetch_benchmarks_akshare.py --akshare_symbol 000300 --name SZZZ --out config/benchmarks.csv --start 2019-01-01
python scripts/pipeline.py --prices data/prices.csv --benchmarks config/benchmarks.csv --benchmark_symbol SZZZ --sectors_map config/sectors_map.csv --out_daily data/daily_metrics.csv --out_tickers data/tickers.csv
```

## Notion 手动导入
- 方式一：在 Notion 新建一个数据库，点击右上角 "Import"，选择 CSV，导入 `data/daily_metrics.csv` 或 `data/tickers.csv`。
- 方式二：在已有数据库视图中，直接将 CSV 文件拖拽到页面，Notion 会自动创建并映射列。
- 字段映射建议：
  - 文本：Ticker、Name、Sector、Buy_Signal、Signal_Light
  - 日期：Date
  - 数字：其余数值型指标（RSI14、MA50、MA200、Radar_Score、Volume 等）
- 主键：使用 Ticker + Date（Notion 不强制主键，但建议开启 "Merge with existing" 以避免重复）。

## 配置说明
- config/tickers.csv：维护标的清单及所属行业
- config/sectors_map.csv：Ticker 到行业映射（用于相对强度）
- benchmark（可选）：工作流默认自动抓取沪深300（000300）作为基准，保存到 config/benchmarks.csv，管道使用 Symbol=SZZZ

## 时区与触发
- 工作流 cron 以 UTC 计算：08:30 UTC = 北京时间 16:30
- 如需调整时间，修改 `.github/workflows/daily-pipeline.yml` 的 `cron` 表达式

## 常见问题
- AkShare 抓取单位：成交量/成交额使用 AkShare 原始单位；如需标准化可在脚本中调整
- Benchmarks 缺失：即使没有基准或行业映射，管道也会运行，相关相对强度列将为空
