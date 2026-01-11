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

ciena_tvii={"bestf1":{"accuracy":0.965,"precision":0.967,"recall":0.970,"f1_score":0.968},
            "efficient":{"accuracy":0.925,"precision":0.968,"recall":0.894,"f1_score":0.929},
            "fastest":{"accuracy":0.792,"precision" :0.880,"recall":0.698,"f1_score":0.779}
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

def get_fp_fn(real_ds, dataset, test_name) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    if not os.path.exists(f"results/{dataset}/detect/{test_name}/summary.csv"):
        return None
    
    pred_ds = pd.read_csv(f"results/{dataset}/detect/{test_name}/summary.csv")
    df = build_ds_compare(real_ds, pred_ds)
    
    print("---- Extracting FP and FN ----")
    fp_df = df[(df['real_sequia'] == False) & (df['pred_sequia'] == True)]
    fn_df = df[(df['real_sequia'] == True) & (df['pred_sequia'] == False)]
    print(f"Number of False Positives: {len(fp_df)}")
    print(f"Number of False Negatives: {len(fn_df)}")
    return fp_df, fn_df

def save_fn_files(extremadura, hoy, out_dir, fn, dataset):
    #print(extremadura.head())
    #print(hoy.head())
    #print(fn.head())

    data=[]

    pdf_root = f"data/datasets/{dataset}_ds/detect/PDF"
    json_root = f"data/datasets/{dataset}_ds/detect/json"

    for _, row in fn.iterrows():
        file_name = row['file_name']
        #print(f"Processing FN file: {file_name}")
        sExtremadura = extremadura[extremadura['loc'] == str(file_name)]
        sHoy = hoy[hoy['loc'] == str(file_name)]
        if len(sExtremadura) > 0:
            for _, ext_row in sExtremadura.iterrows():
                data.append({"file_name":file_name,"year":ext_row['year'], "source":"extremadura","titular":ext_row['titular'], "frase":ext_row['frase']})
        if len(sHoy) > 0:
            for _, hoy_row in sHoy.iterrows():
                data.append({"file_name":file_name,"year":hoy_row['year'], "source":"hoy","titular":hoy_row['titular'], "frase":hoy_row['frase']})

        if len(sExtremadura) == 0 and len(sHoy) == 0:
            print(f"Warning: FN file {file_name} not found in extremadura or hoy datasets.")
    
        #copy pdf, and json files to out_dir
        pdf_file = f"{pdf_root}/{file_name}.pdf"
        json_file = f"{json_root}/{file_name}.json"
        os.system(f"cp '{pdf_file}' '{out_dir}/'")
        os.system(f"cp '{json_file}' '{out_dir}/'")

    # You might want to save or return the data here
    # For example, save to a CSV file:
    data = pd.DataFrame(data)
    data = data.sort_values(by=['year','file_name'])
    data.to_csv(os.path.join(out_dir, "fn_files.csv"), index=False)


def convert_full_df(df)->pd.DataFrame:
    df = df.dropna(subset=['year.1', 'month', 'day', 'page'])
    def convert_row(row):

        paper = row['paper'].lower()
        news_date = row['news_date']
        titular = row['titular']
        frase = row['frase']
        raw_file = row['raw_file']
        year = int(row['year.1'])
        month = int(row['month'])
        day = int(row['day'])
        page = int(row['page'])
        edition = row['edition']
        clean_file = row['clean_file']
        loc = f"{paper}_{year:04d}_{month:02d}_{day:02d}_page_{page:04d}"
        if edition and not pd.isna(edition):
            loc += f"_{edition}"

        ret = {"loc":loc,
               "year":year,
               "paper":paper,
               "news_date":news_date,
               "titular":titular,
               "frase":frase,
               "raw_file":raw_file,
               "clean_file":clean_file}
        return pd.Series(ret)
    ret = df.apply(lambda x: convert_row(x), axis=1)
    ret = ret.sort_values(by=['year','loc'])
    return ret

def save_fp_files(out_dir, fp, dataset):
    pdf_root = f"data/datasets/{dataset}_ds/detect/PDF"
    json_root = f"data/datasets/{dataset}_ds/detect/json"

    for _, row in fp.iterrows():
        file_name = row['file_name']
        #print(f"Processing FP file: {file_name}")
        #copy pdf, and json files to out_dir
        pdf_file = f"{pdf_root}/{file_name}.pdf"
        json_file = f"{json_root}/{file_name}.json"
        os.system(f"cp '{pdf_file}' '{out_dir}/'")
        os.system(f"cp '{json_file}' '{out_dir}/'")

def main():
    if len(sys.argv) != 4:
        print("Usage: python 06a_repport_detect.py <dataset> <test_name> <out_dir>")
        sys.exit(1)

    dataset = sys.argv[1]
    test_name = sys.argv[2]
    out_dir = sys.argv[3]

    if not os.path.exists(f"results/{dataset}/detect/{test_name}/summary.csv"):
        print(f"Summary file not found for test: {test_name} in dataset: {dataset}")
        sys.exit(1)

    os.makedirs(f"{out_dir}/FP", exist_ok=True)
    os.makedirs(f"{out_dir}/FN", exist_ok=True)

    real_ds = pd.read_csv(f"data/datasets/{dataset}_ds/detect/{dataset}_ds.csv")
    fp,fn =get_fp_fn(real_ds, dataset, test_name)

    extremadura = pd.read_csv(f"data/datasets/clean/extremadura/extremadura_impactos_clean_full.csv")
    extremadura = convert_full_df(extremadura)
    hoy = pd.read_csv(f"data/datasets/clean/hoy/hoy_impactos_clean_full.csv")
    hoy = convert_full_df(hoy)
    
    save_fp_files(f"{out_dir}/FP/", fp, dataset)
    save_fn_files(extremadura, hoy, f"{out_dir}/FN/", fn, dataset)



if __name__ == "__main__":
    main()  