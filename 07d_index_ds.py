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
    disabled = ['entity_linker','entity_ruler','textcat','textcat_multilabel',
           'trainable_lemmatizer','attribute_ruler','sentencizer','transformer']
    nlp_data=list(nlp.pipe(iter(real_ds["CONTENIDO"]),batch_size = 100,disable=disabled,n_process=5))
    real_ds["NLP"]=nlp_data

    return real_ds


def index_files(real_ds: pd.DataFrame, dataset) -> pd.DataFrame:
    
    def _read_file(file: str, dataset, bar) -> str:
        file_path = f"data/datasets/{dataset}_ds/{action}/json/{file}.json"
        ret = read_file(file_path)
        bar()
        return ret
    
    with alive_bar(len(real_ds), title=f'Reading') as bar:
        real_ds['text'] = real_ds['file_name'].apply(lambda fn: _read_file(fn, dataset,bar))
    
    return real_ds
    


def main():
    if len(sys.argv) != 2:
        print("Usage: python 07d_index_ds.py <dataset>")
        sys.exit(1)
    dataset = sys.argv[1]

    ds_dir = f"data/datasets/{dataset}_ds/{action}"
    real_ds = pd.read_csv(f"{ds_dir}/{dataset}_ds.csv")
    real_ds = real_ds[["file_name","has_sequia"]]
    #print(real_ds.head())    
    real_ds = index_files(real_ds,dataset)
    #print(real_ds.head())    

    pass

if __name__ == "__main__":
    main()
