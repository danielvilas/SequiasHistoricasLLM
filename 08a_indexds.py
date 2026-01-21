# Script for read a dataset and create the document index
# usage : python 07d_index_ds.py <dataset>
import os
import sys

from isort import file
import pandas as pd

from alive_progress import alive_bar
import json

import spacy
import es_core_news_md

import ast


nlp = es_core_news_md.load()

action="detect"

def read_file(file: str) -> str:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            ret = f.read()
            ret = json.loads(ret)
            return ret["articleBody"]
    except Exception as e:
        print(f"Error reading file {file}: {e}")
        return ""
    
def spacy_tokenize(real_ds: pd.DataFrame) -> pd.DataFrame:
    print("Tokenizing with spacy...")
    disabled = ['entity_linker','entity_ruler','textcat','textcat_multilabel',
           'trainable_lemmatizer','attribute_ruler','sentencizer','transformer']
    nlp_data=list(nlp.pipe(iter(real_ds["text"]),batch_size = 100,disable=disabled,n_process=5))
    real_ds["NLP"]=nlp_data
    print("Tokenization completed.")
    return real_ds

def calc_UWR(row, exclude_stop=False) -> float:
    doc = row["NLP"]
    words = [token for token in doc if not token.is_punct and not token.is_space]
    
    if exclude_stop:
        words = [token for token in words if not token.is_stop]

    total_words = len(words)
    unk_words = len([token for token in words if token.is_oov])
    if total_words == 0:
        return 0.0
    return unk_words / total_words

def index_files(real_ds: pd.DataFrame, dataset) -> pd.DataFrame:
    
    def _read_file(file: str, dataset, bar) -> str:
        file_path = f"data/datasets/{dataset}_ds/{action}/json/{file}.json"
        ret = read_file(file_path)
        bar()
        return ret

    # Read files    
    with alive_bar(len(real_ds), title=f'Reading') as bar:
        real_ds['text'] = real_ds['file_name'].apply(lambda fn: _read_file(fn, dataset,bar))

    # Tokenize with spacy
    real_ds = spacy_tokenize(real_ds)
    # Calculate UWR
    def _calc_wr(row, bar, exclude_stop=False) -> float:
        ret = calc_UWR(row, exclude_stop=exclude_stop)
        bar()
        return ret
    with alive_bar(len(real_ds), title=f'Calculating UWR') as bar:  
        real_ds["UWR"] = real_ds.apply(lambda row: _calc_wr(row, bar), axis=1)
    with alive_bar(len(real_ds), title=f'Calculating UWR_es') as bar:  
        real_ds["UWR_es"] = real_ds.apply(lambda row: _calc_wr(row, bar, exclude_stop=True), axis=1)

    print(real_ds.head())
    
    return real_ds

def get_pred_sequia(file_name: str, pred_ds: pd.DataFrame) -> bool:
    pred_row = pred_ds[pred_ds['article_filename'].str.contains(file_name)]
    if pred_row.empty:
        print(f"File not found in predictions: {file_name}")
        return False
    if len(pred_row) > 1:
        print(f"Multiple entries found in predictions for file: {file_name}")

    row_sequia = pred_row.iloc[0]['article_extracted_data']
    if row_sequia.startswith("{'"):
        row_sequia = ast.literal_eval(row_sequia)
    else:
        row_sequia = json.loads(row_sequia)
    pred_sequia = row_sequia.get('drought', False)
    if pred_sequia is None:
        pred_sequia = False
    return pred_sequia

def append_test(real_ds: pd.DataFrame, dataset: str, test_name: str) -> pd.DataFrame:
    if not os.path.exists(f"results/{dataset}/detect/{test_name}/summary.csv"):
        print(f"No results found for test: {test_name}")
        return real_ds
    
    pred_ds = pd.read_csv(f"results/{dataset}/detect/{test_name}/summary.csv")
    
    def _get_pred_sequia(file_name: str, pred_ds: pd.DataFrame, bar) -> bool:
        ret = get_pred_sequia(file_name, pred_ds)
        bar()
        return ret

    with alive_bar(len(real_ds), title=f'Appending test results for {test_name}') as bar:
        real_ds[f'pred_sequia_{test_name}'] = real_ds['file_name'].apply(
            lambda fn: _get_pred_sequia(fn, pred_ds, bar)
        )
        
    
    return real_ds

def main():
    if len(sys.argv) != 2:
        print("Usage: python 08a_indexds.py <dataset>")
        sys.exit(1)
    dataset = sys.argv[1]

    ds_dir = f"data/datasets/{dataset}_ds/{action}"
    real_ds = pd.read_csv(f"{ds_dir}/{dataset}_ds.csv")
    real_ds = real_ds[["file_name","has_sequia"]]
    #print(real_ds.head())    
    real_ds = index_files(real_ds,dataset)
    #print(real_ds.head())    

    tests = os.listdir(f"results/{dataset}/detect/")
    tests = [test for test in tests if os.path.isdir(f"results/{dataset}/detect/{test}")]
    for test in tests:
        print(f"Adding test results for test: {test}")
        real_ds = append_test(real_ds, dataset, test)
    
    # Save indexed dataset
    output_file = f"results/{dataset}/detect/{dataset}_indexed_ds.csv"
    out_ds = real_ds.drop(columns=["text","NLP"])
    out_ds.to_csv(output_file, index=False)
    print(f"Indexed dataset saved to: {output_file}")

if __name__ == "__main__":
    main()
