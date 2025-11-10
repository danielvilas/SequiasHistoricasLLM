from .PdfFilePatterns import patterns
from .models import PdfFileInfo

from PyPDF2 import PdfReader
from alive_progress import alive_bar

import re
from os import walk
from typing import List, Optional


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

class PdfManager:
    def __init__(self, pdf_raw_path="./data/datasets/raw"):
        self.pdf_raw_path = pdf_raw_path

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
    
            if pdf.num_pages == 1 and pdf.page is not None:
                pdf.is_one_page = True

            return pdf.num_pages
        except Exception as e:
            print(f"Error reading PDF {path}: {e}")
            return None

    def fill_num_pages(self, pdfs: List[PdfFileInfo]):
        # Placeholder for logic to fill num_pages attribute
        
        with alive_bar(len(pdfs), title='Checking PDFs pages', spinner='dots') as bar:
            for pdf in pdfs:
                pages = self._read_pdf_num_pages(pdf)
                bar()
        pass