import pandas as pd
import re
import os
import kaggle


def preprocess_swat_dataset(input_file, output_csv, column_names_csv):
    print(f"Loading {input_file}...")

    # Load Excel
    df = pd.read_excel(input_file)

    # 1. Remove columns which have _STATE
    print("Step 1: Removing _STATE columns...")
    df = df.drop(columns=[col for col in df.columns if '_STATE' in col])

    # 2. Remove suffixes .Pv and .Status
    print("Step 2: Cleaning suffixes...")
    df.columns = [col.replace('.Pv', '').replace('.Status', '') for col in df.columns]

    # 3. Remove .Alarm columns
    print("Step 3: Removing .Alarm columns...")
    df = df.drop(columns=[col for col in df.columns if '.Alarm' in col])

    # 4. Format column names
    print("Step 4: Formatting column names...")
    def format_col_name(name):
        match = re.search(r'([a-zA-Z])(\d)', name)
        if match:
            return name[:match.start(1)+1] + '-' + name[match.start(2):]
        return name

    df.columns = [format_col_name(col) for col in df.columns]

    # 5. Save intermediate
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Intermediate saved to {output_csv}")

    # Reload and clean
    df = pd.read_csv(output_csv)

    print("Step 5: Removing 'Bad Input' rows...")
    initial_len = len(df)
    df = df[~df.apply(lambda row: row.astype(str).str.contains('Bad Input').any(), axis=1)]
    print(f"Removed {initial_len - len(df)} rows.")

    # Final save
    df.to_csv(output_csv, index=False)
    print(f"Final dataset saved to {output_csv}")

    # 6. Save column names
    print("Step 6: Saving column names...")
    os.makedirs(os.path.dirname(column_names_csv), exist_ok=True)
    pd.DataFrame({'Column Names': df.columns}).to_csv(column_names_csv, index=False)

    print("Preprocessing complete!")


if __name__ == "__main__":

    #  Download dataset from Kaggle
    kaggle.api.dataset_download_files(
        "meera0405/swat-dataset",
        path="data/",
        unzip=True
    )

    #  Correct LOCAL paths
    input_path = "data/SWaT_Data_100Hrs.xlsx"
    output_path = "data/preprocessed_dataset.csv"
    columns_path = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/blob/main/Stage%205/2%20Dataset%20Preprocessing/column_names.csv"
    
    preprocess_swat_dataset(input_path, output_path, columns_path)
