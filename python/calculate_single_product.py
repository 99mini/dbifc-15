#개별 상품 ID별 리셀 지수 계산
import sys
import os
from resell_index import calculate_product_resell_index
from calculate_resell_market import load_transaction_data
import pandas as pd
'''
# 현재 스크립트의 폴더를 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 데이터 로드
transactions = load_transaction_data("36.csv")

# 특정 상품 ID 설정 (예: 36번)
product_id = 36
baseline_date = "2025-02-01"

# 리셀 지수 계산
product_resell_data = calculate_product_resell_index(transactions, product_id, baseline_date)

# 결과 출력
print(product_resell_data)
'''
# 데이터 경로 설정
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "javascript", "output"))

# product_meta_data.csv 경로 설정
product_meta_path = os.path.join(DATA_PATH, "product_meta_data.csv")

# 파일 존재 여부 확인
if not os.path.exists(product_meta_path):
    raise FileNotFoundError(f"파일이 존재하지 않습니다: {product_meta_path}")

# product_meta 데이터 로드
product_meta = pd.read_csv(product_meta_path)

# 거래 데이터 로드
transactions = load_transaction_data("36.csv")

# 특정 상품 ID 및 기준일 설정
product_id = 36
baseline_date = "2025-02-01"

# 리셀 지수 계산
product_resell_data = calculate_product_resell_index(transactions, product_meta, product_id, baseline_date)

# 결과 출력
print(product_resell_data)
print(f"product_id: {product_id}")
print(f"baseline_price: {product_meta[product_meta['product_id'] == product_id]['original_price'].values}")
