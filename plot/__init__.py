"""
econkit.plot — Plotly 기반 시각화 모듈.

PlotAccessor를 통해 df.econ.plot.* 로 접근.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

from econkit.plot import line, bar, heatmap, scatter, dashboard
from econkit.plot._base import DEFAULT_PALETTE, save_html, save_image
from econkit.analyze._results import ForecastResult, DecompositionResult


class PlotAccessor:
    """df.econ.plot — 시각화 서브-accessor."""

    def __init__(self, df: pd.DataFrame, palette: list = None):
        self._df = df
        self._palette = palette or DEFAULT_PALETTE

    # ── line ───────────────────────────────────────────────────

    def line(self, indicators=None, title="경제지표 추이", normalize=False, ma_window=None, resample_freq=None) -> go.Figure:
        """여러 지표 라인 플롯."""
        return line.multi_line(self._df, indicators, title, normalize, ma_window, resample_freq, self._palette)

    def yoy_line(self, indicators=None, periods=4, title="전년 동기 대비 변화율 (%)", resample_freq=None) -> go.Figure:
        return line.yoy_line(self._df, indicators, periods, title, resample_freq, self._palette)

    def qoq_line(self, indicators=None, title="전분기 대비 변화율 (%)", resample_freq=None) -> go.Figure:
        return line.qoq_line(self._df, indicators, title, resample_freq, self._palette)

    def forecast_line(self, indicator: str, forecast_result: ForecastResult, title=None) -> go.Figure:
        """실제값 + 예측 + 신뢰구간."""
        return line.forecast_line(self._df, indicator, forecast_result, title, self._palette)

    def decomposition(self, decomp_result: DecompositionResult) -> go.Figure:
        """시계열 분해 4분할 차트."""
        return line.decomposition_plot(decomp_result, self._palette)

    def cumulative(self, indicators=None, base_period=None, title="기준 시점 대비 누적 변화율 (%)") -> go.Figure:
        return line.cumulative_line(self._df, indicators, base_period, title, self._palette)

    # ── bar ────────────────────────────────────────────────────

    def yoy_bar(self, indicator: str, periods=4, title=None, resample_freq=None) -> go.Figure:
        return bar.yoy_bar(self._df, indicator, periods, title, resample_freq, self._palette)

    def grouped_bar(self, indicators=None, periods=4, title="지표별 YoY 비교", resample_freq=None) -> go.Figure:
        return bar.grouped_bar(self._df, indicators, periods, title, resample_freq, self._palette)

    def period_compare_bar(self, period_a: Tuple, period_b: Tuple, stat="mean", title=None) -> go.Figure:
        return bar.period_compare_bar(self._df, period_a, period_b, stat, title, self._palette)

    def contribution_bar(self, weights=None, periods=4, title="지표별 YoY 기여도") -> go.Figure:
        return bar.contribution_bar(self._df, weights, periods, title, self._palette)

    def rank_bar(self, periods=4, title="최근 YoY 변화율 순위") -> go.Figure:
        return bar.rank_bar(self._df, periods, title, self._palette)

    # ── heatmap ────────────────────────────────────────────────

    def corr_heatmap(self, method="pearson", title="지표 간 상관관계") -> go.Figure:
        return heatmap.corr_heatmap(self._df, method, title)

    def seasonal_heatmap(self, indicator: str, title=None) -> go.Figure:
        return heatmap.seasonal_heatmap(self._df, indicator, title)

    def yoy_heatmap(self, periods=4, title="지표별 YoY 변화율 히트맵") -> go.Figure:
        return heatmap.yoy_heatmap(self._df, periods, title)

    def rolling_corr_heatmap(self, indicator_a: str, indicator_b: str, windows=None, title=None) -> go.Figure:
        return heatmap.rolling_corr_heatmap(self._df, indicator_a, indicator_b, windows, title)

    # ── scatter ────────────────────────────────────────────────

    def scatter(self, x: str, y: str, color=None, title=None, add_trend=False, resample_freq=None) -> go.Figure:
        return scatter.scatter(self._df, x, y, color, title, add_trend, resample_freq, self._palette)

    def corr_scatter(self, indicator_a: str, indicator_b: str, title=None, add_trend=True) -> go.Figure:
        return scatter.corr_scatter(self._df, indicator_a, indicator_b, title, add_trend, self._palette)

    def scatter_matrix(self, indicators=None, title="지표 산점도 매트릭스") -> go.Figure:
        return scatter.scatter_matrix(self._df, indicators, title)

    # ── dashboard ──────────────────────────────────────────────

    def overview(self, indicators=None, title="경제지표 종합 개요", resample_freq=None) -> go.Figure:
        return dashboard.overview(self._df, indicators, title, resample_freq, self._palette)

    def compare_panel(self, indicator_a: str, indicator_b: str, title=None) -> go.Figure:
        return dashboard.compare_panel(self._df, indicator_a, indicator_b, title, self._palette)

    def lead_lag_panel(self, indicator_a: str, indicator_b: str, max_lag=4, title=None) -> go.Figure:
        return dashboard.lead_lag_panel(self._df, indicator_a, indicator_b, max_lag, title, self._palette)
