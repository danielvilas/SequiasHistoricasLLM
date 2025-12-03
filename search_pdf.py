#!/usr/bin/env python3
import os
import sys
from pypdf import PdfReader


# extraemos de los parametros los datos que necesitamos
paper = sys.argv[1]
year = int(sys.argv[2])
month = int(sys.argv[3])
day = int(sys.argv[4])
text = sys.argv[5:]

print(f"Extracting text from {paper} {year}-{month}-{day} and text {text}")
folder =f"./data/datasets/clean/{paper}/{year:04}/{month:02}/{day:02}/"

def get_text(folder, file):
    filepath = os.path.join(folder, file)
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    reader.stream.close()
    return text

def check_text(text, keywords):
    for keyword in keywords:
        if keyword.lower() not in text.lower():
            return False
    return True

print(f"Looking into folder {folder} for PDFs")
for filename in os.listdir(folder):
    if filename.endswith(".pdf"):
        pfdf_text = get_text(folder, filename)
        if check_text(pfdf_text, text):
            print(f"Found text in {filename}")
#text,filepath = pdf_manager.extract_text(paper, year, month, day, page, ed)