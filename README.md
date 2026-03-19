# econkit

경제 데이터 **수집 → 처리 → 분석 → 시각화** 파이프라인을 하나의 패키지로.

pandas DataFrame에 `.econ` accessor를 등록하여, 별도 래퍼 객체 없이 표준 DataFrame 위에서 경제 분석 기능을 바로 사용할 수 있습니다.

```python
import econkit

df.econ.yoy()                                    # YoY 변화율
df.econ.analyze.lead_lag('총지수', '식료품')       # 리드-래그 분석
df.econ.forecast.linear_trend('총지수', steps=4)   # 선형 추세 예측
df.econ.plot.overview()                           # 종합 대시보드
```

---

## 설치

### GitHub에서 pip 설치

```bash
# 기본 설치
pip install git+https://github.com/YOUR_USERNAME/econkit.git

# ARIMA, 시계열 분해 등 전체 기능
pip install "econkit[full] @ git+https://github.com/YOUR_USERNAME/econkit.git"
```

> `YOUR_USERNAME`을 본인의 GitHub 사용자명으로 바꿔주세요.

### 로컬 설치 (클론 후)

```bash
git clone https://github.com/YOUR_USERNAME/econkit.git
cd econkit
pip install -e .          # 개발 모드 (수정 즉시 반영)
pip install -e ".[full]"  # 전체 의존성 포함
```

### PyPI 배포 (선택)

PyPI에 등록하면 `pip install econkit`으로 직접 설치할 수 있습니다:

```bash
pip install build twine
python -m build
twine upload dist/*
```

### 의존성

| 구분 | 패키지 |
|------|--------|
| 필수 | `pandas>=2.0` · `numpy>=1.24` · `requests>=2.28` · `plotly>=5.15` |
| 선택 (`[full]`) | `scipy>=1.10` · `statsmodels>=0.14` |
| 개발 (`[dev]`) | `pytest>=7.0` · `pytest-cov>=4.0` |

> Python 3.10 이상 필요

---

## GitHub 레포지토리 구성

pip install이 동작하려면 레포 루트에 `pyproject.toml`이 있어야 합니다:

```
econkit/                  ← GitHub 레포 루트
├── econkit/              ← Python 패키지 (이 폴더가 import됨)
│   ├── __init__.py
│   ├── fetch/
│   ├── accessor/
│   ├── analyze/
│   ├── plot/
│   └── factors/
├── pyproject.toml        ← 빌드 설정 (반드시 레포 루트)
├── README.md
└── LICENSE
```

zip 파일로 받은 경우 아래처럼 구성합니다:

```bash
# zip 풀기
unzip econkit.zip

# 레포 구성 — pyproject.toml과 README를 루트로 이동
mkdir my-repo && cd my-repo
mv ../econkit/pyproject.toml .
mv ../econkit/README.md .
mv ../econkit/ econkit/

# git 초기화 & push
git init
git add .
git commit -m "initial: econkit v0.1.0"
git remote add origin https://github.com/YOUR_USERNAME/econkit.git
git push -u origin main
```

이제 누구나 `pip install git+https://github.com/YOUR_USERNAME/econkit.git`으로 설치할 수 있습니다.

---

## Quick Start

### 1. 데이터 수집

한국은행(ECOS), 금융감독원(FISIS), 미국 연준(FRED) 세 곳의 API를 통합 인터페이스로 제공합니다.

```python
import econkit

# 한국은행 ECOS
econkit.fetch.ecos.set_api_key("YOUR_KEY")
df = econkit.fetch.ecos.get_data(
    codes=[["M", "901Y009", "0"]],
    start_date="20200101",
    end_date="20241231",
)

# 금융감독원 FISIS
econkit.fetch.fisis.set_api_key("YOUR_KEY")
df = econkit.fetch.fisis.get_data(
    codes=[["0101000", "11101", "A001", "Q"]],
    start_date="202001",
    end_date="202412",
)

# 미국 연준 FRED
econkit.fetch.fred.set_api_key("YOUR_KEY")
df = econkit.fetch.fred.get_data(
    codes=["GDP", "CPIAUCSL", "UNRATE"],
    start_date="20200101",
    end_date="20241231",
)
```

### 2. 데이터 준비

`econkit`은 **DatetimeIndex + 수치형 컬럼**을 가진 표준 DataFrame에서 동작합니다.

```python
import pandas as pd

# 날짜 인덱스 설정
df["date"] = pd.to_datetime(df["date"])
df = raw.set_index("date").select_dtypes("number")

# 유효성 검사 (DatetimeIndex, 수치형, 결측값, 중복 체크)
df.econ.validate()
```

### 3. 변화율 & 기초통계

```python
# 변화율 — 내부적으로 일별 보간 후 계산하여 비정기 데이터도 정확
df.econ.yoy()            # 연간 (365일 기준)
df.econ.qoq()            # 분기 (90일 기준)
df.econ.mom()            # 월간 (30일 기준)

# 기초통계
df.econ.summary()        # mean, std, skewness, kurtosis, latest, quantiles
df.econ.describe_ext()   # pandas describe + skewness + kurtosis
```

### 4. 변환

```python
df.econ.transform.normalize("minmax")      # Min-Max 정규화
df.econ.transform.normalize("zscore")      # Z-score 표준화
df.econ.transform.normalize("base")        # 첫 시점 = 100
df.econ.transform.rebase("2022-01-01")     # 특정 시점 = 100
df.econ.transform.log()                    # 로그 변환
```

### 5. 분석

```python
# 비교 분석
df.econ.analyze.lead_lag("총지수", "식료품", max_lag=4)
df.econ.analyze.rolling_correlation("A", "B", window=12)
df.econ.analyze.dispersion()

# 시계열
result = df.econ.analyze.decompose("총지수")   # 추세 분해
df.econ.analyze.detect_outliers("총지수")       # 이상값 탐지
df.econ.analyze.changepoints("총지수")          # 변곡점

# 기술통계
df.econ.analyze.correlation()                  # 상관행렬
df.econ.analyze.rank_by_change()               # YoY 순위
df.econ.analyze.period_compare(("2020","2021"), ("2022","2023"))
```

### 6. 예측

```python
# 선형 추세
result = df.econ.forecast.linear_trend("총지수", steps=4, confidence=0.95)

# ARIMA (pip install econkit[full] 필요)
result = df.econ.forecast.arima("총지수", steps=4, order=(1,1,1))

# 이동평균 연장
result = df.econ.forecast.ma_extension("총지수", window=4, steps=4)

# 결과 구조
result.forecast    # 예측값 Series
result.lower       # 신뢰 하한
result.upper       # 신뢰 상한
```

### 7. 시각화

모든 plot 메서드는 `plotly.graph_objects.Figure`를 반환합니다.

```python
# 라인
df.econ.plot.line(normalize=True, ma_window=4)
df.econ.plot.yoy_line()
df.econ.plot.forecast_line("총지수", result)
df.econ.plot.cumulative()

# 바
df.econ.plot.yoy_bar("총지수")
df.econ.plot.grouped_bar()
df.econ.plot.rank_bar()
df.econ.plot.contribution_bar(weights={"A": 0.6, "B": 0.4})

# 히트맵
df.econ.plot.corr_heatmap()
df.econ.plot.seasonal_heatmap("총지수")
df.econ.plot.rolling_corr_heatmap("A", "B", [3, 6, 12])

# 산포도
df.econ.plot.scatter("A", "B", add_trend=True)
df.econ.plot.scatter_matrix()

# 대시보드
df.econ.plot.overview()                            # 레벨 + YoY + 변동성
df.econ.plot.compare_panel("A", "B")               # 2×2 상세 비교
df.econ.plot.lead_lag_panel("A", "B", max_lag=4)   # 리드-래그 패널
```

### 8. 팩터 계산

```python
from econkit.factors import ratio_factor, ma_cross_factor

# accessor 방식
df_new = df.econ.transform.compute_factors({
    "ratio_AB": ratio_factor("A", "B"),
    "ma_signal": ma_cross_factor("A", short=5, long=20, method="signal"),
}, zscore=True)

# 함수형 방식 (groupby 기반)
from econkit.factors.grouped import return_factor, compute

factors = {"ret_20": return_factor("code", "close", period=20)}
df = compute(df, factors, zscore=True, date_col="date")
```

---

## End-to-End 예제

```python
import econkit
import pandas as pd

# 1. 데이터 수집
econkit.fetch.ecos.set_api_key("YOUR_KEY")
raw = econkit.fetch.ecos.get_data(
    codes=[["M", "901Y009", "0"]],
    start_date="20150101",
    end_date="20241231",
)

# 2. 준비
raw["date"] = pd.to_datetime(raw["date"])
df = raw.set_index("date").select_dtypes("number")
df.econ.validate()

# 3. 탐색
print(df.econ.summary())
print(df.econ.yoy().tail())

# 4. 분석
lead = df.econ.analyze.lead_lag("소비자물가지수_총지수", "소비자물가지수_식료품", max_lag=6)
print(lead)

# 5. 예측
fc = df.econ.forecast.linear_trend("소비자물가지수_총지수", steps=6)
print(fc.forecast)

# 6. 시각화
df.econ.plot.overview().show()
df.econ.plot.forecast_line("소비자물가지수_총지수", fc).show()
```

---

## API 요약

| Accessor | 메서드 수 | 설명 |
|----------|-----------|------|
| `df.econ` | 9 | 변화율, 요약, 검증 등 자주 쓰는 기능 |
| `df.econ.transform` | 6 | 정규화, 리베이스, 로그, 차분, 팩터 계산 |
| `df.econ.analyze` | 20 | 기술통계, 비교 분석, 시계열 분석 |
| `df.econ.forecast` | 3 | 선형 추세, ARIMA, 이동평균 연장 |
| `df.econ.plot` | 21 | 라인, 바, 히트맵, 산포도, 대시보드 |

### fetch 모듈

| Provider | 함수 |
|----------|------|
| `econkit.fetch.ecos` | `set_api_key` · `get_data` · `get_key_stats` · `search_stats` · `search_word` |
| `econkit.fetch.fisis` | `set_api_key` · `get_data` · `search_company` · `search_stat` · `search_stats` |
| `econkit.fetch.fred` | `set_api_key` · `get_data` · `search_category` · `search_series` · `search_tags` |

### factors 모듈

| 모듈 | 함수 |
|------|------|
| `econkit.factors` (single) | `ratio_factor` · `return_factor` · `rolling_stat_factor` · `log_factor` · `ma_cross_factor` · `compare_factor` · `rolling_zscore_factor` |
| `econkit.factors.grouped` | 위 항목 + `parkinson_vol_factor` · `amihud_factor` · `cs_zscore` · `compute` |

---

## 패키지 구조

```
econkit/
├── __init__.py              # import econkit → accessor 자동 등록
├── _types.py                # 공통 타입 정의
├── _utils.py                # safe_div, describe_df
│
├── fetch/                   # 외부 API 데이터 수집
│   ├── _base.py             #   BaseClient (공통 HTTP, 에러 처리)
│   ├── _parsers.py          #   parse_time, pivot_stat_info
│   ├── ecos.py              #   한국은행 ECOS
│   ├── fisis.py             #   금융감독원 FISIS
│   └── fred.py              #   미국 연준 FRED
│
├── accessor/                # pandas .econ accessor
│   ├── _registry.py         #   EconAccessor 등록
│   ├── _validate.py         #   데이터 유효성 검증
│   ├── _stats.py            #   기술통계
│   ├── _change.py           #   변화율 (일별 보간 로직 포함)
│   └── _transform.py        #   정규화, 리베이스, 팩터 계산
│
├── analyze/                 # 분석 모듈
│   ├── __init__.py          #   AnalyzeAccessor, ForecastAccessor
│   ├── _results.py          #   ForecastResult, DecompositionResult
│   ├── descriptive.py       #   기술통계 함수
│   ├── comparative.py       #   비교 분석 함수
│   ├── timeseries.py        #   시계열 분석 함수
│   └── forecast.py          #   예측 모델
│
├── plot/                    # Plotly 시각화
│   ├── __init__.py          #   PlotAccessor
│   ├── _base.py             #   공통 레이아웃, 팔레트
│   ├── line.py              #   라인 차트 (6종)
│   ├── bar.py               #   바 차트 (5종)
│   ├── heatmap.py           #   히트맵 (4종)
│   ├── scatter.py           #   산포도 (3종)
│   └── dashboard.py         #   대시보드 (3종)
│
└── factors/                 # 팩터 생성 함수
    ├── single.py            #   단일 인덱스 (7종)
    └── grouped.py           #   그룹별 (10종 + compute)
```

---

## 라이선스

MIT
