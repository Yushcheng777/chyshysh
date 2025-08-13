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
    
    # Process each ticker separately to avoid groupby issues with small data
    result_dfs = []
    for ticker in df['Ticker'].unique():
        ticker_df = df[df['Ticker'] == ticker].copy()
        
        # Moving averages
        ticker_df['MA20'] = ticker_df['Close'].rolling(20).mean()
        ticker_df['MA50'] = ticker_df['Close'].rolling(50).mean()
        ticker_df['MA200'] = ticker_df['Close'].rolling(200).mean()

        # EMAs
        ticker_df['EMA20'] = ticker_df['Close'].ewm(span=20, adjust=False).mean()
        ticker_df['EMA50'] = ticker_df['Close'].ewm(span=50, adjust=False).mean()
        ticker_df['EMA200'] = ticker_df['Close'].ewm(span=200, adjust=False).mean()

        # Bollinger Bands (20, 2)
        ticker_df['BB_Middle'] = ticker_df['MA20']
        bb_std = ticker_df['Close'].rolling(20).std()
        ticker_df['BB_Upper'] = ticker_df['MA20'] + 2 * bb_std
        ticker_df['BB_Lower'] = ticker_df['MA20'] - 2 * bb_std
        ticker_df['BB_Width'] = (ticker_df['BB_Upper'] - ticker_df['BB_Lower']) / ticker_df['BB_Middle'].replace(0, np.nan)
        ticker_df['BB_PctB'] = (ticker_df['Close'] - ticker_df['BB_Lower']) / (ticker_df['BB_Upper'] - ticker_df['BB_Lower'])

        # Ichimoku (simplified)
        ticker_df['Ichimoku_Tenkan'] = ((ticker_df['High'].rolling(9).max() + ticker_df['Low'].rolling(9).min()) / 2)
        ticker_df['Ichimoku_Kijun'] = ((ticker_df['High'].rolling(26).max() + ticker_df['Low'].rolling(26).min()) / 2)
        ticker_df['Ichimoku_SenkouA'] = ((ticker_df['Ichimoku_Tenkan'] + ticker_df['Ichimoku_Kijun']) / 2).shift(26)
        ticker_df['Ichimoku_SenkouB'] = ((ticker_df['High'].rolling(52).max() + ticker_df['Low'].rolling(52).min()) / 2).shift(26)
        ticker_df['Ichimoku_Chikou'] = ticker_df['Close'].shift(-26)

        # Basic RSI
        delta = ticker_df['Close'].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.rolling(14).mean()
        roll_down = down.rolling(14).mean()
        rs = roll_up / roll_down.replace(0, np.nan)
        ticker_df['RSI14'] = 100 - (100 / (1 + rs))

        # Stochastic
        ll14 = ticker_df['Low'].rolling(14).min()
        hh14 = ticker_df['High'].rolling(14).max()
        ticker_df['Stoch_K'] = (ticker_df['Close'] - ll14) / (hh14 - ll14)
        ticker_df['Stoch_D'] = ticker_df['Stoch_K'].rolling(3).mean()

        # Basic MACD
        ema12 = ticker_df['Close'].ewm(span=12).mean()
        ema26 = ticker_df['Close'].ewm(span=26).mean()
        ticker_df['MACD_Line'] = ema12 - ema26
        ticker_df['MACD_Signal'] = ticker_df['MACD_Line'].ewm(span=9).mean()
        ticker_df['MACD_Hist'] = ticker_df['MACD_Line'] - ticker_df['MACD_Signal']

        # Simple indicators
        ticker_df['ROC_20'] = ticker_df['Close'].pct_change(20)
        ticker_df['HV20'] = ticker_df['Close'].pct_change().rolling(20).std() * np.sqrt(252)
        
        # VWAP approximation
        tp = (ticker_df['High'] + ticker_df['Low'] + ticker_df['Close']) / 3.0
        ticker_df['VWAP'] = (tp * ticker_df['Volume']).cumsum() / ticker_df['Volume'].cumsum()
        
        # Gap and volume
        ticker_df['Gap_Pct'] = (ticker_df['Open'] - ticker_df['Close'].shift(1)) / ticker_df['Close'].shift(1)
        ticker_df['AvgVol20'] = ticker_df['Volume'].rolling(20).mean()
        ticker_df['VolumeRatio20'] = ticker_df['Volume'] / ticker_df['AvgVol20']
        ticker_df['Ret1D'] = ticker_df['Close'].pct_change(1)
        ticker_df['Ret5D'] = ticker_df['Close'].pct_change(5)
        ticker_df['Ret20D'] = ticker_df['Close'].pct_change(20)

        # Fill some missing indicators with defaults for compatibility
        ticker_df['ADX'] = np.nan
        ticker_df['DI_Plus'] = np.nan
        ticker_df['DI_Minus'] = np.nan
        ticker_df['ATR14'] = ((ticker_df['High'] - ticker_df['Low']).rolling(14).mean())  # Simplified ATR
        ticker_df['OBV'] = np.nan
        ticker_df['CMF_20'] = np.nan
        
        result_dfs.append(ticker_df)
    
    return pd.concat(result_dfs, ignore_index=True).sort_values(['Ticker', 'Date'])