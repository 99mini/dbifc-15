#개별 상품 리셀 지수 계산 함수 정의
import pandas as pd
from data_processing import get_adjusted_baseline_price, get_adjusted_baseline_volume, save_interpolation_log, interpolation_logs
from resell_utils import compute_resell_index, normalize_index, compute_resell_index_custom, get_discount_volume_threshold

def calculate_product_resell_index(transactions: pd.DataFrame, product_meta: pd.DataFrame, product_id: int, baseline_date: str, alpha: float, discount_volume_quantile: float = 0.5, default_discount_threshold: float = 1):
    """    
    특정 상품 ID에 대해 할인 및 거래량을 반영한 리셀 지수를 계산하는 함수.

    Parameters:
        transactions (pandas.DataFrame): 거래 데이터
        product_meta (pandas.DataFrame): 상품 메타 데이터
        product_id (int): 상품 ID
        baseline_date (str): 기준 시점
        alpha (float): 약성값
        discount_volume_quantile (float): 할인 거래량 임계값 산출에 사용할 분위수 (기본 0.5)
        default_discount_threshold (int): 할인 거래 데이터가 없거나 계산 결과가 0일 경우 사용할 기본 임계값 (기본 1)

    Returns:
        pandas.DataFrame: 리셀 지수를 담은 DataFrame
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
    
    # 기준 시점 가격 설정
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
    
    # 기준 거래량 계산 (날짜가 baseline_date인 경우)
    baseline_volume = product_resell_index.loc[product_resell_index["date_created"] == pd.to_datetime(baseline_date).date(), "total_volume"]
    if baseline_volume.empty:
        baseline_volume = get_adjusted_baseline_volume(product_resell_index, baseline_date)
    else:
        baseline_volume = baseline_volume.iloc[0]
    
    # 할인 거래량 임계값 산출
    discount_volume_threshold = get_discount_volume_threshold(product_data, baseline_price, quantile=discount_volume_quantile, default_threshold=default_discount_threshold)
    
    # compute_resell_index_custom 호출 시 discount_volume_threshold 인자 추가
    product_resell_index["resell_index"] = product_resell_index.apply(
        lambda row: compute_resell_index_custom(
            row["avg_price"], 
            row["total_volume"], 
            baseline_price, 
            baseline_volume, 
            alpha, 
            discount_volume_threshold
        ),
        axis=1
    )
    
    product_resell_index["resell_index"] = product_resell_index["resell_index"].replace([float("inf"), -float("inf")], None)
    
    return product_resell_index
