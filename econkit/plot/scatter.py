"""Plotly 산포도."""

from __future__ import annotations

from typing import List, Optional, cast

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from econkit.plot._base import base_layout, DEFAULT_PALETTE, DEFAULT_WIDTH, DEFAULT_HEIGHT


def scatter(
    df, x: str, y: str,
    color: Optional[str] = None,
    title: Optional[str] = None,
    add_trend: bool = False,
    resample_freq: Optional[str] = None,
    palette: list = None,
) -> go.Figure:
    """두 지표 산점도."""
    palette = palette or DEFAULT_PALETTE
    cols = [x, y] + ([color] if color else [])
    data = df[cols].copy()
    if resample_freq:
        data = data.resample(resample_freq).mean()
    data = data.dropna()

    fig = go.Figure()
    if color:
        marker_kwargs = dict(
            color=data[color], colorscale="Viridis", showscale=True,
            colorbar=dict(title=color), size=6,
        )
    else:
        marker_kwargs = dict(color=palette[0], size=6)

    fig.add_trace(go.Scatter(
        x=data[x], y=data[y], mode="markers", marker=marker_kwargs,
        hovertemplate=f"<b>%{{text}}</b><br>{x}: %{{x:.2f}}<br>{y}: %{{y:.2f}}<extra></extra>",
        text=cast(pd.DatetimeIndex, data.index).strftime("%Y-%m"),
    ))

    if add_trend and len(data) >= 2:
        a, b = np.polyfit(data[x], data[y], 1)
        xs = np.array([data[x].min(), data[x].max()])
        ys = a * xs + b
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines",
            line=dict(color=palette[1], dash="dash"),
            name="trend", hoverinfo="skip",
        ))

    corr = data[x].corr(data[y])
    t = title or f"{x} vs {y}"
    fig.update_layout(
        **base_layout(title=f"{t} (corr={corr:.2f})"),
        xaxis_title=x, yaxis_title=y,
    )
    return fig


def corr_scatter(
    df, indicator_a: str, indicator_b: str,
    title: Optional[str] = None, add_trend: bool = True,
    palette: list = None,
) -> go.Figure:
    """상관계수 포함 산점도."""
    return scatter(df, indicator_a, indicator_b, title=title, add_trend=add_trend, palette=palette)


def scatter_matrix(
    df, indicators: Optional[List[str]] = None,
    title: str = "지표 산점도 매트릭스",
) -> go.Figure:
    """페어와이즈 산점도 행렬."""
    cols = indicators or list(df.columns)
    data = df[cols].dropna()
    fig = px.scatter_matrix(data, dimensions=cols, title=title, template="plotly_white")
    fig.update_layout(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT)
    return fig
