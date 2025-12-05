from sequias_historicas.PagesManager import PagesManager
import os

extremadura = PagesManager(paper="extremadura")
hoy = PagesManager(paper="hoy")

def main():

    #print(extremadura._extract_page_info(["Extremadura-estacional/Verano 1923/P.diarios_verano1923/19230621.pdf", "1", "hash1"]))
    if not os.path.exists(f"{extremadura.clean_path}/{extremadura.paper}/{extremadura.paper}_pages_clean.csv"):
        extremadura.fill_page_locations()
        print (extremadura.df_pages.head())
        extremadura.save_pages_df()
    else:
        print(f"{extremadura.paper}_pages_clean.csv already exists.")
    if not os.path.exists(f"{hoy.clean_path}/{hoy.paper}/{hoy.paper}_pages_clean.csv"):
        hoy.fill_page_locations()
        print (hoy.df_pages.head())
        hoy.save_pages_df()
    else:
        print(f"{hoy.paper}_pages_clean.csv already exists.")
    #

if __name__ == "__main__":
    main()