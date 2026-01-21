import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

tests = ["bestf1","bestf13","efficient","efficient3","fastest","deepseek"]
modes = ["no-summary","summary","summary-expert"]

# Definimos un orden fijo de que prueba es mas sencilla
# Nos basamos en los tiempos de ejecucion y numero de parametros
order=[
    "fastest-no-summary",
    "efficient-no-summary",
    "fastest-summary-expert",
    "fastest-summary",
    "efficient-summary-expert",
    "efficient-summary",
    "efficient3-no-summary",
    "deepseek-no-summary",
    "efficient3-summary-expert",
    "efficient3-summary",
    "deepseek-summary-expert",
    "deepseek-summary",
    "bestf13-no-summary",
    "bestf1-no-summary",
    "bestf13-summary-expert",
    "bestf13-summary",
    "bestf1-summary-expert",
    "bestf1-summary",
]

def list_no_tests(data):
    for test in tests:
        for mode in modes:
            col_name = f'pred_sequia_{test}-{mode}'
            if col_name not in data.columns:
                print(f"Missing column: {col_name}")

def extract_series(data,uwr_col)->dict:
    print("--------")
    print("Extracting series from indexed dataset")
    result = {}
    for test in tests:
        result[test] = {}
        for mode in modes:
            col_name = f'pred_sequia_{test}-{mode}'
            if col_name in data.columns:
                result[test][mode] = data[data['selected_test']==test+'-'+mode][uwr_col]
                
    return result

def _flattenr(series):
    flat=[]
    names = []
    ret = {}
    for model in series:
        for mode in series[model]:
            ret[f"{model}-{mode}"]=series[model][mode]
            
    for name in order:
        if name in ret:
            flat.append(ret[name])
            names.append(f"{name}({len(ret[name])})")
    
    return flat, names

def plot_series(series, title="UWR Boxplot", ylabel="UWR"):
    flat, names = _flattenr(series)
    # hacemos un bloxplotde los ok o fail
    plt.figure(figsize=(12,6))
        
    plt.boxplot(flat, tick_labels=names, vert=True)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.tick_params(axis='x', rotation=90)
    #ax.set_yticklabels(10.0**(-ax.get_yticks()))

    plt.tight_layout()
    plt.show()
    pass

def select_test(row):
    for test in order:
        col_name = f'pred_sequia_{test}'
        if col_name not in row:
            print(f"Column not found: {col_name}")
            continue
        if row[col_name]==row['has_sequia']:
            return test
    return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python 08b_report_index.py <dataset>")
        sys.exit(1)
    dataset = sys.argv[1]
    file = f"results/{dataset}/detect/{dataset}_indexed_ds.csv"
    data = pd.read_csv(file)
    list_no_tests(data)
    
    data["selected_test"] = data.apply(lambda row:select_test(row), axis=1)
    data.to_csv(f"results/{dataset}/detect/{dataset}_indexed_ds2.csv", index=False)
    print(data.head())
    

    #data["UWR"] = -np.log(data["UWR"]) 
    #data["UWR_es"] = -np.log(data["UWR_es"])

    #print(data.head())
    
    uwr = extract_series(data, "UWR")
    uwr_es = extract_series(data, "UWR_es")

    plot_series(uwr, title="UWR Boxplot (full)", ylabel="UWR")
    plot_series(uwr_es, title="UWR_es Boxplot (full)", ylabel="UWR_es")


    data = data[data['has_sequia']==True]
    uwr = extract_series(data, "UWR")
    uwr_es = extract_series(data, "UWR_es") 
    plot_series(uwr, title="UWR Boxplot (only droughts)", ylabel="UWR")
    plot_series(uwr_es, title="UWR_es Boxplot (only droughts)", ylabel="UWR_es")

if __name__ == "__main__":
    main()