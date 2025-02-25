import pandas as pd
import numpy as np

from data_processing import get_adjusted_baseline_price, interpolation_logs, get_adjusted_baseline_volume

def compute_resell_index(avg_price, total_volume, baseline_price, baseline_volume, alpha):
    '''
    @deprecated: not used anymore

    주어진 값들을 바탕으로 resell index를 계산합니다.
    
    price_premium = avg_price - baseline_price
    normalized_premium = price_premium / baseline_price
    adjusted_weight = alpha * total_volume + (1 - alpha) * normalized_premium
    return (avg_price * adjusted_weight) / (baseline_price * baseline_volume) * 100
    '''
    '''
    # 로그 함수를 사용함으로써 가격 차이의 스케일을 변환하여 극단적인 값들의 영향을 완화
    #avg_price - baseline_price 값이 너무 낮아져서 음수가 지나치게 커지는 것을 방지. 즉, 최소값을 -baseline_price로 제한하여 음수에 대한 안전장치
    #기준 가격이 0보다 클 때만 나누기를 수행하고, 그렇지 않으면 0을 할당하여 0으로 나누는 오류를 방지
    price_premium = np.log1p(max(avg_price - baseline_price, -baseline_price,0))  # 🔹 음수 방지 (최소 -baseline_price)
    normalized_premium = price_premium / baseline_price if baseline_price > 0 else 0
    adjusted_weight = alpha * total_volume + (1 - alpha) * normalized_premium
    return (avg_price * adjusted_weight) / (baseline_price * baseline_volume) * 100'''
    
    #손해 보고 파는 경우 지수를 0으로 설정
    price_premium = max(avg_price - baseline_price, 0)  # 🔹 음수 방지
    normalized_premium = price_premium / baseline_price if baseline_price > 0 else 0
    adjusted_weight = alpha * total_volume + (1 - alpha) * normalized_premium
    return (avg_price * adjusted_weight) / (baseline_price * baseline_volume) * 100

def compute_resell_index_custom(avg_price, total_volume, baseline_price, baseline_volume, alpha, discount_volume_threshold):
    """
    리셀 지수를 할인률과 거래량을 고려해 계산하는 함수.
    
    Parameters:
      avg_price: 현재 거래 평균가격
      total_volume: 현재 거래량
      baseline_price: 발매가(기준가격)
      baseline_volume: 기준 거래량 (예: 발매 당일 거래량)
      alpha: 거래량의 기여도를 조정하는 가중치 (0 <= α <= 1)
      discount_volume_threshold: 할인 거래를 의미 있게 반영하기 위한 거래량 임계값
      
    Returns:
      계산된 리셀 지수
    """
    # 거래량을 기준 거래량으로 정규화 (단위 맞추기)
    normalized_volume = total_volume / baseline_volume if baseline_volume > 0 else 0
    
    if avg_price >= baseline_price:
        # 프리미엄 케이스: 발매가보다 높은 경우
        normalized_premium = (avg_price - baseline_price) / baseline_price
        # 프리미엄과 정규화된 거래량을 가중치로 결합
        combined_factor = (1 - alpha) * normalized_premium + alpha * normalized_volume
    else:
        # 할인 케이스: 발매가보다 낮은 경우
        discount_rate = (baseline_price - avg_price) / baseline_price  # 할인율은 양수 값
        # 거래량이 임계값 이상일 때 할인 효과 반영, 그 외엔 할인 효과 무시
        if total_volume >= discount_volume_threshold:
            # 할인은 부정적인 효과로 반영하되, 거래량이 크면 시장의 활성을 반영하도록 함
            combined_factor = (1 - alpha) * (-discount_rate) + alpha * normalized_volume
        else:
            # 임계값 미달이면 할인 효과는 무시 (또는 0으로 처리)
            combined_factor = alpha * normalized_volume
    
    # 최종 지수 계산:
    # avg_price/baseline_price가 가격 변동을 반영하고, (1 + combined_factor)가 거래 및 프리미엄/할인 효과를 반영
    index = (avg_price / baseline_price) * (1 + combined_factor) * 100
    return index

def compute_resell_index_laspeyres(avg_price, baseline_price, baseline_volume):
    """
    @internal

    라스파이레스 방식으로 리셀 지수를 계산하는 함수.
    - 거래량을 기준 시점에서 고정하고, 이후 가격 변동만 반영.
    """
    if baseline_price <= 0 or baseline_volume <= 0:
        return np.nan  # 0 나누기 방지

    #return (avg_price * baseline_volume) / (baseline_price * baseline_volume) * 100
    return (avg_price ) / (baseline_price ) * 100

def calculate_product_resell_index_laspeyres(transactions, product_meta, product_id, baseline_date):
    """
    @deprecated: not used anymore

    특정 상품 ID에 대해 거래량을 고정한 리셀 지수를 계산하는 함수.
    """
    transactions.loc[:, 'date_created'] = pd.to_datetime(transactions['date_created'])
    product_data = transactions[(transactions["product_id"] == product_id) & (transactions["date_created"] >= baseline_date)]
    
    if product_data.empty:
        return pd.DataFrame(columns=["date_created", "avg_price", "resell_index"])

    # 날짜별 평균 가격 및 거래량 계산
    product_resell_index = product_data.groupby(product_data["date_created"].dt.date).agg(
        avg_price=("price", "mean"),
        total_volume=("price", "count")
    ).reset_index()

    # 기준 시점 가격 설정 (없으면 보정값 사용)
    baseline_price = product_meta.loc[product_meta["product_id"] == product_id, "original_price"].values
    baseline_price = baseline_price[0] if len(baseline_price) > 0 else get_adjusted_baseline_price(product_resell_index, baseline_date, product_id)

    if pd.isna(baseline_price) or baseline_price <= 0:
        baseline_price = 10  # 기본값 설정하여 0 나누기 방지
        interpolation_logs.append({
            "product_id": product_id,
            "date_created": baseline_date,
            "column": "original_price",
            "method": "adjusted_price",
            "original_value": None,
            "new_value": baseline_price
        })

    # 거래 데이터에서 baseline_volume 직접 계산 (기존 compute_resell_index 방식 유지)
    baseline_volume = product_resell_index.loc[product_resell_index["date_created"] == pd.to_datetime(baseline_date).date(), "total_volume"]
    if baseline_volume.empty:
        baseline_volume = get_adjusted_baseline_volume(product_resell_index, baseline_date, product_id)  # 보정값 사용
    else:
        baseline_volume = baseline_volume.iloc[0]  # 첫 번째 값 사용

    # 리셀 지수 계산 (라스파이레스 방식 적용)
    product_resell_index["resell_index"] = product_resell_index["avg_price"].apply(
        lambda avg_price: compute_resell_index_laspeyres(avg_price, baseline_price, baseline_volume)
    )

    # NaN 및 Inf 값 처리
    product_resell_index["resell_index"] = product_resell_index["resell_index"].replace([float("inf"), -float("inf")], None)

    return product_resell_index

def normalize_index(df, index_column="resell_index", baseline_date=None):
    """
    DataFrame의 지수를 기준일(또는 첫 행의 값)으로 정규화하여 기준일의 값이 100이 되도록 조정합니다.
    baseline_date가 주어지면 해당 날짜의 값을 기준으로, 그렇지 않으면 첫 행의 값을 사용합니다.
    """
    '''
    if baseline_date is not None and baseline_date in df["date_created"].values:
        base_value = df.loc[df["date_created"] == baseline_date, index_column].iloc[0]
    else:
        base_value = df[index_column].iloc[0]
    df[index_column] = df[index_column] / base_value * 100
    return df'''
    # 데이터프레임이 비어있거나 필요한 컬럼이 없을 때, 그리고 기준값이 NaN인 경우에 대해 명시적인 에러 처리를 추가
    if df.empty or index_column not in df.columns:
        print("⚠️ 데이터프레임이 비어 있거나 지정된 인덱스 컬럼이 없음 → 빈 데이터 반환")
        return df  # 빈 DataFrame 반환

    # 기준일의 값 가져오기 (없으면 첫 번째 값 사용)
    if baseline_date is not None and baseline_date in df["date_created"].values:
        base_value = df.loc[df["date_created"] == baseline_date, index_column].iloc[0]
    else:
        base_value = df[index_column].iloc[0] if not df[index_column].isna().all() else None

    # NaN 발생 방지: 기준값이 NaN이면 기본값(100) 사용
    if pd.isna(base_value):
        print(f"⚠️ 기준값({index_column})이 NaN → 기본값(100)으로 설정")
        base_value = 100  

    df[index_column] = df[index_column] / base_value * 100
    return df

def get_discount_volume_threshold(df, baseline_price, quantile=0.5, default_threshold=1):
    """
    특정 상품의 거래 데이터(df)에서 할인 거래량 임계값을 계산합니다.
    
    Parameters:
      df: 특정 상품의 거래 데이터가 담긴 DataFrame (반드시 'price'와 'date_created' 컬럼 포함)
      baseline_price: 발매가(원래 가격)
      quantile: 임계값 산출에 사용할 분위수 (기본 0.5는 중앙값)
      default_threshold: 할인 거래 데이터가 없거나 계산 결과가 0일 경우 사용할 기본 임계값
      
    Returns:
      할인 거래량 임계값 (최소 거래 건수)
    """
    df.loc[:, 'date_created'] = pd.to_datetime(df['date_created'])
    discount_df = df[df['price'] < baseline_price]
    if discount_df.empty:
        return default_threshold
    discount_volume_by_day = discount_df.groupby(discount_df['date_created'].dt.date).size()
    threshold = discount_volume_by_day.quantile(quantile)
    return threshold if threshold > 0 else default_threshold

meta_df = pd.read_csv('../source/meta/product_meta_data.csv')

def analyze_alpha_sensitivity(df, baseline_volume, discount_volume_quantile, alpha_values):
    """
    @deprecated: not used anymore

    전체 거래 데이터(df)에서 상품별로 다양한 α 값에 따른 리셀 지수를 계산합니다.
    
    Parameters:
      df: 전체 거래 데이터 DataFrame (product_id, price, date_created 포함)
      baseline_volume: 기준 거래량 (고정값 또는 별도 산출)
      discount_volume_quantile: 할인 거래량 임계값 산출에 사용할 분위수 (예: 0.5)
      alpha_values: 분석할 α 값 리스트 (예: [0.3, 0.5, 0.7])
      
    Returns:
      상품별로 α 민감도 결과를 담은 딕셔너리 {product_id: {alpha: index, ...}, ...}
    """
    results = {}
    
    # 전체 할인 거래량 분포 분석 (상품별 요약 통계)
    baseline_price_lookup = {row['product_id']: row['original_price'] for _, row in meta_df.iterrows()}
    discount_stats = analyze_discount_volume_distribution(df, baseline_price_lookup)

    for product_id, group in df.groupby('product_id'):
        # 발매가 정보 가져오기
        baseline_price = meta_df.loc[meta_df['product_id'] == product_id, 'original_price'].values[0]
        avg_price = group['price'].mean()
        total_volume = len(group)

        # 할인 거래량 임계값 계산
        discount_volume_threshold = get_discount_volume_threshold(group, baseline_price, quantile=discount_volume_quantile, default_threshold=1)

        # α 값 자동 조정 (할인 거래량 통계를 활용)
        std_dev_discount_volume = discount_stats.get(product_id, {}).get('std', 0)  # 할인 거래량 표준편차 사용
        alpha = min(1, max(0, 1 - std_dev_discount_volume / total_volume))  # 변동성이 클수록 α 감소

        product_alpha_results = {}
        for alpha in alpha_values:
            index = compute_resell_index_custom(avg_price, total_volume, baseline_price, baseline_volume, alpha, discount_volume_threshold)
            product_alpha_results[alpha] = index

        results[product_id] = product_alpha_results

    return results

def analyze_discount_volume_distribution(df, baseline_price_lookup):
    """
    @deprecated: not used anymore

    거래 데이터에서 할인 거래(가격 < baseline_price)의 날짜별 건수를 계산하고, 
    통계 요약(descriptive statistics)을 반환합니다.
    
    Parameters:
      transactions_file: 거래 데이터 CSV 파일 경로 (예: "36.csv")
      baseline_price: 발매가 (예: 139000)
      
    Returns:
      할인 거래 건수의 날짜별 분포에 대한 요약 통계 (pandas Series의 describe() 결과)
    """
    # 날짜 형식 변환
    df.loc[:, 'date_created'] = pd.to_datetime(df['date_created'])
    results = {}
    for product_id, group in df.groupby('product_id'):
        baseline_price = baseline_price_lookup.get(product_id)
        if baseline_price is None:
            continue
        discount_df = group[group['price'] < baseline_price]
        # 상품별 날짜별 할인 거래 건수 집계
        discount_volume_by_day = discount_df.groupby(discount_df['date_created'].dt.date).size()
        results[product_id] = discount_volume_by_day.describe()  # 또는 원하는 방식으로 저장
    return results
