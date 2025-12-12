import sys
import os
from subprocess import Popen
import pandas as pd
import json

base_path = "./tests"

def get_tests(ds_path):
    folders = os.listdir(f'{base_path}/{ds_path}/')
    folders = [f for f in folders if os.path.isdir(os.path.join(f'{base_path}/{ds_path}/', f))]
    return folders

def merge_csv(ds_1, ds_2, test, output,file):
    # read ds1/test/file and ds2/test/file
    
    df1 = pd.read_csv(f"{base_path}/{ds_1}/{test}/{file}")
    df2 = pd.read_csv(f"{base_path}/{ds_2}/{test}/{file}")
    # concatenate dataframes
    merged_df = pd.concat([df1, df2])
    # write to output/test/file
    merged_df.to_csv(f"{base_path}/{output}/{test}/{file}", index=False)
    
    pass

def merge_ciena_json(ds_1, ds_2, test, file, output):
    # read ds1/test/file and ds2/test/file
    with open(f"{base_path}/{ds_1}/{test}/{file}", 'r') as f:
        data1 = json.load(f)
    with open(f"{base_path}/{ds_2}/{test}/{file}", 'r') as f:
        data2 = json.load(f)
    # merge json data
    merged_data = {"total":data1["total"] + data2["total"]
                   }
    for base in data1.keys():
        if base == "total":
            continue
        merged_data[base] = {"total":data1[base]["total"] + data2[base]["total"]}
        for key in data1[base]:
            if key != "total":
                dict_ = {}
                dict_.update(data1[base][key])
                dict_.update(data2[base][key])
                merged_data[base][key] = dict_
    # write to output/test/file
    with open(f"{base_path}/{output}/{test}/{file}", 'w') as f:
        json.dump(merged_data, f, indent=4)

    pass

def merge(ds_1, ds_2, test, output):
    #print(f"Merging test {test} from {ds_1} and {ds_2} into {output}")
    #copy ciena_config.yaml from ds_1 to output
    cmd = f"cp {base_path}/{ds_1}/{test}/ciena_config.yaml {base_path}/{output}/{test}/ciena_config.yaml"
    process = Popen(cmd, shell=True)
    process.wait()
    #merge summary.csv
    merge_csv(ds_1, ds_2, test, output,"summary.csv")
    #merge excluded_problematic_articles.csv
    merge_csv(ds_1, ds_2, test, output,"excluded_problematic_articles.csv")
    #merge execution_times.json
    merge_ciena_json(ds_1, ds_2, test,"execution_times.json", output) 
    #merge parsing_errors.json
    merge_ciena_json(ds_1, ds_2, test,"parsing_errors.json", output)

    pass

def copy_test(ds, test, output):
    #execute copy command
    cmd = f"cp -a {base_path}/{ds}/{test}/* {base_path}/{output}/{test}/."
    process = Popen(cmd, shell=True)
    process.wait()
    pass

def join_tests(ds_1, ds_2,test,output):
    # Placeholder for the actual joining logic
    print(f"Joining test {test} from {ds_1} and {ds_2} into {output}")
    if not os.path.exists(f"{base_path}/{output}/{test}"):
        os.makedirs(f"{base_path}/{output}/{test}")
    if not os.path.exists(f"{base_path}/{ds_1}/{test}/summary.csv") and not os.path.exists(f"{base_path}/{ds_2}/{test}/summary.csv"):
        print(f"Summary file missing for test {test}. Skipping.")
        return
    if not os.path.exists(f"{base_path}/{ds_1}/{test}/summary.csv"):
        print(f"Summary file missing for ds {ds_1}.")
        copy_test(ds_2, test, output)
        return
    if not os.path.exists(f"{base_path}/{ds_2}/{test}/summary.csv"):
        print(f"Summary file missing for ds {ds_2}.")
        copy_test(ds_1, test, output)
        return
    merge(ds_1, ds_2, test, output)

def main():
    if len(sys.argv) != 4:
        print("Usage: python 96_join_ciena.py <ds_1> <ds_2> <output>")
        sys.exit(1)
    ds_1 = sys.argv[1]
    ds_2 = sys.argv[2]
    output = sys.argv[3]
    tests_1 = get_tests(ds_1)
    tests_2 = get_tests(ds_2)
    all_tests = set(tests_1).union(set(tests_2))
    print(f"All tests to process: {all_tests}")
    for test in all_tests:
        join_tests(ds_1, ds_2, test, output)
if __name__ == "__main__":
    main()
