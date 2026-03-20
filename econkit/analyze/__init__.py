"""
econkit.analyze — 분석 모듈.

AnalyzeAccessor와 ForecastAccessor를 통해 df.econ.analyze / df.econ.forecast로 접근.
"""

from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd

from econkit.analyze._results import ForecastResult, DecompositionResult
from econkit.analyze import descriptive, comparative, timeseries, forecast


class AnalyzeAccessor:
    """df.econ.analyze — 기술통계, 비교 분석, 시계열 분석."""

    def __init__(self, df: pd.DataFrame):
        self._df = df

    # ── descriptive ───────────────────────────────────────────

    def describe_ext(self) -> pd.DataFrame:
        """확장 describe (skewness, kurtosis 포함)."""
        from econkit.accessor._stats import describe_ext
        return describe_ext(self._df)

    def cumulative(self, base_period: Optional[str] = None) -> pd.DataFrame:
        """기준 시점 대비 누적 변화율 (%)."""
        return descriptive.cumulative(self._df, base_period)

    def correlation(self, method: str = "pearson") -> pd.DataFrame:
        """지표 간 상관계수 행렬."""
        return descriptive.correlation(self._df, method)

    def correlation_with(self, target: str, lag: int = 0) -> pd.Series:
        """특정 지표와 나머지 지표 간 상관계수."""
        return descriptive.correlation_with(self._df, target, lag)

    def rank_by_change(self, periods: int = 4, ascending: bool = False) -> pd.DataFrame:
        """최근 YoY 변화율 기준 순위."""
        return descriptive.rank_by_change(self._df, periods, ascending)

    def contribution(self, weights: Optional[dict] = None, periods: int = 4) -> pd.DataFrame:
        """가중치 기반 기여도."""
        return descriptive.contribution(self._df, weights, periods)

    def period_compare(
        self,
        period_a: Tuple[str, str],
        period_b: Tuple[str, str],
        stat: str = "mean",
    ) -> pd.DataFrame:
        """두 기간의 통계량 비교."""
        return descriptive.period_compare(self._df, period_a, period_b, stat)

    # ── comparative ───────────────────────────────────────────

    def lead_lag(self, indicator_a: str, indicator_b: str, max_lag: int = 4) -> pd.Series:
        """리드-래그 상관계수."""
        return comparative.lead_lag(self._df, indicator_a, indicator_b, max_lag)

    def relative_performance(self, base_period: Optional[str] = None) -> pd.DataFrame:
        """기준 시점 대비 상대 성과 (%)."""
        return comparative.relative_performance(self._df, base_period)

    def dispersion(self) -> pd.DataFrame:
        """시점별 지표 간 분산도."""
        return comparative.dispersion(self._df)

    def rolling_correlation(
        self, indicator_a: str, indicator_b: str, window: int = 4,
    ) -> pd.Series:
        """두 지표 간 이동 상관계수."""
        return comparative.rolling_correlation(self._df, indicator_a, indicator_b, window)

    def pairwise_corr(
        self,
        period: Optional[Tuple[str, str]] = None,
        method: str = "pearson",
    ) -> pd.DataFrame:
        """전체 / 특정 기간의 지표 간 상관행렬."""
        return comparative.pairwise_corr(self._df, period, method)

    # ── timeseries ────────────────────────────────────────────

    def decompose(
        self, indicator: str, model: str = "additive", period: Optional[int] = None,
    ) -> DecompositionResult:
        """시계열 분해."""
        return timeseries.decompose(self._df, indicator, model, period)

    def decompose_all(self, **kwargs) -> dict[str, DecompositionResult]:
        """전체 지표 일괄 분해."""
        return timeseries.decompose_all(self._df, **kwargs)

    def detect_outliers(
        self, indicator: str, method: str = "zscore", threshold: float = 2.5,
    ) -> pd.Series:
        """이상값 탐지."""
        return timeseries.detect_outliers(self._df, indicator, method, threshold)

    def changepoints(
        self, indicator: str, window: int = 4, threshold_std: float = 1.5,
    ) -> pd.DatetimeIndex:
        """변곡점 탐지."""
        return timeseries.changepoints(self._df, indicator, window, threshold_std)

    def seasonal_pattern(self, indicator: str) -> pd.DataFrame:
        """계절성 패턴."""
        return timeseries.seasonal_pattern(self._df, indicator)

    def seasonal_adjustment(self, indicator: str) -> pd.Series:
        """계절 조정 시계열."""
        return timeseries.seasonal_adjustment(self._df, indicator)

    def rolling_volatility(self, indicator: str, window: int = 4) -> pd.Series:
        """이동 변동성."""
        return timeseries.rolling_volatility(self._df, indicator, window)

    def volatility_table(self, window: int = 4) -> pd.DataFrame:
        """전체 지표 이동 변동성 테이블."""
        return timeseries.volatility_table(self._df, window)


class ForecastAccessor:
    """df.econ.forecast — 단기 예측 모델."""

    def __init__(self, df: pd.DataFrame):
        self._df = df

    def linear_trend(
        self,
        indicator: str,
        steps: int = 4,
        window: Optional[int] = None,
        confidence: float = 0.95,
    ) -> ForecastResult:
        """선형 회귀 추세선 연장 예측."""
        return forecast.linear_trend(self._df, indicator, steps, window, confidence)

    def arima(
        self,
        indicator: str,
        steps: int = 4,
        order: tuple = (1, 1, 1),
        confidence: float = 0.95,
    ) -> ForecastResult:
        """ARIMA 예측."""
        return forecast.arima(self._df, indicator, steps, order, confidence)

    def ma_extension(
        self,
        indicator: str,
        window: int = 4,
        steps: int = 4,
    ) -> ForecastResult:
        """이동평균 수평 연장."""
        return forecast.ma_extension(self._df, indicator, window, steps)
