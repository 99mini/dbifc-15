# resell_utils.py
import pandas as pd

def compute_resell_index(avg_price, total_volume, baseline_price, baseline_volume, alpha):
    """
    주어진 값들을 바탕으로 resell index를 계산합니다.
    """
    price_premium = avg_price - baseline_price
    normalized_premium = price_premium / baseline_price
    adjusted_weight = alpha * total_volume + (1 - alpha) * normalized_premium
    return (avg_price * adjusted_weight) / (baseline_price * baseline_volume) * 100

def normalize_index(df, index_column="resell_index", baseline_date=None):
    """
    DataFrame의 지수를 기준일(또는 첫 행의 값)으로 정규화하여 기준일의 값이 100이 되도록 조정합니다.
    baseline_date가 주어지면 해당 날짜의 값을 기준으로, 그렇지 않으면 첫 행의 값을 사용합니다.
    """
    if baseline_date is not None and baseline_date in df["date_created"].values:
        base_value = df.loc[df["date_created"] == baseline_date, index_column].iloc[0]
    else:
        base_value = df[index_column].iloc[0]
    df[index_column] = df[index_column] / base_value * 100
    return df
