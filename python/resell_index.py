#개별 상품 리셀 지수 계산 함수 정의
import pandas as pd
from data_processing import get_adjusted_baseline_price, get_adjusted_baseline_volume, save_interpolation_log, interpolation_logs

def calculate_product_resell_index(transactions, product_meta, product_id, baseline_date):
    """
    특정 상품 ID에 대해 거래량 가중치를 적용한 리셀 지수를 계산하는 함수
    :param transactions: 전체 거래 데이터 (DataFrame)
    :param product_id: 특정 상품의 ID (int)
    :param baseline_date: 기준 날짜 (str, 예: "2025-01-01")
    :return: 특정 상품의 리셀 지수 DataFrame
    """
    # 날짜 변환
    transactions["date_created"] = pd.to_datetime(transactions["date_created"])
    # 특정 상품 ID 필터링과 기준 시점 이후 데이터 필터링
    product_data = transactions[(transactions["product_id"] == product_id) & (transactions["date_created"] >= baseline_date)]
    
    
    # 데이터가 없을 경우 스킵하도록 처리
    if product_data.empty:
        #print(f"상품 ID {product_id}에 대한 거래 데이터 없음, 스킵")
        return pd.DataFrame(columns=["date_created", "avg_price", "total_volume", "resell_index"])
    
    # 날짜별 평균 가격 및 거래량 계산
    product_resell_index = product_data.groupby(product_data["date_created"].dt.date).agg(
        avg_price=("price", "mean"),
        total_volume=("price", "count")  # 거래량을 건수로 계산
    ).reset_index()

    # 기준 시점 가격 및 거래량 설정
    #baseline_price = product_resell_index["original_price"].iloc[0]
    '''
    try:
        baseline_price = product_meta[product_meta["product_id"] == product_id]["original_price"].values[0]
    except IndexError:
        #print(f"상품 ID {product_id}에 대한 발매가 데이터 없음, 스킵")
        return pd.DataFrame(columns=["date_created", "avg_price", "total_volume", "resell_index"])
    '''
    #try-except 대신 get()을 활용하여 product_meta에서 가격 가져오기
    baseline_price = product_meta.loc[product_meta["product_id"] == product_id, "original_price"].values
    baseline_price = baseline_price[0] if len(baseline_price) > 0 else get_adjusted_baseline_price(product_resell_index, baseline_date, product_id)
    
    # 발매가가 NaN이거나 0 이면 보정값 대체
    if pd.isna(baseline_price) or baseline_price == 0:
        #baseline_price = get_adjusted_baseline_price(product_resell_index, baseline_date, product_id)
        interpolation_logs.append({"product_id": product_id, "method": "adjusted_price", "date": baseline_date})

    if "total_volume" not in product_resell_index.columns or product_resell_index.empty:
        return pd.DataFrame(columns=["date_created", "avg_price", "total_volume", "resell_index"])

    # 기준 거래량 설정
    baseline_volume = product_resell_index["total_volume"].iloc[0] if not product_resell_index["total_volume"].isna().all() \
        else get_adjusted_baseline_volume(product_resell_index, baseline_date, product_id)
    
    '''
    # 기준일 거래량 설정 (거래량이 없으면 1로 설정)
    baseline_volume = product_resell_index["total_volume"].iloc[0] if not product_resell_index.empty else 1
    '''

    # 지수 계산
    product_resell_index["resell_index"] = (
        (product_resell_index["avg_price"] * product_resell_index["total_volume"]) /
        (baseline_price * baseline_volume) * 100
    )
    '''
    # 무한대 값 처리
    product_resell_index["resell_index"].replace([float("inf"), -float("inf")],  inplace=True)
    # NaN 값 보간
    # 보간 적용 (새로운 pandas 3.0 방식)
    product_resell_index["resell_index"] = product_resell_index["resell_index"].ffill()
    product_resell_index["resell_index"] = product_resell_index["resell_index"].bfill()
    product_resell_index["resell_index"] = product_resell_index["resell_index"].interpolate(method="linear")
    '''
    # NaN 및 Inf 값 처리
    product_resell_index["resell_index"] = product_resell_index["resell_index"].replace([float("inf"), -float("inf")], None)
    product_resell_index["resell_index"] = product_resell_index["resell_index"].ffill().bfill().interpolate(method="linear")
    
    # 보간법 적용 여부 확인
    if product_resell_index["resell_index"].isna().sum() > 0:
        interpolation_logs.append({"product_id": product_id, "method": "interpolation", "date": baseline_date})
    

    # 보간법 사용 로그 저장 (보간법 사용 내역이 있을 경우에만 저장)
    if interpolation_logs:
        save_interpolation_log()

    return product_resell_index
