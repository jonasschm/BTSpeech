import glob
import sys
import os
import json
import pandas as pd


COLUMNS = ["date", "name", "party", "text"]


def make_df_from(json_file: str) -> pd.DataFrame:
    data = []  # list of rows
    with open(json_file, encoding="utf-8") as fp:
        json_data = json.load(fp)

        for speech in json_data["speeches"]:
            row = [json_data["date"], speech["name"], speech["party"].upper(), speech["text"]]
            data.append(row)

    return pd.DataFrame(data, columns=COLUMNS)


def print_usage():
    print(f"Usage: {sys.argv[0]} <folder_with_jsons> <output_dataset.csv>")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)
    
    input_folder = sys.argv[1]
    if not os.path.isdir(input_folder):
        print(f"No such directory: {input_folder}")
        sys.exit(1)
    
    output_file = sys.argv[2]

    aggregated = pd.DataFrame(columns=COLUMNS)

    for json_file in glob.glob(f"{input_folder}/*.json"):
        print(f"Processing {json_file} ...")
        df = make_df_from(json_file)
        aggregated = pd.concat([aggregated, df])

    aggregated["date"] = pd.to_datetime(aggregated["date"], format="%d.%m.%Y")
    aggregated["party"].replace({"BÜNDNIS 90/DIE GRÜNEN": "GRUENE"}, inplace=True)
    print("Writing dataset to disk ...")
    aggregated.to_csv(output_file, encoding="utf-8")
    print("OK")
