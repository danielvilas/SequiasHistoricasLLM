
from sequias_historicas.PdfManager import PdfManager, PdfFileInfo
import re
import os

from typing import List

pdf_manager = PdfManager()
cvs_output_path = "data/datasets/clean/pdfs_metadata.csv"

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

def s01_fill_num_pages(pdfs: List[PdfFileInfo]):
    pdf_manager.fill_num_pages(pdfs) # Que el manager rellene num_pages

    return pdfs


def main():
    pdfs = s00_check_filenames()
    pdfs = s01_fill_num_pages(pdfs)

    pdf_manager.save_cvs(pdfs, cvs_output_path)
    

if __name__ == "__main__":
    main()
    pass