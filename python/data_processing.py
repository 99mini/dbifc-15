#기준일 보정
import pandas as pd
from datetime import datetime, timedelta
#timedelta는 datetime 모듈에서 제공하는 클래스, 날짜와 시간 간의 차이를 표현하는 데 사용,특정 날짜에서 며칠을 더하거나 빼는 계산을 할 때 유용

#기준일(baseline_date)에 거래가 없으면 하루씩 앞뒤로 이동하여 가장 가까운 거래일의 데이터를 사용
def get_closest_trading_day(product_data, baseline_date):
    baseline_date = datetime.strptime(baseline_date, "%Y-%m-%d")
    
    # 날짜 정렬
    available_dates = sorted(product_data["date_created"].dt.date.unique())
    
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
    return product_data["total_volume"].interpolate(method="linear").fillna(method="ffill").fillna(method="bfill").mean()