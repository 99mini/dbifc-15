import sys
import os

# 현재 스크립트의 폴더를 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resell_index import calculate_product_resell_index
from calculate_resell_market import load_transaction_data

# 데이터 로드
transactions = load_transaction_data("36.csv")

# 특정 상품 ID 설정 (예: 36번)
product_id = 36
baseline_date = "2025-02-01"

# 리셀 지수 계산
product_resell_data = calculate_product_resell_index(transactions, product_id, baseline_date)

# 결과 출력
print(product_resell_data)
