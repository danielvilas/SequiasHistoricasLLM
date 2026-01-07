import pandas as pd
import random
from typing import List, Dict, Tuple
from alive_progress import alive_bar
import os

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

def _select_random_date_pdf(paper, year:int, month:int) -> Tuple[int,int,str|None]:
    folder = f"data/datasets/clean/{paper}/{year}/{month:02d}/"
    days=os.listdir(folder)
    #print(days)
    day_f = random.choice(days)
        # Escoger una pagina aleatoria
    folder_day = folder+f"{day_f}/"
    pages=os.listdir(folder_day)
    #print(pages)
    page = random.choice(pages)
    

    day = int(day_f)
    parts = page.replace(".pdf","").split("_")
    day = int(day_f)
    page_n = int(parts[1])
    ed = None
    if len(parts)>2:
        ed = parts[2]

    if page_n==0:
        print(f"Warning: selected page 0 for {paper} {year}-{month}-{day}")
        print(f" folder_day: {folder_day}")
        print(f"pdf:{page}",os.listdir(folder_day))
        
        exit(1)

    return day, page_n, ed


def _random_no_impact_row(paper, year:int, month:int) -> dict:
    
    day, page, ed = _select_random_date_pdf(paper, year, month)
    ret = {
        "periodico": paper,
        "news_date": f"{day:02d}/{month:02d}/{year:04d}",
        "year": year,
        "month": month,
        "day": day,
        "page": page,
        #"ed": ed,
        #"evento":None,
        #"event_code":None,
        #"ubicacion":None,
        "has_sequia": False,
        "agrocultura":0,
        "ganaderia":0,
        "hidrologia":0,
        "energia":0,
        #"latitud":None,
        #"longitud":None,
        }
    if ed is not None:
        ret["ed"] = ed
    return ret

tried = []

def is_already_in_df(df: pd.DataFrame, candidate_row: dict) -> bool:
    t_id = f"{candidate_row['periodico']}_{candidate_row['year']}_{candidate_row['month']}_{candidate_row['day']}_{candidate_row['page']}"
    if t_id in tried:
        return True
    tried.append(t_id)
    matches = df[
        (df["periodico"] == candidate_row["periodico"]) &
        (df["year"] == candidate_row["year"]) &
        (df["month"] == candidate_row["month"]) &
        (df["day"] == candidate_row["day"]) &
        (df["page"] == candidate_row["page"])
    ]
    return not matches.empty

def _search_no_impact_row(df: pd.DataFrame,paper, year:int, month:int) -> dict:
    candidate_row = _random_no_impact_row(paper, year, month)
    tries = 0
    while is_already_in_df(df, candidate_row):
        candidate_row = _random_no_impact_row(paper, year, month)
        tries += 1
        if tries > 10:
            print(f"Warning: Could not find a non-impact row for {paper} {year}-{month}")
            print(f"last candidate_row: {candidate_row}")
            exit(1)

    return candidate_row
    

def build_paper_dataset(paper) -> pd.DataFrame:
    df = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean_full.csv")
    
    # remove not found
    df = df.dropna(subset=["year.1"]).reset_index(drop=True) 
    df["year.1"] = df["year.1"].astype(int)
    df["month"] = df["month"].astype(int)
    df["day"] = df["day"].astype(int)
    df["page"] = df["page"].astype(int)

    # extract only truth data (not all columns are needed)
    def _process_truth(row, bar):
        ret = _extract_data_from_row(paper,row)
        bar()
        return pd.Series(ret)
    
    with alive_bar(len(df), title=f"Extract truth for {paper}") as bar:
        df = df.apply(lambda row: _process_truth(row, bar), axis=1)
    
    # for each row we find another random row without impact in the same year and month
    def _process_no_impact(row, bar):
        ret = _search_no_impact_row(df, paper, row["year"], row["month"])
        bar()
        return pd.Series(ret)
    with alive_bar(len(df), title=f"Extract no-impact for {paper}") as bar:
        df_no_impact = df.apply(lambda row: _process_no_impact(row, bar), axis=1)
    
    # Concatenate both dataframes
    df = pd.concat([df, df_no_impact], ignore_index=True)
    #df_no_impact.to_csv(f"tmp/{paper}_no_impact_full.csv", index=False)
    # reordenamos por fecha y pagina
    df = df.sort_values(by=["year","month","day","page"]).reset_index(drop=True)
    return pd.DataFrame(df)


def main():
    random.seed(42)
    df_extremadura = build_paper_dataset("extremadura")
    
    random.seed(42)
    df_hoy = build_paper_dataset("hoy")

    # Combine datasets
    df = pd.concat([df_extremadura, df_hoy], ignore_index=True)
    # reordenamos por fecha y pagina
    df = df.sort_values(by=["year","month","day","page"]).reset_index(drop=True)
    # Save to CSV
    df.to_csv("data/full_ds.csv", index=False)

if __name__ == "__main__":
    main()