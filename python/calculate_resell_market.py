import pandas as pd
import os
from resell_market_index import calculate_resell_market_index, calculate_resell_market_index_4h
from data_processing import save_interpolation_log
from visualization import plot_resell_index

# 데이터 경로 설정 (javascript/output 폴더에서 CSV 파일 로드)
DATA_PATH = os.path.join('..', 'javascript', 'output')

def load_transaction_data():

    all_transactions = []

    # output 폴더 내의 모든 .csv 파일을 불러오기
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".csv") and filename != "product_meta_data2.csv":  # 메타데이터 파일 제외
            file_path = os.path.join(DATA_PATH, filename)
            df = pd.read_csv(file_path)
            all_transactions.append(df)

    # 모든 데이터를 하나의 DataFrame으로 병합
    return pd.concat(all_transactions, ignore_index=True)

# product_meta_data.csv에서 상품 ID 리스트 불러오기
product_meta_path = os.path.join(DATA_PATH, "product_meta_data2.csv")
product_meta = pd.read_csv(product_meta_path)
# 전체 상품 목록에서 상품 ID만 리스트로 추출
product_ids = product_meta["product_id"].unique().tolist()

# 모든 거래 데이터 불러오기
transactions = load_transaction_data()
# ✅ 거래 데이터와 product_meta 병합 (발매가 추가)
transactions = transactions.merge(product_meta[['product_id', 'original_price']], on="product_id", how="left")

# 리셀 시장 지수 계산 (이 부분이 누락되지 않았는지 확인)
baseline_date = "2025-02-01T00:00:00Z"
# 24시간 간격 리셀 시장 지수 계산
[market_resell_index_24h, market_data] = calculate_resell_market_index(transactions, product_meta, product_ids, baseline_date)
print("\n리셀 시장 지수 (24시간 간격):")
print(market_resell_index_24h)

plot_resell_index(market_resell_index_24h, title="Resell Market Index (24h)", save=True)

filtered_data = market_data[market_data['date_created'] == '2025-02-01']
sorted_data = filtered_data.sort_values(by='total_volume', ascending=False).head(50)
sorted_product_ids = sorted_data['product_id'].tolist()

# 지수에 사용될 상품 목록 출력
print(sorted_product_ids)

# 4시간 간격 리셀 시장 지수 계산
market_resell_index_4h = calculate_resell_market_index_4h(transactions, product_meta, sorted_product_ids, baseline_date)
print("\n리셀 시장 지수 (4시간 간격):")
print(market_resell_index_4h)

plot_resell_index(market_resell_index_4h, title="Resell Market Index (4h)", save=True)

# 보간법 사용 내역 저장
save_interpolation_log()