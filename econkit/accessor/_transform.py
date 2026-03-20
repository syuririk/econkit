"""데이터 변환 서브-accessor."""

from __future__ import annotations

from typing import Optional, Dict, Callable

import numpy as np
import pandas as pd


class TransformAccessor:
    """df.econ.transform — 정규화, 리베이스, 로그, 차분, 팩터 계산."""

    def __init__(self, df: pd.DataFrame):
        self._df = df

    def _check_columns(self, columns: Optional[list[str]]) -> list[str]:
        if columns is None:
            return list(self._df.select_dtypes(include="number").columns)
        missing = [c for c in columns if c not in self._df.columns]
        if missing:
            raise KeyError(f"컬럼을 찾을 수 없습니다: {missing}")
        return columns

    def normalize(
        self,
        method: str = "minmax",
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """정규화.

        Parameters
        ----------
        method : str
            'minmax' | 'zscore' | 'base' (첫 시점=100)
        columns : list[str], optional
            대상 컬럼. None이면 전체 수치형.

        Returns
        -------
        pd.DataFrame
            정규화된 DataFrame.
        """
        cols = self._check_columns(columns)
        sub = self._df[cols]

        if method == "minmax":
            return (sub - sub.min()) / (sub.max() - sub.min())
        elif method == "zscore":
            return (sub - sub.mean()) / sub.std()
        elif method == "base":
            return sub / sub.iloc[0] * 100
        else:
            raise ValueError(f"지원하지 않는 method: {method}")

    def rebase(
        self,
        base_period: str,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """특정 시점을 100으로 환산."""
        cols = self._check_columns(columns)
        sub = self._df[cols]
        return sub / sub.loc[base_period] * 100

    def log(self, columns: Optional[list[str]] = None) -> pd.DataFrame:
        """로그 변환."""
        cols = self._check_columns(columns)
        return np.log(self._df[cols])

    def diff(
        self,
        periods: int = 1,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """차분."""
        cols = self._check_columns(columns)
        from econkit.accessor._change import diff
        return diff(self._df[cols], periods)

    def pct_change(
        self,
        periods: int = 1,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """백분율 변화."""
        cols = self._check_columns(columns)
        from econkit.accessor._change import pct_change
        return pct_change(self._df[cols], periods) * 100

    def compute_factors(
        self,
        factor_dict: Dict[str, Callable],
        zscore: bool = True,
        zscore_method: str = "rolling",
        rolling_window: int = 4,
    ) -> pd.DataFrame:
        """팩터를 계산하여 DataFrame에 추가.

        Parameters
        ----------
        factor_dict : dict
            {name: func} 형태. func는 DataFrame을 받아 Series 반환.
        zscore : bool
            Z-score 표준화 여부.
        zscore_method : str
            'rolling' 또는 'cross'.
        rolling_window : int
            rolling 방식의 윈도우 크기.

        Returns
        -------
        pd.DataFrame
            팩터가 추가된 DataFrame.
        """
        result = self._df.copy()

        for name, func in factor_dict.items():
            result[name] = func(result).astype("float32")

            if zscore:
                zname = f"{name}_Z"
                if zscore_method == "rolling":
                    result[zname] = self._rolling_zscore(
                        result[name], rolling_window,
                    ).astype("float32")
                elif zscore_method == "cross":
                    result[zname] = self._cs_zscore(result[name]).astype("float32")
                else:
                    raise ValueError(f"지원하지 않는 zscore_method: {zscore_method}")

        return result

    @staticmethod
    def _rolling_zscore(s: pd.Series, window: int = 4, eps: float = 1e-8) -> pd.Series:
        def score(x):
            mu = x.mean()
            sigma = x.std() + eps
            return (x.iloc[-1] - mu) / sigma
        return s.rolling(window).apply(score, raw=False)

    @staticmethod
    def _cs_zscore(s: pd.Series, eps: float = 1e-8) -> pd.Series:
        return (s - s.mean()) / (s.std() + eps)
