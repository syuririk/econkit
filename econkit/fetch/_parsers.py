"""데이터 변환 유틸리티."""

from __future__ import annotations

import re

import pandas as pd


def parse_time(val) -> pd.Timestamp:
    """ECOS 시간 문자열을 Timestamp로 변환.

    지원 형식: YYYY, YYYYMM, YYYYMMDD, YYYYQN, YYYYSN, YYYYMMSN
    """
    pattern = re.compile(r"""
        ^
        (?P<y>\d{4})
        (?:
            (?P<m>\d{2})
            (?:
                (?P<d>\d{2})
                |
                S(?P<sm>[12])
            )?
            |
            Q(?P<q>[1-4])
            |
            S(?P<s>[12])
        )?
        $
    """, re.X)

    m = pattern.match(str(val))
    if not m:
        return pd.NaT

    y = int(m["y"])

    if m["q"]:
        return pd.Timestamp(y, (int(m["q"]) - 1) * 3 + 1, 1)
    if m["s"]:
        return pd.Timestamp(y, (int(m["s"]) - 1) * 6 + 1, 1)
    if m["sm"]:
        return pd.Timestamp(y, int(m["m"]), 1 if m["sm"] == "1" else 16)
    if m["d"]:
        return pd.Timestamp(y, int(m["m"]), int(m["d"]))
    if m["m"]:
        return pd.Timestamp(y, int(m["m"]), 1)

    return pd.Timestamp(y, 1, 1)


def pivot_stat_info(df: pd.DataFrame) -> pd.DataFrame:
    """FISIS statisticsInfoSearch 결과를 피벗."""
    result = df.pivot(
        index=["base_month", "finance_cd"],
        columns="account_nm",
        values="a",
    )
    result.columns.name = None
    result = result.reset_index().rename(columns={"base_month": "date"})
    return result
