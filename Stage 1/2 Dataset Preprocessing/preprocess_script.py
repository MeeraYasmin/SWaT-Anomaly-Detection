import pandas as pd
import re
import os

def preprocess_swat_dataset(input_file, output_csv, column_names_csv):
    print(f"Loading {input_file}...")
    # Load the Excel file
    # Note: openpyxl or calamine might be needed for large xlsx files
    df = pd.read_excel(input_file)
    
    # 1. Remove columns which have _STATE
    print("Step 1: Removing _STATE columns...")
    df = df.drop(columns=[col for col in df.columns if '_STATE' in col])
    
    # 2. Remove suffixes .Pv and .Status
    print("Step 2: Removing .Pv and .Status suffixes...")
    df.columns = [col.replace('.Pv', '').replace('.Status', '') for col in df.columns]
    
    # 3. Remove columns which have .Alarm
    print("Step 3: Removing .Alarm columns...")
    df = df.drop(columns=[col for col in df.columns if '.Alarm' in col])
    
    # 4. Add hyphen between last letter and first number
    print("Step 4: Formatting column names (e.g., FIT101 -> FIT-101)...")
    def format_col_name(name):
        # Find the transition from letter to digit
        match = re.search(r'([a-zA-Z])(\d)', name)
        if match:
            # Insert hyphen between the letter and the digit
            return name[:match.start(1)+1] + '-' + name[match.start(2):]
        return name

    df.columns = [format_col_name(col) for col in df.columns]
    
    # 5. Data cleaning: Remove rows with "Bad Input"
    print("Step 5: Cleaning data (removing 'Bad Input')...")
    # We apply this to the whole dataframe. If any cell has "Bad Input", remove the row.
    # Note: We do this BEFORE saving the final CSV to match requested flow but ensure clean data.
    # The prompt says: save as preprocessed_dataset.csv, THEN do data cleaning on preprocessed_dataset.csv
    
    # Save intermediate if strictly following context, but usually better to clean before final save.
    # I'll save it, then reload/clean as instructed.
    df.to_csv(output_csv, index=False)
    print(f"Intermediate saved to {output_csv}")
    
    # Reload to ensure we are cleaning exactly what was saved
    df = pd.read_csv(output_csv)
    
    # Remove rows containing "Bad Input"
    initial_len = len(df)
    df = df[~df.apply(lambda row: row.astype(str).str.contains('Bad Input').any(), axis=1)]
    print(f"Removed {initial_len - len(df)} rows with 'Bad Input'.")
    
    # Final save of preprocessed_dataset.csv
    df.to_csv(output_csv, index=False)
    print(f"Final preprocessed dataset saved to {output_csv}")
    
    # 6. Extract column names
    print(f"Step 6: Saving column names to {column_names_csv}...")
    pd.DataFrame({'Column Names': df.columns}).to_csv(column_names_csv, index=False)
    
    print("Preprocessing complete!")

if __name__ == "__main__":
    input_path = "https://www.kaggle.com/datasets/meera0405/swat-dataset?select=SWaT_Data_100Hrs.xlsx"
    output_path = "https://www.kaggle.com/datasets/meera0405/swat-dataset?select=preprocessed_dataset.csv"
    columns_path = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/blob/main/Stage%201/2%20Dataset%20Preprocessing/column_names.csv"
    
    preprocess_swat_dataset(input_path, output_path, columns_path)
