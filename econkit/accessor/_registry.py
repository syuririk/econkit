"""EconAccessor — pandas DataFrame에 .econ 확장 등록."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from econkit.accessor._validate import validate_econ_df
from econkit.accessor._stats import summary_df, describe_ext
from econkit.accessor._change import pct_change, diff, rolling_std, yoy, qoq, mom
from econkit.accessor._transform import TransformAccessor


@pd.api.extensions.register_dataframe_accessor("econ")
class EconAccessor:
    """
    경제 데이터 분석을 위한 pandas DataFrame accessor.

    Usage
    -----
    >>> import econkit
    >>> df.econ.yoy()
    >>> df.econ.summary()
    >>> df.econ.transform.normalize('minmax')
    >>> df.econ.analyze.lead_lag('총지수', '식료품')
    >>> df.econ.forecast.linear_trend('총지수', steps=4)
    >>> df.econ.plot.overview()
    """

    def __init__(self, df: pd.DataFrame):
        self._df = df

    # ── 검증 ──────────────────────────────────────────────────

    def validate(self) -> None:
        """데이터 유효성 검사 (DatetimeIndex, 수치형, 결측값, 중복)."""
        validate_econ_df(self._df)

    # ── 기초통계 ──────────────────────────────────────────────

    def summary(self) -> pd.DataFrame:
        """전체 지표 요약 통계."""
        return summary_df(self._df)

    def describe_ext(self) -> pd.DataFrame:
        """확장 describe (skewness, kurtosis 포함)."""
        return describe_ext(self._df)

    # ── 변화율 (보간 로직 보존) ───────────────────────────────

    def pct_change(self, periods: int = 1) -> pd.DataFrame:
        """보간 인덱스 기반 백분율 변화율."""
        return pct_change(self._df, periods)

    def diff(self, periods: int = 1) -> pd.DataFrame:
        """보간 인덱스 기반 차분."""
        return diff(self._df, periods)

    def rolling_std(self, window: int, offset: int = 1) -> pd.DataFrame:
        """보간 인덱스 기반 롤링 표준편차."""
        return rolling_std(self._df, window, offset)

    def yoy(self) -> pd.DataFrame:
        """Year-over-year 변화율 (%)."""
        return yoy(self._df)

    def qoq(self) -> pd.DataFrame:
        """Quarter-over-quarter 변화율 (%)."""
        return qoq(self._df)

    def mom(self) -> pd.DataFrame:
        """Month-over-month 변화율 (%)."""
        return mom(self._df)

    # ── 서브-accessor (lazy) ──────────────────────────────────

    @property
    def transform(self) -> TransformAccessor:
        """데이터 변환: normalize, rebase, log, diff, pct_change, compute_factors."""
        return TransformAccessor(self._df)

    @property
    def analyze(self):
        """분석: 기술통계, 비교, 시계열."""
        from econkit.analyze import AnalyzeAccessor
        return AnalyzeAccessor(self._df)

    @property
    def forecast(self):
        """예측: linear_trend, arima, ma_extension."""
        from econkit.analyze import ForecastAccessor
        return ForecastAccessor(self._df)

    @property
    def plot(self):
        """시각화: line, bar, heatmap, scatter, dashboard."""
        from econkit.plot import PlotAccessor
        return PlotAccessor(self._df)
