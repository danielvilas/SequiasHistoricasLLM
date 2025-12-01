import os
import json

from sequias_historicas.PdfManager import PdfManager

pdfs_to_process = [
    #peridico,ano,mes,dia,pagina,ed
    ("hoy",1933,3,5,1,"BAD"),  # portada
    ("hoy",1933,3,5,5,"BAD"), # 6 Columnas,
    ("hoy",1933,9,3,6,"BAD"), # Sequia

]

pdf_manager = PdfManager()



def main():
    os.makedirs("data/datasets/json_test/PDF", exist_ok=True)
    os.makedirs("data/datasets/json_test/json", exist_ok=True)
    for pdf in pdfs_to_process:
        paper, year, month, day, page, ed = pdf
        
        text,filepath = pdf_manager.extract_text(paper, year, month, day, page, ed)
        print(f"Text from {paper} {year}-{month}-{day} page {page} ed {ed}\n({filepath}):\n{text[0:min(25,len(text))]}\n{'-'*40}\n")
        
        outfile=f"data/datasets/json_test/PDF/{paper}_{year}_{month}_{day}_page_{page}"
        if ed:
            outfile+=f"_{ed}"
        outfile+=f".pdf"
        #copy filepath to outfile
        os.system(f"cp '{filepath}' '{outfile}'")
        print(f"Copied PDF to {outfile}\n{'-'*40}\n")
        json_data ={"@context": "https://schema.org/"
                    "@type":"NewsArticle",
                    "headline":f"{paper} {year}-{month}-{day} page {page}",
                    "articleBody":text,
                    "datePublished":f"{year:04}-{month:02}-{day:02}T00:00:00+01:00",
                    "mainEntityOfPage":"https://not-existent.example.com/",
                
                    }
        json_outfile=f"data/datasets/json_test/json/{paper}_{year}_{month}_{day}_page_{page}"
        if ed:
            json_outfile+=f"_{ed}"
        json_outfile+=f".json"
        with open (json_outfile,"w",encoding="utf-8") as f:
            
            json.dump(json_data,f,ensure_ascii=False,indent=4)
        print(f"Wrote JSON to {json_outfile}\n{'-'*40}\n")
    pass

if __name__ == "__main__":
    main()
