# -*- coding: utf-8 -*-
"""
Fetch OHLCV for A-share tickers via AkShare and produce a unified CSV.
Input: config/tickers.csv (columns: Ticker,Name,Sector)
Output: CSV with columns ['Ticker','Date','Open','High','Low','Close','AdjClose','Volume','Turnover']
Usage:
  python scripts/fetch_akshare.py --tickers config/tickers.csv --out data/prices.csv --start 2019-01-01 --end 2025-08-13
"""
from __future__ import annotations
import argparse
import pandas as pd
import akshare as ak
from datetime import datetime

def to_ak_symbol(ticker: str) -> str | None:
    # Expect Ticker like "600519.SH" or "000001.SZ"
    if ticker.endswith(".SH") or ticker.endswith(".SZ"):
        return ticker.split(".")[0]
    return None  # Only support A-share in this script

def fetch_one(ticker: str, start: str, end: str) -> pd.DataFrame:
    code = to_ak_symbol(ticker)
    if not code:
        raise ValueError(f"Unsupported ticker for AkShare A-share fetch: {ticker}")
    # AkShare requires yyyymmdd
    s = start.replace("-", "")
    e = end.replace("-", "")
    df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=s, end_date=e, adjust="")
    # Expected columns: 日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, ...
    rename_map = {
        "日期": "Date",
        "开盘": "Open",
        "收盘": "Close",
        "最高": "High",
        "最低": "Low",
        "成交量": "Volume",
        "成交额": "Turnover",
    }
    df = df.rename(columns=rename_map)
    df = df[list(rename_map.values())].copy()
    df["Ticker"] = ticker
    # AdjClose not provided here; use Close as placeholder
    df["AdjClose"] = df["Close"]
    # Ensure types
    df["Date"] = pd.to_datetime(df["Date"])
    numeric_cols = ["Open", "High", "Low", "Close", "AdjClose", "Volume", "Turnover"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[["Ticker", "Date", "Open", "High", "Low", "Close", "AdjClose", "Volume", "Turnover"]]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", required=True, help="CSV with Ticker,Name,Sector")
    ap.add_argument("--out", required=True, help="Output CSV path")
    ap.add_argument("--start", required=False, default="2019-01-01")
    ap.add_argument("--end", required=False, default=datetime.today().strftime("%Y-%m-%d"))
    args = ap.parse_args()

    tickers = pd.read_csv(args.tickers)["Ticker"].dropna().unique().tolist()
    frames = []
    for t in tickers:
        try:
            df = fetch_one(t, args.start, args.end)
            frames.append(df)
        except Exception as e:
            print(f"[WARN] Skipped {t}: {e}")
    if not frames:
        raise SystemExit("No data fetched; please check tickers.")
    out = pd.concat(frames, ignore_index=True).sort_values(["Ticker", "Date"])
    out.to_csv(args.out, index=False)
    print(f"Wrote {args.out}, rows={len(out)}")

if __name__ == "__main__":
    main()