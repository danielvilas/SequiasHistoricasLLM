import pandas as pd
import os

from sequias_historicas.TfIDFSearcher import TfIDFSearcher
from sequias_historicas.PdfManager import PdfManager
from sequias_historicas.CsvManager import CsvManager
from sequias_historicas.PdfFilePatterns import month_map

from alive_progress import alive_bar

pdfManager = PdfManager()
csvManager = CsvManager()

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


def find_day_in_month_page(paper, year, sMonth, page, scnt =0):
    start_dir = f"data/datasets/clean/{paper}/{year}/{sMonth:02}/"
    cnt = scnt
    for day in range(1,32):
        day_str = f"{day:02}"
        day_folder = os.path.join(start_dir, day_str)
        #print (f"Checking folder: {day_folder}")
        if not os.path.exists(day_folder):
            continue
        files=[]
        for filename in os.listdir(day_folder):
            files.append(filename)
        #print (f"Checking folder: {day_folder} (files found: {len(files)})")
        if len(files)<=0:
            continue
        if cnt+len(files)>=page:
            return (day, cnt)
        cnt += len(files)
    return (None, cnt)

def find_page_in_month(paper,year, sMonth, page):
    day, cnt = find_day_in_month_page(paper, year, sMonth, page)
    if day is None:
        print ("Day not found in sMonth, trying next month")
        sMonth += 1
        day, cnt = find_day_in_month_page(paper, year, sMonth, page, scnt=cnt)
    if day is None:
        print ("Day not found")
        return None
    print (f"Day found: {day} at cnt={cnt} for page={page}")
    page_in_day = page - cnt
    return f"{year:04}{sMonth:02}{day:02}_{page_in_day:04}.pdf"

def find_missing_aggreation(paper, row):
    print("--------------------------------")
    print(f"titular: {row['titular']}")
    print(f"frase: {row['frase']}")
    print(f"fecha: {row['news_date']}")
    titular_lower = row['titular'].lower()
    frase_lower = row['frase'].lower()
    fecha_str = str(row['news_date'])

    loc = csvManager._extract_page_number(row['pdf_page'])
    print (f"loc: {loc} ({row['pdf_page']})")
    
    if loc is None:
        return {"localizador":row['pdf_page'],"titular":row['titular'],"fecha":fecha_str,}
    pdf_file, page_number = loc

    sMonth=pdf_file[0:3]
    year = pdf_file[-4:]
    month_num = month_map.get(sMonth.lower())
    print(f"pdf_file: {pdf_file}, page_number: {page_number}, sMonth: {sMonth}, month_num: {month_num}, year: {year}")
    
    pdf = find_page_in_month(paper, year, month_num, page_number)
    print(f"Found pdf loc  : {pdf}" )

    return {"localizador":row['pdf_page'],"titular":row['titular'],"fecha":fecha_str,"pdf":pdf}

def main(paper):
    
    # Load the dataset
    if os.path.exists(f"data/datasets/clean/{paper}/{paper}_impactos_clean_full.csv"):
        df = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean_full.csv")
    else:
        df = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean.csv")

    # Filter rows where 'pdf_page' is NaN
    df_no_aggreagation = df[df['pdf_page'].notna()]
    df_no_aggreagation = df_no_aggreagation[df_no_aggreagation['raw_file'].isna()]
    print(f"Number of entries without location data: {len(df_no_aggreagation)}")
    print(df_no_aggreagation.head())
    
    def update_bar_and_find(row,bar):
        result = find_missing_aggreation(paper, row)
        bar()
        return pd.Series(result)
    
    #find_missing_aggreation(paper, df_no_aggreagation.iloc[0])  # Test run to avoid overhead in the loop
    #return
    with alive_bar(len(df_no_aggreagation), title='Processing entries without location data') as bar:
        search_results_df = df_no_aggreagation.apply(lambda row: update_bar_and_find(row, bar), axis=1)
    search_results_df.to_csv(f"data/datasets/clean/{paper}/{paper}_search_blank_01.csv", index=False)
    print ("Search results saved to CSV.")
    print("****")
    for index, row in search_results_df.iterrows():
        #print (index)
        #print(row)
        #print(df.iloc[index])
        if not row['pdf'] or pd.isna(row['pdf']):
            continue
        pdf_s=fileName_2_struct(row['pdf'],f"data/datasets/clean/{paper}/")
        #print (pdf_s)
        df.at[index,'clean_file']=row['pdf']
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
    #main("hoy")