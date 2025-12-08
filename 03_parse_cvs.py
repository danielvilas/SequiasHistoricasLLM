from hashlib import md5
from sequias_historicas.PdfManager import PdfManager
from sequias_historicas.CsvManager import CsvManager
from es_geo_locator.geoLocator import GeoLocatorDB
from sequias_historicas.PagesManager import PagesManager

import os
import pandas as pd
import numpy as np

import logging

#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)


pdf_manager = PdfManager()
geoLocator = GeoLocatorDB()
geoLocator.load_data()  
csv_manager = CsvManager(pdf_manager=pdf_manager, geoLocator=geoLocator)

bad_names={"extremadura":{"nov-dic_1941":"nov_1941"},
           "hoy": {"mar_1954 HOY":"mar_1952 HOY",
                   "sep_1958":"sep-1958 HOY",
                   "jun_1976 HOY":"jun_1966 HOY",
                   "sep_1976 HOY_2":"sep_1976_2 HOY",
                   "oct_1976_2 HOY":"oct_1976 HOY_2",
                   "ago_1982_1 HOY":"ago_1882_1 HOY",
                   "abr_1983_1 HOY":"abr_1983_1HOY",
                   "mar_1989_2 HOY":"mar_1984_2 HOY",
                   "dic_1989_1 HOY":"dic_19891 HOY"
                   }

}

def locate_raw_csv(paper_name, raw_df):
    loc_df = csv_manager.locate_location(raw_df)
    #print (loc_df.columns)
    no_loc = loc_df[loc_df["latitud"].isnull()]
    no_loc_unic = no_loc["ubicacion"].unique()
    print (f"Locations not found ({len(no_loc_unic)}): {no_loc_unic}")
    csv_manager.save_clean_csv(loc_df, paper_name)
    return loc_df

def test_location(paper_name, location,year):

    pages_manager = PagesManager(paper=paper_name)
    pages_manager.set_bad_names(bad_names.get(paper_name, {}))
    pages_df=pages_manager.load_pages_df()
    print(csv_manager._search_page_in_page_manager(paper_name, {"pdf_page":location,"year":year}, pages_manager=pages_manager))

    pages_df_f =pages_df[pages_df["year"]==1933]
    print(len(pages_df_f))
    pages_df_f =pages_df_f[(pages_df_f["month"]==4)]
    print(len(pages_df_f))
    pages_df_f =pages_df_f[pages_df_f["page"]==102]
    print(len(pages_df_f))
    print(pages_df_f.head())
    print("----")
    print(pages_df_f["day"].value_counts())
    exit()

def test_location_2(paper_name, index):

    pages_manager = PagesManager(paper=paper_name)
    pages_manager.set_bad_names(bad_names.get(paper_name, {}))
    pages_df=pages_manager.load_pages_df()
    loc_df = pd.read_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean_rawlocations.csv")

    print(csv_manager._search_image_in_page_manager(paper_name, loc_df.iloc[index], pages_manager=pages_manager))

def fill_raw_locations(paper_name, loc_df, pages_manager):
    pdf_df, loc_df = csv_manager.fill_page_locations(paper_name, loc_df, pages_manager=pages_manager)  
    pdf_df.to_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_pdf_locations.csv", index=False)
    pdf_df_return = pdf_df.copy()
    print (f"Number of records with no PDF found: {len(pdf_df[pdf_df['found']==False])} out of {len(pdf_df)}")
    print (f" File is empty for {len(pdf_df[pdf_df['file'].isnull()])} records.")
    pdf_df = pdf_df.dropna(subset=["file"], how="any")
    pdf_df = pdf_df[pdf_df["found"]==False]
    print (f" Number of records with no PDF found and file is not empty: {len(pdf_df)}")
    pdf_df = pdf_df.dropna(subset=["file","fail_reason"], how="any")
    print(pdf_df.head(10))

    loc_df.to_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean_rawlocations.csv", index=False)
    return loc_df, pdf_df_return

def fill_clean_locations(paper_name, loc_df, pages_manager):
    loc_df, pdf_clean_loc_df = csv_manager.fill_clean_page_locations(paper_name, loc_df, pages_manager=pages_manager)

    pdf_clean_loc_df.to_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_pdf_clean_locations.csv", index=False)

    test_df = pdf_clean_loc_df[pdf_clean_loc_df["found"]==False]
    print (f"Number of records with no PDF found: {len(test_df)} out of {len(pdf_clean_loc_df)}")
    print (f" File is empty for {len(test_df[test_df['file'].isnull()])} records.")

    test_df = test_df.dropna(subset=["file"], how="any")
    print (f" Number of records with no PDF found and file is not empty: {len(test_df)}")
    print(test_df.head(10))
    found= pdf_clean_loc_df[pdf_clean_loc_df["found"]==True]
    print (f"Number of records with PDF found: {len(found)} out of {len(pdf_clean_loc_df)}")
    print(f" Number of records with correct image hash: {len(found[found['hash_matches']==True])} out of {len(found)}")
    return loc_df, pdf_clean_loc_df

def process_paper(paper_name):
    print(f"Processing paper: {paper_name}")
    raw_df = csv_manager.read_raw_csv(paper_name)
    if os.path.exists(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean.csv"):
        print (f"Clean CSV already exists for paper {paper_name}, skipping location step.")
        loc_df = pd.read_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean.csv")
    else:
        #raw_df =raw_df[0:10] 
        loc_df = locate_raw_csv(paper_name, raw_df)
        csv_manager.save_clean_csv(loc_df, paper_name)

    pages_manager = PagesManager(paper=paper_name)
    pages_df=pages_manager.load_pages_df()
    pages_manager.set_bad_names(bad_names.get(paper_name, {}))

    if os.path.exists(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean_rawlocations.csv"):
        print (f"PDF locations CSV already exists for paper {paper_name}, skipping PDF location step.")
        pdf_loc_df = pd.read_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_pdf_locations.csv")
        loc_df = pd.read_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean_rawlocations.csv")
    else:
        loc_df, pdf_loc_df = fill_raw_locations(paper_name, loc_df, pages_manager)
    
    if os.path.exists(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean_cleanlocations.csv"):
        print (f"PDF locations CSV already exists for paper {paper_name}, skipping PDF location step.")
        loc_df = pd.read_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_clean_cleanlocations.csv")
    else:
        loc_df, pdf_clean_loc_df = fill_clean_locations(paper_name, loc_df, pages_manager)
        

def check_img_same(paper_name, index):
    df = pd.read_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_pdf_clean_locations.csv")

    reg = df.iloc[index]
    year = int(reg["year"])
    month = int(reg["month"])
    day = int(reg["day"]) 
    page = int(reg["page"])
    edition = reg.get("edition", None)
    hash_expected = reg["file"]
    if edition is not None and (isinstance(edition, float) and np.isnan(edition)):
        edition = None
    res_ok = pdf_manager.check_image_hash_tool(hash_expected,paper_name, year, month, day, page, edition)
    if res_ok:
        print(f"Image at index {index} matches expected hash.")
    else:
        print(f"Image at index {index} does NOT match expected hash.")

def main():
    #csv_manager._get_location("Cáceres, España")
    #res =   geoLocator.search_unidad_adm("Extremadura")
    #print(res.data[0]["latitud"], res.data[0]["longitud"])
    print("-----")
    process_paper("extremadura")
    print("-----")
    process_paper("hoy")
    print("-----")
    #test_location("hoy","sep_1958 Pag 308","1958")
    #test_location_2("hoy", 600)
    #check_img_same("extremadura", 0)
    
def test_regex():
    import re
    patter_2_monhts= r'^([a-zA-Z]{3})-([a-zA-Z]{3})_(\d{4}) Pag (\d+)$'
    m = re.match (patter_2_monhts,'ago-sep_1923 Pag 165')
    print (m)
    if m:
        print (f"Matched: {m.groups()}")

if __name__ == "__main__":
    main()
    #test_regex()