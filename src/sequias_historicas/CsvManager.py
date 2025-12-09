import pandas as pd
import numpy as np
from es_geo_locator.geoLocator import GeoLocatorDB 
from es_geo_locator.consts import prov_geo_map
from .PdfManager import PdfManager

import csv
from alive_progress import alive_bar
from .PagesManager import PagesManager


import re
pattern_2_monhts= r'^([a-zA-Z]{3})-([a-zA-Z]{3})_(\d{4}) Pag (\d+)$' #mar-abr_1959 Pag 32
pattern_1_monhts= r'^([a-zA-Z]{3})_(\d{4})[\s_]Pag (\d+)$' #mar-abr_1959 Pag 32
pattern_1_monhts_Ed= r'^([a-zA-Z]{3})_(\d{4})_(\d)[\s_]Pag (\d+)$' #mar-abr_1959 Pag 32

class CsvManager:
    def __init__(self, pdf_raw_path="./data/datasets/raw", pdf_clean_path="./data/datasets/clean", pdf_manager:PdfManager=None,geoLocator:GeoLocatorDB=None):
        self.pdf_raw_path = pdf_raw_path
        self.pdf_clean_path = pdf_clean_path
        if pdf_manager is None:
            pdf_manager = PdfManager(pdf_raw_path=pdf_raw_path, pdf_clean_path=pdf_clean_path)
        self.pdf_manager = pdf_manager
        if geoLocator is None:
            geoLocator = GeoLocatorDB()
            geoLocator.load_data()
        self.geoLocator = geoLocator

        self.geoCache = {}

    
    def read_line_std(self, line):
        # process a line from the csv
        # return a dict with the data
        	
        data = {
            "paper": line[0],   #Extremadura
            "news_date": line[1], #18/09/1923
            "pdf_page": line[2],#ago-sep_1923 Pag 165
            "titular": line[3],	#Desde Casas de Don Antonio	
            "frase": line[4], # Llueve después de tres meses sin llover
            "evento": line[5], # Calor	
            "evento_fecha": line[6], # 18/09/1923 v.d.
            "evento_razon": line[7], # Sequía, Lluvia
            "ubicacion": line[8], # Casas de Don Antonio
            "code_1": line[9], # 1	
            "code_2": line[10], # D	
            "comment_1": line[11], # ''
            "event_code": line[12], # S
            "comment_2": line[13], # ''
            "agrocultura": line[14], # 1 Agricultura
            "ganaderia": line[15], # 0 Ganadería
            "hidrologia": line[16], # 0 Hidrología
            "energia": line[17], # 0 Energía
            "year": line[18], # 1923
        }
        return data

    def read_line_alt(self, line, paper):
        # process a line from the csv
        # return a dict with the data
        data = {
            "paper": paper,         
            "news_date": line[1],   
            "pdf_page": line[2],    
            "titular": line[3],	    	
            "frase": line[4],       
            "evento": None,         
            "evento_fecha": None,   
            "evento_razon": None,   
            "ubicacion": line[6],   
            "code_1": line[9],      	
            "code_2": line[0],     
            "comment_1": line[11],  
            "event_code": line[5], 
            "comment_2": line[13],  
            "agrocultura": line[14],
            "ganaderia": line[15],  
            "hidrologia": line[16], 
            "energia": line[17],    
            "year": line[18],
        }

        def check_fields(data, line_item):
            for key in data:
                if data[key] == line_item:
                    return key
            return None

        for i, column in enumerate(line):
            if i in [7,19]:
                continue # skip, no es un campo procesado
            field = check_fields(data, column)
            if field is None:
                print (f"Warning: Unprocessed field[{i}] ({column})")

        return data



    def read_raw_csv(self, paper) -> pd.DataFrame:
        file_path = f"{self.pdf_raw_path}/{paper}/{paper}_impactos.csv"
        
        data = []
        bad_starts=[]
        # read the csv line by line
        with open(file_path, "r") as f:
            reader = csv.reader(f, delimiter=",")
            for i, line in enumerate(reader):
                if i == 0:
                    continue  # skip header
                
                if line[0] in ["C","S","C y S"]:
                    # skip bad lines
                    #return None# for debugging
                    #print(line)
                    line_d = self.read_line_alt(line,paper)
                    #print(line_d)
                    #return None# for debugging
                else:
                    line_d = self.read_line_std(line)
                
                # fix known typos
                if line_d["ubicacion"] =="Trijillo":
                    line_d["ubicacion"] ="Trujillo"
                if line_d["ubicacion"] =="Cácceres":
                    line_d["ubicacion"] ="Cáceres"
                if line_d["ubicacion"] in ["Valencia deAlcánatara","Pedanías de Valencia de Alcántara"]: # Las pedanias son como barrios
                    line_d["ubicacion"] ="Valencia de Alcántara"
                if line_d["ubicacion"] =="Garrovillas":
                    line_d["ubicacion"] ="Garrovillas de Alconétar"
                data.append(line_d)

                #print('line[{}] = {}'.format(i, line))
        
        ret = pd.DataFrame(data)
        
        ret["ubicacion"] = ret["ubicacion"].replace([' ', '', '-'], None)
        return ret

    def _get_location_one(self, location:str, print_results:bool=False):
        if location == "España":
            return []
        result = self.geoLocator.lookup(location)


        return_list = []
        if result is None:
            return []

        if print_results:
            print (f"Location: {location} -> Result: {result.data}")

        if len(result.data) == 1:
            return_list.append(result.data[0])
        elif len(result.data) > 1:
            # multiple results
            # we could implement a better disambiguation here
            cand = []
            for item in result.data:
                prov = item.get('provincia',None)
                if prov in [6,10]:
                    cand.append(item)
            if len(cand) == 1:
                return_list.append(cand[0])
            else:
                for item in result.data:
                    return_list.append(item)
        return return_list

    def _may_have_multiple(self, location:str):
        # heuristic to determine if a location may have multiple matches
        # for now, we consider locations that are just a town name without province
        if location is None:
            return False

        if ',' in location or 'y' in location or '(' in location or '/' in location:
            return True
        return False

    def _try_multiple_char(self, location:str,char_sep=','):
        ret = []
        parts = location.split(char_sep)
        for part in parts:
            part = part.strip()
            #print (f"Trying part: {part}")
            ret_list = self._get_location_one(part,print_results=False)

            ret.extend(ret_list)
        
        return ret

    def _try_multple(self, location:str):
        ret = []
        if ',' in location:
            #print (f"Trying multiple with , for location: {location}")
            ret = self._try_multiple_char(location, char_sep=',')
            #print (f"Found {len(ret)} results")
            if len(ret) > 0:
                return ret
        if 'y' in location:
            #print (f"Trying multiple with y for location: {location}")
            ret = self._try_multiple_char(location, char_sep='y')
            #print (f"Found {len(ret)} results")
            if len(ret) > 0:
                return ret
        if '/' in location:
            #print (f"Trying multiple with / for location: {location}")
            ret = self._try_multiple_char(location, char_sep='/')
            #print (f"Found {len(ret)} results")
            if len(ret) > 0:
                return ret
        if '(' in location and ')' in location:
            start = location.index('(')
            end = location.index(')')
            part = location[0:start].strip()
            ret = self._get_location_one(part,print_results=False)
            #print (f"Found {len(ret)} results")
            if len(ret) > 0:
                return ret
            else :
                part = location[start+1:end].strip()
                ret = self._get_location_one(part,print_results=False)
                #print (f"Found {len(ret)} results")
                if len(ret) > 0:
                    return ret
        return ret

    def _get_location(self, location:str):
        if location in self.geoCache:
            return pd.Series(self.geoCache[location],dtype="float64")   
        

        ret_list = self._get_location_one(location)
        if len(ret_list) == 0 and self._may_have_multiple(location):
            ret_list = self._try_multple(location)

        if len(ret_list) == 0:
            ret = {"latitud":None, "longitud":None, "radius":None}
        #elif len(ret_list) == 1:
        #    ret = {"latitud":ret_list[0].get("latitud"), "longitud":ret_list[0].get("longitud"), "radius":0.0}
        else:
            ret = self.geoLocator.get_lat_lon_rad(ret_list)
            # multiple results
        #    ret = {"latitud":None, "longitud":None}



        self.geoCache[location] = ret
        
        return pd.Series(ret,dtype="float64")

    def locate_location(self, df:pd.DataFrame):
        with alive_bar(len(df), title="Locating places") as bar:
            def wrapped_get_location(location):
                res = self._get_location(location)
                bar()
                return res
            loc_df = df['ubicacion'].apply(wrapped_get_location)
        
        df = pd.concat([df, loc_df], axis=1)
        #print (df.head())
        return df

    def save_clean_csv(self, df:pd.DataFrame, paper:str):
        file_path = f"{self.pdf_clean_path}/{paper}/{paper}_impactos_clean.csv"
        df.to_csv(file_path, index=False)

    def save_full_csv(self, df:pd.DataFrame, paper:str):
        file_path = f"{self.pdf_clean_path}/{paper}/{paper}_impactos_full.csv"
        df.to_csv(file_path, index=False)

    def load_clean_csv(self, paper:str) -> pd.DataFrame:
        file_path = f"{self.pdf_clean_path}/{paper}/{paper}_impactos_clean.csv"
        df = pd.read_csv(file_path)
        return df
    
    def load_full_csv(self, paper:str) -> pd.DataFrame:
        file_path = f"{self.pdf_clean_path}/{paper}/{paper}_impactos_full.csv"
        df = pd.read_csv(file_path)
        return df

    def _extract_page_number(self, pdf_page:str):
        if "_Pag" in pdf_page:
            pdf_page = pdf_page.replace("_Pag"," Pag").strip()
            
        if "pag" in pdf_page:
            pdf_page = pdf_page.replace("pag"," Pag").strip()
        
        parts= pdf_page.split(" Pag ")
        if len(parts) != 2:
            return None

        name = parts[0].strip()
        if parts[1].strip().isdigit() == False:
            return None
        page_num = int(parts[1].strip())
        return (name, page_num)
    
    def _extract_page_number_pattern(self, pdf_page:str):
        pattern = r'^(.*)[\s_](\d+)$'
        match = re.match(pattern, pdf_page)
        if match:
            name = match.group(1).strip()
            page_num = match.group(2).strip()
            return (name, page_num)
        return None

    def _search_page_in_page_manager(self, paper:str, row, pages_manager:PagesManager):
        pdf_page = row['pdf_page']
        if (isinstance(pdf_page, float) and np.isnan(pdf_page)) or \
            pdf_page is None or np.nan == pdf_page or pdf_page == '':
            return {"file":pdf_page, "found":False, "img_hash": None,"fail_reason":"no_page_info"}
        name = None
        page_num = None

        if "pag" in pdf_page.lower():
            res = self._extract_page_number(pdf_page)
        else:
            res = self._extract_page_number_pattern(pdf_page)
        
        if res is not None:
               name, page_num = res
        if res is not None:
            name, page_num = res
        else:
            return {"file":pdf_page, "found":False, "img_hash": None,"fail_reason":"bad_page_format"}
        if page_num is None or str(page_num).isdigit() == False:
            return {"file":pdf_page, "found":False, "img_hash": None,"fail_reason":"page_not_digit"}
        page_num = int(page_num)
        year = row["year"]
        info = pages_manager.search_page(name, page_num, year) # primera busqueda
        
        #Si no hemos encontrado, probamos variantes
        if info is None and "_HOY" in name:  # A veces el _HOY esta separado
            name_alt = name.replace("_HOY"," HOY").strip()
            info = pages_manager.search_page(name_alt, page_num, year)
        if info is None and '_' in name:    # A veces es - en vez de _
            name_alt = name.replace("_","-")
            info = pages_manager.search_page(name_alt, page_num, year)
        if info is None and ' HOY' in name:    # A veces es es _HOY
            name_alt = name.replace(" HOY","_HOY")
            info = pages_manager.search_page(name_alt, page_num, year)
        if info is None and paper=="hoy" and "HOY" not in name:  # En el Hoy siempre debe estar el HOY
            name_alt = name + " HOY"
            info = pages_manager.search_page(name_alt, page_num, year)
        if info is None and 'Extremadura' in name: # Varias formas de escribir Extremadura
            name_alt = name.replace("Extremadura","EXTREMADURA")
            info = pages_manager.search_page(name_alt, page_num, year)
        
        if info is not None:
            return {"file":pdf_page,"raw_file":info.get("file_path", None), "found":True, "img_hash": info.get("img_hash", None),"fail_reason":None}
        
        # Ficheros que sabemos que no estan indexados por mes-pagina
        if paper=="extremadura":
            if row["year"]in["1954","1955","1957","1944-1945 y 1948-1949","1958","1959"] \
                    or row["news_date"][-4:] in ["1958","1959"] \
                    or row["news_date"][-4:] in ["1975","1976",]:  # estas fechas tenemos dias complentos y no mes
                return {"file":pdf_page, "found":False, "img_hash": None,"fail_reason":None}

        return {"file":pdf_page, "found":False, "img_hash": None,"fail_reason":"not_found"}


    def fill_page_locations(self, paper:str, df:pd.DataFrame, pages_manager:PagesManager) -> tuple[pd.DataFrame,pd.DataFrame]:

        with alive_bar(len(df), title="Filling page locations") as bar:
            def fill_page(row):
                ret= self._search_page_in_page_manager(paper, row, pages_manager)
                bar()
                return pd.Series(ret)
            df_file = df.apply(lambda row: fill_page(row), axis=1)
        
        df = pd.concat([df, df_file[["img_hash","raw_file"]]], axis=1)

        return df_file,df
    
    def _search_image_in_page_manager(self, paper:str, row, pages_manager:PagesManager):
        img_hash = row['img_hash']
        if (isinstance(img_hash, float) and np.isnan(img_hash)) or \
            img_hash is None or np.nan == img_hash or img_hash == '':
            return {"file":img_hash, "found":False, "raw_file": None,"fail_reason":"no_image_info"}
        
        info = pages_manager.search_image(paper,img_hash) # primera busqueda

        if info is not None:
            return {"file":img_hash,"found":True,
                    "year":info.get("year", None),
                    "month":info.get("month", None),
                    "day":info.get("day", None),
                    "page":info.get("page", None),
                    "edition":info.get("edition", None),
                    "clean_file":info.get("clean_file", None),}
        
        return {"file":img_hash, "found":False}
    

    def fill_clean_page_locations(self, paper:str, df:pd.DataFrame, pages_manager:PagesManager) -> tuple[pd.DataFrame,pd.DataFrame]:

        with alive_bar(len(df), title="Filling clean page locations") as bar:
            def fill_page(row):
                ret= self._search_image_in_page_manager(paper, row, pages_manager)
                bar()
                return pd.Series(ret)
            df_file = df.apply(lambda row: fill_page(row), axis=1)
        
        df_file = self.check_image_hashes(paper, df_file, pages_manager)
        columns_to_add = ["year","month","day","page","edition","clean_file","hash_matches"]
        df = pd.concat([df, df_file[columns_to_add]], axis=1)

        return df,df_file
    
    def _check_image_tool(self,row,paper):
        hash_expected = row['file']
        if (isinstance(hash_expected, float) and np.isnan(hash_expected)) or \
            hash_expected is None or np.nan == hash_expected or hash_expected == '':
            
            return False
        year = int(row["year"])
        month = int(row["month"])
        day = int(row["day"])
        page = int(row["page"])
        edition = row.get("edition", None)
        if edition is not None and (isinstance(edition, float) and np.isnan(edition)):
            edition = None
        
        return self.pdf_manager.check_image_hash_tool(hash_expected,paper, year, month, day, page, edition)
                
    def check_image_hashes(self, paper:str, df:pd.DataFrame, pages_manager:PagesManager) -> pd.DataFrame:
        with alive_bar(len(df), title="Checking image hashes") as bar:
            def check_image(row):
                res_ok = self._check_image_tool(row, paper)
                bar()
                return res_ok
            df['hash_matches'] = df.apply(lambda row: check_image(row), axis=1)

        return df