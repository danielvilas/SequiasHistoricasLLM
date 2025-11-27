import pandas as pd
from es_geo_locator.geoLocator import GeoLocatorDB 
from es_geo_locator.consts import prov_geo_map
from .PdfManager import PdfManager

import csv
from alive_progress import alive_bar
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