from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_resell_index(resell_index_data, output_dir, title="Resell Market Index", save=False):
    plt.figure(figsize=(10, 5))
    plt.plot(resell_index_data["date_created"], resell_index_data["market_resell_index"], marker='o', linestyle='-', color='b', label="Resell Index")

    plt.xlabel("Date")
    plt.ylabel("Resell Index (Baseline = 100)")
    plt.title(title)
    plt.legend()
    plt.grid(True)

    if save:
        plt.savefig(f'output/{output_dir}/{title}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.png', dpi=300, bbox_inches='tight')

    plt.close()

def plot_single_product(data, product_id, output_dir, title="resell", save=False):
    plt.figure(figsize=(10, 5))
    plt.plot(data["date_created"], data["price"], linestyle='-', color='b', label="Resell")

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