import os
import random
import time

import pandas as pd

from resell_market_index import calculate_resell_market_index, calculate_resell_market_index_4h
from data_processing import save_interpolation_log
from visualization import plot_resell_index, plot_premium_with_resell_index
from utils import load_transaction_data

# javascript/output 폴더 경로 설정
DATA_PATH = os.path.join("..", "source")

baseline_date   = "2025-01-15T00:00:00Z"
endline_date    = "2025-02-15T00:00:00Z"

start_time = time.time()

def main():
    # product_meta_data.csv에서 상품 ID 리스트 불러오기
    product_meta_path = os.path.join(DATA_PATH, "meta", "product_meta_data.csv")
    product_meta = pd.read_csv(product_meta_path)
    # 전체 상품 목록에서 상품 ID만 리스트로 추출
    product_ids = product_meta["product_id"].unique().tolist()

    # 모든 거래 데이터 불러오기
    transactions = load_transaction_data()
    # ✅ 거래 데이터와 product_meta 병합 (발매가 추가)
    #transactions["date_created"] = pd.to_datetime(transactions["date_created"])
    transactions = transactions.merge(product_meta[["product_id", "original_price"]], on="product_id", how="left")

    # 기준일 ~ endline_date 이간 데이터만 사용
    transactions = transactions[transactions["date_created"] >= baseline_date]
    transactions = transactions[transactions["date_created"] < endline_date]

    # 24시간 간격 리셀 시장 지수 계산
    [market_resell_index_24h, market_data] = calculate_resell_market_index(transactions, product_meta, product_ids, baseline_date)
    print("\n리셀 시장 지수 (24시간 간격):")
    print(market_resell_index_24h)

    plot_resell_index(
        market_resell_index_24h,
        "resell_index", 
        title="Resell Market Index (24h) - 0115~0215", 
        save=True,
        # show=True
    )

    filtered_data = market_data[market_data["date_created"] == baseline_date.split("T")[0]]
    sorted_data = filtered_data.sort_values(by="total_volume", ascending=False).head(25)

    # 지수에 사용될 상품 id 목록
    sorted_product_ids = sorted_data["product_id"].tolist()

    # 지수에 편입되지 않은 삼풍 id 목록
    non_transfer_product_ids = [id for id in product_ids if id not in sorted_product_ids]

    # 지수에 사용될 상품 목록 출력
    print(sorted_product_ids)

    # 4시간 간격 리셀 시장 지수 계산
    market_resell_index_4h = calculate_resell_market_index_4h(transactions, product_meta, sorted_product_ids, baseline_date)
    print("\n리셀 시장 지수 (4시간 간격):")
    print(market_resell_index_4h)

    plot_resell_index(
        market_resell_index_4h,
        "resell_index",
        title="Resell Market Index (4h) - 0115~0215", 
        save=True,
        # show=True
    )

    # 보간법 사용 내역 저장
    save_interpolation_log()

    # 상품별 리셀 가격 타임시리즈 그래프 그리기
    # 지수에 편입된 상품들
    # for product_id in sorted_product_ids:
    #     data = pd.read_csv(f"{DATA_PATH}/{product_id}.csv")


    # sample 갯수
    sample_size = 4
    premium_data = []
    # 지수에 편입되지 않은 상품들
    for product_id in random.sample(non_transfer_product_ids, k = sample_size):
        data = pd.read_csv(f"{DATA_PATH}/all-trading/{product_id}.csv")

        original_price = product_meta[product_meta["product_id"] == product_id]["original_price"].values[0]
        data["normalized_premium"] = (data["price"] - original_price) / original_price * 100

        data["name"] = product_meta[product_meta["product_id"] == product_id]["name"].values[0]

        if data["name"].empty:
            data["name"] = "Unknown"

        data["date_created"] = pd.to_datetime(data["date_created"])

        # baseline_date ~ endline_date 데이터만 선택
        data = data[data["date_created"] >= baseline_date]
        data = data[data["date_created"] < endline_date]

        premium_data.append(data)

    # 리셀 시장 지수와 상품별 리셀 가격 타임시리즈 그래프 그리기
    plot_premium_with_resell_index(
        market_resell_index_4h,
        premium_data,
        output_dir="merged",
        title="Resell & Premium (4h) - 0115~0215",
        save=True,
        # show=True
    )
    plot_premium_with_resell_index(
        market_resell_index_24h,
        premium_data,
        output_dir="merged",
        title="Resell & Premium (24h) - 0115~0215",
        save=True,
        # show=True
    )

    print(f"execution time: {time.time() - start_time}")

if __name__ == "__main__":
	main()