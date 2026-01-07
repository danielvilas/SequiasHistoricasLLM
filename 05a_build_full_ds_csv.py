import pandas as pd
import random
from typing import List, Dict
from alive_progress import alive_bar


def _extract_data_from_row(paper,row: pd.Series) -> Dict:
        return {
        "periodico": paper,
        "news_date": row["news_date"],
        "year": row["year.1"],
        "month": row["month"],
        "day": row["day"],
        "page": row["page"],
        "ed": row["edition"],
        "evento":row["evento"],
        "event_code":row["event_code"],
        "ubicacion":row["ubicacion"],
        "has_sequia": True,
        "agrocultura":row["agrocultura"],
        "ganaderia":row["ganaderia"],
        "hidrologia":row["hidrologia"],
        "energia":row["energia"],
        "latitud":row["latitud"],
        "longitud":row["longitud"],
        } 

def build_paper_dataset(paper) -> pd.DataFrame:
    df = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean_full.csv")
    def _process_row(row, bar):
        ret = _extract_data_from_row(paper,row)
        bar()
        return pd.Series(ret)
    with alive_bar(len(df), title=f"Extract truth for {paper}") as bar:
        df = df.apply(lambda row: _process_row(row, bar), axis=1)
         
        
    return pd.DataFrame(df)


def main():
    random.seed(42)
    df_extremadura = build_paper_dataset("extremadura")
    
    random.seed(42)
    df_hoy = build_paper_dataset("hoy")

    # Combine datasets
    df = pd.concat([df_extremadura, df_hoy], ignore_index=True)
    # Save to CSV
    df.to_csv("data/full_ds.csv", index=False)

if __name__ == "__main__":
    main()