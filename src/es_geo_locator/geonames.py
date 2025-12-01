import requests
import zipfile
import pandas as pd
import os


import logging

from .model import LookupResult, NameNormalizer, NameNormalizer
from typing import List, Optional


LOG = logging.getLogger(__name__)

class GeoNamesGazetteer:
    def __init__(self, db_path: str = "./geo_db", country: str = "ES", normalizer: NameNormalizer = NameNormalizer()):
        self.db_path = db_path
        self.country = country
        self.df: pd.DataFrame = None
        self.normalizer = normalizer

    def download(self, country: str = None):
        if country is None:
            country = self.country

        url = f"https://download.geonames.org/export/dump/{country}.zip"
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"./geo_db/{country}.zip", "wb") as f:
                f.write(response.content)
        else:
            LOG.error(f"Failed to download {url}")
            return
        # unzip the downloaded file

        with zipfile.ZipFile(f"./geo_db/{country}.zip", "r") as zip_ref:
            zip_ref.extractall(f"./geo_db/{country}")
            LOG.info(f"Extracted {country}.zip")
        self.cleanup()
    
    def cleanup(self):
        # Leemos el TSV y nos quedamos con lo que nos interesa
        df = pd.read_csv(f"./geo_db/{self.country}/{self.country}.txt", sep="\t", header=None, low_memory=False)
        df.columns = ["geonameid", "name", "asciiname", "alternatenames", 
                      "latitude", "longitude", "feature class", "feature code", 
                      "country code", "cc2", "admin1 code", "admin2 code",
                      "admin3 code", "admin4 code",
                      "population", "elevation", "dem", "timezone", "modification date"]      
        
        # zgz = df[df["name"] == "Zaragoza"]
        # for i in range(zgz.shape[0]):
        #     print(zgz.iloc[i])
        #     print()

        # Nos quedamos solos con las clases P (poblaciones) y A (administrativas)
        df = df[df["feature class"].isin(["P", "A"])]

        #quitamos columnas que no nos interesan
        
        # country code es en todos ES
        # population es numero de habitantes (no lo necesitamos)
        # dem es modelo de elevacion digital (no lo necesitamos)
        # timezone es la zona horaria (no lo necesitamos)
        # modification date es la fecha de modificacion (no lo necesitamos)

        df = df.drop(columns=["country code","population", "elevation", "dem", "timezone", "modification date"], errors="ignore")
        df = df.drop(columns=["cc2"])# cuando una localidad pertenece a dos paises (ejemplo candanchu)
        df = df.drop(columns=["admin4 code", "admin3 code"], errors="ignore") # 3 es municipio 4 barrio (no lo necesitamos)
        
        
        df = df.rename(columns={"admin1 code": "ccaa", "admin2 code": "provincia"})
        #print(df.columns)

        df.to_csv(f"./geo_db/{self.country}/{self.country}.csv")
   

    def load_data(self):
        # Load the GeoNames data into the database
        path = f"./geo_db/{self.country}/{self.country}.csv"
        if os.path.exists(path):
            self.df= pd.read_csv(path)
        else:
            self.df = pd.DataFrame()

        df = self.df
        LOG.debug(f"Loaded {df.shape[0]} from geonames")
        LOG.debug(f"duplicated names: {df[df.duplicated(subset=['name'])].shape[0]}")

    def _is_row_match(self, row: pd.Series, name: str) -> bool:
        name_norm = self.normalizer.normalize_name(name)

        # Check for exact match
        if row["name"] == name:
            return True

        # Check Normalized Name
        if name_norm == self.normalizer.normalize_name(row["name"]):
            return True

        alt_names = row["alternatenames"].split(",") if pd.notna(row["alternatenames"]) else []
        
        if name in alt_names:
            return True
        
        alt_names_norm = [self.normalizer.normalize_name(name) for name in alt_names]
        if name_norm in alt_names_norm:
            return True

        return False

    def lookup(self, name: str) -> Optional[LookupResult]:

        idx = self.df.apply(lambda x: self._is_row_match(x, name), axis=1)
        LOG.debug(f"Geonames lookup for '{name}': {idx.sum()} matches found")
        results = self.df[idx]
        
        if not results.empty:
            res = [r.to_dict() for i, r in results.iterrows()]
            return LookupResult(name, res, "geonames")
        return None

    def posible_names(self, lookup_result: LookupResult) -> List[str]:
        if not lookup_result:
            return []

        possible_names = []
        for item in lookup_result.data:
            if item["name"] not in possible_names:
                possible_names.append(item["name"])
        
        return list(possible_names)

    #def lookup(self, name: str) -> Optional[LookupResult]:
    #    return self.db.lookup(name)
