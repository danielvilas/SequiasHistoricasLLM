from .PdfFilePatterns import patterns
from .models import PdfFileInfo

from pypdf import PdfReader, PdfWriter
from alive_progress import alive_bar

import pandas as pd

import re
from os import walk
from typing import List, Optional
import shutil
import os

bad_ends=[
    " EXTREMADURA.pdf",
    " EXTREMATURA.pdf",
    " EXTREMADURAA.pdf",
    " Extremadura.pdf",
    " EXTREMADURAAA.pdf",
    " EXTREMAADURA.pdf",
    " EXTREMDURA.pdf",
    

    "  HOY.pdf",
    " HOY.pdf",
    "_HOY.pdf",
    " HOY0.pdf",
    " HOY_1.pdf",
    " HOY_2.pdf",
    "_ 2HOY.pdf",
    " HOy.pdf",
    " Hoy.pdf",
    " hoy.pdf",
    "_1HOY.pdf",
    " H0Y.pdf",
]

ediciones_hoy = ['BAD', 'CAC', 'MER', 'SUP', 'DEP', 'SUB']  # Badajoz, Caceres, Merida, Suplemento, Deportes, Suplemento B

class PdfManager:
    def __init__(self, pdf_raw_path="./data/datasets/raw", pdf_clean_path="./data/datasets/clean"):
        self.pdf_raw_path = pdf_raw_path
        self.pdf_clean_path = pdf_clean_path

    def extract_text(self):
        # Placeholder for text extraction logic
        pass

    def save_text(self, text, output_path):
        # Placeholder for saving extracted text logic
        pass

    def _validate_newspaper(self, newspaper):
        if newspaper not in ["extremadura", "hoy"]:
            raise ValueError(f"Newspaper '{newspaper}' is not supported.")
        pass


    def _match_patterns(self, line: str, periodico=None, debug=False) -> Optional[PdfFileInfo]:
        path = line.strip()
        if debug:
            print (f"Matching line: {line.strip()}")
        
        if line.endswith("19891 HOY.pdf\n"):
            line = line.replace("19891 HOY.pdf\n","1989.pdf\n")

        if "1er semestre/" in line:
            line = line.replace("1er semestre/","")
        if "2o semestre/" in line:
            line = line.replace("2o semestre/","")
        if "2do semestre/" in line:
            line = line.replace("2do semestre/","")

        for bad_end in bad_ends:
            if line.endswith(bad_end):
                line = line.replace(bad_end,".pdf\n")
        if "/julio_" in line:
            line = line.replace("/julio_","/jul_")
        if "/junio_" in line:
            line = line.replace("/junio_","/jun_")

        for pattern in patterns:
            if debug:
                print(f"Trying pattern: {pattern['name']}") 
            match = re.match(pattern['pattern'], line.strip())

            if match:
                try:
                    pdf = pattern['callback'](match,path=path)
                    pdf.periodico = periodico
                except Exception as e:
                    print(f"Error processing line: {line.strip()} with pattern: {pattern['name']}") 
                    raise e
                
                pattern['count'] += 1
                return pdf
        print(f"No pattern matched for line: {line.strip()}")
        return None

    def list_pdfs(self,newspaper="extremadura", year=None) -> List[PdfFileInfo]:
        self._validate_newspaper(newspaper)
        print ("Listing PDFs for newspaper:", newspaper)
        lines=0
        pdfs = []
        for pattern in patterns:
            pattern['count']=0 
        root_path = f"{self.pdf_raw_path}/{newspaper}"
        for root, dirs, files in walk(root_path):
            for file in files:
                if not file.endswith(".pdf"):
                    continue
                relative_path = f".{root.replace(root_path, '')}/{file}"
                #print(f"Processing file: {relative_path}")
                pdf = self._match_patterns(relative_path, periodico=newspaper)
                if pdf:
                    if year is None or pdf.year == year:
                        pdfs.append(pdf)
                        lines += 1
                else:
                    print(f"Line did not match any pattern: {relative_path}") 
                    # self._match_patterns(relative_path, debug=True)
                    #return pdfs #
                    
        print(f"Found {lines} PDFs for newspaper '{newspaper}' with year filter '{year}'")
        return pdfs

    def save_cvs(self, pdfs: List[PdfFileInfo], output_path: str):
        import csv
        with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['path', 'year', 'month', 'day', 'page', 'coherent_path', 'periodico', 'num_pages', 'is_clean', 'is_one_page']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for pdf in pdfs:
                writer.writerow({
                    'path': pdf.path,
                    'year': pdf.year,
                    'month': pdf.month,
                    'day': pdf.day,
                    'page': pdf.page,
                    'coherent_path': pdf.coherent_path,
                    'periodico': pdf.periodico,
                    'num_pages': pdf.num_pages,
                    'is_clean': pdf.is_clean,
                    'is_one_page': pdf.is_one_page,
                })
        print(f"Saved CSV to {output_path}")

    def load_csv(self, input_path: str) -> List[PdfFileInfo]:
        import csv
        pdfs = []
        with open(input_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pdf = PdfFileInfo(
                    path=row['path'],
                    year=int(row['year']),
                    month=int(row['month']) if row['month'] else None,
                    day=int(row['day']) if row['day'] else None,
                    page=int(row['page']) if row['page'] else None,
                    coherent_path=row['coherent_path'].lower() == 'true' if row['coherent_path'] else None,
                    periodico=row['periodico'],
                    num_pages=int(row['num_pages']) if row['num_pages'] else None,
                    is_clean=row['is_clean'].lower() == 'true',
                    is_one_page=row['is_one_page'].lower() == 'true',
                )
                pdfs.append(pdf)
        print(f"Loaded {len(pdfs)} PDFs from CSV {input_path}")
        return pdfs

    def _read_pdf_num_pages(self, pdf: PdfFileInfo) -> int:
        if pdf.num_pages is not None:
            return pdf.num_pages
        path = f"{self.pdf_raw_path}/{pdf.periodico}/{pdf.path.lstrip('./')}"
        try:
            reader = PdfReader(path)
            pdf.num_pages = len(reader.pages)
            reader.stream.close()
            if pdf.num_pages == 1 and pdf.page is not None:
                pdf.is_one_page = True

            return pdf.num_pages
        except Exception as e:
            print(f"Error reading PDF {path}: {e}")
            return None

    def fill_num_pages(self, pdfs: List[PdfFileInfo]):
       
        with alive_bar(len(pdfs), title='Checking PDFs pages', spinner='dots') as bar:
            for pdf in pdfs:
                pages = self._read_pdf_num_pages(pdf)
                bar()
        pass

    def sumnary_pages(self, pdfs: List[PdfFileInfo]):
        total_pages = 0
        data = {}
        for pdf in pdfs:
            id = f"{pdf.periodico}-{pdf.year}-{pdf.month}"
            
            n_pages = pdf.num_pages or 0
            empty_pages = 1 if pdf.num_pages == 0 or pdf.num_pages==None else 0
            
            day_pdfs = 0
            day_pages = 0
            month_pdfs = 0
            month_pages = 0

            if pdf.day is None and pdf.month is None:
                print("PDF with no month and no day:", pdf.path)
            if pdf.day is not None and pdf.month is None:
                print("PDF with day but no month:", pdf.path)
            if pdf.num_pages>1 and pdf.is_one_page:
                print("PDF with more than one page but marked as one page:", pdf.path)  
             
            if pdf.day is None and pdf.month is not None:
                # es un PDF mensual
                month_pdfs = 1
                month_pages = n_pages
            if pdf.day is not None and pdf.month is not None \
                and (pdf.is_one_page is None or pdf.is_one_page == False):
                # es un PDF diario pero con varias paginas
                day_pdfs = 1
                day_pages = n_pages

            
            if id not in data:
                data[id] = {'periodico': pdf.periodico, 
                    'years': pdf.year, 'month': pdf.month,
                    'num_pdfs': 0, 'total_pages': 0,
                    'empty_pages': 0,
                    'one_page_pdfs': 0,
                    'month_pdfs':0,
                    'month_pages':0,
                    'day_pdfs':0,
                    'day_pages':0,
                    }
            data[id]['num_pdfs'] += 1
            data[id]['total_pages'] += n_pages
            data[id]['empty_pages'] += empty_pages
            if pdf.is_one_page: # esto es cuando el patron ha sacado que es de una pagina
                data[id]['one_page_pdfs'] += 1
            data[id]['month_pdfs'] += month_pdfs
            data[id]['month_pages'] += month_pages
            data[id]['day_pdfs'] += day_pdfs
            data[id]['day_pages'] += day_pages

        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.sort_values(by=['years','month'])
        return df

    def _classify_row(self, row):
        if row['day_pdfs'] > 0 and row['month_pdfs'] == 0 and row['one_page_pdfs'] == 0:
            return 'OnlyDayPdfs'
        if row['month_pdfs'] > 0 and row['day_pdfs'] == 0 and row['one_page_pdfs'] == 0:
            return 'OnlyMonthPdfs'
        if row['day_pages'] == row['month_pages']:
            if row['one_page_pdfs'] == row['day_pages']:
                return 'DaysAndOnePageAggregatedExploded'
            if row['one_page_pdfs'] == 0:
                return 'DaysAndMonthAggregated'
            return 'DaysAndMonthAggregatedErrorOnPage'
        if row['day_pages'] == row['one_page_pdfs'] and row['month_pages'] == 0:
            return 'DaysExplodedNoMonth'
        
        return 'other'

    def classify_pdfs(self, df: pd.DataFrame) -> pd.DataFrame:
        df["class"] = df.apply(lambda x: self._classify_row(x), axis=1)
        return df

    def save_per_class_summary(self, df: pd.DataFrame, output_path: str):
        classes = df['class'].unique()
        for cls in classes:
            df_class = df[df['class'] == cls]
            df_class.to_csv(f"{output_path}/{cls}_summary.csv", index=False, header=True)
        pass

    def _iterate_over_pdfs_by_class(self, pdfs: List[PdfFileInfo], df: pd.DataFrame, classification: str, 
        extra_filter, action, force_reprocess=False, msg="Copying"):

        df_class = df[df['class'] == classification]
        
        total= len(df_class)
        i=0    
        for _, row in df_class.iterrows(): # el _ es el indice de pandas, que es "libre"
            periodico = row['periodico']
            year = row['years']
            month = row['month']
            i+=1
            if row['is_month_cleaned'] and not force_reprocess:
                continue
            # Filtrar los PDFs correspondientes a este periodo
            # Que no esten ya limpios (is_clean is None or False)
            # Que sean del periodico, año y mes correctos
            # Que ademas sean diarios (day is not None) y de reconocidos como pagina (page is not None)
            filtered_pdfs = [pdf for pdf in pdfs if pdf.periodico == periodico and 
                (force_reprocess or pdf.is_clean is None or pdf.is_clean == False) and 
                pdf.year == year and pdf.month == month 
                and extra_filter(pdf, row)]
            with alive_bar(len(filtered_pdfs), title=f'  ({i+1}/{total}) {msg} {periodico} {year}-{str(month).zfill(2)}', spinner='dots') as bar_inner:
                for pdf in filtered_pdfs:
                    action(pdf, row)
                    bar_inner()
        pass

    
    def _copy_single_pdf_clean(self, pdf: PdfFileInfo, code=None):
        source_path = f"{self.pdf_raw_path}/{pdf.periodico}/{pdf.path.lstrip('./')}"
        target_dir = f"{self.pdf_clean_path}/{pdf.periodico}/{pdf.year}/{str(pdf.month).zfill(2)}/{str(pdf.day).zfill(2)}"
        os.makedirs(target_dir, exist_ok=True)
        if code is not None:
            target_path = f"{target_dir}/{pdf.year}{str(pdf.month).zfill(2)}{str(pdf.day).zfill(2)}_{str(code['n_pag']).zfill(4)}_{code['prov']}.pdf"
        else:
            target_path = f"{target_dir}/{pdf.year}{str(pdf.month).zfill(2)}{str(pdf.day).zfill(2)}_{str(pdf.page).zfill(4)}.pdf"
        shutil.copy2(source_path, target_path)
        pdf.is_clean = True
        pass

    def copy_pages_files_clean(self, pdfs: List[PdfFileInfo], df: pd.DataFrame, classification: str):
        print(f"Copying cleaned files for classification: {classification}")

        extra_filter = lambda pdf, row: pdf.day is not None and pdf.page is not None
        action = lambda pdf, row: self._copy_single_pdf_clean(pdf)

        self._iterate_over_pdfs_by_class(pdfs, df, classification, extra_filter, action)

        print(f"Finished copying cleaned files for classification: {classification}\n")

    def check_pages_files_clean(self, pdfs: List[PdfFileInfo], df: pd.DataFrame, classification: str):
        print(f"Checking cleaned files for classification: {classification}")

        extra_filter = lambda pdf, row: pdf.day is not None and pdf.page is not None
        action = lambda pdf, row: self._check_single_pdf_clean(pdf)

        self._iterate_over_pdfs_by_class(pdfs, df, classification, extra_filter, action)

        print(f"Finished checking cleaned files for classification: {classification}\n")


    def _check_month_cleaned(self, row: pd.Series) -> bool:
        target_dir = f"{self.pdf_clean_path}/{row['periodico']}/{row['years']}/{str(row['month']).zfill(2)}"
        if not os.path.exists(target_dir):
            return False
        n_files = 0
        for root, dirs, files in walk(target_dir):
            n_files += len(files)
        
        if n_files == 0: return False
        if row['class'] in ['DaysAndOnePageAggregatedExploded', 'DaysExplodedNoMonth', # Los que ya estan G1 y G2
                         'OnlyDayPdfs', 'DaysAndMonthAggregatedErrorOnPage',# Los que extraemos de los diarios G3 y G5
                         'DaysAndMonthAggregated']: # Los que extraemos de los diarios G4
            expected_files = row['day_pages'] # Sacamos el nuero que tener de los diarios
            if n_files == expected_files:
                return True
            else:
                return False

        if row['class'] == 'OnlyMonthPdfs': # Los casos especiales de meses solo con el mes G6
            expected_files = row['month_pages'] # Sacamos el nuero que tener de los mensuales
            if n_files == expected_files:
                return True
            else:   
                return False

    
        return False

    def _action_clean_month(self, pdf: PdfFileInfo, row):
        if row['is_month_cleaned'] is not None and row['is_month_cleaned'] == False:
            pdf.is_clean = False
        pass

    def check_month_cleaned(self, df: pd.DataFrame,pdfs: List[PdfFileInfo])-> pd.DataFrame:

        df["is_month_cleaned"] = df.apply(lambda row: self._check_month_cleaned(row), axis=1)

        extra_filter = lambda pdf, row: True
        action = lambda pdf, row: self._action_clean_month(pdf, row)

        # Los que ya estan extraidos
        self._iterate_over_pdfs_by_class(pdfs, df, 'DaysAndOnePageAggregatedExploded', extra_filter, action, force_reprocess=True,msg="Setting isClean" ) #G1
        self._iterate_over_pdfs_by_class(pdfs, df, 'DaysExplodedNoMonth', extra_filter, action, force_reprocess=True,msg="Setting isClean" ) #G2
        
        # Los que extraemos de los diarios
        self._iterate_over_pdfs_by_class(pdfs, df, 'DaysAndMonthAggregatedErrorOnPage', extra_filter, action, force_reprocess=True,msg="Setting isClean" ) #G3
        self._iterate_over_pdfs_by_class(pdfs, df, 'DaysAndMonthAggregated', extra_filter, action, force_reprocess=True,msg="Setting isClean" ) # G4
        self._iterate_over_pdfs_by_class(pdfs, df, 'OnlyDayPdfs', extra_filter, action, force_reprocess=True,msg="Setting isClean" ) # G5

        # los casos especiales de meses solo con el mes
        self._iterate_over_pdfs_by_class(pdfs, df, 'OnlyMonthPdfs', extra_filter, action, force_reprocess=True,msg="Setting isClean" ) # G6 

        return df

    def _extract_pages_from_daily_pdfs(self, pdf: PdfFileInfo,row):

        if pdf.num_pages == 1:
            ret = True
            if pdf.periodico=="hoy" and pdf.page is None:
                codes = self.extract_hoy_codes(pdf)
                if codes is not None:
                    self._copy_single_pdf_clean(pdf, code=codes)

            # Dos casos que tienen un PDF diario de una sola pagina pero que es correcto
            if pdf.periodico=="extremadura" and pdf.year == 1949 and pdf.month ==3: ret = False
            if pdf.periodico=="extremadura" and pdf.year == 1955 and pdf.month ==4: ret = False
            
            if ret:  return

        source_path = f"{self.pdf_raw_path}/{pdf.periodico}/{pdf.path.lstrip('./')}"
        target_dir = f"{self.pdf_clean_path}/{pdf.periodico}/{pdf.year}/{str(pdf.month).zfill(2)}/{str(pdf.day).zfill(2)}"
        os.makedirs(target_dir, exist_ok=True)
        reader = PdfReader(source_path)
        for i in range(len(reader.pages)):
            target_path = f"{target_dir}/{pdf.year}{str(pdf.month).zfill(2)}{str(pdf.day).zfill(2)}_{str(i+1).zfill(4)}.pdf"
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            with open(target_path, 'wb') as f_out:
                writer.write(f_out)
            
        pass

    def extract_pages_from_daily_pdfs(self, pdfs: List[PdfFileInfo], df: pd.DataFrame, classification: str):
        
        extra_filter = lambda pdf, row: True if pdf.day is not None and (pdf.page is  None) else False
        action = lambda pdf, row: self._extract_pages_from_daily_pdfs(pdf, row)

        self._iterate_over_pdfs_by_class(pdfs, df, classification, extra_filter, action, msg="Extracting") 
        pass

    def _extract_pages_from_monthly_pdfs(self, pdf: PdfFileInfo,row):
        source_path = f"{self.pdf_raw_path}/{pdf.periodico}/{pdf.path.lstrip('./')}"
        target_dir = f"{self.pdf_clean_path}/{pdf.periodico}/{pdf.year}/{str(pdf.month).zfill(2)}/00"
        os.makedirs(target_dir, exist_ok=True)
        reader = PdfReader(source_path)
        for i in range(len(reader.pages)):
            target_path = f"{target_dir}/{pdf.year}{str(pdf.month).zfill(2)}00_{str(i+1).zfill(4)}.pdf"
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            with open(target_path, 'wb') as f_out:
                writer.write(f_out)
        pass
    
    def extract_pages_from_monthly_pdfs(self, pdfs: List[PdfFileInfo], df: pd.DataFrame, classification: str):
        
        extra_filter = lambda pdf, row: True if pdf.day is None else False
        action = lambda pdf, row: self._extract_pages_from_monthly_pdfs(pdf, row)
        self._iterate_over_pdfs_by_class(pdfs, df, classification, extra_filter, action, msg="Extracting") 
        pass

    def extract_hoy_codes(self, pdf: PdfFileInfo):
        filename = pdf.path.split("/")[-1]
        #print (f"{pdf.path} -> {pdf.year}-{pdf.month}-{pdf.day}-{pdf.page} : {filename}")
        
        pattern = r'(\d{2})(\d{8})([a-zA-Z\d])([a-zA-Z]{3})\.pdf$'
        match = re.search(pattern, filename)
        if not match and pdf.year==1993 and pdf.month==5 and pdf.day in [2,24]:
            # en estos dos dias hay un formato diferente
            # 4419930502DEPCAC 44 19930502 DEPCAC
            pattern = r'(\d{2})(\d{8})([a-zA-Z\d]{3})([a-zA-Z]{3})\.pdf$'
            match = re.search(pattern, filename)
        if match:
            day_str = f"{pdf.year}{str(pdf.month).zfill(2)}{str(pdf.day).zfill(2)}"
            day_fname = match.group(2)
            if day_str != day_fname:
                print (f" {pdf.path}  -> MISMATCH in day: {day_str} vs {day_fname}")
            n_pag = match.group(1)
            code = match.group(3)
            prov = match.group(4)
            return {
                "code": code,
                "prov": prov,
                "n_pag": n_pag,
                "date_ok": day_str == day_fname,
            }
        else:
            print (f"{filename}  -> NO MATCH")
        return None


    def extract_text(self, paper:str, year:int, month:int, day:int, page:int, ed:str=None)-> str:
        filename = f"{year:04d}{month:02d}{day:02d}_{page:04d}" 
        if ed:
            filename += f"_{ed}"
        filepath =f"./data/datasets/clean/{paper}/{year:04}/{month:02}/{day:02}/{filename}.pdf"
        if os.path.exists (filepath):
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            reader.stream.close()
            return text,filepath
        else:
            print (f"File NOT found: {filepath}")
            return None,filepath