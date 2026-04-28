import sys
import pandas as pd
import os
import re
import csv

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE_DIR = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 6)\Project_Steps (Stage 6_1)"
INVARIANTS_XLSX = os.path.join(_BASE_DIR, "6_Invariants_Generation", "invariants_6_1.xlsx")
DATA_PATH = os.path.join(_BASE_DIR, "3_Graph_Generation", "stage_6_components_1.csv")

OUTPUT_TEST = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_results_6_1.csv")
OUTPUT_COUNT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_count_6_1.csv")
OUTPUT_WINDOWSIZE = os.path.join(_BASE_DIR, "7_Invariants_Testing", "minimum_windowsize_6_1.csv")
OUTPUT_STATEMENTS_TXT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_statements_6_1.txt")
OUTPUT_ANOMALIES = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomalies_6_1.csv")
OUTPUT_DATASET = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_dataset_6_1.xlsx")

def clean_expr(expr):
    """Converts invariant strings to pandas-compatible expressions."""
    # Replace single '=' with '==' (but not '>=', '<=', '!=')
    expr = re.sub(r'(?<![<>!])=(?!=)', '==', expr)
    return expr

def negate_condition(condition):
    """Negates a mathematical condition for anomalies.csv and anomaly statements."""
    negations = {
        ">": "<=",
        "<": ">=",
        "==": "!=",
        "!=": "==",
        ">=": "<",
        "<=": ">",
        "=": "!="
    }
    # Sort by length to match multi-character ops first (e.g. <= before <)
    sorted_ops = sorted(negations.keys(), key=len, reverse=True)
    for op in sorted_ops:
        # Use regex to match the operator and replace it
        pattern = rf"\s*{re.escape(op)}\s*"
        if re.search(pattern, condition):
            return re.sub(pattern, f"{negations[op]}", condition)
    return f"not({condition})"

def transform_comment(comment):
    """Transforms a base invariant comment into an anomaly comment."""
    # Example: "P601 RUN implies flow on FIT602" -> "P601 RUN and no flow on FIT602 implies anomaly"
    if "implies flow on" in comment:
        return comment.replace("implies flow on", "and no flow on") + " implies anomaly"
    elif "implies no flow on" in comment:
        return comment.replace("implies no flow on", "and flow on") + " implies anomaly"
    elif "implies" in comment:
        # For LIT or other comparisons
        # "P601 RUN implies LIT601 > 200" -> "P601 RUN and LIT601 <= 200 implies anomaly"
        parts = comment.split(" implies ")
        antecedent_part = parts[0]
        consequent_part = parts[1]
        neg_consequent_part = negate_condition(consequent_part)
        return f"{antecedent_part} and {neg_consequent_part} implies anomaly"
    return f"{comment} implies anomaly"

def analyze_invariants():
    if not os.path.exists(INVARIANTS_XLSX):
        print(f"Error: {INVARIANTS_XLSX} not found. Run generate_invariants_6_1.py first.")
        return
    if not os.path.exists(DATA_PATH):
         print(f"Error: {DATA_PATH} not found.")
         return

    print(f"Loading invariants from {INVARIANTS_XLSX}...")
    inv_df = pd.read_excel(INVARIANTS_XLSX)
    
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # rename columns (remove hyphens)
    original_cols = df.columns
    df.columns = [c.replace("-", "") for c in df.columns]
    
    # Save test_dataset_6_1.xlsx (cleaned input data, no invariant columns)
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
        comment_base = str(row["Comments"])
        
        print(f"Checking {inv_id} ({alert_code}): If {antecedent}, then {consequent}...")
        
        try:
            ant_expr = clean_expr(antecedent)
            cons_expr = clean_expr(consequent)
            
            # Evaluate masks
            ant_mask = df.eval(ant_expr)
            cons_mask = df.eval(cons_expr)
            
            # Followed logic: (NOT Antecedent) OR (Consequent)
            followed_mask = (~ant_mask) | cons_mask
            output_df[inv_id] = followed_mask.map({True: "yes", False: "no"})
            
            # Violation Counts
            not_anomaly_count = followed_mask.sum()
            anomaly_count = len(followed_mask) - not_anomaly_count
            
            # Calculate minimum_windowsize (max consecutive violations + 1)
            violation_mask = ant_mask & (~cons_mask)
            if violation_mask.any():
                # Group consecutive True values
                violation_groups = (violation_mask != violation_mask.shift()).astype(int).cumsum()
                max_consecutive = violation_mask[violation_mask == True].groupby(violation_groups).count().max()
                min_window = max_consecutive + 1
            else:
                min_window = 1
            
            # Negated Consequent for anomalies.csv and anomaly statements
            neg_cons = negate_condition(consequent)
            
            # Anomaly Statement
            sample_text = "sample" if int(min_window) == 1 else "samples"
            statement = f"INV{idx+1}: If {antecedent}, after a window of {int(min_window)} {sample_text}, if {neg_cons} then it is an anomaly."
            statements_txt.append(statement)
            
            # stats for anomaly_count_6_1.csv
            count_results.append({
                "invariant_number": inv_id,
                "anomaly": anomaly_count,
                "not anomaly": not_anomaly_count
            })
            
            # stats for minimum_windowsize_6_1.csv
            window_results.append({
                "invariant_number": inv_id,
                "minimum_windowsize": int(min_window)
            })
            
            # anomalies_6_1.csv row
            anomalies_data.append({
                "Plant stage": 6,
                "Alert Code": alert_code,
                "Antecedent": antecedent,
                "Consequent": neg_cons,
                "Comments": transform_comment(comment_base)
            })

        except Exception as e:
            print(f"  Error evaluating {inv_id}: {e}")
            output_df[inv_id] = "error"

    # ── Save Results ──────────────────────────────────────────────────────────
    print(f"\nFinalizing and saving results...")
    output_df.to_csv(OUTPUT_TEST, index=False)
    pd.DataFrame(count_results).to_csv(OUTPUT_COUNT, index=False)
    pd.DataFrame(window_results, columns=["invariant_number", "minimum_windowsize"]).to_csv(OUTPUT_WINDOWSIZE, index=False)
    pd.DataFrame(anomalies_data).to_csv(OUTPUT_ANOMALIES, index=False)
    
    with open(OUTPUT_STATEMENTS_TXT, "w") as f:
        f.write("\n".join(statements_txt))

    print(f"Done. {len(inv_df)} invariants analyzed.")
    print(f" - {OUTPUT_DATASET}")
    print(f" - {OUTPUT_TEST}")
    print(f" - {OUTPUT_COUNT}")
    print(f" - {OUTPUT_WINDOWSIZE}")
    print(f" - {OUTPUT_ANOMALIES}")
    print(f" - {OUTPUT_STATEMENTS_TXT}")

if __name__ == "__main__":
    analyze_invariants()
