# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import numpy as np

def compute_composite_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['GoldenCross_ShortOverLong']   = (df.get('MA50', 0) > df.get('MA200', 0)).astype(int)
    df['DeathCross_ShortUnderLong']   = (df.get('MA50', 0) < df.get('MA200', 0)).astype(int)
    df['BB_Breakout_Upper']  = (df['Close'] > df.get('BB_Upper', float('inf'))).astype(int)
    df['BB_Breakdown_Lower'] = (df['Close'] < df.get('BB_Lower', 0)).astype(int)
    df['MACD_AboveZero'] = (df.get('MACD_Line', 0) > 0).astype(int)
    
    if 'MACD_Line' in df.columns and 'MACD_Signal' in df.columns:
        macd_cross = np.sign(df['MACD_Line'] - df['MACD_Signal'])
        df['MACD_BullCross'] = ((macd_cross.shift(1) <= 0) & (macd_cross > 0)).astype(int)
        df['MACD_BearCross'] = ((macd_cross.shift(1) >= 0) & (macd_cross < 0)).astype(int)
    else:
        df['MACD_BullCross'] = 0
        df['MACD_BearCross'] = 0
        
    df['RSI_BullRange'] = (df.get('RSI14', 50) >= 48).astype(int)
    df['RSI_BearRange'] = (df.get('RSI14', 50) <= 45).astype(int)
    df['RSI_Divergence_Flag'] = 0
    
    if 'ATR14' in df.columns:
        df['ATR_Breakout_Flag'] = (df['ATR14'] >= df['ATR14'].rolling(20).mean() * 1.5).astype(int)
    else:
        df['ATR_Breakout_Flag'] = 0
    
    df['Vol_Expansion_Flag'] = (df.get('VolumeRatio20', 1) >= 1.2).astype(int)
    
    df['Tech_Confirm'] = (
        (df['Close'] > df.get('MA200', 0)) &
        (df['Close'] > df.get('MA50', 0)) &
        (df.get('RSI14', 50) >= 48) &
        (df.get('VolumeRatio20', 1) >= 1.2)
    ).astype(int)
    
    df['Radar_Pass'] = ((df.get('RelToSector20D', 0).fillna(0) > 0) | (df.get('RelToBenchmark20D', 0).fillna(0) > 0)).astype(int)
    
    score = (
        20 * df['Tech_Confirm'] +
        15 * df['MACD_AboveZero'] +
        15 * df['GoldenCross_ShortOverLong'] +
        10 * df['RSI_BullRange'] +
        10 * df['Vol_Expansion_Flag'] +
        10 * (df.get('RelToSector20D', 0).fillna(0) > 0).astype(int) +
        20 * df['Radar_Pass']
    )
    df['Radar_Score'] = score.clip(lower=0, upper=100)
    
    def decide(row):
        if row['Radar_Pass'] and row['Tech_Confirm']:
            return 'BUY'
        if row['Radar_Pass'] and not row['Tech_Confirm']:
            return 'WATCH'
        return 'AVOID'
    df['Buy_Signal'] = df.apply(decide, axis=1)
    df['Signal_Light'] = df['Buy_Signal'].map({'BUY': '🟢', 'WATCH': '🟡', 'AVOID': '🔴'})
    return df