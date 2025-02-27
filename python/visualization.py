#visualization.py
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os

from utils import save_csv

color_list = ['b', 'g', 'r', 'c', 'm', 'k', 'w']

def plot_resell_index(
    resell_index_data, 
    output_dir, 
    title="Resell Market Index", 
    save=False,
    show=False ):
    """
    Resell Index 그래프를 생성하는 함수

    Parameters:
    - resell_index_data: df
    - output_dir: str
    - title: str
    - save: bool

    Returns:
    - None
    """
    plt.figure(figsize=(10, 5))
    plt.plot(resell_index_data["date_created"], resell_index_data["market_resell_index"], marker='o', linestyle='-', color='b', label="Resell Index")

    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.ylabel("Resell Index (Baseline = 100)")
    plt.title(title)
    plt.legend()
    plt.grid(True)

    if save:
        plt.savefig(f'output/{output_dir}/{title}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.png', dpi=300, bbox_inches='tight')
        save_csv(resell_index_data, f"{output_dir}/{title}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv")

    if show:
        plt.show()

    plt.close()


def plot_single_resell_index(
    data,
    product_id,
    output_dir,
    title="resell",
    save=False,
    show=False ):
    plt.figure(figsize=(10, 5))
    plt.plot(
        data["date_created"], 
        data["resell_index"], 
        marker='o', 
        linestyle='-', 
        color='b', 
        label=f'{data["name"][0]}'
    )

    plt.xlabel("Date")
    plt.xticks([])
    plt.ylabel("Price")
    plt.title(f"{title} (Product ID: {product_id})")
    plt.legend()
    plt.grid(True)

    if save:
        save_csv(data, f"{output_dir}/{title}_{product_id}.csv")
        filename = f'output/{output_dir}/{title}_{product_id}.png'

        if filename not in os.listdir(f"output/{output_dir}"):
            plt.savefig(filename, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    plt.close()


def plot_premium_with_resell_index(
    resell_index_data, 
    premium_data_list, 
    output_dir, 
    title="Resell & Premium", 
    save=False,
    show=False):
    """
    :param resell_index_data: df
    :param premium_data_list: 프리미엄 데이터 리스트 (date_created, premium, product_id, name)
    :param output_dir:
    :param title:
    :param save:
    :return:
    """

    plt.figure(figsize=(15, 5))

    fig, resell_index_ax = plt.subplots()

    resell_index_ax.set_xlabel("Date")
    resell_index_ax.set_xticks(
        rotation=45, 
        ticks=[i for i in range(len(resell_index_data["date_created"]))],
        labels=resell_index_data["date_created"]
    )

    min_resell_index = int(resell_index_data["market_resell_index"].min()) // 10 * 10 - 10
    max_resell_index = int(resell_index_data["market_resell_index"].max()) // 10 * 10 + 10

    plt.ylim([-min_resell_index, max_resell_index])

    resell_index_ax.set_ylabel("Resell Index")
    resell_index_ax.set_yticks([i for i in range(min_resell_index, max_resell_index, 10)])

    premium_ax = resell_index_ax.twinx()

    min_premium = int(
        min(premium_data["normalized_premium"].min() for premium_data in premium_data_list)
    ) // 10 * 10 - 10
    max_premium = int(
        max(premium_data["normalized_premium"].max() for premium_data in premium_data_list)
    ) // 10 * 10 + 10

    premium_ax.set_ylabel("Normalized Premium")
    premium_ax.set_yticks([i for i in range(min_premium, max_premium, 10)])

    plt.title(title)
    plt.grid(True)

    resell_line = resell_index_ax.plot(
        resell_index_data["date_created"], 
        resell_index_data["market_resell_index"], 
        linestyle='-',
        linewidth=2,
        color='y', 
        label="Resell Index",
        dash_joinstyle='round'
    )

    lines = resell_line
    for idx, premium_data in enumerate(premium_data_list):
        lines += premium_ax.plot(
            premium_data["date_created"], 
            premium_data["normalized_premium"], 
            linestyle='-', 
            color=color_list[idx % len(color_list)], 
            label=f"{premium_data['name'].values[0]}",
            linewidth=1,
            alpha=0.5,
            dash_joinstyle='round'
        )

    labels = [l.get_label() for l in lines]
    resell_index_ax.legend(lines, labels, loc='upper right')

    fig.tight_layout()

    if save:
        plt.savefig(f'output/{output_dir}/{title}.png', dpi=300, bbox_inches='tight')
        save_csv(resell_index_data, f"{output_dir}/{title}-resell.csv")

        for premium_data in premium_data_list:
            product_id = premium_data["product_id"].values[0]
            save_csv(premium_data, f"{output_dir}/{title}-{product_id}.csv")

    if show:
        plt.show()
    plt.close()


def plot_resell_index_for_alpha(
    resell_index_data_with_alpha, 
    output_dir, 
    title="Resell Market Index", 
    save=False,
    show=False ):
    """
    alpha(민감도)값을 기준으로 resell index 그래프를 그리는 함수
    x축: 

    :params resell_index_data_with_alpha: list(df)["alpha", "date_created", "market_resell_index"]
    """
    plt.figure(figsize=(10, 5))

    for idx, values in enumerate(resell_index_data_with_alpha):
        alpha, data = values
        plt.plot(data["date_created"], data["market_resell_index"], linestyle='-', label=f"α={alpha}", color=color_list[idx % len(color_list)])

    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.ylabel("Resell Index")
    plt.legend()


    if save:
        for values in resell_index_data_with_alpha:
            alpha, data = values
            save_csv(data, f"{output_dir}/{title}-α-{alpha}.csv")

        plt.savefig(f'output/{output_dir}/{title}.png', dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    plt.close()

def plot_stock_index(
    stock_index_data,
    output_dir,
    title="Stock Index",
    save=False,
    show=False ):
    """
    Parametres:
    - stock_index_data: df ["날짜", "종가", "시가", "고가", "저가", "거래량", "변동 %"]
    - output_dir: str
    - title: str
    - save: bool
    - show: bool
    """

    stock_index_data["날짜"] = pd.to_datetime(stock_index_data["날짜"])
    plt.figure(figsize=(10, 5))
    
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.ylabel("Close")
    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.plot(stock_index_data["날짜"], stock_index_data["종가"], linestyle='-', color='b', label="Close")

    if save:
        save_csv(stock_index_data, f"{output_dir}/{title}.csv")
        plt.savefig(f'output/{output_dir}/{title}.png', dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    plt.close()

