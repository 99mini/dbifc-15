#calculate_resell_market.py
import pandas as pd
import os

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