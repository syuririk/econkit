"""데이터 유효성 검증."""

from __future__ import annotations

import pandas as pd


def validate_econ_df(df: pd.DataFrame) -> None:
    """경제 데이터 DataFrame 유효성 검사.

    Raises
    ------
    TypeError
        DatetimeIndex가 아닌 경우.
    ValueError
        수치형이 아닌 컬럼이 있는 경우.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("index가 DatetimeIndex여야 합니다.")

    non_num = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    if non_num:
        raise ValueError(f"수치형이 아닌 컬럼 발견: {non_num}")

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        print(f"[경고] 결측값 존재:\n{missing}")

    dupes = df.index.duplicated().sum()
    if dupes:
        print(f"[경고] 중복 날짜 {dupes}개 발견.")
