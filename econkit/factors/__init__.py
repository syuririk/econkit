"""
econkit.factors — 팩터 생성 함수 모음.

Usage:
    from econkit.factors import ratio_factor, return_factor, compute
    from econkit.factors.single import ma_cross_factor
    from econkit.factors.grouped import parkinson_vol_factor
"""

# single-index (groupby 없음)
from econkit.factors.single import (
    ratio_factor,
    return_factor,
    rolling_stat_factor,
    log_factor,
    ma_cross_factor,
    compare_factor,
    rolling_zscore_factor,
)

# grouped (groupby 기반) — 네임스페이스 충돌 방지를 위해 grouped 모듈로 접근
from econkit.factors.grouped import compute, cs_zscore

# grouped 전용 함수는 econkit.factors.grouped.* 으로 접근
from econkit.factors import grouped  # noqa: F401
