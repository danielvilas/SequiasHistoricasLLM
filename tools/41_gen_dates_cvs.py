#!/usr/bin/env python3
# this script generates the dates.csv from the clean dataset
# calculates the number of files on each date for hoy and extremadura

import os.path

base_path = "data/datasets/clean/"
papers = ["hoy", "extremadura"]

def process_year(paper, year):
    dates = []
    for month in os.listdir(base_path + paper + "/" + year):
        if not os.path.isdir(base_path + paper + "/" + year + "/" + month):
            continue
        for day in os.listdir(base_path + paper + "/" + year + "/" + month):
            if not os.path.isdir(base_path + paper + "/" + year + "/" + month + "/" + day):
                continue
            date = year + "-" + month + "-" + day
            num_files = len(os.listdir(base_path + paper + "/" + year + "/" + month + "/" + day))
            dates.append({"paper": paper, "year":year, "month": month, "day": day, "date": date, "num_files": num_files})
    return dates

def process_paper(paper):
    dates = []
    os.listdir(base_path + paper)
    for file in os.listdir(base_path + paper):
        if  not os.path.isdir(base_path + paper + "/" + file):
            continue
        dates += process_year(paper, file)
    return dates

def main():
    ret = []
    for paper in papers:
        ret += process_paper(paper)
    # write to csv
    with open(f"{base_path}/dates.csv", "w") as f:
        f.write("paper,year,month,day,date,num_files\n")
        for date in ret:
            f.write(date["paper"] + "," + date["year"] + "," + date["month"] + "," + date["day"] + "," + date["date"] + "," + str(date["num_files"]) + "\n")
    pass

if __name__ == "__main__":
    main()