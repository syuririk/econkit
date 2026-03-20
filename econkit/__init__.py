"""
econkit — 경제 데이터 수집·처리·분석·시각화 유틸리티.

Usage:
    import econkit

    # accessor 자동 등록
    df.econ.yoy()
    df.econ.analyze.lead_lag('총지수', '식료품')
    df.econ.plot.overview()

    # fetch
    econkit.fetch.ecos.set_api_key("...")
    df = econkit.fetch.ecos.get_data(codes, "20200101", "20241231")

    # factors
    from econkit.factors import ratio_factor
"""

__version__ = "0.1.0"

# accessor 자동 등록
from econkit.accessor import _registry  # noqa: F401

# 서브패키지 접근
from econkit import fetch  # noqa: F401
from econkit import factors  # noqa: F401
