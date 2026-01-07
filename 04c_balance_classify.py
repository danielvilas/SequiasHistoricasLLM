import pandas as pd

classes = ['has_sequia', 'agrocultura', 'ganaderia', 'hidrologia', 'energia']

def print_class_distribution(df):
    total = len(df)
    print(f"Total samples: {total}")
    for cls in classes:
        if cls not in df.columns:
            print(f"Class '{cls}' not found in DataFrame columns.")
            continue
        count = len(df[df[cls] == 1])
        percentage = (count / total) * 100
        print(f"Class '{cls}': {count} samples ({percentage:.2f}%)")

def print_additional_info(paper):
    print(f"\nClass distribution for paper: {paper}")
    paper_df = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_clean.csv")
    paper_df = paper_df[paper_df['hash_matches']==True] # solo los que tengamos informacion
    print_class_distribution(paper_df)
    return paper_df[paper_df['energia']==1]

def convert_row_to_dict(paper,row):
        return {
        "peridico": paper,
        "news_date": row["news_date"],
        "year": row["year"],
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

def main():
    clasify_df = pd.read_csv("data/datasets/work_ds/classify/work_ds.csv")
    if len(clasify_df[clasify_df['energia']==1])>=1:
        print ("Already with energia class")
        return
    
    print_class_distribution(clasify_df)
    ext_df = print_additional_info("extremadura")
    hoy_df = print_additional_info("hoy")

    ret = []
    for _, row in ext_df.iterrows():
        ret.append(convert_row_to_dict("extremadura",row))
    for _, row in hoy_df.iterrows():
        ret.append(convert_row_to_dict("hoy",row))
    balanced_df = pd.DataFrame(ret)
    print("\nBalanced DataFrame class distribution:")
    print_class_distribution(balanced_df)

    balanced_df.to_csv("data/classify_extra.csv", index=False)

    pass

if __name__ == "__main__":
    main()