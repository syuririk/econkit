"""변화율 계산 — EconDataset의 _df_full 보간 로직을 보존."""

from __future__ import annotations

import pandas as pd


def _make_full_index(df: pd.DataFrame) -> pd.DataFrame:
    """일별 인덱스로 리인덱스 (보간용)."""
    full_idx = pd.date_range(df.index.min(), df.index.max())
    return df.reindex(full_idx)


def pct_change(df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
    """보간 인덱스 기반 백분율 변화율.

    원본 EconDataset._df_full 기반 계산 로직을 보존합니다.
    일별 리인덱스 후 pct_change를 계산하고, 원본 인덱스로 필터합니다.
    """
    full = _make_full_index(df)
    pct = full.pct_change(periods)
    return pct.loc[df.index]


def diff(df: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
    """보간 인덱스 기반 차분."""
    full = _make_full_index(df)
    d = full.diff(periods)
    return d.loc[df.index]


def rolling_std(df: pd.DataFrame, window: int, offset: int = 1) -> pd.DataFrame:
    """보간 인덱스 기반 롤링 표준편차.

    offset일 차분을 기준으로 window일 롤링 표준편차를 계산합니다.
    """
    full = _make_full_index(df)
    d = full.diff(offset)
    rs = d.rolling(window).std()
    return rs.loc[df.index]


def yoy(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year 변화율 (%). 365일 기준."""
    return pct_change(df, 365) * 100


def qoq(df: pd.DataFrame) -> pd.DataFrame:
    """Quarter-over-quarter 변화율 (%). 90일 기준."""
    return pct_change(df, 90) * 100


def mom(df: pd.DataFrame) -> pd.DataFrame:
    """Month-over-month 변화율 (%). 30일 기준."""
    return pct_change(df, 30) * 100
