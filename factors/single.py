"""단일 인덱스 팩터 생성 함수.

DataFrame을 받아 Series를 반환하는 클로저 팩토리.
groupby 없이 단일 시계열에 적용.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from econkit._utils import safe_div


def ratio_factor(numer, denom):
    """비율 팩터. numer/denom 계산."""
    def factor(df):
        if isinstance(numer, (int, float)):
            return safe_div(pd.Series(numer, index=df.index), df[denom])
        return safe_div(df[numer], df[denom])
    return factor


def return_factor(col, period, subtract=None):
    """수익률 팩터. pct_change 기반."""
    def factor(df):
        base = df[col].pct_change(period)
        if subtract:
            base -= df[col].pct_change(subtract)
        return base.replace([np.inf, -np.inf], np.nan)
    return factor


def rolling_stat_factor(col, window, stat="mean"):
    """이동통계 팩터."""
    def factor(df):
        s = df[col]
        if stat == "mean":
            return s.rolling(window).mean()
        elif stat == "std":
            return s.rolling(window).std()
        else:
            raise ValueError("stat must be 'mean' or 'std'")
    return factor


def log_factor(col):
    """로그 변환 팩터."""
    def factor(df):
        return np.log(df[col])
    return factor


def ma_cross_factor(col, short=5, long=60, method="ratio"):
    """이동평균 교차 팩터."""
    def factor(df):
        s = df[col]
        short_ma = s.rolling(short).mean()
        long_ma = s.rolling(long).mean()

        if method == "ratio":
            return safe_div(short_ma, long_ma)
        elif method == "diff":
            return short_ma - long_ma
        elif method == "signal":
            return (short_ma > long_ma).astype("float32")
        else:
            raise ValueError("method must be ratio | diff | signal")
    return factor


def compare_factor(left, right, op="gt"):
    """비교 팩터."""
    def factor(df):
        l = df[left] if isinstance(left, str) else left
        r = df[right] if isinstance(right, str) else right

        if op == "gt":
            out = l > r
        elif op == "ge":
            out = l >= r
        elif op == "eq":
            out = l == r
        elif op == "ne":
            out = l != r
        else:
            raise ValueError("op must be gt | ge | eq | ne")
        return out.astype(int)
    return factor


def rolling_zscore_factor(col, window, eps=1e-8):
    """이동 Z-score 팩터."""
    def factor(df):
        s = df[col]
        mean = s.rolling(window).mean()
        std = s.rolling(window).std()
        return ((s - mean) / (std + eps)).astype("float32")
    return factor
