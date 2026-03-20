"""Plotly 라인 차트."""

from __future__ import annotations

from typing import List, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from econkit.plot._base import base_layout, DEFAULT_PALETTE, DEFAULT_HEIGHT, DEFAULT_WIDTH
from econkit.analyze._results import ForecastResult, DecompositionResult


def multi_line(
    df,
    indicators: Optional[List[str]] = None,
    title: str = "경제지표 추이",
    normalize: bool = False,
    ma_window: Optional[int] = None,
    resample_freq: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """여러 지표 동시 라인 플롯."""
    palette = palette or DEFAULT_PALETTE
    cols = indicators or list(df.columns)
    data = df[cols].copy()
    if resample_freq:
        data = data.resample(resample_freq).mean()
    if normalize:
        data = (data - data.iloc[0]) / data.iloc[0] * 100

    fig = go.Figure()
    for i, col in enumerate(cols):
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=data.index, y=data[col], name=col, mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}<extra></extra>",
        ))
        if ma_window:
            fig.add_trace(go.Scatter(
                x=data.index, y=data[col].rolling(ma_window).mean(),
                name=f"{col} MA{ma_window}", mode="lines",
                line=dict(color=color, width=1.5, dash="dash"),
                opacity=0.6,
            ))

    ylabel = "기준 대비 변화(%)" if normalize else "지수"
    fig.update_layout(**base_layout(title=title, yaxis_title=ylabel))
    return fig


def yoy_line(
    df,
    indicators: Optional[List[str]] = None,
    periods: int = 4,
    title: str = "전년 동기 대비 변화율 (%)",
    resample_freq: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    palette = palette or DEFAULT_PALETTE
    cols = indicators or list(df.columns)
    data = df[cols].copy()
    if resample_freq:
        data = data.resample(resample_freq).mean()
    yoy = data.pct_change(periods=periods) * 100

    fig = go.Figure()
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
    for i, col in enumerate(cols):
        fig.add_trace(go.Scatter(
            x=yoy.index, y=yoy[col], name=col, mode="lines",
            line=dict(color=palette[i % len(palette)], width=2),
            hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
        ))
    fig.update_layout(**base_layout(title=title, yaxis_title="YoY 변화율 (%)"))
    return fig


def qoq_line(
    df,
    indicators: Optional[List[str]] = None,
    title: str = "전분기 대비 변화율 (%)",
    resample_freq: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    palette = palette or DEFAULT_PALETTE
    cols = indicators or list(df.columns)
    data = df[cols].copy()
    if resample_freq:
        data = data.resample(resample_freq).mean()
    q = data.pct_change(periods=1) * 100

    fig = go.Figure()
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
    for i, col in enumerate(cols):
        fig.add_trace(go.Scatter(
            x=q.index, y=q[col], name=col, mode="lines+markers",
            line=dict(color=palette[i % len(palette)], width=2),
            marker=dict(size=5),
            hovertemplate=f"<b>{col}</b><br>%{{x|%Y-%m}}: %{{y:.2f}}%<extra></extra>",
        ))
    fig.update_layout(**base_layout(title=title, yaxis_title="QoQ 변화율 (%)"))
    return fig


def forecast_line(
    df,
    indicator: str,
    forecast_result: ForecastResult,
    title: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """실제값 + 예측값 + 신뢰구간."""
    palette = palette or DEFAULT_PALETTE
    s = df[indicator].dropna()
    fr = forecast_result
    t = title or f"{indicator} — {fr.method} 예측"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=s.index, y=s, name="실제값", mode="lines",
        line=dict(color=palette[0], width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=list(fr.upper.index) + list(fr.lower.index[::-1]),
        y=list(fr.upper.values) + list(fr.lower.values[::-1]),
        fill="toself", fillcolor="rgba(220,38,38,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name=f"{int(fr.confidence*100)}% 신뢰구간",
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=fr.forecast.index, y=fr.forecast, name="예측값",
        mode="lines+markers",
        line=dict(color=palette[1], width=2, dash="dash"),
        marker=dict(size=6, symbol="circle-open"),
    ))
    fig.update_layout(**base_layout(title=t, yaxis_title="지수"))
    return fig


def decomposition_plot(
    decomp_result: DecompositionResult,
    palette: list = None,
) -> go.Figure:
    """분해 결과 4분할 차트."""
    palette = palette or DEFAULT_PALETTE
    dr = decomp_result
    components = [
        (dr.observed, "관측값"),
        (dr.trend, "추세"),
        (dr.seasonal, "계절성"),
        (dr.residual, "잔차"),
    ]
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        subplot_titles=[label for _, label in components],
        vertical_spacing=0.06,
    )
    for row, (data, label) in enumerate(components, start=1):
        fig.add_trace(go.Scatter(
            x=data.index, y=data, name=label, mode="lines",
            line=dict(color=palette[row - 1], width=1.8),
        ), row=row, col=1)

    fig.update_layout(
        title=dict(
            text=(
                f"{dr.indicator} — 시계열 분해 "
                f"(추세 강도: {dr.strength_trend:.2f}, "
                f"계절성 강도: {dr.strength_seasonal:.2f})"
            ),
            font=dict(size=15, color="#1e293b"), x=0.02,
        ),
        height=DEFAULT_HEIGHT * 2, width=DEFAULT_WIDTH,
        showlegend=False, template="plotly_white",
        paper_bgcolor="white", plot_bgcolor="white",
    )
    return fig


def cumulative_line(
    df,
    indicators: Optional[List[str]] = None,
    base_period: Optional[str] = None,
    title: str = "기준 시점 대비 누적 변화율 (%)",
    palette: list = None,
) -> go.Figure:
    palette = palette or DEFAULT_PALETTE
    cols = indicators or list(df.columns)
    data = df[cols].copy()
    base = data.loc[base_period] if base_period else data.iloc[0]
    cumul = (data / base - 1) * 100

    fig = go.Figure()
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
    for i, col in enumerate(cols):
        fig.add_trace(go.Scatter(
            x=cumul.index, y=cumul[col], name=col, mode="lines",
            line=dict(color=palette[i % len(palette)], width=2),
        ))
    fig.update_layout(**base_layout(title=title, yaxis_title="누적 변화율 (%)"))
    return fig
