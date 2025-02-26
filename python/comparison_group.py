import os

from visualization import plot_stock_index
from utils import load_csv

stock_path = os.path.join('stock-index')

def comparison_group():
    """
    S&P 500과 KOSPI 주가 그래프 저장
    """
    snp500_path = os.path.join(stock_path, "snp500.csv")
    kospi_path = os.path.join(stock_path, "kospi.csv")
    
    snp500 = load_csv(snp500_path)
    plot_stock_index(snp500, "stock-index", "S&P 500", save=True, show=True)

    kospi = load_csv(kospi_path)
    plot_stock_index(kospi, "stock-index", "KOSPI", save=True, show=True)

comparison_group()
