from sequias_historicas.PdfManager import PdfManager
from sequias_historicas.CsvManager import CsvManager
from es_geo_locator.geoLocator import GeoLocatorDB

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

def locate_raw_csv(paper_name, raw_df):
    loc_df = csv_manager.locate_location(raw_df)
    #print (loc_df.columns)
    no_loc = loc_df[loc_df["latitud"].isnull()]
    no_loc_unic = no_loc["ubicacion"].unique()
    print (f"Locations not found ({len(no_loc_unic)}): {no_loc_unic}")
    csv_manager.save_clean_csv(loc_df, paper_name)
    return loc_df

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
    
    pdf_df = csv_manager.fill_page_locations(paper_name, loc_df)  
    print (pdf_df[pdf_df["pattern"].isnull()].head())

def main():
    #csv_manager._get_location("Cáceres, España")
    #res =   geoLocator.search_unidad_adm("Extremadura")
    #print(res.data[0]["latitud"], res.data[0]["longitud"])
    process_paper("extremadura")
    process_paper("hoy")

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