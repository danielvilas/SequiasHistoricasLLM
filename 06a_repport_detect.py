# Script for generating reports on drought detection
# usage : python 06a_repport_detect.py <dataset>
import os
import sys

import pandas as pd
from alive_progress import alive_bar
import ast
import json
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import precision_recall_fscore_support,accuracy_score

import jinja2
import io
import base64

from matplotlib import pyplot as plt

def build_ds_compare(real_ds, pred_ds): 
    with alive_bar(len(pred_ds), title=f'Building comparison dataset') as bar:
        merged = []
        for _, pred_row in pred_ds.iterrows():
            file_name = pred_row['article_filename'].split('/')[-1]
            file_name = file_name.replace('.json', '')
            real_row = real_ds[real_ds['file_name'] == file_name]
            if real_row.empty:
                print(f"File not found in real data: {file_name}")
                bar()
                continue
            real_sequia = real_row.iloc[0]['has_sequia']
            row_sequia = pred_row['article_extracted_data']
            if row_sequia.startswith("{'"):
                row_sequia = ast.literal_eval(row_sequia)
            else:
                row_sequia = json.loads(row_sequia)
            #print (row_sequia)
            merged.append({
                'file_name': file_name,
                'real_sequia': real_sequia,
                'pred_sequia': row_sequia["drought"]
            })
            bar()
    return pd.DataFrame(merged)

def generate_reports(real_ds, dataset, test_name):
    if not os.path.exists(f"results/{dataset}/detect/{test_name}/summary.csv"):
        return None
    
    pred_ds = pd.read_csv(f"results/{dataset}/detect/{test_name}/summary.csv")
    df = build_ds_compare(real_ds, pred_ds)
    print("---- Report ----")
    print (f"Report for test: {test_name}")
    print(f"Number of Droughts detected: {df['pred_sequia'].sum()} out of {len(df)} ")
    print(f"Number of Real Droughts: {df['real_sequia'].sum()} out of {len(df)} ") 
    #print (df.head())
    
    # Make confusion matrix
    cm = confusion_matrix(df['real_sequia'], df['pred_sequia'],labels=[True, False])
    print("Confusion Matrix:")
    print(cm)
    fig, ax = plt.subplots(figsize=(5, 2.5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Drought', 'No Drought'])
    disp.plot(ax=ax)
    #save to memory
    buf = io.BytesIO()
    disp.figure_.savefig(buf, format='png')
    buf.seek(0)
    b64_img = base64.b64encode(buf.read()).decode('utf-8')
    
    # Display stats (accuracy, precision, recall, f1-score )º
    accuracy = accuracy_score(df['real_sequia'], df['pred_sequia'])
    print(f"Accuracy: {accuracy:.2f}")
    score = precision_recall_fscore_support(df['real_sequia'], df['pred_sequia'],labels=[True])
    print("Precision, Recall, F1-Score:")
    print(score)
    print("---- End Report ----")
    return {
        'test_name': test_name,
        'accuracy': accuracy,
        'precision': score[0][0],
        'recall': score[1][0],
        'f1_score': score[2][0],
        'total': len(df),
        "cm_image": b64_img
    }

def build_table(data, key):
    table = {}
    for row in data:
        model = row['test_name'].split('-')[0]
        mode = row['test_name'].replace(f'{model}-','')
        if model not in table:
            table[model] = {'model': model}
        table[model][mode] = row[key]
    return pd.DataFrame.from_dict(table, orient='index')

def main():
    if len(sys.argv) != 2:
        print("Usage: python 06a_repport_detect.py <dataset>")
        sys.exit(1)

    dataset = sys.argv[1]
    tests = os.listdir(f"results/{dataset}/detect/")
    tests = [test for test in tests if os.path.isdir(f"results/{dataset}/detect/{test}")]
    real_ds = pd.read_csv(f"data/datasets/{dataset}_ds/detect/work_ds.csv")
    data = []

    tests = sorted(tests)

    for test in tests:
        print(f"Generating report for test: {test}")
        tdata=generate_reports(real_ds, dataset, test)
        if tdata is not None:
            data.append(tdata)
    
    df_acc=build_table(data, 'accuracy')
    df_f1=build_table(data, 'f1_score')
    print("=== Accuracy Table ===")
    print(df_acc)
    print("=== F1-Score Table ===")
    print(df_f1)

    renderer = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath="./data/templates/")
    )
    template = renderer.get_template("detect.html.jinja")
    output = template.render(
        dataset=dataset,
        accuracy_table=df_acc.to_html(index=False, float_format="{:.2f}".format),
        f1_score_table=df_f1.to_html(index=False, float_format="{:.2f}".format),
        results=data
    )

    with open(f"results/{dataset}/detect/report.html", "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()  