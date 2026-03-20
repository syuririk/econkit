"""Plotly 히트맵."""

from __future__ import annotations

from typing import Optional, List, cast

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from econkit.plot._base import base_layout


def corr_heatmap(
    df, method: str = "pearson", title: str = "지표 간 상관관계",
) -> go.Figure:
    corr = df.corr(method=method).round(3)
    labels = corr.columns.tolist()
    h = max(400, len(labels) * 80)

    fig = go.Figure(go.Heatmap(
        z=corr.values, x=labels, y=labels,
        colorscale="RdYlGn", zmin=-1, zmax=1,
        text=corr.values.round(2), texttemplate="%{text}",
        textfont=dict(size=11),
        colorbar=dict(title="상관계수", thickness=15),
    ))
    fig.update_layout(**base_layout(title=title, height=h))
    fig.update_xaxes(tickangle=30)
    return fig


def seasonal_heatmap(
    df, indicator: str, title: Optional[str] = None,
) -> go.Figure:
    """연도 × 분기 YoY 변화율 히트맵."""
    yoy = df[indicator].pct_change(4) * 100
    idx = cast(pd.DatetimeIndex, yoy.index)
    pivot = (
        pd.DataFrame({"value": yoy, "year": idx.year, "quarter": idx.quarter})
        .pivot(index="year", columns="quarter", values="value")
    )
    pivot.columns = [f"Q{q}" for q in pivot.columns]
    z = pivot.values.round(2)
    text = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z]
    h = max(400, len(pivot) * 45)

    fig = go.Figure(go.Heatmap(
        z=z, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale="RdYlGn", zmid=0,
        text=text, texttemplate="%{text}", textfont=dict(size=11),
        colorbar=dict(title="YoY (%)", thickness=15),
    ))
    fig.update_layout(**base_layout(
        title=title or f"{indicator} — 연도×분기 YoY (%)",
        xaxis_title="분기", yaxis_title="연도", height=h,
    ))
    return fig


def yoy_heatmap(df, periods: int = 4, title: str = "지표별 YoY 변화율 히트맵") -> go.Figure:
    yoy = df.pct_change(periods) * 100
    idx = cast(pd.DatetimeIndex, yoy.index)
    z = yoy.T.values.round(2)
    text = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z]
    h = max(300, len(yoy.columns) * 60)

    fig = go.Figure(go.Heatmap(
        z=z, x=idx.strftime("%Y-%m").tolist(), y=yoy.columns.tolist(),
        colorscale="RdYlGn", zmid=0,
        text=text, texttemplate="%{text}", textfont=dict(size=9),
        colorbar=dict(title="YoY (%)", thickness=15),
    ))
    fig.update_layout(**base_layout(title=title, height=h, xaxis_title="날짜"))
    fig.update_xaxes(tickangle=45)
    return fig


def rolling_corr_heatmap(
    df, indicator_a: str, indicator_b: str,
    windows: Optional[List[int]] = None, title: Optional[str] = None,
) -> go.Figure:
    """다양한 window 크기의 이동 상관계수 히트맵."""
    windows = windows or [2, 3, 4, 6, 8]
    idx = cast(pd.DatetimeIndex, df.index)
    z = [
        df[indicator_a].rolling(w).corr(df[indicator_b]).round(3).values
        for w in windows
    ]
    h = max(300, len(windows) * 60)

    fig = go.Figure(go.Heatmap(
        z=z, x=idx.strftime("%Y-%m").tolist(),
        y=[f"window={w}" for w in windows],
        colorscale="RdYlGn", zmid=0, zmin=-1, zmax=1,
        colorbar=dict(title="상관계수", thickness=15),
    ))
    fig.update_layout(**base_layout(
        title=title or f"{indicator_a} × {indicator_b} — Rolling 상관계수",
        xaxis_title="날짜", yaxis_title="Window", height=h,
    ))
    fig.update_xaxes(tickangle=45)
    return fig
