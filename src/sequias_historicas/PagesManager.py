import pandas as pd
import csv
import re
from .PdfFilePatterns import extract_hoy_codes, month_map, pdf_match_patterns

from alive_progress import alive_bar

class PagesManager:
    def __init__(self, raw_path="./data/datasets/raw", clean_path="./data/datasets/clean",paper="extremadura"):
        self.raw_path = raw_path
        self.clean_path = clean_path
        self.paper = paper
        self.df_pages:pd.DataFrame = None
        self.bad_names = None
        

    def load_pages_df(self):
        if self.df_pages is None:
            self.df_pages = pd.read_csv(f"{self.clean_path}/{self.paper}/{self.paper}_pages_clean.csv")
        return self.df_pages
    def save_pages_df(self):
        if self.df_pages is not None:
            self.df_pages.to_csv(f"{self.clean_path}/{self.paper}/{self.paper}_pages_clean.csv", index=True)

    def extract_date_from_path(self, filename):
        '''
        Extract date from file path
        
        :param self: Description
        :param filename: Description
        '''
        parts = filename.split("/")
        base = 0
        if "-" in parts[0]:
            base = 1
        try:
            #print(parts)
            #print (f"years= parts[{base}]")
            if parts[base].endswith(".pdf"):
                patter = r"(\d{4})(\d{2})(\d{2})\.pdf$"
                
                match = re.search(patter, parts[base])
                if match:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    return (year, month, day, parts[base])
                return None
            else:
                year = int(parts[base])

            if(parts[base] == parts[base + 1]): #Cuando el año se repite
                base += 1
            if(not parts[base + 1].isdigit()): #Cuando no es un digito
                base += 1 #Semestre o trimestre
                

            #print (f"month= parts[{base+1}]")
            month=None
            day=None
            if len(parts) > base + 2:   
                month = int(parts[base + 1])
            
            if len(parts) > base + 3:
                if parts[base + 2].startswith("Revista"):
                    day = None
                else:   
                    day = int(parts[base + 2])

            file_name = parts[-1]
            if month is None:
                mstr= file_name[:3].lower()
                month= month_map.get(mstr, None)
            
            if year < 1920 or year > 2020:
                raise ValueError(f"Year out of range: {year}")
            if month is not None and (month < 1 or month > 12):
                raise ValueError(f"Month out of range: {month}")
            if day is not None and (day < 1 or day > 31):
                raise ValueError(f"Day out of range: {day}")
            return (year, month, day, file_name)
        except Exception as e:
            print("Error extracting date from path:", filename)
            print(e)
        return None


    def _extract_date_from_estacional2(self, filename):
        if filename=="V1923.pdf": return [] #lo omitimos, lo tenemos no esta referenciado en las sequias
        if filename=="P1923.pdf": return [] #lo omitimos, lo tenemos no esta referenciado en las sequias
        try:
            patter = r"^(\d{0,2})([a-z]{3})-(\d{0,2})([a-z]{3})_(\d{4}).pdf$"
            match = re.search(patter, filename.lower())
            if match:
                m1 = (match.group(2))
                m2 = (match.group(4))
                year = int(match.group(5))
                m1 = month_map.get(m1, None)
                m2 = month_map.get(m2, None)
                
                if m1 is None:
                    raise ValueError(f"Month abbreviation not recognized: {match.group(2)}")
                if m2 is None:
                    raise ValueError(f"Month abbreviation not recognized: {match.group(4)}")
                return [(year, m1, None, filename),(year, m2, None, filename)]
            
            res = self.extract_date_from_path(filename)
            if res is not None:
                return [res]
            
            return None
        except Exception as e:
            print("Error extracting date from estacional2 path:", filename)
            print(e)
        return None

    def _extract_date_from_estacional(self, filename):
        '''
        Extract date from estacional file path
        
        :param self: Description
        :param filename: Description
        '''
        if filename.lower().startswith("primavera") or filename.lower().startswith("verano"):
            return self._extract_date_from_estacional2(filename.split("/")[-1])
        try:
            patter1 = r"^([a-z]{3})[_\-](\d{4})\.pdf$"
            match = re.search(patter1, filename.lower())
            if match:
                m1 = (match.group(1))
                year = int(match.group(2))
                m1 = month_map.get(m1, None)
                if m1 is None:
                    raise ValueError(f"Month abbreviation not recognized: {match.group(1)}")
                return [(year, m1, None, filename)]
            
            patter2 = r"^([a-z]{3})-([a-z]{3})_(\d{4})\.pdf$"
            match = re.search(patter2, filename.lower())
            if match:
                m1 = (match.group(1))
                m2 = (match.group(2))
                year = int(match.group(3))
                m1 = month_map.get(m1, None)
                m2 = month_map.get(m2, None)
                if m1 is None:
                    raise ValueError(f"Month abbreviation not recognized: {match.group(1)}")
                if m2 is None:
                    raise ValueError(f"Month abbreviation not recognized: {match.group(2)}")
                return [(year, m1, None, filename),(year, m2, None, filename)]
            
            #print("not matched estacional filename:", filename)
            return None
        except Exception as e:
            print("Error extracting date from estacional path:", filename)
            print(e)
        return None

    def _extract_page_info(self, row):
        '''
        Extract page information from a row
        
        :param self: Description
        :param row: Description
        '''
        
        file_path = row[0]
        file_path = file_path.replace("/data.lcsc/nfs/personal/jvela/news-extremadura/", "")
        file_path = file_path.replace("/data.lcsc/nfs/personal/jvela/news-extremadura-hoy/HOY/", "")
        page = int(row[1])
        img_hash = row[2]

        if file_path.startswith("Extremadura-estacional"):
            #print ("treating estacional file:", file_path)
            date_info= self._extract_date_from_estacional(file_path.replace("Extremadura-estacional/", ""))
    
            if date_info is not None:
                ret = []
                for (year, month, day, file_name) in date_info:
                    ret.append(pd.Series({
                        "file_path": file_path,
                        "page": page,
                        "img_hash": img_hash,
                        "year": year,
                        "month": month,
                        "day": day,
                        "file_name": file_name
                    }))
                return ret
        
        
        date_info= self.extract_date_from_path(file_path)

        if date_info is not None:
            (year, month, day, file_name) = date_info
        else:
            print("Date info could not be extracted from file path:", file_path)
            exit(0)

        return [pd.Series({
            "file_path": file_path,
            "page": page,
            "img_hash": img_hash,
            "year": year,
            "month": month,
            "day": day,
            "file_name": file_name
        })]

    def fill_page_locations(self, paper_file="pages.txt"):
        '''
        Fill page locations from csv text files
        
        :param self: Description
        :param paper_file: Description
        '''
        data=[]
        with open(f"{self.raw_path}/{self.paper}/{paper_file}", "r", encoding="utf-8") as f:
            reader = csv.reader(f)

            with alive_bar() as bar:

                for row in reader:
                    info = self._extract_page_info(row)
                    data.extend(info)
                    #print(info)
                    
                    if data[-1]["file_path"] == "":#
                        print("Found target file:", info)
                        exit(0)
                    bar()
        self.df_pages = pd.DataFrame(data)
        return self.df_pages
    
    def set_bad_names(self, bad_names:dict):
        self.bad_names = bad_names

    def search_page(self, file_name:str, page:int, year):
        in_file_name = file_name
        if self.df_pages is None:
            self.load_pages_df()
        if self.bad_names is not None and file_name in self.bad_names:
            file_name=self.bad_names[file_name]

        #print(f"Searching for file_name={file_name} (original: {in_file_name}), page={page}, year={year}")

        df_page = self.df_pages[(self.df_pages["file_name"]==f"{file_name}.pdf")]
        
        #print(f"Filtered by file_name, found {len(df_page)} entries")
        df_page = df_page[df_page["page"]==page]
        #print(f"Filtered by page, found {len(df_page)} entries")
        #print(df_page)
        
        if len(df_page) == 0:
            return None

        if len(df_page) == 1:
            return df_page.iloc[0].to_dict()

        if len(df_page) > 1:
            chk0 = df_page.iloc[0]["img_hash"]
            if(all(df_page["img_hash"]==chk0)):
                return df_page.iloc[0].to_dict()
            #print (f"Multiple entries found, checking img_hash: {chk0}")
        
        if year is not None:
            if not isinstance(year, int):
                try:
                    year = int(year)
                except:
                    return None
            df_page_year = df_page[df_page["year"]==int(year)]
            #print(f"Filtered by year, found {len(df_page_year)} entries")
            if len(df_page_year) == 1:
                return df_page_year.iloc[0].to_dict()
            
        return None
    
    def _to_img_dict(self, pdf_info, row, img_hash, periodico):
        page = None

        ed = None
        ed_info = None
        if periodico=="hoy":
            ed_info = extract_hoy_codes(pdf_info)
            if ed_info is not None:
                ed = ed_info.get("prov", None)
                if pdf_info.page is None:
                    pdf_info.page = int(ed_info.get("n_pag", None))
        
        if pdf_info.page is not None:
            #print("Using page from pdf_info")
            page = pdf_info.page
        else:
            #print("Using page from row")
            page = row["page"]
        #print(row)

        
        return {"img_hash": img_hash,
                "paper:": periodico,
                "year": pdf_info.year,
                "month": pdf_info.month,
                "day": pdf_info.day,
                "page": page,
                "edition": ed,
                "clean_file": row["file_name"]
                }
    
    def _all_img_same(self, canditatos):
        chk =f"{canditatos[0]['year']}-{canditatos[0]['month']}-{canditatos[0]['day']}-P{canditatos[0]['page']}"
        for c in canditatos:
            cand = f"{c['year']}-{c['month']}-{c['day']}-P{c['page']}"
            if cand != chk:
                return False
        return True
    
    def search_image(self, periodico, img_hash:str):
        if self.df_pages is None:
            self.load_pages_df()
        
        df_img = self.df_pages[self.df_pages["img_hash"]==img_hash]
        
        #print(df_img)
        if len(df_img) == 0:
            return None
        
        canditatos = []
        for _, row in df_img.iterrows():
            pdf_info =  pdf_match_patterns("./"+row["file_path"], periodico, False)
            if pdf_info is not None:
                c = self._to_img_dict(pdf_info, row, row["img_hash"], periodico)
                if c["day"] is not None:
                    canditatos.append(c)
        
        #print(canditatos)
        if len(canditatos) == 0:
            # Agrupados por mes (ignorando dia)
            for _, row in df_img.iterrows():
                pdf_info =  pdf_match_patterns("./"+row["file_path"], periodico, False)
                if pdf_info is not None:
                    c = self._to_img_dict(pdf_info, row, row["img_hash"], periodico)
                    if c["day"] is None:
                        c["day"] = 0 
                        canditatos.append(c)
        if  len(canditatos) == 0:
            return None
        if len(canditatos) == 1:
            return canditatos[0]
        if self._all_img_same(canditatos):
            return canditatos[0]
        
        


        
        return None