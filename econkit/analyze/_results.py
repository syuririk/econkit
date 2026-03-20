"""분석 결과 데이터 컨테이너."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ForecastResult:
    """예측 결과 컨테이너."""
    indicator: str
    forecast: pd.Series
    lower: pd.Series
    upper: pd.Series
    method: str
    confidence: float = 0.95


@dataclass
class DecompositionResult:
    """시계열 분해 결과 컨테이너."""
    indicator: str
    observed: pd.Series
    trend: pd.Series
    seasonal: pd.Series
    residual: pd.Series
    strength_trend: float = field(init=False)
    strength_seasonal: float = field(init=False)

    def __post_init__(self):
        var_r = self.residual.var()
        self.strength_trend = max(0, 1 - var_r / (self.trend + self.residual).var())
        self.strength_seasonal = max(0, 1 - var_r / (self.seasonal + self.residual).var())
