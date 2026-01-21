import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

tests= ["fastest","efficient","efficient3","deepseek","bestf13","bestf1"]
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


def plot_series(series, title="UWR Boxplot", ylabel="UWR", file=None):
    # hacemos un subplot de test filas y model columnas
    fig, axs = plt.subplots(nrows=len(tests), ncols=len(modes), figsize=(16,12), sharex=True)
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
                ax.tick_params(axis='x', rotation=45)
                ax.legend()
            else:
                ax.set_visible(False)
    plt.tight_layout()
    if file:
        plt.savefig(f"tmp/{file}")
    else:
        plt.show()
    pass

def plot_data(uwr, uwr_es, file=None):
    # hacemos un histograma de los dos series
    plt.figure(figsize=(4,3))
    plt.hist([uwr, uwr_es], label=["UWR","UWR_es"], bins=20, alpha=0.7)
    plt.title("UWR vs UWR_es")
    plt.ylabel("UWR")
    plt.legend()
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
    #data["UWR_es"] = -np.log(data["UWR_es"])

    plot_data(data["UWR"], data["UWR_es"],file="hist_uwr_vs_uwr_es.png")
    #print(data.head())
    list_no_tests(data)
    uwr = extract_series(data, "UWR")
    uwr_es = extract_series(data, "UWR_es")

    plot_series(uwr, title="UWR Boxplot (full)", ylabel="UWR",file="uwr_hist_full.png")
    plot_series(uwr_es, title="UWR_es Boxplot (full)", ylabel="UWR_es",file="uwr_es_hist_full.png")


    data = data[data['has_sequia']==True]
    uwr = extract_series(data, "UWR")
    uwr_es = extract_series(data, "UWR_es") 
    plot_series(uwr, title="UWR Boxplot (only droughts)", ylabel="UWR",file="uwr_hist_droughts.png")
    plot_series(uwr_es, title="UWR_es Boxplot (only droughts)", ylabel="UWR_es",file="uwr_es_hist_droughts.png")

if __name__ == "__main__":
    main()