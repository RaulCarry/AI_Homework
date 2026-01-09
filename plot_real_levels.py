import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

filename = "experiment_data.csv"
if not os.path.exists(filename):
    print("Error: experiment_data.csv not found.")
    exit()

try:
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip() 
except:
    exit()

df_success = df[(df["Level"] == "Level 1") & (df["Status"] == "SUCCESS")]

if df_success.empty:
    print("No successful runs for Level 1 found in the CSV.")
    exit()

sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

plot = sns.barplot(data=df_success, x="Algorithm", y="Time (s)")
plt.yscale("log") 

plt.title("Performance Comparison: Level 1 (Lower is Better)")
plt.xticks(rotation=45, ha='right')
plt.ylabel("Time (seconds) - Log Scale")
plt.tight_layout()

output_file = "level1_comparison.png"
plt.savefig(output_file)
print(f"Successfully created {output_file}")