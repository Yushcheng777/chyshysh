# -*- coding: utf-8 -*-
"""
Fetch benchmark index series via AkShare and save as config/benchmarks.csv
Columns: Symbol,Date,Close
Usage:
  python scripts/fetch_benchmarks_akshare.py --akshare_symbol 000300 --name SZZZ --out config/benchmarks.csv --start 2019-01-01
"""
from __future__ import annotations
import argparse
import pandas as pd
import akshare as ak

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--akshare_symbol", required=True, help="Index code, e.g., 000300 for CSI 300")
    ap.add_argument("--name", required=True, help="Name used in pipeline, e.g., SZZZ")
    ap.add_argument("--out", required=True, help="Output CSV path, e.g., config/benchmarks.csv")
    ap.add_argument("--start", required=False, default="2019-01-01")
    ap.add_argument("--end", required=False, default=None)
    args = ap.parse_args()

    s = args.start.replace("-", "")
    e = args.end.replace("-", "") if args.end else None
    df = ak.index_zh_a_hist(symbol=args.akshare_symbol, period="daily", start_date=s, end_date=e)
    # Columns: 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, ...
    df = df.rename(columns={"日期":"Date","收盘":"Close"})
    df = df[["Date","Close"]].copy()
    df["Symbol"] = args.name
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[["Symbol","Date","Close"]].sort_values(["Symbol","Date"])
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out}, rows={len(df)}")

if __name__ == "__main__":
    main()