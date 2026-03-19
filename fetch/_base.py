"""공통 API 클라이언트 베이스."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import requests


class APIError(Exception):
    """API 호출 에러 기본 클래스."""
    pass


@dataclass
class APIConfig:
    """API 설정."""
    base_url: str
    api_key: Optional[str] = None


class BaseClient:
    """
    API 클라이언트 공통 기반.

    서브클래스는 BASE_URL과 _check_error를 구현해야 합니다.
    """

    BASE_URL: str = ""

    def __init__(self, api_key: str):
        self._config = APIConfig(base_url=self.BASE_URL, api_key=api_key)

    @property
    def api_key(self) -> str:
        if self._config.api_key is None:
            raise ValueError("API key가 설정되지 않았습니다.")
        return self._config.api_key

    def _get(self, url: str) -> dict:
        """HTTP GET 요청 + 에러 처리."""
        resp = requests.get(url)
        if resp.status_code != 200:
            raise APIError(f"HTTP Error: {resp.status_code}")
        data = resp.json()
        self._check_error(data)
        return data

    def _check_error(self, data: dict) -> None:
        """제공자별 에러 코드 검사. 서브클래스에서 오버라이드."""
        raise NotImplementedError
