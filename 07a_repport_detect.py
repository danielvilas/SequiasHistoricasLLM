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

ciena_tvii={"qwen25.72b.cot":{"accuracy":0.965,"precision":0.967,"recall":0.970,"f1_score":0.968},
            "qwen25.7b":{"accuracy":0.925,"precision":0.968,"recall":0.894,"f1_score":0.929},
            "qwen25.3b":{"accuracy":0.792,"precision":0.880,"recall":0.698,"f1_score":0.779}
            }

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
            pred_sequia = row_sequia.get('drought', False)
            if pred_sequia is None:
                pred_sequia = False
            #print (row_sequia)
            merged.append({
                'file_name': file_name,
                'real_sequia': real_sequia,
                'pred_sequia': pred_sequia
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
    print("******* Confusion Matrix *******")
    print(df.head())
    cm = confusion_matrix(df['real_sequia'], df['pred_sequia'],labels=[True, False])
    print("Confusion Matrix:")
    print(cm)
    fig, ax = plt.subplots(figsize=(4, 2.5),layout="constrained")
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Sequía', 'No Sequía'])
    disp.plot(ax=ax, text_kw={'fontsize':14}, cmap=plt.cm.Blues)
    ax.set_ylabel("Real", fontsize=10)
    ax.set_xlabel("Predicción", fontsize=10)
    #save to memory
    buf = io.BytesIO()
    disp.figure_.savefig(buf, format='png')
    buf.seek(0)
    b64_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(disp.figure_)
    
    # Display stats (accuracy, precision, recall, f1-score )º
    accuracy = accuracy_score(df['real_sequia'], df['pred_sequia'])
    print(f"Accuracy: {accuracy:.2f}")
    score = precision_recall_fscore_support(df['real_sequia'], df['pred_sequia'],labels=[True])
    print("Precision, Recall, F1-Score:")
    print(score)

    times_js=json.loads(open(f"results/{dataset}/detect/{test_name}/execution_times.json").read())
    full_time=times_js.get("total",None)
    avg_time=full_time/len(df) if full_time is not None else None
    parrsing_errors_js= json.loads(open(f"results/{dataset}/detect/{test_name}/parsing_errors.json").read())
    parsing_errors=parrsing_errors_js.get("total",0)

    print(f"Total Execution Time: {full_time:.2f} seconds" if full_time is not None else "Total Execution Time: N/A")
    print(f"Average Time per Article: {avg_time:.2f} seconds" if avg_time is not None else "Average Time per Article: N/A")
    print(f"Total Parsing Errors: {parsing_errors}")
    print("---- End Report ----")
    return {
        'test_name': test_name,
        'accuracy': accuracy,
        'precision': score[0][0],
        'recall': score[1][0],
        'f1_score': score[2][0],
        'total': len(df),
        "cm_image": b64_img,
        "full_time": full_time,
        "avg_time": avg_time,
        "parsing_errors": parsing_errors

    }

def build_table(data, key):
    table = {}
    models =[]
    for row in data:
        model = row['test_name'].split('-')[0]
        mode = row['test_name'].replace(f'{model}-','')
        if model not in table:
            table[model] = {'model': model}
        table[model][mode] = row[key]
        if model not in models:
            models.append(model)
    for model in models:
        if model not in ciena_tvii:
            continue
        if key not in ciena_tvii[model]:
            continue
        table[model]["ciena"] = ciena_tvii[model][key]
    return pd.DataFrame.from_dict(table, orient='index')

def calc_diff_summary(df_f1):
    print("Calculating difference summary...")

    def calc_diff(row):
        name = row.name
        base = row.get('no-summary')
        summary = row.get('summary')
        summary_expert = row.get('summary-expert', None)
        ret = {'summary': summary - base}
        if summary_expert is not None:
            ret['summary_expert'] = summary_expert - base

        return pd.Series(ret, name=name)
    return df_f1.apply(calc_diff, axis=1)

def plot_diff_summary(diff_summary):
    fig, ax = plt.subplots(figsize=(6, 4))
    diff_summary.plot(kind='bar', ax=ax)
    ax.set_title('Cambios F1 Score tras aplicar resúmenes')
    ax.set_ylabel('Diferencia F1-Score')
    ax.axhline(0, color='gray', linestyle='--')
    plt.xticks(rotation=45)
    plt.tight_layout()
    #plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    b64_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64_img

def sort_tests(tests):
    def sort_key(test_name):
        parts = test_name.split('-')
        model = parts[0]
        mode = '-'.join(parts[1:])
        model_order = {'qwen25.72b.cot': 0, 'qwen25.7b': 1, 'qwen25.3b': 2, 'deepseek.8b': 3}
        model_order= {"qwen25.3b":0,"qwen25.7b":1,"deepseek.8b":2,"qwen3.8b":3,"qwen3.32b.cot":4,"qwen25.72b.cot":5}        
        mode_order = {'no-summary': 0, 'summary': 1, 'summary-expert': 2}

        return (model_order.get(model, 99), mode_order.get(mode, 99))
    
    return sorted(tests, key=sort_key)

def plot_f1_scores(df_f1:pd.DataFrame, times:pd.DataFrame):
    # Plot F1 scores with execution times
    # color for model
    colors = {
        'qwen25.3b': '#E91E63',
        'qwen25.7b': '#FF9800',
        'deepseek.8b': '#D1D5DB',
        'qwen3.8b': '#C6FF00',
        'qwen3.32b.cot': '#2ECC71',
        'qwen25.72b.cot': '#1E5AA8',
    }
    markers = {
        'no-summary': 'o',
        'summary': 's',
        'summary-expert': 'D'
    }
    fig, ax1 = plt.subplots(figsize=(8, 5))
    for model in df_f1['model']:
        model_data = df_f1[df_f1['model'] == model]
        for mode in ['no-summary', 'summary', 'summary-expert']:
            if mode in model_data.columns:
                ax1.scatter(times.loc[model, mode],
                model_data[mode],
                label=f"{model} - {mode}",
                color=colors.get(model, 'gray'),
                marker=markers.get(mode, 'o'))
    ax1.set_ylabel('F1 Score')
    ax1.set_xlabel('Tiempo por artículo (s)')
    # Leyenda personalizada
    # colores únicos para modelos
    handles = [plt.Line2D([0], [0], marker='None', color='w', label='Modelo')] 
    for model in df_f1['model']:
        handles.append(plt.Line2D([0], [0], marker='o', color='w', label=model, markerfacecolor=colors.get(model, 'gray'), markersize=10))
    # Agregar separación entre modelos y modos
    handles.append(plt.Line2D([0], [0], marker='None', color='w', label=''))
    handles.append(plt.Line2D([0], [0], marker='None', color='w', label='Resumen'))
    # marcadores únicos para modos 
    for mode in ['no-summary', 'summary', 'summary-expert']:
        handles.append(plt.Line2D([0], [0], marker=markers.get(mode, 'o'), color='w', label=mode, markerfacecolor='black', markersize=10))
    ax1.legend(handles=handles, loc='best')
    plt.title('F1 Score en Detección de Sequías')
    plt.tight_layout()
    #plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')  
    buf.seek(0)
    b64_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64_img

def main():
    if len(sys.argv) != 2:
        print("Usage: python 06a_repport_detect.py <dataset>")
        sys.exit(1)

    dataset = sys.argv[1]
    tests = os.listdir(f"results/{dataset}/detect/")
    tests = [test for test in tests if os.path.isdir(f"results/{dataset}/detect/{test}")]
    real_ds = pd.read_csv(f"data/datasets/{dataset}_ds/detect/{dataset}_ds.csv")
    data = []

    tests = sort_tests(tests)

    for test in tests:
        print(f"Generating report for test: {test}")
        tdata=generate_reports(real_ds, dataset, test)
        if tdata is not None:
            data.append(tdata)
    
    df_acc=build_table(data, 'accuracy')
    df_f1=build_table(data, 'f1_score')
    avg_time = build_table(data, 'avg_time')
    errors = build_table(data, 'parsing_errors')
    print("=== Accuracy Table ===")
    print(df_acc)
    print("=== F1-Score Table ===")
    print(df_f1)
    img_f1_scores = plot_f1_scores(df_f1, avg_time)
    print("=== Average Time per Article ===")
    print(avg_time)
    print("=== Parsing Errors ===")
    print(errors)

    diff_summary  = calc_diff_summary(df_f1)
    print("=== Difference Summary ===")
    print(diff_summary)
    diff_summary_img = plot_diff_summary(diff_summary)


    renderer = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath="./data/templates/")
    )
    template = renderer.get_template("detect.html.jinja")
    output = template.render(
        dataset=dataset,
        accuracy_table=df_acc.to_html(index=False, float_format="{:.2f}".format),
        f1_score_table=df_f1.to_html(index=False, float_format="{:.2f}".format),
        average_time_table=avg_time.to_html(index=False, float_format="{:.2f}".format),
        parsing_errors_table=errors.to_html(index=False),
        results=data,
        diff_summary_image=diff_summary_img,
        img_f1_scores=img_f1_scores
    )

    with open(f"results/{dataset}/detect/report-detect.html", "w", encoding='utf-8') as f:
        f.write(output)

    for _, row in df_f1.iterrows():
        print(f"\"{row['model']}-no-summary\": {row['no-summary']:.3f},")
        print(f"\"{row['model']}-summary\": {row['summary']:.3f},")
        if 'summary-expert' in row:
            print(f"\"{row['model']}-summary-expert\": {row['summary-expert']:.3f},")

if __name__ == "__main__":
    main()  