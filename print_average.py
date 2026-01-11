import pandas as pd
import numpy as np

def generate_average_table(file_name):
    df = pd.read_csv(file_name)
    df['Metric Value'] = pd.to_numeric(df['Metric Value'], errors='coerce')

    run_meta = df.groupby(['Algorithm', 'Level']).agg({
        'Time (s)': 'max',
        'Status': lambda x: 'SUCCESS' if 'SUCCESS' in x.values else ('FAILED' if 'FAILED' in x.values else x.iloc[0])
    })

    metrics = df.pivot_table(
        index=['Algorithm', 'Level'],
        columns='Metric Type',
        values='Metric Value',
        aggfunc='mean'
    )

    data = run_meta.join(metrics)

    success_rate = data.groupby('Algorithm')['Status'].apply(lambda x: (x == 'SUCCESS').mean() * 100)
    avg_time = data.groupby('Algorithm')['Time (s)'].mean()
    avg_nodes = data.groupby('Algorithm')['Nodes Expanded'].mean()
    avg_sol_len = data[data['Status'] == 'SUCCESS'].groupby('Algorithm')['Solution Length'].mean()

    summary = pd.DataFrame({
        'Success Rate (%)': success_rate,
        'Avg Time (s)': avg_time,
        'Avg Nodes': avg_nodes,
        'Avg Sol. Len.': avg_sol_len
    })
    
    summary = summary.fillna(0)

    return summary

file_path = 'experiment_data_ez.csv'
results = generate_average_table(file_path)

print(results)
print(results.to_latex(float_format="%.2f"))