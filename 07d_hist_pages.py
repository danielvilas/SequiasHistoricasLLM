# create an histogram of the number of pages per year
import matplotlib.pyplot as plt
import pandas as pd

def extract_paper(df,paper, st_year, end_year):
    df_paper = df[df["paper"] == paper]

    ret = []
    for year in range(st_year, end_year + 1):
        if year in df_paper["year"].values:
            num_files = df_paper[df_paper["year"] == year]["num_files"].values[0]
        else:
            num_files = 0
        ret.append({"paper": paper, "year": year, "num_files": num_files})
    return pd.DataFrame(ret)

labels = {"hoy":"Hoy", "extremadura":"El Periódico Extremadura"}

def main():
    df = pd.read_csv("data/datasets/clean/dates.csv")
    #print (df.head())
    # group by "paper", "year" and sum "num_files"
    df_grouped = df.groupby(["paper", "year"])["num_files"].sum().reset_index()
    #print (df_grouped.head())

    # create an bar plot of the number of pages per year
    # color by "paper"
    plt.figure(figsize=(10, 6))
    st_year = df_grouped["year"].min()
    end_year = df_grouped["year"].max()
    bottom = [0] * (end_year - st_year + 1)
    
    for i, paper in enumerate(df_grouped["paper"].unique()):
        df_paper = extract_paper(df_grouped, paper, st_year, end_year)
        plt.bar(df_paper["year"], df_paper["num_files"], label=labels.get(paper, paper), bottom=bottom)
        bottom += df_paper["num_files"].values

    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.xlabel("Año")
    plt.ylabel("Número de Páginas")
    plt.title("Número de Páginas por Año")
    plt.legend()
    plt.xticks(rotation=45, ha="right", rotation_mode="anchor")
    plt.tight_layout()
    #plt.show()
    plt.savefig("reports/hist_pages.png")
    

if __name__ == "__main__":
    main()