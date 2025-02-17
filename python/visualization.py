import matplotlib.pyplot as plt
import pandas as pd

def plot_resell_index(resell_index_data, title="Resell Market Index"):
    plt.figure(figsize=(10, 5))
    plt.plot(resell_index_data["date_created"], resell_index_data["market_resell_index"], marker='o', linestyle='-', color='b', label="Resell Index")

    plt.xlabel("Date")
    plt.ylabel("Resell Index (Baseline = 100)")
    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.show()
