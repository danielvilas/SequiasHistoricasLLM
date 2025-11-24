import os
import pandas as pd
from typing import Optional,List

from .geonames import GeoNamesGazetteer
from .ign_ogc_client import Ign_Nucleos_Poblacion_Client
from .model import LookupResult, NameNormalizer

import logging

LOG = logging.getLogger(__name__)


class GeoLocatorDB:

    def __init__(self, db_path: str = "./geo_db", normalizer=NameNormalizer()):
        self.db_path = db_path
        self.normalizer = normalizer
        # Initialize database connection here
        if not os.path.exists(db_path):
            os.makedirs(db_path)

        self.nuc_file = os.path.join(self.db_path, "nucleos_de_poblacion.csv")
        self.nuc_data: pd.DataFrame = None
        self.geo_client = GeoNamesGazetteer(normalizer=self.normalizer)
        self.ign_nuc_client = Ign_Nucleos_Poblacion_Client()

    def load_data(self):
        if os.path.exists(self.nuc_file):
            self.nuc_data = pd.read_csv(self.nuc_file)
        else:
            self.nuc_data = pd.DataFrame()
        
        # Comprobamos que no haya nombres repetidos
        df = self.nuc_data
        LOG.debug(f"Duplicated names: {df['nombre'].duplicated().sum()}")
        LOG.debug(f"Duplicated normalized names: {df['norm_name'].duplicated().sum()}")


        self.geo_client.load_data()

    def _match_name(self, name: str, query: str, province: str = None) -> Optional[LookupResult]:
        
        if name == query: #Match Perfecto
            return True
        
        if name.count("/")==1: # Nombres dobles en castellano y en local
            names = name.split("/")
            if query in names:
                return True

        # En las provincias de habla vasca se consideran los nombres en euskera
        # pero tenemos el nombre en castellano junto al vasco separados por guion
        pvasco = [1,31,48,20] # Provincias de habla vasca
        if province in pvasco and name.count("-") == 1:
            names = name.split("-")
            if query in names:
                return True 
        # elif province not in pvasco and name.count("-") == 1:
        #     print(f"{name} - {province} ni")
        return False

    def _lookup_by_name(self, name: str) -> Optional[LookupResult]:
        ndf = self.nuc_data
        idx = ndf.apply(lambda x: self._match_name(x["nombre"], name, x["provincia"]), axis=1)

        result = ndf[idx]
        if not result.empty:
            res = [result.iloc[i].to_dict() for i in range(result.shape[0])]
            return LookupResult(name, res, "nuc")

    def _lookup_by_normalized_name(self, name: str) -> Optional[LookupResult]:
        ndf = self.nuc_data
        idx = ndf.apply(lambda x: self._match_name(x["norm_name"], self.normalizer.normalize_name(name),x["provincia"]), axis=1)
        result = ndf[idx]
        if not result.empty:
            res = [result.iloc[i].to_dict() for i in range(result.shape[0])]
            return LookupResult(name, res, "nuc-norm")
        return None

    def lookup(self, name: str) -> Optional[LookupResult]:
        if name is None or name.strip() == "":
            return None
        if self.nuc_data is None or self.nuc_data.empty:
            LOG.warning(f"Lookup failed: Database not loaded")
            return None
        
        #primero buscamos por nombre exacto
        result = self._lookup_by_name(name)
        if result:
            return result

        result = self._lookup_by_normalized_name(name)
        if result:
            return result

        # Si no encontramos nada, buscamos en geonames
        geo_result = self.geo_client.lookup(name)
        possible_names = self.geo_client.posible_names(geo_result)
        res = []
        for pname in possible_names:
            result = self._lookup_by_name(pname)
            if result:
                res.extend(result.data)
        if len(res) > 0:
            return LookupResult(name, res, "geonames")

        return None

    def download_nuc(self):
        
        items = self.ign_nuc_client.get_all_items()
        # Store items in the database
        df = pd.DataFrame(items)
        df["norm_name"] = df["nombre"].apply(lambda x: self.normalizer.normalize_name(x))
        self.nuc_data = df
        self.nuc_data.to_csv(self.nuc_file, index=True)

    def download_geonames(self):
        self.geo_client.download()

    def get_lat_lon_rad(self, locs: List[dict]) -> Optional[dict]:
        if len(locs) == 0:
            return None
        if len(locs) == 1:
            # print (f"Getting lat/lon/rad for single location: {locs[0]}")
            # data = self.ign_nuc_client.search_item(locs[0].get("nombre"))
            # print (data)
            # exit(0)
            return {"latitud": locs[0].get("latitud"), "longitud": locs[0].get("longitud"), "radius": 0.0}
        else:
            lat = sum([item.get("latitud") for item in locs]) / len(locs)
            lon = sum([item.get("longitud") for item in locs]) / len(locs)
            dist = max([((item.get("latitud") - lat)**2 + (item.get("longitud") - lon)**2)**0.5 for item in locs])
            return {"latitud": lat, "longitud": lon, "radius": dist}    
        

