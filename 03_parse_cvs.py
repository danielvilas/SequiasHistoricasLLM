from sequias_historicas.PdfManager import PdfManager
from sequias_historicas.CsvManager import CsvManager
from es_geo_locator.geoLocator import GeoLocatorDB
from sequias_historicas.PagesManager import PagesManager

import os
import pandas as pd


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

    pdf_df = csv_manager.fill_page_locations(paper_name, loc_df, pages_manager=pages_manager)  
    pdf_df.to_csv(f"./data/datasets/clean/{paper_name}/{paper_name}_impactos_pdf_locations.csv", index=False)

    print (f"Number of records with no PDF found: {len(pdf_df[pdf_df['found']==False])} out of {len(pdf_df)}")
    print (f" File is empty for {len(pdf_df[pdf_df['file'].isnull()])} records.")
    pdf_df = pdf_df.dropna(subset=["file"], how="any")
    pdf_df = pdf_df[pdf_df["found"]==False]
    print (f" Number of records with no PDF found and file is not empty: {len(pdf_df)}")

    pdf_df = pdf_df.dropna(subset=["file","fail_reason"], how="any")
    print(pdf_df.head(10))
    

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