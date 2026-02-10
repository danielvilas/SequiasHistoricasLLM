import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

tests= ["fastest","efficient","deepseek","efficient3","bestf13","bestf1"]
modes = ["no-summary","summary","summary-expert"]

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
                result[test][mode] = {}
                res_ok = data[data['has_sequia']==data[col_name]]
                res_fail = data[data['has_sequia']!=data[col_name]]
                result[test][mode]['ok'] = res_ok[uwr_col]
                result[test][mode]['fail'] = res_fail[uwr_col]
    return result


def plot_series(series, title="UWR Boxplot", ylabel="instances", file=None):
    # hacemos un subplot de test filas y model columnas
    fig, axs = plt.subplots(nrows=len(tests), ncols=len(modes), figsize=(16,12))
    plt.suptitle(title)
    for i, test in enumerate(tests):
        for j, mode in enumerate(modes):
            ax = axs[i, j]
            if test in series and mode in series[test]:
                data_ok = series[test][mode]['ok']
                data_fail = series[test][mode]['fail']
                #hacemos un histograma con los dos
                ax.hist([data_ok, data_fail], label=['ok', 'fail'], bins=20, alpha=0.7)
                ax.set_title(f"{test}-{mode}")
                ax.set_ylabel(ylabel)
                ax.set_xlabel("UWR")
                #ax.tick_params(axis='x')
                ax.legend()
            else:
                ax.set_visible(False)
    plt.tight_layout()
    if file:
        plt.savefig(f"tmp/{file}")
    else:
        plt.show()
    pass

def plot_data(uwr, uwr_drought, uwr_no_drought, file=None):
    # hacemos un bloxplot de los dos series
    #fig,axes = plt.subplots(nrows=2, ncols=1, figsize=(4,6))
    
    #ax = axes[0]
    # hacemos un histograma de los dos series
    fig = plt.figure(figsize=(6,4))
    plt.hist([uwr], label=["UWR"], bins=20, alpha=0.7)
    plt.ylabel("número de PDFs")
    plt.xlabel("UWR")
    # ax = axes[1]
    # ax.hist([uwr_drought, uwr_no_drought], label=["UWR Drought", "UWR No Drought"], bins=20, alpha=0.7)
    # ax.set_ylabel("instances")
    #plt.legend()
    if file:
        plt.savefig(f"tmp/{file}")
    else:
        plt.show()
    pass

def main():
    if len(sys.argv) != 2:
        print("Usage: python 08b_report_index.py <dataset>")
        sys.exit(1)
    dataset = sys.argv[1]
    file = f"results/{dataset}/detect/{dataset}_indexed_ds.csv"
    data = pd.read_csv(file)

    #data["UWR"] = -np.log(data["UWR"]) 

    plot_data(data["UWR"],data[data["has_sequia"]==True]["UWR"], data[data["has_sequia"]==False]["UWR"], file=f"{dataset}_hist_uwr_overall.png")
    #print(data.head())
    
    list_no_tests(data)
    uwr = extract_series(data, "UWR")
    
    plot_series(uwr, title="UWR Boxplot (full)", ylabel="instances",file=f"{dataset}_hist_uwr_full.png")

    data = data[data['has_sequia']==True]
    uwr = extract_series(data, "UWR")
    plot_series(uwr, title="UWR Boxplot (only droughts)", ylabel="instances",file=f"{dataset}_hist_uwr_droughts.png")
if __name__ == "__main__":
    main()