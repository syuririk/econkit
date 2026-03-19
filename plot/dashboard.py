"""Plotly 대시보드 — 서브플롯 조합."""

from __future__ import annotations

from typing import List, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from econkit.plot._base import DEFAULT_PALETTE, DEFAULT_WIDTH, DEFAULT_HEIGHT


def overview(
    df,
    indicators: Optional[List[str]] = None,
    title: str = "경제지표 종합 개요",
    resample_freq: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """3행 서브플롯: 지수 레벨 / YoY / 이동 변동성."""
    palette = palette or DEFAULT_PALETTE
    cols = indicators or list(df.columns)
    data = df[cols].copy()
    if resample_freq:
        data = data.resample(resample_freq).mean()
    yoy = data.pct_change(4) * 100
    vol = data.rolling(4).std()

    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        subplot_titles=["지수 레벨", "YoY 변화율 (%)", "이동 변동성 (4기 rolling std)"],
        vertical_spacing=0.07, row_heights=[0.4, 0.35, 0.25],
    )
    for i, col in enumerate(cols):
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=data.index, y=data[col], name=col, mode="lines",
            line=dict(color=color, width=2), legendgroup=col,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=yoy.index, y=yoy[col], name=col, mode="lines",
            line=dict(color=color, width=2), legendgroup=col, showlegend=False,
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=vol.index, y=vol[col], name=col, mode="lines",
            line=dict(color=color, width=1.5, dash="dot"), legendgroup=col, showlegend=False,
        ), row=3, col=1)

    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#1e293b"), x=0.02),
        height=DEFAULT_HEIGHT * 2, width=DEFAULT_WIDTH,
        template="plotly_white", paper_bgcolor="white", plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=40, t=100, b=60),
    )
    return fig


def compare_panel(
    df,
    indicator_a: str,
    indicator_b: str,
    title: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """2×2 비교: Level, 누적%, YoY, Rolling corr."""
    palette = palette or DEFAULT_PALETTE
    sub = df[[indicator_a, indicator_b]]
    yoy = sub.pct_change(4) * 100
    norm = (sub - sub.iloc[0]) / sub.iloc[0] * 100
    rc = sub[indicator_a].rolling(4).corr(sub[indicator_b])
    ca, cb = palette[0], palette[1]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Level", "누적 변화 (%)", "YoY", "Rolling corr"],
        vertical_spacing=0.14, horizontal_spacing=0.1,
    )
    for row, source in [(1, sub), (2, yoy)]:
        for col_name, color in [(indicator_a, ca), (indicator_b, cb)]:
            fig.add_trace(go.Scatter(
                x=source.index, y=source[col_name], name=col_name, mode="lines",
                line=dict(color=color, width=2),
                legendgroup=col_name, showlegend=(row == 1),
            ), row=row, col=1)

    for col_name, color in [(indicator_a, ca), (indicator_b, cb)]:
        fig.add_trace(go.Scatter(
            x=norm.index, y=norm[col_name], name=col_name, mode="lines",
            line=dict(color=color, width=2), legendgroup=col_name, showlegend=False,
        ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=rc.index, y=rc, name="Rolling corr", mode="lines",
        line=dict(color=palette[2], width=2),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.08)", showlegend=False,
    ), row=2, col=2)

    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=2, col=1)
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=2, col=2)
    fig.update_layout(
        title=dict(text=title or f"{indicator_a} vs {indicator_b}", font=dict(size=16, color="#1e293b"), x=0.02),
        height=DEFAULT_HEIGHT * 2, width=DEFAULT_WIDTH,
        template="plotly_white", paper_bgcolor="white", plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0),
    )
    return fig


def lead_lag_panel(
    df,
    indicator_a: str,
    indicator_b: str,
    max_lag: int = 4,
    title: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """YoY 오버레이 + lag별 상관계수."""
    palette = palette or DEFAULT_PALETTE
    yoy_a = df[indicator_a].pct_change(4) * 100
    yoy_b = df[indicator_b].pct_change(4) * 100

    lags = list(range(-max_lag, max_lag + 1))
    corrs = [
        yoy_a.corr(yoy_b.shift(-lag)) if lag < 0 else yoy_a.shift(lag).corr(yoy_b)
        for lag in lags
    ]
    best_lag = lags[int(np.argmax(np.abs(corrs)))]
    bar_colors = [palette[0] if v >= 0 else palette[1] for v in corrs]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["YoY 변화율 오버레이", f"Lag별 상관계수 (best lag={best_lag})"],
        horizontal_spacing=0.12,
    )
    for series, label, color in [
        (yoy_a, indicator_a, palette[0]),
        (yoy_b, indicator_b, palette[1]),
    ]:
        fig.add_trace(go.Scatter(
            x=series.index, y=series, name=label, mode="lines",
            line=dict(color=color, width=2),
        ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=lags, y=corrs, marker_color=bar_colors, name="상관계수", showlegend=False,
    ), row=1, col=2)

    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=1, col=1)
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#94a3b8", row=1, col=2)
    fig.update_layout(
        title=dict(
            text=title or f"{indicator_a} ↔ {indicator_b} 리드-래그 분석",
            font=dict(size=16, color="#1e293b"), x=0.02,
        ),
        height=DEFAULT_HEIGHT, width=DEFAULT_WIDTH,
        template="plotly_white", paper_bgcolor="white", plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0),
    )
    return fig
