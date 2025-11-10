
from sequias_historicas.PdfManager import PdfManager
import re


pdf_manager = PdfManager()
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