
from sequias_historicas.PdfManager import PdfManager, PdfFileInfo
import re
import os
import pandas as pd

from typing import List

import logging

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)


pdf_manager = PdfManager()
cvs_output_path = "data/datasets/clean/pdfs_metadata.csv"
pd_summary_output_path = "data/datasets/clean/pdfs_summary.csv"
pd_summary_class_output_path = "data/datasets/clean/summary/"

def s00_check_filenames() -> List[PdfFileInfo]:

    found_pdfs = []
    if os.path.exists(cvs_output_path):
        print(f"CSV file already exists at {cvs_output_path}. Skipping filename check.")
        found_pdfs = pdf_manager.load_csv(cvs_output_path)
    else:
        found_e = pdf_manager.list_pdfs(newspaper="extremadura", year=None)
        found_h = pdf_manager.list_pdfs(newspaper="hoy", year=None)
        found_pdfs = found_e + found_h
        print (f"Total PDFs found (Extremadura): {len(found_e)}")
        print (f"Total PDFs found (Hoy): {len(found_h)}")       
    
    print (f"Total PDFs found: {len(found_pdfs)}")
    coherent_founds = 0
    for pdf in found_pdfs:
        if pdf.coherent_path == False:
            print (f"Incoherent path: {pdf.path} -> {pdf.year}-{pdf.month}-{pdf.day}")
        elif pdf.coherent_path == True:
            coherent_founds += 1
    print(f"Total coherent paths found: {coherent_founds}")
    print("")
    return found_pdfs


def s01_fill_num_pages(pdfs: List[PdfFileInfo])->pd.DataFrame:
    print ("Filling number of pages...")
    pdf_manager.fill_num_pages(pdfs) # Que el manager rellene num_pages
    df = pdf_manager.sumnary_pages(pdfs)
    df.to_csv(pd_summary_output_path, index=False,header=True)
    df = pdf_manager.classify_pdfs(df)
    pdf_manager.save_per_class_summary(df, pd_summary_class_output_path)
    return df

def s02_check_month_cleaned(df: pd.DataFrame,pdfs: List[PdfFileInfo])->pd.DataFrame:
    print ("Checking cleaned months...")
    # Comprobamos que los meses que ya estan extraidas las noticias
    
    df = pdf_manager.check_month_cleaned(df,pdfs)

    df.to_csv(pd_summary_output_path, index=False,header=True)
    df = pdf_manager.classify_pdfs(df)
    pdf_manager.save_per_class_summary(df, pd_summary_class_output_path)
    return df

def s03_copy_files(pdfs: List[PdfFileInfo],df: pd.DataFrame):

    # Copiamos los meses que ya estan extraidas las noticias
    # Meses que tienen agregados los dias y el propio mes
    pdf_manager.copy_pages_files_clean(pdfs, df,'DaysAndOnePageAggregatedExploded') # G1 doc
    # Meses que tienen agregados los dias pero no el propio mes
    pdf_manager.copy_pages_files_clean(pdfs, df,'DaysExplodedNoMonth') # G2 doc
    # Meses que tienen solo los diarios
    pdf_manager.extract_pages_from_daily_pdfs(pdfs, df,'DaysAndMonthAggregatedErrorOnPage') # G3 doc
    pdf_manager.extract_pages_from_daily_pdfs(pdfs, df,'DaysAndMonthAggregated') # G4 doc
    pdf_manager.extract_pages_from_daily_pdfs(pdfs, df,'OnlyDayPdfs') # G5 doc

    # Meses que tienen solo el mes
    pdf_manager.extract_pages_from_monthly_pdfs(pdfs, df,'OnlyMonthPdfs') # G6 doc

    #PDTe ver que hacemos con los siguientes grupos
    # Meses solo con el mes
    #pdf_manager.extract_pages_from_monthly_pdfs(pdfs, df,'OnlyMonthPdfs') # G6 doc
    # Meses inchorentes
    #pdf_manager.extract_pages_from_????(pdfs, df,'other') # G7 doc


def main():
    pdfs = s00_check_filenames()
    pdf_manager.save_cvs(pdfs, cvs_output_path)
    
    df = s01_fill_num_pages(pdfs)
    df = s02_check_month_cleaned(df,pdfs)
    s03_copy_files(pdfs, df)

    pdf_manager.save_cvs(pdfs, cvs_output_path)
    

# A partir de aqui son funciones de testeo

def extract_files(peridico,year,month):
    pdfs = pdf_manager.list_pdfs(newspaper=peridico, year=year)
    for pdf in pdfs:
        if pdf.month == month:
            print (f"{pdf.path} -> {pdf.year}-{pdf.month}-{pdf.day}-{pdf.page}")

from sequias_historicas.PdfManager import ediciones_hoy

def extract_hoy_codes(year,month, day, test_day = True, only_mismatch=False, pdfs: List[PdfFileInfo]=None):
    if pdfs is None:
        pdfs = pdf_manager.load_csv(cvs_output_path)
    data = []

    pdfs = [pdf for pdf in pdfs if pdf.periodico == "hoy" and pdf.year == year and pdf.month == month and pdf.day == day]
    #print (f"Total PDFs found for hoy {year}-{month}-{day}: {len(pdfs)}")
    if len(pdfs) == 0:
        return
    for pdf in pdfs:
        info = pdf_manager.extract_hoy_codes(pdf)
        if info is not None:
            data.append(info)
        else :
            print (f"No info extracted for {pdf.path}")

    df = pd.DataFrame(data)
    n_pags = df['n_pag'].unique()
    n_pags.sort()
    if test_day:
        print ("Dias incorrectos:")
        print (df[df['date_ok'] == False])
        print ("Codigos extraidos:")
        print (df['prov'].unique())
        print (df['code'].unique())
        print (n_pags)
        for n in n_pags:
            print (f"  - {n}: {len(df[df['n_pag'] == n])} ")
    if only_mismatch:
        
        for n in n_pags:
            subset = df[df['n_pag'] == n]
            found_provs = []
            valid = True
            for _,item in subset.iterrows():
                if item['prov'] in found_provs:
                    print(f"Duplicate code in {year}-{month}-{day} page {n}: {item['prov']} - {item['code']}")
                    valid = False
                found_provs.append(item['prov'])
                if item['prov'] not in ediciones_hoy:
                    print (f"Mismatch code in {year}-{month}-{day} page {n}: {item['prov']} - {item['code']}")
                    valid = False
            if not valid:
                print (f"data for {year}-{month}-{day} on page {n}:")
                print (subset)
    

from alive_progress import alive_bar
def test_pypdf():
    pdfs = pdf_manager.load_csv(cvs_output_path)
    test = [pdfs[617]]

    with alive_bar(len(test), title='Checking PDFs pages', spinner='dots') as bar:
        for pdf in test:
            pre = pdf.num_pages
            pdf.num_pages = None
            n = pdf_manager._read_pdf_num_pages(pdf)
            print (f"{pre} vs {n} for {pdf.path}") 
            bar()
    

def test_extract_codes_hoy():
    pdfs = pdf_manager.load_csv(cvs_output_path)
    for a in range(1933,1995): # Se han detectado errores en estos años
        for m in range(1,13):
            print (f"Extracting hoy codes for {a}-{m}")
            extract_hoy_codes(a,m,1,False,True, pdfs=pdfs)

if __name__ == "__main__":
    main()
    #extract_files("extremadura",1962,2)
    #test_pypdf()
    #extract_hoy_codes(1975,2,1)
    #test_extract_codes_hoy()
    #extract_hoy_codes(1993,5,2, True, True)
    #extract_hoy_codes(1993,5,24, True, True)

    pass