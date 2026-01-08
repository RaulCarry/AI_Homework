import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("experiment_data_ez.csv")

df_success = df[df["Status"] == "SUCCESS"]

sns.set_theme(style="whitegrid")

plt.figure(figsize=(12, 6))
plot = sns.barplot(data=df_success, x="Level", y="Time (s)", hue="Algorithm")
plt.yscale("log")
plt.title("Execution Time per Level (Log Scale)")
plt.ylabel("Time (seconds)")
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("plot_time.png")
print("Generated plot_time.png")

df_nodes = df_success[df_success["Metric Type"] == "Nodes Expanded"]

plt.figure(figsize=(12, 6))
sns.barplot(data=df_nodes, x="Level", y="Metric Value", hue="Algorithm")
plt.yscale("log")
plt.title("Nodes Expanded by Algorithm")
plt.ylabel("Number of Nodes")
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("plot_nodes.png")
print("Generated plot_nodes.png")

df_len = df_success[df_success["Metric Type"].isin(["Solution Length", "Plan Length"])]

plt.figure(figsize=(12, 6))
sns.barplot(data=df_len, x="Level", y="Metric Value", hue="Algorithm")
plt.title("Solution Length Comparison (Optimality)")
plt.ylabel("Steps")
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("plot_quality.png")
print("Generated plot_quality.png")