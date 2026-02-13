import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from sklearn.metrics import precision_recall_fscore_support,accuracy_score

#tests = ["qwen25.72b.cot","qwen3.32b.cot","qwen25.7b","qwen3.8b","qwen25.3b","deepseek.8b"]

tests= ["qwen25.3b","qwen25.7b","deepseek.8b","qwen3.8b","qwen3.32b.cot","qwen25.72b.cot"]
modes = ["no-summary","summary","summary-expert"]

def list_no_tests(data):
    for test in tests:
        for mode in modes:
            col_name = f'pred_sequia_{test}-{mode}'
            if col_name not in data.columns:
                print(f"Missing column: {col_name}")

def calc_scores(real_data, pred_data):
    if len(real_data) != len(pred_data):
        return None
    if len(real_data) == 0:
        return None
    # Calculate scores: Accuracy, Precision, Recall, F1-Score
    accuracy = accuracy_score(real_data, pred_data)
    score = precision_recall_fscore_support(real_data, pred_data,labels=[True])

    return {
        'accuracy': accuracy,
        'precision': score[0][0],
        'recall': score[1][0],
        'f1_score': score[2][0]
    }

def extract_series(data)->dict:
    print("--------")
    print("Extracting series from indexed dataset")
    result = {}
    for bin_str in data:
        if bin_str not in result:
            result[bin_str] = {}
    
        rows = data[bin_str]
        result[bin_str]["len"] = len(rows)

        df_bin = pd.DataFrame(rows)
        for test in tests:
            result[bin_str][test] = {}
            for mode in modes:
                if df_bin.empty:
                    result[bin_str][test][mode] = None
                    continue
                col_name = f'pred_sequia_{test}-{mode}'
                if col_name not in df_bin.columns:
                    result[bin_str][test][mode] = None
                    continue
                try:
                    scores = calc_scores(df_bin['has_sequia'], df_bin[col_name])
                    result[bin_str][test][mode] = scores
                except Exception as e:
                    print(f"Error calculating scores for bin {bin_str}, test {test}, mode {mode}: {e}")
                    result[bin_str][test][mode] = None            
        #print(f"Extracted scores for bin {bin_str}")
        #exit(0)
                
    return result

def get_max(series):
    max_val = -np.inf
    for s in series:
        if len(s) > 0:
            local_max = s.max()
            if local_max > max_val:
                max_val = local_max
    return max_val



def bin_data(data:pd.DataFrame, column, steps=0.05):

    max_len = get_max([data[column]])
    ret = {}
    bin_edges = []
    current = 0.0
    while current <= max_len + steps:
        bin_edges.append(current)
        current += steps

    for i in range(len(bin_edges)-1):
        bin_str = f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}"
        ret[bin_str] = []
    
    for _,row in data.iterrows():
        bin = np.digitize(row[column], bin_edges) -1    
        bin_str = f"{bin_edges[bin]:.2f}-{bin_edges[bin+1]:.2f}"
        ret[bin_str].append(row)

    return ret, bin_edges

def _flattenr(series,score, min_score=0.0):
    flat ={}
    
    for model in series:
        if model == "len":
            continue
        for mode in series[model]:
            name = f"{model}-{mode}"
            if series[model][mode] is None or series[model][mode][score] == 0.0 or series[model][mode][score] < min_score:
                flat.update({name:None})
            else:
                flat.update({name:series[model][mode][score]})
            
    return flat

def to_heatmap(data, score, min_score=0.0):
    result =[]
    for bin_str in data:
        scores = _flattenr(data[bin_str],score, min_score)
        s = pd.Series(scores, name=f"{bin_str} ({data[bin_str]['len']})")
        result.append(s)
    df = pd.DataFrame(result)
    
    return df


order = {
"qwen25.3b-no-summary": 0.109,
"qwen25.3b-summary": 0.411,
"qwen25.3b-summary-expert": 0.675,
"qwen25.7b-no-summary": 0.742,
"qwen25.7b-summary": 0.718,
"qwen25.7b-summary-expert": 0.858,
"deepseek.8b-no-summary": 0.860,
"deepseek.8b-summary": 0.732,
"deepseek.8b-summary-expert": 0.828,
"qwen3.8b-no-summary": 0.898,
"qwen3.8b-summary": 0.757,
"qwen3.8b-summary-expert": 0.870,
"qwen3.32b.cot-no-summary": 0.908,
"qwen3.32b.cot-summary": 0.832,
"qwen3.32b.cot-summary-expert": 0.890,
"qwen25.72b.cot-no-summary": 0.916,
"qwen25.72b.cot-summary": 0.823,
"qwen25.72b.cot-summary-expert": 0.906
}

def order_series(df):
    column = sorted(list (order.keys()),key=lambda x: order[x])
    df = df[column]

    for col in df.columns:
        df= df.rename(columns={col: f"{col} ({order[col]:.3f})"})

    return df

def plot_series(series, title="UWR HeatMap", score="f1_score", min_score=0.0, file=None):

    title_full = f"{title} - {score} ({min_score})"
    print(f"Plotting series: {title_full}")
    df = to_heatmap(series, score, min_score)
    df = order_series(df)
    plt.figure(figsize=(10,6))
    sns.heatmap(df, annot=True, cmap="YlGnBu")
    plt.title(title_full   )
    plt.xticks(rotation=45, ha='right', rotation_mode='anchor')
    plt.tight_layout()
    if file:
        plt.savefig(f"tmp/{file}")
    else:   
        plt.show()

    pass


def main():
    if len(sys.argv) not in [2, 3]:
        print("Usage: python 08b_report_index.py <dataset> [min_score]")
        sys.exit(1)
    dataset = sys.argv[1]
    min_score = 0.0
    if len(sys.argv) == 3:
        min_score = float(sys.argv[2])
    file = f"results/{dataset}/detect/{dataset}_indexed_ds.csv"
    data = pd.read_csv(file)
    list_no_tests(data)
    #data["UWR"] = -np.log(data["UWR"]) 

    data_bin, bin_edges = bin_data(data, "UWR", steps=0.1)
    # for bin_str in data_bin:
    #     print(f"Bin {bin_str}: {len(data_bin[bin_str])} instances")
    
    #print(data.head())
    
    uwr = extract_series(data_bin)

    plot_series(uwr, title="UWR HeatMap", score="f1_score", min_score=min_score, file=f"{dataset}_hm_{min_score:.3f}_f1_det.png")
    #plot_series(uwr, title="UWR HeatMap", score="accuracy", min_score=min_score, file=f"{dataset}_hm_{min_score:.3f}_accuracy.png")
    

if __name__ == "__main__":
    main()