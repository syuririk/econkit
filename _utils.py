"""범용 유틸리티 함수."""

from __future__ import annotations

import numpy as np
import pandas as pd


def safe_div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    """안전한 나눗셈. 0 나눗셈 및 inf를 NaN으로 처리."""
    result = numer / denom.replace(0, np.nan)
    return result.replace([np.inf, -np.inf], np.nan)


def describe_df(df: pd.DataFrame) -> pd.DataFrame:
    """DataFrame 컬럼별 요약 (dtype, null 수, unique 수)."""
    return pd.DataFrame({
        "dtype": df.dtypes,
        "non_null": df.count(),
        "null_cnt": df.isna().sum(),
        "n_unique": df.nunique(),
    })


def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """DatetimeIndex가 아니면 변환 시도."""
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = pd.to_datetime(df.index)
    return df


def numeric_columns(df: pd.DataFrame) -> list[str]:
    """수치형 컬럼 목록 반환."""
    return list(df.select_dtypes(include="number").columns)
