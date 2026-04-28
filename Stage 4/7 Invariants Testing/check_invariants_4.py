import sys
import pandas as pd
import os
import re
import csv

# paths
_BASE_DIR = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 4)"
INVARIANTS_XLSX = os.path.join(_BASE_DIR, "6_Invariants_Generation", "invariants_4_updated.xlsx")
DATA_PATH = os.path.join(_BASE_DIR, "3_Graph_Generation", "stage_4_components.csv")

OUTPUT_TEST = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_results_4.csv")
OUTPUT_COUNT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_count_4.csv")
OUTPUT_WINDOWSIZE = os.path.join(_BASE_DIR, "7_Invariants_Testing", "minimum_windowsize_4.csv")
OUTPUT_STATEMENTS_TXT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_statements_4.txt")
OUTPUT_ANOMALIES = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomalies_4.csv")
OUTPUT_DATASET = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_dataset_4.xlsx")

def clean_expr(expr):
    """Converts invariant strings to pandas-compatible expressions."""
    # Strip prefix like "after windowSize seconds, " or "after windowSize, "
    expr = re.sub(r'^after windowSize( seconds)?,?\s*', '', str(expr), flags=re.IGNORECASE)
    # Replace single '=' with '==' (but not '>=', '<=', '!=')
    expr = re.sub(r'(?<![<>!])=(?!=)', '==', expr)
    return expr

def negate_condition(condition):
    """Negates a mathematical condition for anomalies_3.csv."""
    negations = {
        ">": "<=",
        "<": ">=",
        "==": "!=",
        "!=": "==",
        ">=": "<",
        "<=": ">",
        "=": "!="
    }
    sorted_ops = sorted(negations.keys(), key=len, reverse=True)
    for op in sorted_ops:
        pattern = rf"\s*{re.escape(op)}\s*"
        if re.search(pattern, condition):
            return re.sub(pattern, f"{negations[op]}", condition)
    return f"not({condition})"

def analyze_invariants():
    if not os.path.exists(INVARIANTS_XLSX):
        print(f"Error: {INVARIANTS_XLSX} not found. Run generate_invariants_3.py first.")
        return

    print(f"Loading invariants from {INVARIANTS_XLSX}...")
    inv_df = pd.read_excel(INVARIANTS_XLSX)
    
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # ── Clean Dataframe ───────────────────────────────────────────────────────
    # 1. Rename columns (remove hyphens)
    df.columns = [c.replace("-", "") for c in df.columns]
    
    # Save test_dataset_3.xlsx (cleaned input data, no invariant columns)
    print(f"Saving cleaned dataset to {OUTPUT_DATASET}...")
    df.to_excel(OUTPUT_DATASET, index=False)
    
    output_df = df.copy()
    count_results = []
    window_results = []
    anomalies_data = []
    statements_txt = []

    for idx, row in inv_df.iterrows():
        inv_id = f"invariant_{idx+1}"
        alert_code = row["Alert Code"]
        antecedent = row["Antecedent"]
        consequent = row["Consequent"]
        comment_base = row["Comments"]
        
        # Clean strings for reports
        clean_ant = re.sub(r'^after windowSize( seconds)?,?\s*', '', str(antecedent), flags=re.IGNORECASE)
        clean_cons = re.sub(r'^after windowSize( seconds)?,?\s*', '', str(consequent), flags=re.IGNORECASE)
        
        print(f"Checking {inv_id} ({alert_code}): If {clean_ant}, then {clean_cons}...")
        
        try:
            ant_expr = clean_expr(clean_ant)
            cons_expr = clean_expr(clean_cons)
            
            ant_mask = df.eval(ant_expr)
            cons_mask = df.eval(cons_expr)
            
            # Followed: (NOT Antecedent) OR Consequent
            followed_mask = (~ant_mask) | cons_mask
            output_df[inv_id] = followed_mask.map({True: "yes", False: "no"})
            
            # Stats
            not_anomaly_count = followed_mask.sum()
            anomaly_count = len(followed_mask) - not_anomaly_count
            
            # Min window size (consecutive violations)
            violation_mask = ant_mask & (~cons_mask)
            if violation_mask.any():
                group_ids = (violation_mask != violation_mask.shift()).astype(int).cumsum()
                max_consecutive = violation_mask[violation_mask == True].groupby(group_ids).count().max()
                min_window = max_consecutive + 1
            else:
                min_window = 1
            
            # Anomaly Statement
            neg_cons = negate_condition(clean_cons)
            sample_text = "sample" if min_window == 1 else "samples"
            statement = f"INV{idx+1}: If {clean_ant}, after a window of {min_window} {sample_text}, if {neg_cons} then it is an anomaly."
            
            statements_txt.append(statement)
            
            count_results.append({
                "invariant_number": inv_id,
                "anomaly": anomaly_count,
                "not anomaly": not_anomaly_count
            })
            window_results.append({
                "invariant_number": inv_id,
                "minimum_windowsize": min_window
            })
            
            # anomalies_4.csv row
            # Format: [Antecedent] and no [Consequent/Flow] implies anomaly
            anomaly_comment = comment_base.replace("implies", "and no") + " implies anomaly"
            if "no flow" in comment_base:
                 anomaly_comment = comment_base.replace("implies no", "and") + " implies anomaly"
            
            anomalies_data.append({
                "Plant stage": 4,
                "Alert Code": alert_code,
                "Antecedent": clean_ant,
                "Consequent": neg_cons,
                "Comments": anomaly_comment
            })

        except Exception as e:
            print(f"  Error evaluating {inv_id}: {e}")
            output_df[inv_id] = "error"

    # ── Save Files ────────────────────────────────────────────────────────────
    print(f"\nSaving results...")
    output_df.to_csv(OUTPUT_TEST, index=False)
    pd.DataFrame(count_results).to_csv(OUTPUT_COUNT, index=False)
    pd.DataFrame(window_results).to_csv(OUTPUT_WINDOWSIZE, index=False)
    pd.DataFrame(anomalies_data).to_csv(OUTPUT_ANOMALIES, index=False)
    
    with open(OUTPUT_STATEMENTS_TXT, "w") as f:
        f.write("\n".join(statements_txt))

    print("Done. Generated:")
    print(f" - {OUTPUT_DATASET}")
    print(f" - {OUTPUT_TEST}")
    print(f" - {OUTPUT_COUNT}")
    print(f" - {OUTPUT_WINDOWSIZE}")
    print(f" - {OUTPUT_ANOMALIES}")
    print(f" - {OUTPUT_STATEMENTS_TXT}")

if __name__ == "__main__":
    analyze_invariants()
