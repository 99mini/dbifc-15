# resell_utils.py
import pandas as pd
import numpy as np
from data_processing import get_adjusted_baseline_price, save_interpolation_log, interpolation_logs, get_adjusted_baseline_volume


def compute_resell_index(avg_price, total_volume, baseline_price, baseline_volume, alpha):
    '''
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

def compute_resell_index_laspeyres(avg_price, baseline_price, baseline_volume):
    """
    라스파이레스 방식으로 리셀 지수를 계산하는 함수.
    - 거래량을 기준 시점에서 고정하고, 이후 가격 변동만 반영.
    """
    if baseline_price <= 0 or baseline_volume <= 0:
        return np.nan  # 0 나누기 방지

    #return (avg_price * baseline_volume) / (baseline_price * baseline_volume) * 100
    return (avg_price ) / (baseline_price ) * 100

def calculate_product_resell_index_laspeyres(transactions, product_meta, product_id, baseline_date):
    """
    특정 상품 ID에 대해 거래량을 고정한 리셀 지수를 계산하는 함수.
    """
    transactions["date_created"] = pd.to_datetime(transactions["date_created"])
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


