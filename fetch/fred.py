"""미국 연방준비은행 FRED API 클라이언트."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from econkit.fetch._base import BaseClient, APIError


class FredClient(BaseClient):
    """FRED API 클라이언트."""

    BASE_URL = "https://api.stlouisfed.org/fred"

    def _check_error(self, data: dict) -> None:
        err_cd = data.get("error_code")
        if err_cd:
            msg = data.get("error_message", "API Error")
            raise APIError(f"[{err_cd}] {msg}")

    def _url(self, endpoint: str, **params) -> str:
        params["api_key"] = self.api_key
        params["file_type"] = "json"
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.BASE_URL}/{endpoint}?{qs}"

    # ── services ──────────────────────────────────────────────

    def _series_observations(self, series_id: str, start: str, end: str) -> list[dict]:
        url = self._url(
            "series/observations",
            series_id=series_id, observation_start=start, observation_end=end,
        )
        return self._get(url).get("observations", [])

    def _category(self, category_id) -> list[dict]:
        url = self._url("category", category_id=category_id)
        return self._get(url).get("categories", [])

    def _category_children(self, category_id, start_date=None, end_date=None) -> list[dict]:
        params = {"category_id": category_id}
        if start_date and end_date:
            params["realtime_start"] = start_date
            params["realtime_end"] = end_date
        url = self._url("category/children", **params)
        return self._get(url).get("categories", [])

    def _category_series(self, category_id) -> list[dict]:
        url = self._url(
            "category/series", category_id=category_id,
            order_by="popularity", sort_order="desc",
        )
        return self._get(url).get("seriess", [])

    def _series(self, series_id: str, start: str, end: str) -> list[dict]:
        url = self._url(
            "series", series_id=series_id,
            realtime_start=start, realtime_end=end,
        )
        return self._get(url).get("seriess", [])

    def _tags(self) -> list[dict]:
        url = self._url("tags")
        return self._get(url).get("tags", [])

    def _tags_series(self, tag: str) -> list[dict]:
        url = self._url(
            "tags/series", tag_names=tag,
            order_by="popularity", sort_order="desc",
        )
        return self._get(url).get("seriess", [])

    # ── endpoints (public) ────────────────────────────────────

    def get_data(self, codes: list, start_date: str, end_date: str) -> pd.DataFrame:
        """시계열 데이터 조회.

        Parameters
        ----------
        codes : list[str]
            FRED 시리즈 ID 목록.
        start_date, end_date : str
            YYYYMMDD 형식.
        """
        start_fmt = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_fmt = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"

        dfs: list[pd.DataFrame] = []
        for code in codes:
            rows = self._series_observations(code, start_fmt, end_fmt)
            df = pd.DataFrame(rows)
            df = df[["date", "value"]].rename(columns={"value": code})
            df = df.set_index("date")
            dfs.append(df)

        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, axis=1).reset_index()

    def search_category(self, category_id) -> dict:
        """카테고리 조회 (하위 카테고리 포함)."""
        data = self._category(category_id)
        try:
            result = data[0]
            result["children"] = self._category_children(category_id)
        except (IndexError, KeyError):
            result = data
        return result

    def search_series(self, val_id: str, method: str = "category") -> pd.DataFrame:
        """시리즈 검색.

        method: 'category' | 'tag'
        """
        if method == "category":
            return pd.DataFrame(self._category_series(val_id))
        elif method == "tag":
            return pd.DataFrame(self._tags_series(val_id))
        else:
            raise ValueError(f"method는 'category' 또는 'tag'이어야 합니다: {method}")

    def search_tags(self, keyword: Optional[str] = None, col: str = "name") -> pd.DataFrame:
        """태그 검색."""
        all_tags = self._tags()
        if keyword is None:
            return pd.DataFrame(all_tags)
        return pd.DataFrame([t for t in all_tags if keyword in t.get(col, "")])


# ── 모듈 레벨 편의 인터페이스 ────────────────────────────────

_client: Optional[FredClient] = None


def _get_client() -> FredClient:
    if _client is None:
        raise ValueError("API key가 설정되지 않았습니다. econkit.fetch.fred.set_api_key()를 먼저 호출하세요.")
    return _client


def set_api_key(key: str) -> None:
    """FRED API 키 설정."""
    global _client
    _client = FredClient(api_key=key)


def get_data(codes: list, start_date: str, end_date: str) -> pd.DataFrame:
    return _get_client().get_data(codes, start_date, end_date)


def search_category(category_id) -> dict:
    return _get_client().search_category(category_id)


def search_series(val_id: str, method: str = "category") -> pd.DataFrame:
    return _get_client().search_series(val_id, method)


def search_tags(keyword: str = None, col: str = "name") -> pd.DataFrame:
    return _get_client().search_tags(keyword, col)
