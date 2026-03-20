"""한국은행 ECOS API 클라이언트."""

from __future__ import annotations

import re
from typing import Optional, List

import pandas as pd

from econkit.fetch._base import BaseClient, APIError
from econkit.fetch._parsers import parse_time


_ERR_DICT = {
    "INFO-100": "인증키가 유효하지 않습니다.",
    "INFO-200": "해당하는 데이터가 없습니다.",
    "ERROR-100": "필수 값이 누락되어 있습니다.",
    "ERROR-101": "주기와 다른 형식의 날짜 형식입니다.",
    "ERROR-200": "파일타입 값이 누락 혹은 유효하지 않습니다.",
    "ERROR-300": "조회건수 값이 누락되어 있습니다.",
    "ERROR-400": "검색범위 초과로 60초 TIMEOUT이 발생했습니다.",
    "ERROR-500": "서버 오류입니다.",
    "ERROR-600": "DB Connection 오류입니다.",
    "ERROR-601": "SQL 오류입니다.",
    "ERROR-602": "과도한 호출로 이용이 제한되었습니다.",
}


class EcosClient(BaseClient):
    """한국은행 ECOS API 클라이언트."""

    BASE_URL = "https://ecos.bok.or.kr/api"

    def _check_error(self, data: dict) -> None:
        if data.get("RESULT"):
            err_cd = data["RESULT"].get("CODE", "")
            msg = _ERR_DICT.get(err_cd, "API Error")
            raise APIError(f"[{err_cd}] {msg}")

    def _url(self, service: str, *parts, count: int = 100000) -> str:
        base = f"{self.BASE_URL}/{service}/{self.api_key}/json/kr/1/{count}"
        if parts:
            base += "/" + "/".join(str(p) for p in parts)
        return base

    # ── services ──────────────────────────────────────────────

    def _statistic_search(
        self, stat_code: str, cycle: str, start: str, end: str,
        item1: str = "?", item2: str = "?", item3: str = "?", item4: str = "?",
    ) -> list[dict]:
        url = self._url(
            "StatisticSearch", stat_code, cycle, start, end,
            item1, item2, item3, item4,
        )
        data = self._get(url)
        return data.get("StatisticSearch", {}).get("row", [])

    def _statistic_table_list(self, stat_code: Optional[str] = None) -> list[dict]:
        if stat_code:
            url = self._url("StatisticTableList", stat_code)
        else:
            url = self._url("StatisticTableList")
        data = self._get(url)
        return data.get("StatisticTableList", {}).get("row", [])

    def _statistic_item_list(self, stat_code: str) -> list[dict]:
        url = self._url("StatisticItemList", stat_code)
        data = self._get(url)
        return data.get("StatisticItemList", {}).get("row", [])

    def _key_statistic_list(self, count: int = 200) -> list[dict]:
        url = self._url("KeyStatisticList", count=count)
        data = self._get(url)
        return data.get("KeyStatisticList", {}).get("row", [])

    def _statistic_word(self, word: str) -> list[dict]:
        url = self._url("StatisticWord", word, count=1000)
        data = self._get(url)
        return data.get("StatisticWord", {}).get("row", [])

    def _statistic_meta(self, data_name: str) -> list[dict]:
        url = self._url("StatisticMeta", data_name)
        data = self._get(url)
        return data.get("StatisticMeta", {}).get("row", [])

    # ── endpoints (public) ────────────────────────────────────

    def get_data(self, codes: list, start_date: str, end_date: str) -> pd.DataFrame:
        """통계 데이터 조회.

        Parameters
        ----------
        codes : list
            각 원소는 [cycle, stat_code, item1?, item2?, ...] 형태의 리스트.
        start_date, end_date : str
            YYYYMMDD 형식.
        """
        period_map = {
            "A": lambda d: d[:4],
            "Q": lambda d: d[:4] + "Q1",
            "M": lambda d: d[:6],
            "D": lambda d: d,
            "S": lambda d: d[:4] + "S1",
            "SM": lambda d: d[:6] + "S1",
        }

        dfs: list[pd.DataFrame] = []
        for code in codes:
            code = list(code)  # copy
            try:
                cycle = code.pop(0)
                start_var = period_map[cycle](start_date)
                end_var = period_map[cycle](end_date)

                code += [None] * (5 - len(code))
                rows = self._statistic_search(
                    stat_code=code[0], cycle=cycle,
                    start=start_var, end=end_var,
                    item1=code[1] or "?", item2=code[2] or "?",
                    item3=code[3] or "?", item4=code[4] or "?",
                )

                stat_name = re.sub(r"^[\d\.]+\s*", "", rows[0]["STAT_NAME"])
                df = pd.DataFrame(rows)
                df["TIME"] = df["TIME"].map(parse_time)
                df = df.rename(columns={"TIME": "date"})
                df["DATA_VALUE"] = pd.to_numeric(df["DATA_VALUE"], errors="coerce")

                name_cols = ["ITEM_NAME1", "ITEM_NAME2", "ITEM_NAME3", "ITEM_NAME4"]
                df["stat_name"] = df[name_cols].apply(
                    lambda row: f"{stat_name}_" + "_".join(
                        str(v).strip() for v in row if v
                    ),
                    axis=1,
                )

                pivot = df.pivot_table(
                    index="date", columns="stat_name",
                    values="DATA_VALUE", aggfunc="first",
                )
                pivot = pivot.rename_axis(None, axis=1).sort_index()
                dfs.append(pivot)
            except Exception as e:
                print(f"fail to download {code} - {e}")

        if not dfs:
            return pd.DataFrame()
        result = pd.concat(dfs, axis=1).reset_index().rename(columns={"index": "date"})
        return result

    def get_key_stats(self) -> pd.DataFrame:
        """100대 주요 통계지표 조회."""
        return pd.DataFrame(self._key_statistic_list())

    def search_stats(
        self, keyword: str,
        sub_col: Optional[str] = None,
        col_val: Optional[str] = None,
    ) -> pd.DataFrame:
        """통계 테이블 검색."""
        all_tables = self._statistic_table_list()

        candidate_dict = {}
        for row in all_tables:
            if keyword in row.get("STAT_NAME", ""):
                candidate_dict[row["STAT_NAME"]] = row

        result = {}
        for name, val in candidate_dict.items():
            result[name] = val
            try:
                detail = self._statistic_item_list(val["STAT_CODE"])
                for line in detail:
                    if sub_col:
                        if line.get(sub_col) == col_val:
                            result[f"{name} - {line['ITEM_NAME']}"] = line
                    else:
                        result[f"{name} - {line['ITEM_NAME']}"] = line
            except Exception:
                pass

        return pd.DataFrame(result).T

    def search_word(self, word: str) -> list[dict]:
        """용어 사전 검색."""
        return self._statistic_word(word)


# ── 모듈 레벨 편의 인터페이스 ────────────────────────────────

_client: Optional[EcosClient] = None


def _get_client() -> EcosClient:
    if _client is None:
        raise ValueError("API key가 설정되지 않았습니다. econkit.fetch.ecos.set_api_key()를 먼저 호출하세요.")
    return _client


def set_api_key(key: str) -> None:
    """ECOS API 키 설정."""
    global _client
    _client = EcosClient(api_key=key)


def get_data(codes: list, start_date: str, end_date: str) -> pd.DataFrame:
    """통계 데이터 조회."""
    return _get_client().get_data(codes, start_date, end_date)


def get_key_stats() -> pd.DataFrame:
    """100대 주요 통계지표 조회."""
    return _get_client().get_key_stats()


def search_stats(keyword: str, sub_col: str = None, col_val: str = None) -> pd.DataFrame:
    """통계 테이블 검색."""
    return _get_client().search_stats(keyword, sub_col, col_val)


def search_word(word: str) -> list[dict]:
    """용어 사전 검색."""
    return _get_client().search_word(word)
