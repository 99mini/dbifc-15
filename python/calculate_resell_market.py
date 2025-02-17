import pandas as pd
import os

# 데이터 경로 설정 (javascript/output 폴더에서 CSV 파일 로드)
DATA_PATH = r"C:\Users\eujin\dbifc-15\javascript\output"


def load_transaction_data(filename):
    """ 거래 데이터를 불러오는 함수 """
    file_path = os.path.join(DATA_PATH, filename)

     # 경로 확인을 위한 출력
    print(f"파일을 찾는 경로: {file_path}")
    print(f"파일 존재 여부: {os.path.exists(file_path)}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일이 존재하지 않습니다: {file_path}")

    return pd.read_csv(file_path)

# 예제: 36.csv 파일 로드
transactions = load_transaction_data("36.csv")

# 데이터 확인
print(transactions.head())
