# 15회 DB보험금융공모전

# 주제

리셀 시장을 활용한 대체투자지수 개발 및 효용성 분석: 리셀 시장 지수(Resell Market Index, RMI)의 구축과 평가

## 리셀 시장을 반영한 대체투자 지수 개발

- 최근 리셀 시장(스니커즈, 명품, 한정판 상품 등)은 대체 투자 자산군으로 주목받고 있음.
- 기존 금융시장(주가지수, 채권, 금)과 달리 **리셀 시장의 가격 변동성을 반영하는 지수**가 존재하지 않음.
- 본 프로젝트에서는 **리셀 시장을 반영한 "Resell Market Index"** 를 개발하여, 리셀 상품의 시장 동향을 분석하고, 투자 가치 평가 및 자산 헤지 가능성을 살펴보고자 함.

## 리셀 시장 지수 계산 공식 정리

### 개별 상품 리셀 인덱스 (Resell Index)

각 상품의 리셀 인덱스를 계산하는 공식

$$
ResellIndex = \left( \frac{AvgPrice \times TotalVolume}{BaselinePrice \times BaselineVolume} \right) \times 100
$$

### 전체 리셀 시장 지수 (Market Resell Index)

여러 상품의 개별 리셀 인덱스를 평균 내어 시장 전체의 리셀 지수를 계산

$$
MarketResellIndex = \frac{\sum ResellIndex}{N}
$$

### 기준값 설정 (Baseline Price & Volume)

- 기준 가격(Baseline Price) 설정
  특정 상품의 발매가를 가져옴

$$
BaselinePrice = ProductMeta[ProductID]["originalPrice"]
$$

- 기준 거래량(Baseline Volume) 설정
  첫 번째 거래일의 거래량을 기준으로 함

$$
BaselineVolume = TotalVolume_{FirstDay}
$$

# 구성원

- [99mini](https://github.com/99mini/)
- [cakejin](https://github.com/cakejin)
