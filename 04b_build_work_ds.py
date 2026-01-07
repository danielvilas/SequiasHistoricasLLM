import sys
import os
import pandas as pd
import shutil
from alive_progress import alive_bar
import json

from sequias_historicas.PdfManager import PdfManager
pdf_manager = PdfManager()


def create_json(paper, year, month, day, page, text):
    date_pub = day
    if date_pub==0:
        date_pub=15
    json_data ={"@context": "https://schema.org/",
                "@type":"NewsArticle",
                "headline":f"{paper} {year}-{month}-{day} page {page}",
                "articleBody":text,
                "datePublished":f"{year:04}-{month:02}-{date_pub:02}T00:00:00+01:00",
                "mainEntityOfPage":{"@id":"https://not-existent.example.com/"},
            
                }
    return json_data


def copy_page(row, pdf_folder, json_folder):
    paper = row["periodico"]
    year = int(row["year"])
    month = int(row["month"])
    day = int(row["day"])
    page = int(row["page"])
    ed = row["ed"]
    if ed == "None" or pd.isna(ed):
        ed = None
    text, file = pdf_manager.extract_text(paper, year, month, day, page, ed)
    print (f"Copying {file}...")
    outFilename = f"{paper}_{year}_{month:02d}_{day:02d}_page_{page:04d}"
    if ed:
        outFilename += f"_{ed}"
    shutil.copy(file, f"{pdf_folder}/{outFilename}.pdf")
    json_outfile = f"{json_folder}/{outFilename}.json"
    json_data = create_json(paper, year, month, day, page, text)
    with open (json_outfile,"w",encoding="utf-8") as f:
            json.dump(json_data,f,ensure_ascii=False,indent=4)
    return outFilename

def build(folder, year):
    work_ds_df = pd.read_csv(f"data/work_ds.csv")
    work_ds_df = work_ds_df[work_ds_df["year"]>=year]
    work_ds_path=f"data/datasets/work_ds/{folder}"

    if folder=="classify":
        work_ds_df = work_ds_df[work_ds_df["has_sequia"]==True]
        if os.path.exists(f"data/classify_extra.csv"):
            print("Classify Extra exits, appending to work_ds.")
            extra_df = pd.read_csv("data/classify_extra.csv")
            work_ds_df = pd.concat([work_ds_df, extra_df], ignore_index=True)
        else:
            print("Classify Extra does not exist, proceed without it.")
        
    if os.path.exists(work_ds_path):
        shutil.rmtree(work_ds_path)
    os.makedirs(work_ds_path, exist_ok=True)
    pdf_folder = f"{work_ds_path}/PDF"
    json_folder = f"{work_ds_path}/json"
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(json_folder, exist_ok=True)
    

    
    def apply_copy_page(row,bar):
        outFilename = copy_page(row, pdf_folder, json_folder)
        bar()
        return outFilename

    with alive_bar(len(work_ds_df), title=f"Building work_ds in {folder} for year >= {year}") as bar:
        work_ds_df["file_name"] = work_ds_df.apply(lambda row: apply_copy_page(row,bar), axis=1)
        


    work_ds_df = work_ds_df.drop(columns=["periodico", "year", "month", "day", "page", "ed","evento","event_code"])
    work_ds_df.to_csv(f"{work_ds_path}/work_ds.csv", index=False)

def main():
    year = 1922
    folder = "detect"
    if len(sys.argv) == 3:
        year = int(sys.argv[2])
        folder = sys.argv[1]
    elif len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        print("Usage: python script.py [detect|classify] [year]")
        sys.exit(1)

    if folder not in ["detect", "classify"]:
        print("Folder must be 'detect' or 'classify'")
        sys.exit(1)
    build(folder, year)

if __name__ == "__main__":
    main()