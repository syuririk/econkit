"""공통 타입 정의."""

from __future__ import annotations

from typing import Union, List, Optional, Dict, Callable, Tuple

import pandas as pd

Indicator = str
IndicatorList = Optional[List[str]]
PeriodTuple = Tuple[str, str]
FactorDict = Dict[str, Callable]
