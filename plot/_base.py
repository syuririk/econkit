"""Plotly 차트 공통 설정."""

from __future__ import annotations

from typing import Optional

import plotly.graph_objects as go


DEFAULT_PALETTE = [
    "#2563EB", "#DC2626", "#16A34A", "#D97706",
    "#7C3AED", "#0891B2", "#DB2777", "#65A30D",
]

DEFAULT_THEME = "plotly_white"
DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 500


def base_layout(
    title: str = "",
    xaxis_title: str = "",
    yaxis_title: str = "",
    width: Optional[int] = None,
    height: Optional[int] = None,
    theme: str = DEFAULT_THEME,
) -> dict:
    """공통 Plotly 레이아웃 설정."""
    return dict(
        title=dict(text=title, font=dict(size=16, color="#1e293b"), x=0.02),
        xaxis=dict(title=xaxis_title, showgrid=True, gridcolor="#e2e8f0", zeroline=False),
        yaxis=dict(title=yaxis_title, showgrid=True, gridcolor="#e2e8f0", zeroline=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color="#334155"),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#e2e8f0", borderwidth=1,
        ),
        width=width or DEFAULT_WIDTH,
        height=height or DEFAULT_HEIGHT,
        hovermode="x unified",
        margin=dict(l=60, r=40, t=80, b=60),
        template=theme,
    )


def save_html(fig: go.Figure, path: str) -> None:
    """Figure를 HTML로 저장."""
    fig.write_html(path)
    print(f"저장 완료 (HTML): {path}")


def save_image(fig: go.Figure, path: str, scale: int = 2) -> None:
    """Figure를 이미지로 저장."""
    fig.write_image(path, scale=scale)
    print(f"저장 완료 (Image): {path}")
