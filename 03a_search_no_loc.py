import pandas as pd
import os

from sequias_historicas.TfIDFSearcher import TfIDFSearcher
from sequias_historicas.PdfManager import PdfManager

from alive_progress import alive_bar

pdfManager = PdfManager()
def fileName_2_struct(filename,dir):
    # 19550105_0001_BAD.pdf
    # 19550105_0001.pdf
    year = filename[0:4]
    month = filename[4:6]
    day = filename[6:8]
    page = filename[9:13]
    if filename[14]==".":
        edition = None
    else:
        edition = filename[14:-4]

    return {"year.1":int(year),"month":int(month),"day":int(day),"page":int(page),"edition":edition,"clean_file":filename,"dir":dir}
    return filename
#    year.1,month,day,page,edition,clean_file

def get_pdfs_month(paper,fecha_str):
    # Load the dataset
    fecha_parts = fecha_str.split("/")
    year = fecha_parts[2]
    month = fecha_parts[1]
    dir = f"data/datasets/clean/{paper}/{year}/{month}/"

    pdf_names = []
    for root, dirs, files in os.walk(dir):
        pass
    return pdf_names

def get_pdfs_day(paper,fecha_str):
    # Load the dataset
    fecha_parts = fecha_str.split("/")
    year = fecha_parts[2]
    month = fecha_parts[1]
    day = fecha_parts[0]
    fecha_dir = f"{year}/{month}/{day}/"
    dir = f"data/datasets/clean/{paper}/{fecha_dir}/"
    pdf_names = []
    for filename in os.listdir(dir):
        if filename.endswith(".pdf"):
            pdf_names.append(fileName_2_struct(filename,dir)) 
    return pdf_names

def extract_text(paper,pdf_struct):
    dir = pdf_struct["dir"]
    year = pdf_struct["year.1"]
    month = pdf_struct["month"]
    day = pdf_struct["day"]
    page = pdf_struct["page"]
    edition = pdf_struct["edition"]
    text,_ = pdfManager.extract_text(paper,year,month,day,page,edition)
    return text

def find_missing_location_entries(paper, row):
    print("--------------------------------")
    print(f"titular: {row['titular']}")
    print(f"frase: {row['frase']}")
    print(f"fecha: {row['news_date']}")
    titular_lower = row['titular'].lower()
    frase_lower = row['frase'].lower()
    fecha_str = str(row['news_date'])

    pdfs = get_pdfs_day(paper, fecha_str)
    print(f"PDFs found for date {fecha_str}: {len(pdfs)}")
    texts = [extract_text(paper,pdf) for pdf in pdfs]
    #print(texts)
    searcher = TfIDFSearcher(texts)

    if titular_lower=="-":
        titular_lower=frase_lower
    results = searcher.search(titular_lower, top_n=1)
    result = results[0] if results else None
    if result:
        (index, document, score) = result
        print(f"Matched PDF (titular): {pdfs[index]['clean_file']} with score {score}")
    #     if score < 0.1:
    #         result = None
    # if not result:
    #     results = searcher.search(frase_lower, top_n=1)
    #     result = results[0] if results else None
    #     if result:
    #         (index, document, score) = result
    #         print(f"Matched PDF (frase): {pdfs[index]['clean_file']} with score {score}")
    #         if score < 0.1:
    #             result = None
    
    if result:
        return {"titular":row['titular'],"frase":row['frase'],"fecha":fecha_str,"matched_pdf":pdfs[index]['clean_file'],"score":score}
    else:
        # casos especiales manuales
        if fecha_str=="21/06/1945": 
            return {"titular":row['titular'],"frase":row['frase'],"fecha":fecha_str,"matched_pdf":"19450621_0002_BAD.pdf","score":0}
        if fecha_str=="07/07/1945": 
            return {"titular":row['titular'],"frase":row['frase'],"fecha":fecha_str,"matched_pdf":"19450707_0003_BAD.pdf","score":0}
        if fecha_str=="13/09/1950": 
            return {"titular":row['titular'],"frase":row['frase'],"fecha":fecha_str,"matched_pdf":"19500913_0007_CAC.pdf","score":0}
        print("No matching PDF found.")
        return {"titular":row['titular'],"frase":row['frase'],"fecha":fecha_str,"matched_pdf":None,"score":0}
    # print(f"PDFs found for date {fecha_str}: {pdfs}")
    #print(row)

def main(paper):
    # Load the dataset
    if os.path.exists(f"data/datasets/clean/{paper}/{paper}_impactos_clean_full.csv"):
        df = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean_full.csv")
    else:
        df = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean.csv")

    # Filter rows where 'pdf_page' is NaN
    df_no_location = df[df['pdf_page'].isna() & (df['clean_file'].isna() | (df['clean_file']==""))]
    print(f"Number of entries without location data: {len(df_no_location)}")
    if len(df_no_location)==0:
        print("No entries without location data found. Exiting.")
        return
    #print(df_no_location.head())
    
    def update_bar_and_find(row,bar):
        result = find_missing_location_entries(paper, row)
        bar()
        return pd.Series(result)
    with alive_bar(len(df_no_location), title='Processing entries without location data') as bar:
        search_results_df = df_no_location.apply(lambda row: update_bar_and_find(row, bar), axis=1)
    search_results_df.to_csv(f"data/datasets/clean/{paper}/{paper}_search_blank_00.csv", index=False)
    print ("Search results saved to CSV.")
    print("****")
    for index, row in search_results_df.iterrows():
        #print (index)
        #print(row)
        #print(df.iloc[index])
        if not row['matched_pdf'] or pd.isna(row['matched_pdf']):
            continue
        pdf_s=fileName_2_struct(row['matched_pdf'],f"data/datasets/clean/{paper}/")
        #print (pdf_s)
        df.at[index,'clean_file']=row['matched_pdf']
        df.at[index,'year.1']=pdf_s['year.1']
        df.at[index,'month']=pdf_s['month']
        df.at[index,'day']=pdf_s['day']
        df.at[index,'page']=pdf_s['page']
        if pdf_s['edition'] is not None and pdf_s['edition']!="":
            df.at[index,'edition']=pdf_s['edition']
        #print(df.iloc[index])
    df.to_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean_full.csv", index=False)


if __name__ == "__main__":
    main("extremadura")
    main("hoy")