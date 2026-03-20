"""OECD SDMX REST API 클라이언트.

API 키 불필요. OECD Data Explorer(https://data-explorer.oecd.org/)에서
데이터셋 ID와 필터를 확인한 뒤 사용합니다.

API 기본 URL: https://sdmx.oecd.org/public/rest
"""

from __future__ import annotations

from io import StringIO
from typing import Optional

import pandas as pd
import requests


BASE_URL = "https://sdmx.oecd.org/public/rest"


class OecdAPIError(Exception):
    """OECD API 호출 에러."""
    pass


def _get_csv(url: str) -> pd.DataFrame:
    """URL에서 CSV를 받아 DataFrame으로 반환."""
    resp = requests.get(url)
    if resp.status_code == 404:
        raise OecdAPIError("데이터를 찾을 수 없습니다. dataflow ID와 필터를 확인하세요.")
    if resp.status_code == 413:
        raise OecdAPIError("요청 데이터가 너무 큽니다. 필터를 좁혀주세요.")
    if resp.status_code == 429:
        raise OecdAPIError("API 호출 한도 초과 (60회/시간). 잠시 후 재시도하세요.")
    if resp.status_code != 200:
        raise OecdAPIError(f"HTTP Error {resp.status_code}: {resp.text[:200]}")
    return pd.read_csv(StringIO(resp.text))


def get_data(
    dataflow: str,
    filter_expr: str = "",
    start_period: Optional[str] = None,
    end_period: Optional[str] = None,
    pivot: bool = True,
    ref_area_col: str = "REF_AREA",
    time_col: str = "TIME_PERIOD",
    value_col: str = "OBS_VALUE",
) -> pd.DataFrame:
    """OECD 데이터 조회.

    Parameters
    ----------
    dataflow : str
        데이터플로우 ID. 예: "OECD.SDD.STES,DSD_STES@DF_CLI"
        OECD Data Explorer에서 Developer API 버튼으로 확인 가능.
    filter_expr : str
        차원 필터. 점(.)으로 구분, +로 복수 선택, 빈 값은 전체.
        예: "KOR+USA+JPN.M.LI...AA...H"
    start_period : str, optional
        시작 기간. 예: "2020-01", "2020"
    end_period : str, optional
        종료 기간.
    pivot : bool
        True면 REF_AREA별 컬럼으로 피벗. False면 원본 CSV 그대로.
    ref_area_col : str
        피벗 시 컬럼으로 사용할 지역 컬럼명.
    time_col : str
        시간 컬럼명.
    value_col : str
        관측값 컬럼명.

    Returns
    -------
    pd.DataFrame

    Examples
    --------
    >>> import econkit
    >>> # CLI (경기선행지수) — 한국, 미국, 일본
    >>> df = econkit.fetch.oecd.get_data(
    ...     "OECD.SDD.STES,DSD_STES@DF_CLI",
    ...     "KOR+USA+JPN.M.LI...AA...H",
    ...     start_period="2020-01",
    ... )
    """
    url = f"{BASE_URL}/data/{dataflow}/{filter_expr}"

    params = {
        "dimensionAtObservation": "AllDimensions",
        "format": "csvfilewithlabels",
    }
    if start_period:
        params["startPeriod"] = start_period
    if end_period:
        params["endPeriod"] = end_period

    qs = "&".join(f"{k}={v}" for k, v in params.items())
    full_url = f"{url}?{qs}"

    df = _get_csv(full_url)

    if not pivot:
        return df

    # 피벗: REF_AREA × TIME_PERIOD → 컬럼
    if ref_area_col not in df.columns or time_col not in df.columns or value_col not in df.columns:
        return df

    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    # MEASURE 컬럼이 있으면 복합 키로 사용
    if "Measure" in df.columns:
        df["_series"] = df[ref_area_col].astype(str) + "_" + df["Measure"].astype(str)
    elif "MEASURE" in df.columns and df["MEASURE"].nunique() > 1:
        df["_series"] = df[ref_area_col].astype(str) + "_" + df["MEASURE"].astype(str)
    else:
        df["_series"] = df[ref_area_col].astype(str)

    pivot_df = df.pivot_table(
        index=time_col, columns="_series", values=value_col, aggfunc="first",
    )
    pivot_df.index = pd.to_datetime(pivot_df.index)
    pivot_df = pivot_df.rename_axis(None, axis=1).sort_index()

    return pivot_df.reset_index().rename(columns={time_col: "date"})


def get_dataflow_list(agency: str = "OECD", keyword: Optional[str] = None) -> pd.DataFrame:
    """사용 가능한 데이터플로우 목록 조회.

    Parameters
    ----------
    agency : str
        에이전시 ID. 기본값 "OECD".
    keyword : str, optional
        키워드 필터 (데이터플로우 이름에서 검색).

    Returns
    -------
    pd.DataFrame
        id, agency, name 컬럼 포함.
    """
    url = f"{BASE_URL}/dataflow/{agency}"
    resp = requests.get(url, headers={"Accept": "application/vnd.sdmx.structure+csv"})

    if resp.status_code != 200:
        # CSV 안 되면 JSON 시도
        resp = requests.get(
            url,
            headers={"Accept": "application/vnd.sdmx.structure+json"},
        )
        if resp.status_code != 200:
            raise OecdAPIError(f"HTTP Error {resp.status_code}")

        data = resp.json()
        flows = []
        try:
            for df_item in data["data"]["dataflows"]:
                flows.append({
                    "id": df_item.get("id", ""),
                    "agency": df_item.get("agencyID", ""),
                    "name": df_item.get("name", ""),
                    "version": df_item.get("version", ""),
                })
        except (KeyError, TypeError):
            return pd.DataFrame()

        result = pd.DataFrame(flows)
    else:
        result = pd.read_csv(StringIO(resp.text))

    if keyword and not result.empty:
        mask = result.apply(
            lambda row: keyword.lower() in str(row).lower(), axis=1,
        )
        result = result[mask]

    return result


def get_structure(dataflow: str) -> dict:
    """데이터플로우의 구조(차원, 속성) 조회.

    Parameters
    ----------
    dataflow : str
        데이터플로우 ID.

    Returns
    -------
    dict
        JSON 응답 원본.
    """
    url = f"{BASE_URL}/datastructure/{dataflow}?references=all"
    resp = requests.get(
        url,
        headers={"Accept": "application/vnd.sdmx.structure+json"},
    )
    if resp.status_code != 200:
        raise OecdAPIError(f"HTTP Error {resp.status_code}")
    return resp.json()