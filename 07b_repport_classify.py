# Script for generating reports on drought classification
# usage : python 06b_repport_classify.py <dataset>
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
import numpy as np

tipo_agro="agrocultura"
tipo_ganaderia="ganaderia"
tipo_hidrologia="hidrologia"
tipo_energia="energia"
tipos = [tipo_agro, tipo_ganaderia, tipo_hidrologia, tipo_energia]

ciena_tvi={"bestf1":{"accuracy":0.742,"precision":0.737,"recall":0.832,"f1_score":0.782},
            "efficient":{"accuracy":0.686,"precision":0.791,"recall":0.544,"f1_score":0.645},
            "fastest":{"accuracy":0.634,"precision":0.769,"recall":0.320,"f1_score":0.452}
            }

def test_file_name_to_model(file_name):
    
    # extremadura_1962_9_1_page_1 -> extremadura_1962_09_01_page_0001
    parts = file_name.split('_')
    parts[2] = parts[2].zfill(2)
    parts[3] = parts[3].zfill(2)
    parts[5] = parts[5].zfill(4)
    return '_'.join(parts)

def extract_data(row, field):
    val = row.get(field, 0)
    # Default is False
    if val in [0, '0', False, 'False', 'false', None]: return False
    if val in [1, '1', True, 'True', 'true']: return True
    
    print (f"Unknown value for {field}: {val}")
    exit()

def extract_row(pred_row, real_ds):
            file_name = pred_row['article_filename'].split('/')[-1]
            file_name = file_name.replace('.json', '')
            real_row = real_ds[real_ds['file_name'] == file_name]

            if real_row.empty:
                # try with model file name
                model_file_name = test_file_name_to_model(file_name)
                real_row = real_ds[real_ds['file_name'] == model_file_name]

            if real_row.empty:
                print(f"File not found in real data: {file_name}")
                return None
            
            real_sequia = real_row.iloc[0]['has_sequia']
            if not real_sequia:
                return None  # Skip non-drought articles

            row_sequia = pred_row['article_extracted_data']
            if row_sequia.startswith("{'"):
                row_sequia = ast.literal_eval(row_sequia)
            else:
                row_sequia = json.loads(row_sequia)

            #agrocultura,ganaderia,hidrologia,energia
            real_agrocultura = extract_data(real_row.iloc[0], tipo_agro)
            real_ganaderia = extract_data(real_row.iloc[0], tipo_ganaderia)
            real_hidrologia = extract_data(real_row.iloc[0], tipo_hidrologia)
            real_energia = extract_data(real_row.iloc[0], tipo_energia)
            
            pred_agrocultura = extract_data(row_sequia, "agriculture")
            pred_ganaderia = extract_data(row_sequia, "livestock")
            pred_hidrologia = extract_data(row_sequia, "hydrological_resources")
            pred_energia = extract_data(row_sequia, "energy")

            #print (row_sequia)
            return {
                'file_name': file_name,
                'real_'+tipo_agro: real_agrocultura,
                'real_'+tipo_ganaderia: real_ganaderia,
                'real_'+tipo_hidrologia: real_hidrologia,
                'real_'+tipo_energia: real_energia,
                'pred_'+tipo_agro: pred_agrocultura,
                'pred_'+tipo_ganaderia: pred_ganaderia,
                'pred_'+tipo_hidrologia: pred_hidrologia,
                'pred_'+tipo_energia: pred_energia,         
            }


def build_ds_compare(real_ds, pred_ds): 
    with alive_bar(len(pred_ds), title=f'Building comparison dataset') as bar:
        merged = []
        for _, pred_row in pred_ds.iterrows():
            row_data= extract_row(pred_row, real_ds)
            if row_data is not None:
                merged.append(row_data)
            bar()
    return pd.DataFrame(merged)

def generate_reports(real_ds, dataset, test_name):
    if not os.path.exists(f"results/{dataset}/classify/{test_name}/summary.csv"):
        return None
    
    pred_ds = pd.read_csv(f"results/{dataset}/classify/{test_name}/summary.csv")
    df = build_ds_compare(real_ds, pred_ds)

    print("---- Report ----")
    print (f"Report for test: {test_name}")
    print(f"Number of Agro detected: {df['pred_'+tipo_agro].sum()} out of {len(df)} ")
    print(f"Number of Real Agro: {df['real_'+tipo_agro].sum()} out of {len(df)} ") 
    #print (df.head())
    
    # Make confusion matrix
    info = {}
    for tipo in tipos:
        print(f"Confusion Matrix for {tipo}:")
        print (f"Predicted positives: {df['pred_'+tipo].sum()}, Real positives: {df['real_'+tipo].sum()}")
        cm = confusion_matrix(df['real_'+tipo], df['pred_'+tipo],labels=[True, False])
        print(cm)
        fig, ax = plt.subplots(figsize=(4, 2.5),layout="constrained")
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Drought', 'No Drought'])
        disp.plot(ax=ax, text_kw={'fontsize':14}, cmap=plt.cm.Blues)
        #save to memory
        buf = io.BytesIO()
        disp.figure_.savefig(buf, format='png')
        buf.seek(0)
        b64_img = base64.b64encode(buf.read()).decode('utf-8')
        accuracy = accuracy_score(df['real_'+tipo], df['pred_'+tipo])
        print(f"Accuracy: {accuracy:.2f}")
        score = precision_recall_fscore_support(df['real_'+tipo], df['pred_'+tipo],labels=[True])
        print("Precision, Recall, F1-Score:")
        print(score)     
        
        
        info[tipo] = {
            "name": tipo,
            "accuracy": accuracy,
            "precision": score[0][0],
            "recall": score[1][0],
            "f1_score": score[2][0],
            "cm_image": b64_img
        }
    
    # Display stats (accuracy, precision, recall, f1-score )º
    accuracy =0
    precision =0
    recall =0
    f1_score =0
    for tipo in tipos:
        accuracy += info[tipo]["accuracy"]
        precision += info[tipo]["precision"]
        recall += info[tipo]["recall"]
        f1_score += info[tipo]["f1_score"]
    
    accuracy /= len(tipos)
    precision /= len(tipos)
    recall /= len(tipos)
    f1_score /= len(tipos)

    times_js=json.loads(open(f"results/{dataset}/classify/{test_name}/execution_times.json").read())
    full_time=times_js.get("total",None)
    avg_time=full_time/len(df) if full_time is not None else None
    parrsing_errors_js= json.loads(open(f"results/{dataset}/classify/{test_name}/parsing_errors.json").read())
    parsing_errors=parrsing_errors_js.get("total",0)

    print(f"Total Execution Time: {full_time:.2f} seconds" if full_time is not None else "Total Execution Time: N/A")
    print(f"Average Time per Article: {avg_time:.2f} seconds" if avg_time is not None else "Average Time per Article: N/A")
    print(f"Total Parsing Errors: {parsing_errors}")

    print("---- End Report ----")
    return {
        'test_name': test_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'total': len(df),
        'tipos_info': info,
        "full_time": full_time,
        "avg_time": avg_time,
        "parsing_errors": parsing_errors
    }

def build_table(data, key):
    table = {}
    for row in data:
        # model = row['test_name'].split('-')[0]
        # mode = row['test_name'].replace(f'{model}-','')
        # if model not in table:
        #     table[model] = {'model': model}
        # table[model][mode] = row[key]
        name = row['test_name']
        table[name] = {"model":name,"global": row[key]}
        for tipo in tipos:
            if key not in row['tipos_info'][tipo]:
                continue
            table[name][tipo] = row['tipos_info'][tipo][key]

    return pd.DataFrame.from_dict(table, orient='index')

def build_bar_chart(df, name):
    groups = df.columns[1:].to_list()

    x = np.arange(len(groups))  # the label locations
    #print(x)
    width = 0.06  # the width of the bars
    multiplier = 0

    columns = df["model"].to_list()
    #display(columns)

    fig, ax = plt.subplots(figsize=(7.25, 4), layout='constrained')

    for c in columns:
        #display(c)
        measurement=df[df["model"]==c].iloc[0][groups]
        #display(measurement)

        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=c)
        #ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(name)
    ax.set_title(f'{name} por Tipos de Sequia')
    ax.set_xticks(x + width*6.9, groups)
    fig.legend(loc='outside lower center', ncols=3)
    ax.set_ylim(0, 1)

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    b64_img = base64.b64encode(buf.read()).decode('utf-8')
    return b64_img


def cross_table(df, key, include_ciena=True):
    table = {}
    models =[]
    for _, row in df.iterrows():
        model = row['model'].split('-')[0]
        mode = row['model'].replace(f'{model}-','')
        if model not in table:
            table[model] = {'model': model}
        table[model][mode] = row[key]
        if model not in models:
            models.append(model)
    if include_ciena:
        for model in models:
            if model not in ciena_tvi:
                continue
            table[model]["ciena"] = ciena_tvi[model]["f1_score"]
    
    return pd.DataFrame.from_dict(table, orient='index')

def main():
    if len(sys.argv) != 2:
        print("Usage: python 06b_repport_classify.py <dataset>")
        sys.exit(1)

    dataset = sys.argv[1]
    tests = os.listdir(f"results/{dataset}/classify/")
    tests = [test for test in tests if os.path.isdir(f"results/{dataset}/classify/{test}")]
    real_ds = pd.read_csv(f"data/datasets/{dataset}_ds/classify/{dataset}_ds.csv")

    for tipo in tipos:
        print (f"Total real {tipo}: {real_ds[tipo].sum()} out of {len(real_ds)}")

    data = []

    tests = sorted(tests)

    for test in tests:
        print(f"Generating report for test: {test}")
        tdata=generate_reports(real_ds, dataset, test)
        if tdata is not None:
            data.append(tdata)
    
    df_acc=build_table(data, 'accuracy')
    df_f1=build_table(data, 'f1_score')
    avg_time = cross_table(build_table(data, 'avg_time'), 'global', include_ciena=False)
    errors = cross_table(build_table(data, 'parsing_errors'), 'global', include_ciena=False)
    df_f1_global = cross_table(df_f1, 'global')
    print("=== Accuracy Table ===")
    print(df_acc)
    print("=== F1-Score Table ===")
    print(df_f1)
    print("=== F1-Score Global Table ===")
    print(df_f1_global)
    print("=== Average Time per Article ===")
    print(avg_time)
    print("=== Parsing Errors ===")
    print(errors)

    renderer = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath="./data/templates/")
    )
    template = renderer.get_template("classify.html.jinja")
    output = template.render(
        dataset=dataset,
        accuracy_table=df_acc.to_html(index=False, float_format="{:.2f}".format),
        f1_score_table=df_f1.to_html(index=False, float_format="{:.2f}".format),
        f1_global=df_f1_global.to_html(index=False, float_format="{:.2f}".format),
        average_time_table=avg_time.to_html(index=False, float_format="{:.2f}".format),
        parsing_errors_table=errors.to_html(index=False),
        results=data,
        accuracy_chart=build_bar_chart(df_acc, "Accuracy"),
        f1_score_chart=build_bar_chart(df_f1, "F1-Score"),
    )

    with open(f"results/{dataset}/classify/report-classify.html", "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()  