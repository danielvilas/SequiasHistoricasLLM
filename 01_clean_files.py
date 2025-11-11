
from sequias_historicas.PdfManager import PdfManager, PdfFileInfo
import re
import os
import pandas as pd

from typing import List

pdf_manager = PdfManager()
cvs_output_path = "data/datasets/clean/pdfs_metadata.csv"
pd_summary_output_path = "data/datasets/clean/pdfs_summary.csv"
pd_summary_class_output_path = "data/datasets/clean/summary/"

def s00_check_filenames() -> List[PdfFileInfo]:

    if os.path.exists(cvs_output_path):
        print(f"CSV file already exists at {cvs_output_path}. Skipping filename check.")
        return pdf_manager.load_csv(cvs_output_path)

    found_e = pdf_manager.list_pdfs(newspaper="extremadura", year=None)
    found_h = pdf_manager.list_pdfs(newspaper="hoy", year=None)
    print (f"Total PDFs found: {len(found_e) + len(found_h)}")

    print (f"Total PDFs found (Extremadura): {len(found_e)}")
    print (f"Total PDFs found (Hoy): {len(found_h)}")       

    coherent_founds = 0
    for pdf in found_e + found_h:
        if pdf.coherent_path == False:
            print (f"Incoherent path: {pdf.path} -> {pdf.year}-{pdf.month}-{pdf.day}")
        elif pdf.coherent_path == True:
            coherent_founds += 1
    print(f"Total coherent paths found: {coherent_founds}")
    print("")
    return found_e + found_h


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
    # Meses que tienen agregados los dias y el propio mes
    df = pdf_manager.check_month_cleaned(df,pdfs)
    df.to_csv(pd_summary_output_path, index=False,header=True)
    df = pdf_manager.classify_pdfs(df)
    pdf_manager.save_per_class_summary(df, pd_summary_class_output_path)
    return df

def s03_move_files(pdfs: List[PdfFileInfo],df: pd.DataFrame):

    # Copiamos los meses que ya estan extraidas las noticias
    # Meses que tienen agregados los dias y el propio mes
    pdf_manager.copy_pages_files_clean(pdfs, df,'DaysAndOnePageAggregatedExploded')
    # Meses que tienen agregados los dias pero no el propio mes
    pdf_manager.copy_pages_files_clean(pdfs, df,'DaysExplodedNoMonth')


def main():
    pdfs = s00_check_filenames()
    df = s01_fill_num_pages(pdfs)
    #df = s02_check_month_cleaned(df,pdfs)
    #s03_move_files(pdfs, df)

    pdf_manager.save_cvs(pdfs, cvs_output_path)
    

def extract_files(peridico,year,month):
    pdfs = pdf_manager.list_pdfs(newspaper=peridico, year=year)
    for pdf in pdfs:
        if pdf.month == month:
            print (f"{pdf.path} -> {pdf.year}-{pdf.month}-{pdf.day}-{pdf.page}")


if __name__ == "__main__":
    main()
    #extract_files("extremadura",1962,2)
    pass