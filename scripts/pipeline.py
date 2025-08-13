# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import pandas as pd
from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from indicators import compute_indicators
from signals import compute_composite_signals

def load_prices(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['Date'])
    return df

def load_benchmarks(path: Path | None) -> pd.DataFrame | None:
    if not path or not Path(path).exists():
        return None
    return pd.read_csv(path, parse_dates=['Date'])

def attach_relative_strength(df: pd.DataFrame,
                             sectors_map: dict[str,str] | None,
                             benchmarks: pd.DataFrame | None,
                             benchmark_symbol: str | None) -> pd.DataFrame:
    out = df.copy()
    if benchmarks is None:
        out['RelToSector20D'] = pd.NA
        out['RelToBenchmark20D'] = pd.NA
        return out
    if benchmark_symbol:
        bench = benchmarks[benchmarks['Symbol'] == benchmark_symbol][['Date','Close']].rename(columns={'Close':'Bench_Close'})
        out = out.merge(bench, on='Date', how='left')
        # Calculate relative strength ticker by ticker
        rel_benchmark_list = []
        for ticker in out['Ticker'].unique():
            ticker_data = out[out['Ticker'] == ticker].copy()
            ticker_data['RelToBenchmark20D'] = (
                ticker_data['Close'].pct_change(20) - ticker_data['Bench_Close'].pct_change(20)
            )
            rel_benchmark_list.append(ticker_data[['Ticker', 'Date', 'RelToBenchmark20D']])
        rel_benchmark_df = pd.concat(rel_benchmark_list, ignore_index=True)
        out = out.merge(rel_benchmark_df, on=['Ticker', 'Date'], how='left', suffixes=('', '_rel'))
        
    if sectors_map:
        tmp = out[['Ticker','Date','Close']].copy()
        tmp['Sector'] = tmp['Ticker'].map(sectors_map)
        sector_series = tmp.groupby(['Sector','Date'])['Close'].mean().reset_index().rename(columns={'Close':'Sector_Close'})
        out = out.merge(tmp[['Ticker','Date','Sector']].drop_duplicates(), on=['Ticker','Date'], how='left')
        out = out.merge(sector_series, on=['Sector','Date'], how='left')
        # Calculate relative strength ticker by ticker
        rel_sector_list = []
        for ticker in out['Ticker'].unique():
            ticker_data = out[out['Ticker'] == ticker].copy()
            ticker_data['RelToSector20D'] = (
                ticker_data['Close'].pct_change(20) - ticker_data['Sector_Close'].pct_change(20)
            )
            rel_sector_list.append(ticker_data[['Ticker', 'Date', 'RelToSector20D']])
        rel_sector_df = pd.concat(rel_sector_list, ignore_index=True)
        out = out.merge(rel_sector_df, on=['Ticker', 'Date'], how='left', suffixes=('', '_rel2'))
    
    return out

def snapshot_tickers(daily: pd.DataFrame) -> pd.DataFrame:
    daily = daily.sort_values(['Ticker','Date'])
    last = daily.groupby('Ticker').tail(1).copy()
    cols = [
        'Ticker','Close','MA50','MA200','RSI14','AvgVol20','Volume','VolumeRatio20',
        'RelToSector20D','RelToBenchmark20D','Radar_Pass','Tech_Confirm','Buy_Signal','Signal_Light','Radar_Score'
    ]
    snap = last[['Ticker'] + [c for c in cols if c in last.columns]].copy()
    return snap

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prices', required=True, help='CSV with raw OHLCV')
    ap.add_argument('--benchmarks', required=False, help='CSV with sector/benchmark series')
    ap.add_argument('--benchmark_symbol', required=False, default=None, help='Benchmark symbol name in benchmarks CSV')
    ap.add_argument('--sectors_map', required=False, help='CSV mapping Ticker->Sector (columns: Ticker,Sector)')
    ap.add_argument('--out_daily', required=True, help='Output daily_metrics.csv')
    ap.add_argument('--out_tickers', required=True, help='Output tickers.csv snapshot')
    args = ap.parse_args()

    prices = load_prices(Path(args.prices))
    benchmarks = load_benchmarks(Path(args.benchmarks)) if args.benchmarks else None
    sectors_map = None
    if args.sectors_map:
        m = pd.read_csv(args.sectors_map)
        sectors_map = dict(zip(m['Ticker'], m['Sector']))

    enriched = compute_indicators(prices)
    enriched = attach_relative_strength(enriched, sectors_map, benchmarks, args.benchmark_symbol)
    final = compute_composite_signals(enriched)

    final.to_csv(args.out_daily, index=False)
    snap = snapshot_tickers(final)
    snap.to_csv(args.out_tickers, index=False)

if __name__ == '__main__':
    main()