# -*- coding: utf-8 -*-
"""
Compute technical indicators for OHLCV DataFrames.
Requires: pandas, numpy, pandas_ta (recommended).
Input df columns: ['Ticker','Date','Open','High','Low','Close','AdjClose','Volume']
Output: df with appended indicator columns (matching daily_metrics.csv headers).
"""
from __future__ import annotations
import pandas as pd
import numpy as np

try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except Exception:
    HAS_PANDAS_TA = False

def _vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df['High'] + df['Low'] + df['Close']) / 3.0
    cum_pv = (tp * df['Volume']).cumsum()
    cum_v = df['Volume'].cumsum()
    return cum_pv / np.where(cum_v == 0, np.nan, cum_v)

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(['Ticker', 'Date']).copy()
    g = df.groupby('Ticker', group_keys=False)

    # Moving averages
    df['MA20']  = g['Close'].transform(lambda s: s.rolling(20).mean())
    df['MA50']  = g['Close'].transform(lambda s: s.rolling(50).mean())
    df['MA200'] = g['Close'].transform(lambda s: s.rolling(200).mean())

    # EMAs
    df['EMA20']  = g['Close'].transform(lambda s: s.ewm(span=20, adjust=False).mean())
    df['EMA50']  = g['Close'].transform(lambda s: s.ewm(span=50, adjust=False).mean())
    df['EMA200'] = g['Close'].transform(lambda s: s.ewm(span=200, adjust=False).mean())

    # Bollinger Bands (20, 2)
    rolling20 = g['Close'].transform(lambda s: s.rolling(20))
    mid = df['MA20']
    std = rolling20.std()
    df['BB_Middle'] = mid
    df['BB_Upper']  = mid + 2 * std
    df['BB_Lower']  = mid - 2 * std
    df['BB_Width']  = (df['BB_Upper'] - df['BB_Lower']) / mid.replace(0, np.nan)
    df['BB_PctB']   = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])

    # Ichimoku (9,26,52)
    conv = g.apply(lambda x: ((x['High'].rolling(9).max() + x['Low'].rolling(9).min()) / 2)).reset_index(level=0, drop=True)
    base = g.apply(lambda x: ((x['High'].rolling(26).max() + x['Low'].rolling(26).min()) / 2)).reset_index(level=0, drop=True)
    span_a = ((conv + base) / 2)
    span_b = g.apply(lambda x: ((x['High'].rolling(52).max() + x['Low'].rolling(52).min()) / 2)).reset_index(level=0, drop=True)
    chikou = g['Close'].transform(lambda s: s.shift(-26))
    df['Ichimoku_Tenkan'] = conv
    df['Ichimoku_Kijun']  = base
    df['Ichimoku_SenkouA'] = span_a.shift(26)
    df['Ichimoku_SenkouB'] = span_b.shift(26)
    df['Ichimoku_Chikou']  = chikou

    # MACD, RSI, Stoch, ADX, ATR, HV, OBV, CMF
    if HAS_PANDAS_TA:
        macd = g.apply(lambda x: ta.macd(x['Close'], fast=12, slow=26, signal=9)).reset_index(level=0, drop=True)
        df['MACD_Line']   = macd['MACD_12_26_9']
        df['MACD_Signal'] = macd['MACDs_12_26_9']
        df['MACD_Hist']   = macd['MACDh_12_26_9']
        df['RSI14']       = g.apply(lambda x: ta.rsi(x['Close'], length=14)).reset_index(level=0, drop=True)
        stoch = g.apply(lambda x: ta.stoch(x['High'], x['Low'], x['Close'], k=14, d=3)).reset_index(level=0, drop=True)
        df['Stoch_K'] = stoch['STOCHk_14_3_3']
        df['Stoch_D'] = stoch['STOCHd_14_3_3']
        adx = g.apply(lambda x: ta.adx(x['High'], x['Low'], x['Close'], length=14)).reset_index(level=0, drop=True)
        df['ADX']     = adx['ADX_14']
        df['DI_Plus'] = adx['DMP_14']
        df['DI_Minus']= adx['DMN_14']
        df['ATR14']   = g.apply(lambda x: ta.atr(x['High'], x['Low'], x['Close'], length=14)).reset_index(level=0, drop=True)
        df['HV20']    = g['Close'].transform(lambda s: np.log(s).diff().rolling(20).std() * np.sqrt(252))
        df['OBV']     = g.apply(lambda x: ta.obv(x['Close'], x['Volume'])).reset_index(level=0, drop=True)
        df['CMF_20']  = g.apply(lambda x: ta.cmf(x['High'], x['Low'], x['Close'], x['Volume'], length=20)).reset_index(level=0, drop=True)
    else:
        # Minimal RSI fallback
        delta = g['Close'].transform(lambda s: s.diff())
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.rolling(14).mean()
        roll_down = down.rolling(14).mean()
        rs = roll_up / roll_down.replace(0, np.nan)
        df['RSI14'] = 100 - (100 / (1 + rs))

    # Stochastic fallback if needed
    if 'Stoch_K' not in df.columns:
        ll14 = g['Low'].transform(lambda s: s.rolling(14).min())
        hh14 = g['High'].transform(lambda s: s.rolling(14).max())
        df['Stoch_K'] = (df['Close'] - ll14) / (hh14 - ll14)
        df['Stoch_D'] = g['Stoch_K'].transform(lambda s: s.rolling(3).mean())

    # ROC, VWAP, Gap, Volume features, Returns
    df['ROC_20']   = g['Close'].transform(lambda s: s.pct_change(20))
    df['VWAP']     = g.apply(_vwap).reset_index(level=0, drop=True)
    prev_close = g['Close'].shift(1)
    df['Gap_Pct']  = (df['Open'] - prev_close) / prev_close
    df['AvgVol20']      = g['Volume'].transform(lambda s: s.rolling(20).mean())
    df['VolumeRatio20'] = df['Volume'] / df['AvgVol20']
    df['Ret1D']  = g['Close'].transform(lambda s: s.pct_change(1))
    df['Ret5D']  = g['Close'].transform(lambda s: s.pct_change(5))
    df['Ret20D'] = g['Close'].transform(lambda s: s.pct_change(20))
    return df