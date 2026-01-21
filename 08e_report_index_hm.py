import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


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


def get_max(series):
    max_val = -np.inf
    for s in series:
        if len(s) > 0:
            local_max = s.max()
            if local_max > max_val:
                max_val = local_max
    return max_val



def bin_data(data, max_len, steps=0.05):
    
    bin_edges = []
    current = 0.0
    while current <= max_len + steps:
        bin_edges.append(current)
        current += steps
    binned_data = []
    for s in data:
        hist, _ = np.histogram(s, bins=bin_edges)
        binned_data.append(hist)
    return binned_data,bin_edges

def to_heatmap(series):
    flat_ok, flat_fail, names = _flattenr(series)
    max_len = get_max(flat_fail + flat_ok)
    #print(f"Max length: {max_len}")
    data =[]
    for i, name in enumerate(names):
        binned_ok,edges = bin_data([flat_ok[i]], max_len)
        binned_fail,_ = bin_data([flat_fail[i]], max_len)
        point = {}
        for j,_ in enumerate(edges[:-1]):
            total = binned_ok[0][j] + binned_fail[0][j]
            if total > 0:
                point[f"{edges[j]:.2f}-{edges[j+1]:.2f}"] = binned_ok[0][j]/(binned_ok[0][j]+binned_fail[0][j])
        s = pd.Series(point, name=name)
        data.append(s)
        #plt.bar(edges[:-1], binned_ok[0], width=0.04
    
    df = pd.DataFrame(data)
    return df.transpose()

def plot_series(series, title="UWR Boxplot", ylabel="UWR", file=None):
    print(f"Plotting series: {title}")
    df = to_heatmap(series)
    plt.figure(figsize=(10,6))
    sns.heatmap(df, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Proportion of Correct Detections'})
    plt.title(title)
    plt.tight_layout()
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
        plt.close()
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