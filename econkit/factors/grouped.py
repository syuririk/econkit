"""그룹별 팩터 생성 함수.

groupby 기반으로 종목/지표 코드별 팩터를 계산.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from econkit._utils import safe_div


def ratio_factor(numer, denom):
    """비율 팩터."""
    def factor(df):
        if isinstance(numer, (int, float)):
            return safe_div(pd.Series(numer, index=df.index), df[denom])
        return safe_div(df[numer], df[denom])
    return factor


def return_factor(code, col, period, subtract=None, date_col=None):
    """그룹별 수익률 팩터."""
    def factor(df):
        if date_col:
            df = df.sort_values(date_col)
        g = df.groupby(code)[col]
        base = g.pct_change(period)
        if subtract:
            base -= g.pct_change(subtract)
        return base.replace([np.inf, -np.inf], np.nan)
    return factor


def rolling_stat_factor(code, col, window, stat="mean"):
    """그룹별 이동통계 팩터."""
    def factor(df):
        g = df.groupby(code, sort=False)[col]
        if stat == "mean":
            out = g.rolling(window).mean()
        elif stat == "std":
            out = g.rolling(window).std()
        else:
            raise ValueError("stat must be 'mean' or 'std'")
        return out.reset_index(level=0, drop=True)
    return factor


def log_factor(col):
    """로그 변환 팩터."""
    def factor(df):
        return np.log(df[col])
    return factor


def ma_cross_factor(code, col, short=5, long=60, method="ratio"):
    """그룹별 이동평균 교차 팩터."""
    def factor(df):
        g = df.groupby(code, sort=False)[col]
        short_ma = g.rolling(short).mean().reset_index(level=0, drop=True)
        long_ma = g.rolling(long).mean().reset_index(level=0, drop=True)

        if method == "ratio":
            return safe_div(short_ma, long_ma)
        elif method == "diff":
            return short_ma - long_ma
        elif method == "signal":
            return (short_ma > long_ma).astype("float32")
        else:
            raise ValueError("method must be ratio | diff | signal")
    return factor


def parkinson_vol_factor(code, high, low, window=21):
    """Parkinson 변동성 팩터."""
    def factor(df):
        hl = np.log(df[high] / df[low]) ** 2
        return (
            hl.groupby(df[code])
            .rolling(window)
            .mean()
            .mul(1 / (4 * np.log(2)))
            .pow(0.5)
            .reset_index(level=0, drop=True)
        )
    return factor


def amihud_factor(code, price, amount):
    """Amihud 유동성 팩터."""
    def factor(df):
        ret = df.groupby(code, sort=False)[price].pct_change(fill_method=None).abs()
        return safe_div(ret, df[amount])
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


def rolling_zscore_factor(code, col, window, eps=1e-8):
    """그룹별 이동 Z-score 팩터."""
    def factor(df):
        g = df.groupby(code, sort=False)[col]
        mean = g.rolling(window).mean().reset_index(level=0, drop=True)
        std = g.rolling(window).std().reset_index(level=0, drop=True)
        return ((df[col] - mean) / (std + eps)).astype("float32")
    return factor


def cs_zscore(df, col, eps=1e-8, date_col="date"):
    """횡단면 Z-score."""
    return df.groupby(date_col)[col].transform(
        lambda x: (x - x.mean()) / (x.std() + eps)
    )


def compute(df, factor_dict, zscore=True, date_col="date"):
    """일괄 팩터 계산.

    Parameters
    ----------
    df : pd.DataFrame
        입력 데이터.
    factor_dict : dict
        {name: func} 형태.
    zscore : bool
        횡단면 Z-score 표준화 여부.
    date_col : str
        날짜 컬럼명.

    Returns
    -------
    pd.DataFrame
        팩터가 추가된 DataFrame.
    """
    result = df.copy()
    for name, func in factor_dict.items():
        result[name] = func(result).astype("float32")
        if zscore:
            result[f"{name}_Z"] = cs_zscore(result, name, date_col=date_col).astype("float32")
    return result
