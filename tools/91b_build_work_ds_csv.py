from importlib.resources import files
import pandas as pd
from sequias_historicas.CsvManager import CsvManager

from alive_progress import alive_bar
import random

import os

pdfs_to_process = [
    #peridico,ano,mes,dia,pagina,ed
    ("extremadura",1923,9,18,1,None,True), # portada
    ("extremadura",1924,6,7,4,None,True), # Sequia
    ("extremadura",1924,6,7,1,None,False), # Portada
    ("extremadura",1925,5,14,1,None,True), # Sequia
    ("extremadura",1926,9,28,5,None,True), # Sequia
    ("extremadura",1926,9,28,3,None,False), # Tablas
    ("extremadura",1927,2,8,1,None,False), # Portada
    ("extremadura",1927,2,8,4,None,False), # Columnas
    ("extremadura",1928,10,14,1,None,False), # Portada
    ("extremadura",1928,10,14,3,None,False), # Columnas
    ("extremadura",1929,4,16,1,None,True), # Sequia
    ("extremadura",1929,4,16,3,None,False), # Columnas
    ("extremadura",1930,5,2,1,None,False), # Portada
    ("extremadura",1930,5,2,4,None,True), # Sequia
    ("hoy",1933,3,5,1,"BAD",False),  # portada
    ("hoy",1933,3,5,5,"BAD",False), # 6 Columnas,
    ("hoy",1933,9,1,6,"BAD", True), # Sequia
    ("extremadura",1933,9,12,6,None,True), # Sequia
    ("extremadura",1933,9,12,7,None,False), # Texto   
    ("hoy",1934,3,15,1,"BAD",False), # Portada
    ("hoy",1934,3,15,6,"BAD",True), # Sequia
    ("hoy",1934,3,15,7,"BAD",False), # Imagenes
    ("extremadura",1934,11,22,4,None,True), # Sequia
    ("extremadura",1934,11,22,6,None,False), # Texto
    ("hoy",1935,11,0,15,None,False), # portada
    ("hoy",1935,11,0,9,None,True), # Rogativa
    ("extremadura",1935,6,10,3,None,False), # Texto
    ("hoy",1936,1,0,22,None,False), # Fotos
    ("hoy",1936,1,0,14,None,True), # sequia
    ("extremadura",1935,6,10,3,None,False), # Texto
    ("hoy",1937,7,0,23,None,False), # Portada
    ("hoy",1937,7,0,15,None,False), # Columnas
    ("hoy",1938,2,0,7,None,False), # Columnas
    ("hoy",1938,2,0,97,None,False), # Portada
    ("extremadura",1938,3,25,2,None,True), # Sequia
    ("extremadura",1938,3,25,1,None,False), # Texto
    ("hoy",1939,9,0,28,None,False), # Portada
    ("hoy",1939,9,0,16,None,True), # Sequia
    ("hoy",1940,4,0,19,None,False), # Portada
    ("hoy",1940,4,0,11,None,False), # Columnas
    ("extremadura",1940,5,10,2,None,True), # Sequia
    ("extremadura",1940,5,10,4,None,False), # Texto
    ("hoy",1941,11,15,1,"BAD",False), # Portada
    ("hoy",1941,11,15,3,"BAD",True), # Sequia
    ("extremadura",1941,11,25,4,None,True), # Sequia
    ("extremadura",1941,11,25,1,None,False), # Portada
    ("hoy",1942,10,20,1,"BAD",False), # Portada
    ("hoy",1942,10,20,7,"BAD",False), # Columnas
    ("extremadura",1942,8,7,1,None,False), # Portada
    ("hoy",1943,4,17,6,"CAC",True), # Sequia
    ("hoy",1943,4,17,1,"CAC",False), # Portada
    ("extremadura",1943,7,7,1,None,False), # Portada
    ("extremadura",1943,7,7,3,None,True), # Sequia
    ("hoy",1944,3,5,5,"BAD",False), # Columnas
    ("hoy",1944,3,5,4,"MER",True), # Rogativa
    ("extremadura",1944,4,24,2,None,False), # Columnas
    ("extremadura",1944,4,24,3,None,True), # Sequia
    ("hoy",1945,7,18,3,"BAD",False), # Texto Dificil
    ("hoy",1945,7,18,7,"BAD",True), # Sequia
    ("extremadura",1945,8,27,1,None,False), # Portada
    ("extremadura",1945,8,27,4,None,True), # Sequia
    ("hoy",1946,8,18,1,"BAD",False), # Portada
    ("hoy",1946,8,18,4,"BAD",True), # Sequia
    ("extremadura",1946,8,5,4,None,False), # Texto
    ("extremadura",1946,8,5,3,None,True), # Sequia
    ("hoy",1947,5,1,4,"CAC",False), # Anuncios
    ("hoy",1947,5,1,3,"BAD",True), # Sequia
    ("extremadura",1947,5,5,1,None,False), # Portada
    ("extremadura",1947,5,5,3,None,True), # Sequia
    ("hoy",1948,12,1,4,"CAC",False), # Fotos
    ("hoy",1948,12,1,3,"BAD",True), # Sequia
    ("extremadura",1948,12,18,4,None,False), # Columnas
    ("extremadura",1948,12,18,3,None,True), # Sequia
    ("hoy",1949,6,15,1,"BAD",False), # Portada
    ("hoy",1949,6,15,4,"BAD",True), # Sequia
    ("extremadura",1949,8,1,1,None,False), # Portada
    ("extremadura",1949,8,1,3,None,True), # Sequia
    ("hoy",1950,9,21,2,"BAD",False), # Columnas
    ("hoy",1950,9,21,5,"BAD",True), # Sequia
    ("extremadura",1950,9,9,1,None,False), # Portada
    ("extremadura",1950,9,9,4,None,True), # Sequia
    ("hoy",1951,1,17,6,"BAD",False), # Fotos
    ("hoy",1951,1,17,4,"CAC",True), # Sequia
    ("extremadura",1951,2,3,3,None,False), # Texto
    ("hoy",1952,11,18,3,"BAD",False), # Tabla
    ("hoy",1952,11,18,4,"CAC",True), # Sequia
    ("hoy",1952,11,18,6,"BAD",False), # Anuncio pal Sequia
    ("extremadura",1952,11,12,1,None,False), # Portada
    ("extremadura",1952,11,12,4,None,True), # Sequia
    ("hoy",1953,8,30,1,"BAD",False), # Portada
    ("hoy",1953,8,30,4,"CAC",True), # Sequia
    ("extremadura",1953,9,1,1,None,True), # Sequia
    ("hoy",1954,3,4,2,"BAD",False), # Columnas y textos cortos
    ("hoy",1954,3,4,5,"BAD",True), # Sequia
    ("extremadura",1954,10,29,5,None,False), # Fotos
    ("extremadura",1954,10,29,2,None,True), # Sequia
    ("hoy",1955,10,25,1,"CAC",False), # Portada
    ("hoy",1955,10,25,2,"BAD",True), # Sequia 
    ("extremadura",1955,11,10,1,None,False), # Portada
    ("extremadura",1955,11,10,3,None,True), # Sequia
    ("hoy",1956,2,14,2,"BAD",False), # Columnas
    ("hoy",1956,2,14,8,"BAD",False), # Nuevo diseño columnas
    ("extremadura",1956,2,14,3,None,False), # Muchos Anuncios
    ("hoy",1957,4,25,1,"BAD",False), # Portada
    ("hoy",1957,4,25,6,"BAD",True), # Sequia (esta mal en el ods, dice 23)
    ("extremadura",1957,12,10,2,None,False), # Texto
    ("extremadura",1957,12,10,4,None,True), # Sequia
    ("hoy",1958,11,13,8,"CAC",False), # Columnas
    ("hoy",1958,11,13,6,"BAD",True), # Sequia 
    ("extremadura",1958,11,14,1,None,False), # Nueva Portada
    ("extremadura",1958,11,14,5,None,True), # Sequia
    ("hoy",1959,11,13,3,"BAD",False), # Columnas
    ("hoy",1959,11,13,6,"CAC",True), # Sequia 
    ("extremadura",1959,3,5,4,None,False), # Texto
    ("extremadura",1959,3,5,6,None,True), # Sequia
    ("hoy",1960,6,5,3,"BAD",False), # Columnas
    ("hoy",1960,6,5,1,"CAC",False), # Portada
    ("extremadura",1960,5,27,1,None,False), # Portada
    ("extremadura",1960,5,27,9,None,True), # Sequia
    ("hoy",1961,9,20,3,"BAD",False), # Columnas
    ("hoy",1961,9,20,2,"CAC",True), # Sequia 
    ("extremadura",1961,9,20,5,None,False), # Tabla
    ("hoy",1962,3,17,3,"BAD",False), # Columnas
    ("hoy",1962,3,17,9,"BAD",True), # Sequia 
    ("extremadura",1962,9,21,1,None,False), # Portada
    ("extremadura",1962,9,21,4,None,True), # Sequia
    ("hoy",1963,10,6,16,"CAC",False), # Columnas
    ("hoy",1963,10,6,8,"CAC",True), # Sequia 
    ("extremadura",1963,10,10,2,None,False), # Texto
    ("extremadura",1963,10,10,3,None,True), # Sequia
]

cvs_manager=CsvManager()
dfs={"extremadura":cvs_manager.load_full_csv("extremadura"), "hoy":cvs_manager.load_full_csv("hoy")}

def _search_manual_pdf(paper, year, month, day, page, pdf, ed):
    df = dfs[paper]
    df_f = df[(df["year.1"]==year)]
    #print (f"impactos found for year {year}: {len(df_f)}")
    df_f = df_f[(df_f["month"]==month)]
    #print (f"impactos found for month {month}: {len(df_f)}")
    df_f = df_f[(df_f["day"]==day)]
    #print (f"impactos found for day {day}: {len(df_f)}")
    df_f = df_f[(df_f["page"]==page)]
    #print (f"impactos found for page {page}: {len(df_f)}")

    if len(df_f)==0:
        #Miramos si es por no tener pdf_page
        nDate = f"{day:02d}/{month:02d}/{year}"
        df_f = df[(df["news_date"]==nDate)]
        #print (f"impactos found for news_date {nDate}: {len(df_f)}")
    if len(df_f)>1 and ed is not None:
        df_f = df_f[(df_f["edition"]==ed)]
        #print (f"impactos found for ed {ed}: {len(df_f)}")

    if len (df_f)==0:
        if pdf: print(f"WARNING: No se encontro el pdf {pdf}")
        return None
    if len(df_f)>1:
        if pdf: print(f"WARNING: Mas de un pdf encontrado para {pdf}: {len(df_f)}")
        #Los cuatro casos, coniciden en ser el primero
        return df_f.iloc[0]
    return df_f.iloc[0]

def _manual_data2dict(pdf)->dict:
    paper, year, month, day, page, ed, has_sequia = pdf

    if has_sequia:
        row = _search_manual_pdf(paper, year, month, day, page, pdf, ed)

        if row is None:
            print(f"ERROR: No se encontro el pdf con sequia para {pdf}")
            return None
        else:            
            return {
                "peridico": paper,
                "news_date": row["news_date"],
                "year": year,
                "month": month,
                "day": day,
                "page": page,
                "ed": ed,
                "evento":row["evento"],
                "event_code":row["event_code"],
                "ubicacion":row["ubicacion"],
                "has_sequia": has_sequia,
                "agrocultura":row["agrocultura"],
                "ganaderia":row["ganaderia"],
                "hidrologia":row["hidrologia"],
                "energia":row["energia"],
                "latitud":row["latitud"],
                "longitud":row["longitud"],
                }   
    else:
        return {
            "peridico": paper,
            "news_date": f"{year}/{month:02d}/{day:02d}",
            "year": year,
            "month": month,
            "day": day,
            "page": page,
            "ed": ed,
            "evento":None,
            "event_code":None,
            "ubicacion":None,
            "has_sequia": has_sequia,
            "agrocultura":0,
            "ganaderia":0,
            "hidrologia":0,
            "energia":0,
            "latitud":None,
            "longitud":None,
            }

def manual_data()->list:
    ret= []
    with alive_bar(len(pdfs_to_process), title="Building work_ds.csv") as bar:
        for pdf in pdfs_to_process:
            data = _manual_data2dict(pdf)
            if data is not None:
                ret.append( data)
            bar()
    return ret

def _chose_random_row_for_year(paper, year)->dict:
    df = dfs[paper]
    df_year = df[(df["year.1"]==year)]
    if len(df_year)==0:
        print (f"No hay Impacto para {paper} en {year}")
        return None
    #Seleccionamos aleatoriamente uno
    row_i = random.choice(df_year.index)
    row = df.loc[row_i]
    return {
        "peridico": paper,
        "news_date": row["news_date"],
        "year": year,
        "month": row["month"],
        "day": row["day"],
        "page": row["page"],
        "ed": row["edition"],
        "evento":row["evento"],
        "event_code":row["event_code"],
        "ubicacion":row["ubicacion"],
        "has_sequia": True,
        "agrocultura":row["agrocultura"],
        "ganaderia":row["ganaderia"],
        "hidrologia":row["hidrologia"],
        "energia":row["energia"],
        "latitud":row["latitud"],
        "longitud":row["longitud"],
        }   

def _chose_random_row_no_sequia_for_year(paper, year, month)->dict:
    folder = f"data/datasets/clean/{paper}/{year}/{month:02d}/"
    
    # Escoger un dia aleatorio
    days=os.listdir(folder)
    #print(days)
    day_f = random.choice(days)
    
    # Escoger una pagina aleatoria
    folder_day = folder+f"{day_f}/"
    pages=os.listdir(folder_day)
    #print(pages)
    page = random.choice(pages)

    # Sacar pagina y edicion
    #print(f"Elegido {day} pagina {page}"    )
    parts = page.replace(".pdf","").split("_")
    day = int(day_f)
    page_n = int(parts[1])
    ed = None
    if len(parts)>2:
        ed = parts[2]
    #print(f"Elegido {year}-{month:02d}-{day:02d} pagina {page_n} ed {ed}"    )
    res = _search_manual_pdf(paper, year, month, day, page, None,ed)
    if res is not None: 
        return _chose_random_row_no_sequia_for_year(paper, year, month)
    return {
        "peridico": paper,
        "news_date": f"{year}/{month:02d}/{day:02d}",
        "year": year,
        "month": month,
        "day": day,
        "page": page_n,
        "ed": ed,
        "evento":None,
        "event_code":None,
        "ubicacion":None,
        "has_sequia": False,
        "agrocultura":0,
        "ganaderia":0,
        "hidrologia":0,
        "energia":0,
        "latitud":None,
        "longitud":None,
        }
    

def auto_data(start)->list:
    random.seed(42)

    tope = max(dfs["extremadura"]["year.1"].max(), dfs["hoy"]["year.1"].max())
    print (f"Generando datos automaticos desde {start}  hasta  {tope}")

    años = range(int(start), int(tope+1))
    ret = []
    with alive_bar(len(años), title="Building work_ds.csv (auto)") as bar:
        for year in años:
            for paper in ["extremadura", "hoy"]:
                if os.path.exists(f"data/datasets/clean/{paper}/{year}")==False:
                    print (f"No existen datos para {paper} en {year}, saltando")
                    continue
                sequia = _chose_random_row_for_year(paper, year)    
                if sequia is not None:
                    data = sequia
                    ret.append(data)
                    month = int(data["month"])
                else:
                    month = random.randint(1,12)
                no_sequia = _chose_random_row_no_sequia_for_year(paper, year, month)
                ret.append(no_sequia)
                
            bar()
    return ret

def main():
    random.seed(42)
    #print(_chose_random_row_no_sequia_for_year("extremadura", 1923, 9))
    #print(_chose_random_row_no_sequia_for_year("hoy", 1958, 2))
    #exit(0)
    
    #print(_manual_data2dict(pdfs_to_process[16]))
    data = manual_data()

    # Define column names
    #columns = ["peridico", "ano", "mes", "dia", "pagina", "ed", "has_sequia"]

    # Create DataFrame
    df = pd.DataFrame(data)

    auto = auto_data(start=df["year"].max()+1)
    df = pd.concat([df, pd.DataFrame(auto)], ignore_index=True)
    # Save to CSV
    df.to_csv("data/work_ds.csv", index=False)

if __name__ == "__main__":
    main()