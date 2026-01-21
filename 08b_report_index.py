import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#tests = ["bestf1","bestf13","efficient","efficient3","fastest","deepseek"]

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

def _flattenr(series):
    flat_ok =[]
    flat_fail =[]
    names = []
    for model in series:
        for mode in series[model]:
            flat_ok.append(series[model][mode]['ok'])
            flat_fail.append(series[model][mode]['fail'])
            names.append(f"{model}-{mode}")
    return flat_ok, flat_fail, names


def plot_series(series, title="UWR Boxplot", ylabel="UWR", file=None):
    flat_ok, flat_fail, names = _flattenr(series)
    # hacemos un bloxplotde los ok o fail
    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(6,8), sharex=True)
    plt.suptitle(title)
    # ok
    ax = axs[0]
    ax.boxplot(flat_ok, tick_labels=names, vert=True)
    ax.set_title("Correct Predictions")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='x', rotation=45)
    #ax.set_yticklabels(10.0**(-ax.get_yticks()))

    # fail
    ax = axs[1]
    ax.boxplot(flat_fail, tick_labels=names, vert=True)
    ax.set_title("Incorrect Predictions")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='x', rotation=90)
    #ax.set_yticklabels(10.0**(-ax.get_yticks()))
    plt.tight_layout()
    if file:
        plt.savefig(f"tmp/{file}")
    else:
        plt.show()
    pass

def plot_data(uwr, uwr_es, file=None):
    # hacemos un bloxplot de los dos series
    plt.figure(figsize=(4,3))
    plt.boxplot([uwr, uwr_es], tick_labels=["UWR","UWR_es"], vert=True)
    plt.title("UWR vs UWR_es")
    plt.ylabel("UWR")
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

    plot_data(data["UWR"], data["UWR_es"],file="uwr_vs_uwr_es.png")

    #print(data.head())
    list_no_tests(data)
    uwr = extract_series(data, "UWR")
    uwr_es = extract_series(data, "UWR_es")

    plot_series(uwr, title="UWR Boxplot (full)", ylabel="UWR",file="uwr_boxplot_full.png")
    plot_series(uwr_es, title="UWR_es Boxplot (full)", ylabel="UWR_es",file="uwr_es_boxplot_full.png")


    data = data[data['has_sequia']==True]
    uwr = extract_series(data, "UWR")
    uwr_es = extract_series(data, "UWR_es") 
    plot_series(uwr, title="UWR Boxplot (only droughts)", ylabel="UWR",file="uwr_boxplot_droughts.png")
    plot_series(uwr_es, title="UWR_es Boxplot (only droughts)", ylabel="UWR_es",file="uwr_es_boxplot_droughts.png")

if __name__ == "__main__":
    main()