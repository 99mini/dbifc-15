#전체 리셀 시장 지수를 계산
import pandas as pd
from resell_index import calculate_product_resell_index
from data_processing import get_adjusted_baseline_price, get_adjusted_baseline_volume
from resell_utils import normalize_index, compute_resell_index_custom, get_discount_volume_threshold

def calculate_resell_market_index(transactions, product_meta, product_ids, baseline_date):
    """
    여러 상품의 리셀 지수를 기반으로 전체 리셀 시장의 대표 지수를 계산하는 함수
    """
    resell_indices = []

    for product_id in product_ids:
        product_index = calculate_product_resell_index(transactions, product_meta, product_id, baseline_date, alpha=0.1)

        '''if product_index.empty:
            continue  # 거래 데이터가 없는 경우 스킵'''
        # 빈 데이터 또는 resell_index 누락 시 스킵
        if product_index.empty or "resell_index" not in product_index.columns:
            print(f"⚠️ 상품 ID {product_id}의 리셀 지수 데이터 없음, 스킵")
            continue

        product_index["product_id"] = product_id
        product_index["name"] = product_meta[product_meta["product_id"] == product_id]["name"].values[0]

        resell_indices.append(product_index)

    if not resell_indices:
        print("⚠️ 모든 상품의 데이터가 없음 → 빈 데이터프레임 반환")
        return pd.DataFrame(columns=["date_created", "market_resell_index"])

    market_data = pd.concat(resell_indices, ignore_index=True)
    # 24시간 단위로 그룹화 (날짜만 사용)
    market_data["date_created"] = pd.to_datetime(market_data["date_created"])
    market_data["date_only"] = market_data["date_created"].dt.date

    resell_market_index = market_data.groupby("date_created").agg(
        market_resell_index=("resell_index", "mean")
    ).reset_index().rename(columns={"date_only": "date_created"})

     # 기준일(예: baseline_date)에 해당하는 값이 100이 되도록 정규화
    resell_market_index = normalize_index(resell_market_index, index_column="market_resell_index", baseline_date=baseline_date)

    return [resell_market_index, market_data]

def calculate_resell_market_index_4h(transactions, product_meta, product_ids, baseline_date, alpha=0.1):
    """
    여러 상품의 리셀 지수를 기반으로 전체 리셀 시장의 대표 지수를 4시간 단위로 계산하는 함수.
    - 각 4시간 구간에 데이터가 있으면 해당 데이터를 이용해 인덱스를 산출하고,
    - 데이터가 없으면 data_processing.py 내 보정 함수들(get_adjusted_baseline_price, get_adjusted_baseline_volume 등)을
      필요에 따라 호출하여 인덱스 값을 추정하는 방식으로 처리합니다.
    """

    # 4시간 단위로 그룹화
    step = "4h"

    resell_indices = []

    # 우선 각 상품별로 4시간 단위 리셀 지수를 계산
    # 기존 함수와 동일한 calculate_product_resell_index를 사용하면 날짜 단위로 그룹화되므로, 여기서는 직접 4시간 단위로 재계산합니다.
    for product_id in product_ids:
        # 해당 상품의 거래 데이터 필터링 및 날짜 변환
        product_data = transactions[(transactions["product_id"] == product_id)].copy()

        if product_data.empty:
            print(f"⚠️ 상품 ID {product_id}의 거래 데이터 없음, 스킵")
            continue
    
        product_data["date_created"] = pd.to_datetime(product_data["date_created"])
        product_data = product_data.set_index("date_created")

        # 4시간 단위로 그룹화하여 평균 가격과 거래 건수(거래량)를 계산
        grp = product_data.resample(step).agg(
            avg_price=("price", "mean"),
            total_volume=("price", "count")
        ).reset_index()
        
        # 보정이 필요한 경우 (예: 그룹 내에 데이터가 전혀 없는 구간은 NaN으로 남을 수 있으므로)
        # 4시간 그룹 중 NaN이 존재하면, 가장 가까운 거래일의 보정값을 가져오는 방식으로 처리할 수 있습니다.
        # 아래는 예시로 첫 그룹의 값을 기준으로 보정하는 간단한 로직입니다.
        if grp.empty:
            print(f"⚠️ 상품 ID {product_id}의 4시간 그룹 데이터 없음, 스킵")
            continue

        # 기준 가격은 product_meta에서 가져오거나, 없으면 보정 함수 사용
        baseline_price_arr = product_meta.loc[product_meta["product_id"] == product_id, "original_price"].values
        baseline_price = baseline_price_arr[0] if len(baseline_price_arr) > 0 else get_adjusted_baseline_price(grp, baseline_date)

        if baseline_price is None or pd.isna(baseline_price) or baseline_price == 0:
            # 필요 시 보정 함수 호출
            baseline_price = get_adjusted_baseline_price(grp, baseline_date)

        # 기준 거래량: 첫 구간의 거래량 또는 보정 값
        #baseline_volume = grp["total_volume"].iloc[0] if not grp["total_volume"].isna().all() else get_adjusted_baseline_volume(grp, baseline_date)

        '''
        # resell_index.py와 동일한 계산 방식 적용
        grp["price_premium"] = grp["avg_price"] - baseline_price
        grp["normalized_premium"] = grp["price_premium"] / baseline_price
        grp["adjusted_weight"] = alpha * grp["total_volume"] + (1 - alpha) * grp["normalized_premium"]
        grp["resell_index"] = (grp["avg_price"] * grp["adjusted_weight"]) / (baseline_price * baseline_volume) * 100
        '''

        # 지수 계산: (평균가격 * 거래량) / (기준가격 * 기준거래량) * 100
        #grp["resell_index"] = (grp["avg_price"] * grp["total_volume"]) / (baseline_price * baseline_volume) * 100
        '''

        # 결측치나 Inf 값에 대해서는 전/후 값 보간 혹은 fallback 처리
        grp["resell_index"] = grp["resell_index"].replace([float("inf"), -float("inf")], None)
        grp["resell_index"] = grp["resell_index"].ffill().bfill().interpolate(method="linear")
        '''
         # 각 4시간 구간별로 resell index 계산 (공통 함수 사용)
        #grp["resell_index"] = grp.apply(
        #    lambda row: compute_resell_index_custom(row["avg_price"], row["total_volume"], baseline_price, baseline_volume, alpha), axis=1
        #)
        # 기준 거래량: 첫 4시간 그룹의 거래량 또는 보정 값
        if not grp["total_volume"].isna().all():
            baseline_volume = grp["total_volume"].iloc[0]
        else:
            baseline_volume = get_adjusted_baseline_volume(grp, baseline_date)
        
        # 할인 거래량 임계값 산출: 그룹 데이터를 대상으로 get_discount_volume_threshold 함수 사용
        discount_volume_threshold = get_discount_volume_threshold(product_data.reset_index(), baseline_price, quantile=0.5, default_threshold=1)

        # compute_resell_index_custom 호출 시 discount_volume_threshold 인자 추가
        grp["resell_index"] = grp.apply(
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
        grp["resell_index"] = grp["resell_index"].replace([float("inf"), -float("inf")], None)
        grp["resell_index"] = grp["resell_index"].ffill().bfill().interpolate(method="linear")
        
        # 첫 4시간 구간을 기준으로 정규화
        grp = normalize_index(grp, "resell_index", grp["date_created"].iloc[0])

        grp["product_id"] = product_id
        resell_indices.append(grp)

    if not resell_indices:
        print("⚠️ 모든 상품의 4시간 데이터가 없음 → 빈 데이터프레임 반환")
        return pd.DataFrame(columns=["date_created", "market_resell_index"])

    market_data = pd.concat(resell_indices, ignore_index=True)
    market_data = market_data.sort_values("date_created")
    market_data = market_data.set_index("date_created")

    # 4시간 단위로 그룹화하여 시장 지수 산출 (평균값)
    results = []
    grouped = market_data.resample(step)
    for interval, group in grouped:
        idx_value = group["resell_index"].mean() if not group.empty else 0
        results.append({"date_created": interval, "market_resell_index": idx_value})


    return pd.DataFrame(results).reset_index(drop=True)

