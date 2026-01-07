import os
import json

from sequias_historicas.PdfManager import PdfManager

import sys

pdfs_to_process = [
    #periodico,ano,mes,dia,pagina,ed
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
    ("hoy",1933,9,3,6,"BAD", True), # Sequia
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

pdf_manager = PdfManager()



def main():

    if len(sys.argv) == 2:
        limit = int(sys.argv[1])
        pdfs_to_process_subset = pdfs_to_process[:limit]
    else:
        pdfs_to_process_subset = pdfs_to_process

    os.makedirs("data/datasets/json_test/PDF", exist_ok=True)
    os.makedirs("data/datasets/json_test/json", exist_ok=True)
    for pdf in pdfs_to_process_subset:
        paper, year, month, day, page, ed, flag = pdf
        
        text,filepath = pdf_manager.extract_text(paper, year, month, day, page, ed)
        print(f"Text from {paper} {year}-{month}-{day} page {page} ed {ed}\n({filepath}):\n{text[0:min(25,len(text))]}\n{'-'*40}\n")
        
        outfile=f"data/datasets/json_test/PDF/{paper}_{year}_{month}_{day}_page_{page}"
        if ed:
            outfile+=f"_{ed}"
        outfile+=f".pdf"
        #copy filepath to outfile
        os.system(f"cp '{filepath}' '{outfile}'")
        print(f"Copied PDF to {outfile}\n{'-'*40}\n")
        date_pub = day
        if date_pub==0:
            date_pub=15
        json_data ={"@context": "https://schema.org/",
                    "@type":"NewsArticle",
                    "headline":f"{paper} {year}-{month}-{day} page {page}",
                    "articleBody":text,
                    "datePublished":f"{year:04}-{month:02}-{date_pub:02}T00:00:00+01:00",
                    "mainEntityOfPage":{"@id":"https://not-existent.example.com/"},
                
                    }
        json_outfile=f"data/datasets/json_test/json/{paper}_{year}_{month}_{day}_page_{page}"
        if ed:
            json_outfile+=f"_{ed}"
        json_outfile+=f".json"
        with open (json_outfile,"w",encoding="utf-8") as f:
            
            json.dump(json_data,f,ensure_ascii=False,indent=4)
        print(f"Wrote JSON to {json_outfile}\n{'-'*40}\n")
    # gravamos un csv con los ficheros
    with open("data/datasets/json_test/file_list.csv","w",encoding="utf-8") as f:
        f.write("pdf_file,json_file,drought\n")
        for pdf in pdfs_to_process:
            paper, year, month, day, page, ed, flag = pdf
            pdf_file=f"{paper}_{year}_{month}_{day}_page_{page}"
            if ed:
                pdf_file+=f"_{ed}"
            pdf_file+=f".pdf"
            json_file=f"{paper}_{year}_{month}_{day}_page_{page}"
            if ed:
                json_file+=f"_{ed}"
            json_file+=f".json"
            f.write(f"{pdf_file},{json_file},{flag}\n")

if __name__ == "__main__":
    main()
