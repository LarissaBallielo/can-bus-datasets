import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("~/Documents/UNIFEI/IC/can-bus-datasets/data/collected/python_can/dataset.csv")
primeiras = df.head(20)

primeiras.plot(x="timestamp", subplots=True, figsize=(8, 12), marker="o")
plt.tight_layout()
plt.savefig("primeiras_20.png")
plt.show()