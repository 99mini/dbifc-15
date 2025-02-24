from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os

color_list = ['b', 'g', 'r', 'c', 'm', 'k', 'w']

def plot_resell_index(resell_index_data, output_dir, title="Resell Market Index", save=False):
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

    plt.close()

def plot_single_resell_index(data, product_id, output_dir, title="resell", save=False):
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
        filename = f'output/{output_dir}/{title}_{product_id}.png'

        if filename not in os.listdir(f"output/{output_dir}"):
            plt.savefig(filename, dpi=300, bbox_inches='tight')
    else:
        plt.show()

    plt.close()

def plot_premium_with_resell_index(resell_index_data, premium_data_list, output_dir, title="Resell & Premium", save=False):
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
    else:
        plt.show()
    plt.close()