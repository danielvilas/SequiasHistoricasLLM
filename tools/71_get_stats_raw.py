import sys
import pandas as pd

tipos_sequia = ["agrocultura","ganaderia","hidrologia","energia"]

def main():
    if len(sys.argv) != 2:
        print("Usage: python 71_get_stats_raw.py <paper>")
        sys.exit(1)
    paper = sys.argv[1]
    
    
    ds = pd.read_csv(f"data/datasets/clean/{paper}/{paper}_impactos_raw.csv")
    print(f"Dataset: {paper}")
    print(f" Total records: {len(ds)}")
    

    no_impact = ds[ds[tipos_sequia].sum(axis=1)==0]
    print(f" Records with no drought type classified: {len(no_impact)}")    
    for tipo in tipos_sequia:
        print(f" Records with {tipo} drought: {len(ds[ds[tipo]==1])} / {len(ds[ds[tipo]==0])}")
    


if __name__ == "__main__":
    main()