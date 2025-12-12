import pandas as pd
import sys
import os
import json
import ast

from alive_progress import alive_bar

df_real = None

def fill_pages(file):
    file = file.split(".")[0] 
    file_p = file.split("_")
    ret = ""
    for i in range(len(file_p)):
        part = file_p[i]
        if i==1:
            year = int(part)
            part = f"{year:04d}"
        if i in [2,3]:
            num = int(part)
            part = f"{num:02d}"
        if i==5 and len(file_p)==6:
            num = int(part)
            part = f"{num:04d}"
        if i== 5 and len(file_p)>6:
            num = int(part)
            part = f"{num:04d}"
        if i==0:
            ret = part
        else:
            ret += "_" + part
    return ret

def any_true(data:dict):
    for key in data:
        if data[key] is True:
            return True
    return False

def join_data(row_real, row_test):
    row_sequia = row_test["article_extracted_data"]
    if row_sequia.startswith("{'"):
        row_sequia = ast.literal_eval(row_sequia)
    else:
        row_sequia = json.loads(row_sequia)

    if "drought" in row_sequia:
        has_sequia = row_sequia["drought"]
    else:
        has_sequia = any_true(row_sequia)
    return {
        'file_name': row_real['file_name'],
        'real_sequia':row_real['has_sequia'],
        'pred_sequia': has_sequia
    }

def get_stats(df_real, test_path):
    ciena_out = pd.read_csv(os.path.join(test_path, 'summary.csv'))
    data = []
    with alive_bar(len(ciena_out), title=f'Processing {test_path}') as bar:
        total = 0
        correct = 0
        for _, row in ciena_out.iterrows():
            file = row['article_filename'].split('/')[-1]
            file = fill_pages(file)
            real_row = df_real[df_real['file_name'] == file]
            if real_row.empty:
                print (f"File not found in real data: {file}")
                bar()
                continue
            ret = join_data(real_row.iloc[0], row)
            data.append(ret)
            bar()
    #print (data)
    df_data = pd.DataFrame(data)
    real_data = df_data['real_sequia']
    pred_data = df_data['pred_sequia']

    # Calculate accuracy
    correct_predictions = (real_data == pred_data).sum()
    total_predictions = len(real_data)
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0 

    return {'accuracy': accuracy, 'total': total_predictions, 'correct': correct_predictions}

def main():
    if len(sys.argv) != 2:
        print("Usage: python 95_accuracy_test.py <ds>")
        sys.exit(1)
    ds = sys.argv[1]
    df_real = pd.read_csv(f"data/datasets/work_ds/{ds}/work_ds.csv")
    folders = os.listdir(f'./tests/{ds}/')
    folders = [f for f in folders if os.path.isdir(os.path.join(f'./tests/{ds}/', f))]

    print (folders)

    summary = {}

    for folder in folders:
        test_path = os.path.join(f'./tests/{ds}/', folder)
        stats= get_stats(df_real, test_path)
        print("----------------------------")
        print(f"Stats for {folder}: {stats}")
        print("----------------------------")

        model_name = folder.split('-')[0]
        model_mode = folder.replace(model_name+'-','')
        if model_name not in summary:
            summary[model_name] = {'model': model_name, model_mode: stats['accuracy']}
        else:
            summary[model_name][model_mode] = stats['accuracy']
        #exit()
    print("Summary of all models:")
    for model in summary:
        print(summary[model])
    return

if __name__ == "__main__":
    main()