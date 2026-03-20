# econkit

경제 데이터 **수집 → 처리 → 분석 → 시각화** 파이프라인.

pandas DataFrame에 `.econ` accessor를 등록하여, 표준 DataFrame 위에서 경제 분석 기능을 바로 사용할 수 있습니다.

```python
import econkit

df.econ.yoy()                                    # YoY 변화율
df.econ.analyze.lead_lag('총지수', '식료품')       # 리드-래그 분석
df.econ.forecast.linear_trend('총지수', steps=4)   # 선형 추세 예측
df.econ.plot.overview()                           # 종합 대시보드
```

---

## 설치

```bash
pip install git+https://github.com/syuririk/econkit.git

# ARIMA, 시계열 분해 포함
pip install "econkit[full] @ git+https://github.com/syuririk/econkit.git"
```

### 의존성

| 구분 | 패키지 |
|------|--------|
| 필수 | `pandas>=2.0` · `numpy>=1.24` · `requests>=2.28` · `plotly>=5.15` |
| 선택 (`[full]`) | `scipy>=1.10` · `statsmodels>=0.14` |

> Python 3.10+

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
│   ├── fred.py              #   미국 연준 FRED
│   └── oecd.py              #   OECD Data Explorer (API 키 불필요)
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

## API 엔드포인트

### fetch — 데이터 수집

#### `econkit.fetch.oecd` (API 키 불필요)

OECD SDMX REST API. [OECD Data Explorer](https://data-explorer.oecd.org/)에서 Developer API 버튼으로 dataflow ID를 확인합니다.

| 함수 | 설명 |
|------|------|
| `get_data(dataflow, filter_expr, start_period, end_period)` | 데이터 조회 → DataFrame |
| `get_dataflow_list(agency, keyword)` | 데이터플로우 목록 검색 |
| `get_structure(dataflow)` | 데이터플로우 구조(차원, 속성) 조회 |

```python
import econkit

# CLI (경기선행지수) — 한국, 미국, 일본
df = econkit.fetch.oecd.get_data(
    "OECD.SDD.STES,DSD_STES@DF_CLI",
    "KOR+USA+JPN.M.LI...AA...H",
    start_period="2020-01",
)

# GDP — OECD 전체
df = econkit.fetch.oecd.get_data(
    "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
    start_period="2015",
)

# 데이터플로우 검색
flows = econkit.fetch.oecd.get_dataflow_list(keyword="GDP")
```

#### `econkit.fetch.ecos` (한국은행)

| 함수 | 설명 |
|------|------|
| `set_api_key(key)` | API 키 설정 |
| `get_data(codes, start_date, end_date)` | 통계 데이터 조회 |
| `get_key_stats()` | 100대 주요 통계지표 |
| `search_stats(keyword)` | 통계 테이블 검색 |
| `search_word(word)` | 용어 사전 검색 |

```python
econkit.fetch.ecos.set_api_key("YOUR_KEY")
df = econkit.fetch.ecos.get_data(
    codes=[["M", "901Y009", "0"]],
    start_date="20200101", end_date="20241231",
)
```

#### `econkit.fetch.fisis` (금융감독원)

| 함수 | 설명 |
|------|------|
| `set_api_key(key)` | API 키 설정 |
| `get_data(codes, start_date, end_date)` | 금융통계 데이터 조회 |
| `search_company(div)` | 금융회사 검색 |
| `search_stat(list_no)` | 계정 목록 검색 |
| `search_stats(lrg_div, sml_div, details)` | 통계 목록 검색 |

```python
econkit.fetch.fisis.set_api_key("YOUR_KEY")
df = econkit.fetch.fisis.get_data(
    codes=[["0101000", "11101", "A001", "Q"]],
    start_date="202001", end_date="202412",
)
```

#### `econkit.fetch.fred` (미국 연준)

| 함수 | 설명 |
|------|------|
| `set_api_key(key)` | API 키 설정 |
| `get_data(codes, start_date, end_date)` | 시계열 데이터 조회 |
| `search_category(category_id)` | 카테고리 조회 |
| `search_series(val_id, method)` | 시리즈 검색 |
| `search_tags(keyword)` | 태그 검색 |

```python
econkit.fetch.fred.set_api_key("YOUR_KEY")
df = econkit.fetch.fred.get_data(
    codes=["GDP", "CPIAUCSL", "UNRATE"],
    start_date="20200101", end_date="20241231",
)
```

### accessor — 분석 & 시각화

| Accessor | 메서드 수 | 설명 |
|----------|-----------|------|
| `df.econ` | 9 | `yoy` · `qoq` · `mom` · `pct_change` · `diff` · `rolling_std` · `summary` · `describe_ext` · `validate` |
| `df.econ.transform` | 6 | `normalize` · `rebase` · `log` · `diff` · `pct_change` · `compute_factors` |
| `df.econ.analyze` | 20 | `lead_lag` · `correlation` · `decompose` · `detect_outliers` · `changepoints` · `dispersion` · `rolling_correlation` · `pairwise_corr` · `relative_performance` · `cumulative` · `correlation_with` · `rank_by_change` · `contribution` · `period_compare` · `describe_ext` · `decompose_all` · `seasonal_pattern` · `seasonal_adjustment` · `rolling_volatility` · `volatility_table` |
| `df.econ.forecast` | 3 | `linear_trend` · `arima` · `ma_extension` |
| `df.econ.plot` | 21 | `line` · `yoy_line` · `qoq_line` · `forecast_line` · `decomposition` · `cumulative` · `yoy_bar` · `grouped_bar` · `period_compare_bar` · `contribution_bar` · `rank_bar` · `corr_heatmap` · `seasonal_heatmap` · `yoy_heatmap` · `rolling_corr_heatmap` · `scatter` · `corr_scatter` · `scatter_matrix` · `overview` · `compare_panel` · `lead_lag_panel` |

### factors — 팩터 생성 함수

| 모듈 | 함수 |
|------|------|
| `econkit.factors` | `ratio_factor` · `return_factor` · `rolling_stat_factor` · `log_factor` · `ma_cross_factor` · `compare_factor` · `rolling_zscore_factor` |
| `econkit.factors.grouped` | 위 항목 + `parkinson_vol_factor` · `amihud_factor` · `cs_zscore` · `compute` |

---

## 라이선스

MIT