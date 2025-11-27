from sequias_historicas.PdfManager import PdfManager
from sequias_historicas.CsvManager import CsvManager
from es_geo_locator.geoLocator import GeoLocatorDB
import pandas as pd

import logging

#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)


pdf_manager = PdfManager()
geoLocator = GeoLocatorDB()
geoLocator.load_data()  
csv_manager = CsvManager(pdf_manager=pdf_manager, geoLocator=geoLocator)

def process_paper(paper_name):
    print(f"Processing paper: {paper_name}")
    raw_df = csv_manager.read_raw_csv(paper_name)
    #raw_df =raw_df[0:10] 
    loc_df = csv_manager.locate_location(raw_df)
    #print (loc_df.columns)
    no_loc = loc_df[loc_df["latitud"].isnull()]
    no_loc_unic = no_loc["ubicacion"].unique()
    print (f"Locations not found ({len(no_loc_unic)}): {no_loc_unic}")
    csv_manager.save_clean_csv(loc_df, paper_name)

def main():
    #csv_manager._get_location("Cáceres, España")
    #res =   geoLocator.search_unidad_adm("Extremadura")
    #print(res.data[0]["latitud"], res.data[0]["longitud"])
    process_paper("extremadura")
    #process_paper("hoy")

if __name__ == "__main__":
    main()