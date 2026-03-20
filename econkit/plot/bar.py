"""Plotly 바 차트."""

from __future__ import annotations

from typing import List, Optional, Tuple

import plotly.graph_objects as go

from econkit.plot._base import base_layout, DEFAULT_PALETTE


def yoy_bar(
    df, indicator: str, periods: int = 4,
    title: Optional[str] = None, resample_freq: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """단일 지표 YoY 변화율 바 차트."""
    palette = palette or DEFAULT_PALETTE
    data = df[[indicator]].copy()
    if resample_freq:
        data = data.resample(resample_freq).mean()
    yoy = data.pct_change(periods)[indicator] * 100
    colors = [palette[0] if v >= 0 else palette[1] for v in yoy]

    fig = go.Figure(go.Bar(x=yoy.index, y=yoy, marker_color=colors))
    fig.add_hline(y=0, line_width=1, line_color="#94a3b8")
    fig.update_layout(**base_layout(
        title=title or f"{indicator} — YoY 변화율 (%)",
        yaxis_title="YoY 변화율 (%)",
    ))
    return fig


def grouped_bar(
    df, indicators: Optional[List[str]] = None, periods: int = 4,
    title: str = "지표별 YoY 변화율 비교", resample_freq: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    palette = palette or DEFAULT_PALETTE
    cols = indicators or list(df.columns)
    data = df[cols].copy()
    if resample_freq:
        data = data.resample(resample_freq).mean()
    yoy = data.pct_change(periods) * 100

    fig = go.Figure()
    for i, col in enumerate(cols):
        fig.add_trace(go.Bar(
            x=yoy.index, y=yoy[col], name=col,
            marker_color=palette[i % len(palette)],
        ))
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
    fig.update_layout(**base_layout(title=title, yaxis_title="YoY 변화율 (%)"), barmode="group")
    return fig


def period_compare_bar(
    df, period_a: Tuple[str, str], period_b: Tuple[str, str],
    stat: str = "mean", title: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """두 기간 통계량 비교 그룹 바."""
    palette = palette or DEFAULT_PALETTE
    a = getattr(df.loc[period_a[0]:period_a[1]], stat)()
    b = getattr(df.loc[period_b[0]:period_b[1]], stat)()
    la = f"{period_a[0]} ~ {period_a[1]}"
    lb = f"{period_b[0]} ~ {period_b[1]}"

    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(df.columns), y=a, name=la, marker_color=palette[0]))
    fig.add_trace(go.Bar(x=list(df.columns), y=b, name=lb, marker_color=palette[1]))
    fig.update_layout(**base_layout(title=title or f"기간 비교 ({stat})", yaxis_title="지수"), barmode="group")
    return fig


def contribution_bar(
    df, weights: Optional[dict] = None, periods: int = 4,
    title: str = "지표별 YoY 기여도", palette: list = None,
) -> go.Figure:
    """가중치 기반 YoY 기여도 스택 바."""
    palette = palette or DEFAULT_PALETTE
    cols = list(df.columns)
    w = weights or {c: 1 / len(cols) for c in cols}
    yoy = df[cols].pct_change(periods) * 100

    fig = go.Figure()
    for i, col in enumerate(cols):
        fig.add_trace(go.Bar(
            x=yoy.index, y=yoy[col] * w.get(col, 0), name=col,
            marker_color=palette[i % len(palette)],
        ))
    fig.add_hline(y=0, line_width=1, line_color="#94a3b8")
    fig.update_layout(**base_layout(title=title, yaxis_title="기여도 (%p)"), barmode="relative")
    return fig


def rank_bar(
    df, periods: int = 4, title: str = "최근 YoY 변화율 순위",
    palette: list = None,
) -> go.Figure:
    """최신 시점 YoY 변화율 가로 순위 바."""
    palette = palette or DEFAULT_PALETTE
    yoy_sorted = (df.pct_change(periods).iloc[-1] * 100).sort_values()
    colors = [palette[0] if v >= 0 else palette[1] for v in yoy_sorted]
    h = max(300, len(yoy_sorted) * 50)

    fig = go.Figure(go.Bar(
        x=yoy_sorted.values, y=yoy_sorted.index,
        orientation="h", marker_color=colors,
    ))
    fig.add_vline(x=0, line_width=1, line_color="#94a3b8")
    fig.update_layout(**base_layout(title=title, xaxis_title="YoY 변화율 (%)", height=h))
    return fig
