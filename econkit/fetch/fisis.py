"""금융감독원 FISIS API 클라이언트."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from econkit.fetch._base import BaseClient, APIError
from econkit.fetch._parsers import pivot_stat_info


_ERR_DICT = {
    "000": "정상",
    "010": "미등록 인증키",
    "011": "중지된 인증키",
    "012": "삭제된 인증키",
    "013": "샘플 인증키",
    "020": "일일검색 허용횟수 초과",
    "021": "허용된 IP가 아님",
    "022": "허용된 언어가 아님",
    "100": "요청값 누락",
    "101": "잘못된 요청값",
    "102": "시작일이 종료일보다 큼",
    "103": "검색 기간은 40분기를 초과할 수 없음",
    "900": "정의되지 않은 오류",
}


class FisisClient(BaseClient):
    """금융감독원 FISIS API 클라이언트."""

    BASE_URL = "http://fisis.fss.or.kr/openapi"

    def _check_error(self, data: dict) -> None:
        result = data.get("result", {})
        err_cd = result.get("err_cd")
        if err_cd and err_cd != "000":
            msg = _ERR_DICT.get(err_cd, "API Error")
            raise APIError(f"[{err_cd}] {msg}")

    def _url(self, service: str, **params) -> str:
        params["auth"] = self.api_key
        params["lang"] = "kr"
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.BASE_URL}/{service}.json?{qs}"

    # ── services ──────────────────────────────────────────────

    def _statistics_info_search(self, **params) -> list[dict]:
        url = self._url("statisticsInfoSearch", **params)
        return self._get(url).get("result", {}).get("list", [])

    def _statistics_list_search(self, lrg_div: str, sml_div: str) -> list[dict]:
        url = self._url("statisticsListSearch", lrgDiv=lrg_div, smlDiv=sml_div)
        return self._get(url).get("result", {}).get("list", [])

    def _account_list_search(self, list_no: str) -> list[dict]:
        url = self._url("accountListSearch", listNo=list_no)
        return self._get(url).get("result", {}).get("list", [])

    def _company_search(self, part_div: str) -> list[dict]:
        url = self._url("companySearch", partDiv=part_div)
        return self._get(url).get("result", {}).get("list", [])

    # ── endpoints (public) ────────────────────────────────────

    def get_data(self, codes: list, start_date: str, end_date: str) -> pd.DataFrame:
        """금융통계 데이터 조회.

        Parameters
        ----------
        codes : list
            각 원소는 [finance_cd, list_no, account_cd, term] 형태.
        start_date, end_date : str
            YYYYMM 형식.
        """
        dfs: list[pd.DataFrame] = []
        for code in codes:
            finance_cd, list_no, account_cd, term = code
            rows = self._statistics_info_search(
                financeCd=finance_cd, listNo=list_no,
                accountCd=account_cd, term=term,
                startBaseMm=start_date, endBaseMm=end_date,
            )
            df = pd.DataFrame(rows)
            df = pivot_stat_info(df).set_index(["date", "finance_cd"])
            dfs.append(df)

        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, axis=1).reset_index()

    def search_company(self, div: str) -> pd.DataFrame:
        """금융회사 검색.

        div 코드: A=국내은행, J=외은지점, H=생명보험, I=손해보험,
        F=투자매매중개업자Ⅰ, W=투자매매중개업자Ⅱ, G=집합투자업자, ...
        """
        return pd.DataFrame(self._company_search(div))

    def search_stat(self, list_no: str) -> pd.DataFrame:
        """계정 목록 검색."""
        return pd.DataFrame(self._account_list_search(list_no))

    def search_stats(
        self, lrg_div: str, sml_div: str, details: bool = False,
    ) -> pd.DataFrame:
        """통계 목록 검색.

        lrg_div: 대분류, sml_div: 소분류.
        details=True 시 하위 계정까지 조회.
        """
        if details:
            stats = self._statistics_list_search(lrg_div, sml_div)
            stats_df = pd.DataFrame(stats)
            dfs = []
            for list_no in stats_df["list_no"]:
                accts = self._account_list_search(list_no)
                dfs.append(pd.DataFrame(accts))
            if dfs:
                return pd.concat(dfs)[["list_no", "account_cd", "list_nm", "account_nm"]]
            return pd.DataFrame()
        else:
            return pd.DataFrame(self._statistics_list_search(lrg_div, sml_div))


# ── 모듈 레벨 편의 인터페이스 ────────────────────────────────

_client: Optional[FisisClient] = None


def _get_client() -> FisisClient:
    if _client is None:
        raise ValueError("API key가 설정되지 않았습니다. econkit.fetch.fisis.set_api_key()를 먼저 호출하세요.")
    return _client


def set_api_key(key: str) -> None:
    """FISIS API 키 설정."""
    global _client
    _client = FisisClient(api_key=key)


def get_data(codes: list, start_date: str, end_date: str) -> pd.DataFrame:
    return _get_client().get_data(codes, start_date, end_date)


def search_company(div: str) -> pd.DataFrame:
    return _get_client().search_company(div)


def search_stat(list_no: str) -> pd.DataFrame:
    return _get_client().search_stat(list_no)


def search_stats(lrg_div: str, sml_div: str, details: bool = False) -> pd.DataFrame:
    return _get_client().search_stats(lrg_div, sml_div, details)
