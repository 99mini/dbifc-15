import pandas as pd
from resell_index import calculate_product_resell_index

def calculate_resell_market_index(transactions, product_ids, baseline_date):
    """
    여러 상품의 리셀 지수를 기반으로 전체 리셀 시장의 대표 지수를 계산하는 함수
    :param transactions: 전체 거래 데이터 (DataFrame)
    :param product_ids: 리셀 시장에서 추적할 인기 상품들의 ID 리스트
    :param baseline_date: 기준 날짜 (str, 예: "2025-01-01")
    :return: 리셀 시장 지수 DataFrame
    """
    resell_indices = []

    for product_id in product_ids:
        product_index = calculate_product_resell_index(transactions, product_id, baseline_date)
        product_index["product_id"] = product_id
        resell_indices.append(product_index)

    # 모든 상품의 데이터 결합
    market_data = pd.concat(resell_indices)

    # 날짜별 평균 리셀 지수 계산
    resell_market_index = market_data.groupby("date_created").agg(
        market_resell_index=("resell_index", "mean")
    ).reset_index()

    return resell_market_index
