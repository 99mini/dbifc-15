#전체 리셀 시장 지수를 계산
import pandas as pd
from resell_index import calculate_product_resell_index
'''
not_exist = ['229945', '28180',  '442814', '388425',
  '396523', '323894', '227047', '80819',
  '64439',  '90918',  '381854', '52130',
  '47257',  '72385',  '237579', '19328',
  '354255', '77086',  '74156',  '429528',
  '435203', '226052', '215023', '24008',
  '381872', '317696', '74712',  '178942',
  '121861', '277940', '82783',  '313064',
  '302266', '23764',  '288895', '65213',
  '42531',  '312541', '296776', '436226',
  '61862',  '354545', '366013', '118274',
  '436224']

def calculate_resell_market_index(transactions, product_meta, product_ids, baseline_date):
    """
    여러 상품의 리셀 지수를 기반으로 전체 리셀 시장의 대표 지수를 계산하는 함수
    :param transactions: 전체 거래 데이터 (DataFrame)
    :param product_ids: 리셀 시장에서 추적할 인기 상품들의 ID 리스트
    :param baseline_date: 기준 날짜 (str, 예: "2025-01-01")
    :return: 리셀 시장 지수 DataFrame
    """
    resell_indices = []

    for product_id in product_ids:

        if product_id in not_exist:
            continue
        product_index = calculate_product_resell_index(transactions, product_meta, product_id, baseline_date)
        product_index["product_id"] = product_id
        resell_indices.append(product_index)

    # 모든 상품의 데이터 결합
    market_data = pd.concat(resell_indices,  ignore_index=True)

    # 날짜별 평균 리셀 지수 계산
    resell_market_index = market_data.groupby("date_created").agg(
        market_resell_index=("resell_index", "mean")
    ).reset_index()

    return resell_market_index
'''
def calculate_resell_market_index(transactions, product_meta, product_ids, baseline_date):
    """
    여러 상품의 리셀 지수를 기반으로 전체 리셀 시장의 대표 지수를 계산하는 함수
    """
    resell_indices = []

    for product_id in product_ids:
        product_index = calculate_product_resell_index(transactions, product_meta, product_id, baseline_date)

        '''if product_index.empty:
            continue  # 거래 데이터가 없는 경우 스킵'''
        # 🔹 빈 데이터 또는 resell_index 누락 시 스킵
        if product_index.empty or "resell_index" not in product_index.columns:
            print(f"⚠️ 상품 ID {product_id}의 리셀 지수 데이터 없음, 스킵")
            continue

        product_index["product_id"] = product_id
        resell_indices.append(product_index)

    if not resell_indices:
        print("⚠️ 모든 상품의 데이터가 없음 → 빈 데이터프레임 반환")
        return pd.DataFrame(columns=["date_created", "market_resell_index"])

    market_data = pd.concat(resell_indices, ignore_index=True)

    resell_market_index = market_data.groupby("date_created").agg(
        market_resell_index=("resell_index", "mean")
    ).reset_index()

    return resell_market_index
