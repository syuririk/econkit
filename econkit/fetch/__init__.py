"""
econkit.fetch — 외부 API 데이터 수집 모듈.

Providers:
    econkit.fetch.ecos  — 한국은행 경제통계시스템
    econkit.fetch.fisis — 금융감독원 금융통계정보시스템
    econkit.fetch.fred  — 미국 연방준비은행 FRED
    econkit.fetch.oecd  — OECD Data Explorer (API 키 불필요)
"""

from econkit.fetch import ecos  # noqa: F401
from econkit.fetch import fisis  # noqa: F401
from econkit.fetch import fred  # noqa: F401
from econkit.fetch import oecd  # noqa: F401