import sys
import pandas as pd

tipos_sequia = ["agrocultura","ganaderia","hidrologia","energia"]

def main():
    if len(sys.argv) != 2:
        print("Usage: python 70_get_stats.py <dataset>")
        sys.exit(1)
    dataset = sys.argv[1]
    
    
    detect_ds = pd.read_csv(f"data/datasets/{dataset}_ds/detect/{dataset}_ds.csv")
    print(f"Dataset: {dataset}")
    print(f" Total records: {len(detect_ds)}")
    print(f" Records with drought: {len(detect_ds[detect_ds['has_sequia']==True])}")
    print(f" Records without drought: {len(detect_ds[detect_ds['has_sequia']==False])}")

    classify_ds = pd.read_csv(f"data/datasets/{dataset}_ds/classify/{dataset}_ds.csv")
    print(f"Classify Dataset: {dataset}")
    print(f" Total records: {len(classify_ds)}")
    zero_df = classify_ds[classify_ds[tipos_sequia].sum(axis=1)==0]
    print(f" Records with no drought type classified: {len(zero_df)}")
    for tipo in tipos_sequia:
        print(f" Records with {tipo} drought: {len(classify_ds[classify_ds[tipo]==1])} / {len(classify_ds[classify_ds[tipo]==0])}")


if __name__ == "__main__":
    main()