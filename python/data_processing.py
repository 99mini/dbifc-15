#기준일 보정
import os
import pandas as pd
from datetime import datetime, timedelta
#timedelta는 datetime 모듈에서 제공하는 클래스, 날짜와 시간 간의 차이를 표현하는 데 사용,특정 날짜에서 며칠을 더하거나 빼는 계산을 할 때 유용

#기준일(baseline_date)에 거래가 없으면 하루씩 앞뒤로 이동하여 가장 가까운 거래일의 데이터를 사용
def get_closest_trading_day(product_data, baseline_date):
    baseline_date = datetime.strptime(baseline_date, "%Y-%m-%d")
    
    # 날짜 정렬
    available_dates = sorted(product_data["date_created"].dt.date.unique())

     # 사용 가능한 날짜가 없는 경우 예외 처리
    if not available_dates:
        return None
    
    # 기준일이 거래 데이터에 있는 경우 그대로 사용
    if baseline_date.date() in available_dates:
        return baseline_date.date()
    
    # 기준일 이전/이후 데이터 중 가장 가까운 날짜 찾기
    closest_date = min(available_dates, key=lambda x: abs(x - baseline_date.date()))
    
    return closest_date

def get_adjusted_baseline_price(product_data, baseline_date):
    """
    기준일에 거래 데이터가 없으면, 가장 가까운 거래일을 찾아 가격을 가져오거나, 보간법을 적용하여 값을 생성.
    """
    closest_date = get_closest_trading_day(product_data, baseline_date)

    if closest_date is not None:
        return product_data[product_data["date_created"].dt.date == closest_date]["avg_price"].mean()
    
    if product_data["avg_price"].isna().all():
        return product_data["avg_price"].fillna(method="bfill").fillna(method="ffill").interpolate(method="linear").mean()
        #return None  # 모든 데이터가 NaN인 경우 None 반환

    # 그래도 값이 없으면 보간법 적용
    return product_data["avg_price"].interpolate(method="linear").fillna(method="ffill").fillna(method="bfill").mean()

def get_adjusted_baseline_volume(product_data, baseline_date):
    """
    기준일 거래량이 없을 경우, 가장 가까운 거래량 데이터를 가져오거나 보간법을 적용하여 보정된 거래량을 반환.
    :param product_data: 특정 상품의 거래 데이터 (DataFrame)
    :param baseline_date: 기준 날짜 (str, "YYYY-MM-DD")
    :return: 보정된 기준 거래량 (float)
    """
    closest_date = get_closest_trading_day(product_data, baseline_date)

    if closest_date is not None:
        return product_data[product_data["date_created"].dt.date == closest_date]["total_volume"].mean()
    
    # 보간법 적용 (앞/뒤 데이터 활용)
    if product_data["total_volume"].isna().all():
        return None  # 모든 데이터가 NaN이면 None 반환
    # 보간법 적용 (앞/뒤 데이터 활용)
    return product_data["total_volume"].interpolate(method="linear").fillna(method="ffill").fillna(method="bfill").mean()


interpolation_logs = []

# 로그 파일 저장 경로 설정 (python/output 폴더에 저장)
LOG_DIR = os.path.join("output")  # 로그 파일 저장할 폴더명
os.makedirs(LOG_DIR, exist_ok=True)  # 폴더가 없으면 생성
log_file_path = os.path.join(LOG_DIR, "interpolation_log.csv")

def save_interpolation_log():
    """
    보간법 사용 내역을 CSV 파일로 저장 (기존 데이터 유지)
    """
    if interpolation_logs:
        df = pd.DataFrame(interpolation_logs)
        os.makedirs("output", exist_ok=True)  # 폴더 없으면 생성

        # 기존 파일이 있으면 추가 모드로 저장
        if os.path.exists(log_file_path):
            df_existing = pd.read_csv(log_file_path)
            df = pd.concat([df_existing, df], ignore_index=True)

        df.to_csv(log_file_path, index=False)
        print(f"✅ 보간법 사용 내역이 {log_file_path} 파일에 저장되었습니다!")
    else:
        print("ℹ️ 보간법 사용 내역이 없습니다.")