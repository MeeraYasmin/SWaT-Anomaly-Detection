import sys
import pandas as pd
import os
import re
import csv

# paths
_BASE_DIR = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 5)"
INVARIANTS_XLSX = os.path.join(_BASE_DIR, "6_Invariants_Generation", "invariants_5.xlsx")
DATA_PATH = os.path.join(_BASE_DIR, "3_Graph_Generation", "stage_5_components.csv")

# Output files
OUTPUT_DATASET = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_dataset_5.xlsx")
OUTPUT_TEST_RESULTS = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_results_5.csv")
OUTPUT_COUNT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_count_5.csv")
OUTPUT_WINDOWSIZE = os.path.join(_BASE_DIR, "7_Invariants_Testing", "minimum_windowsize_5.csv")
OUTPUT_STATEMENTS_TXT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_statements_5.txt")
OUTPUT_ANOMALIES = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomalies_5.csv")

def clean_expr(expr):
    """Converts invariant strings to pandas-compatible expressions."""
    # Replace single '=' with '==' (but not '>=', '<=', '!=')
    expr = re.sub(r'(?<![<>!])=(?!=)', '==', expr)
    return expr

def negate_condition(condition):
    """Negates a mathematical condition for anomalies_5.csv."""
    negations = {
        ">": "<=",
        "<": ">=",
        "==": "!=",
        "!=": "==",
        ">=": "<",
        "<=": ">",
        "=": "!="
    }
    # Sort by length to match multi-char operators first
    sorted_ops = sorted(negations.keys(), key=len, reverse=True)
    for op in sorted_ops:
        pattern = rf"\s*{re.escape(op)}\s*"
        if re.search(pattern, condition):
            return re.sub(pattern, f"{negations[op]}", condition)
    return f"not({condition})"

def analyze_invariants():
    if not os.path.exists(INVARIANTS_XLSX):
        print(f"Error: {INVARIANTS_XLSX} not found. Run generate_invariants_5.py first.")
        return

    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        return

    print(f"Loading invariants from {INVARIANTS_XLSX}...")
    inv_df = pd.read_excel(INVARIANTS_XLSX)
    
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # ── Clean Dataframe ───────────────────────────────────────────────────────
    # Rename columns (remove hyphens)
    df.columns = [c.replace("-", "") for c in df.columns]
    
    # Save test_dataset_5.xlsx (original columns + no hyphens)
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
        
        print(f"Checking {inv_id} ({alert_code}): If {antecedent}, then {consequent}...")
        
        try:
            ant_expr = clean_expr(antecedent)
            cons_expr = clean_expr(consequent)
            
            ant_mask = df.eval(ant_expr)
            cons_mask = df.eval(cons_expr)
            
            # Followed: (NOT Antecedent) OR Consequent
            # If followed, value is "yes". If violated (Ant is True, Cons is False), value is "no".
            followed_mask = (~ant_mask) | cons_mask
            output_df[inv_id] = followed_mask.map({True: "yes", False: "no"})
            
            # Stats for count_results
            not_anomaly_count = followed_mask.sum()
            anomaly_count = len(followed_mask) - not_anomaly_count
            
            # Violation: Antecedent is True, but Consequent is False
            violation_mask = ant_mask & (~cons_mask)
            
            # ── Min Window Size calculation ──────────────────────────────────
            # Identify consecutive violation blocks
            if violation_mask.any():
                # group_ids increments every time the mask changes
                group_ids = (violation_mask != violation_mask.shift()).astype(int).cumsum()
                # Consider only violation blocks
                violation_blocks = violation_mask[violation_mask == True]
                # Group by group_ids and count size of each block
                max_consecutive_violations = violation_blocks.groupby(group_ids).count().max()
                min_window = max_consecutive_violations + 1
            else:
                max_consecutive_violations = 0
                min_window = 1
            
            # ── Anomaly Statement formatting ──────────────────────────────────
            neg_cons = negate_condition(consequent)
            sample_text = "sample" if min_window == 1 else "samples"
            # Format: INV#: If [Antecedent], after a window of [minimum_windowsize] samples, if [Negated_Consequent] then it is an anomaly.
            statement = f"INV{idx+1}: If {antecedent}, after a window of {min_window} {sample_text}, if {neg_cons} then it is an anomaly."
            statements_txt.append(statement)
            
            # ── Results storage ───────────────────────────────────────────────
            count_results.append({
                "invariant_number": inv_id,
                "anomaly": anomaly_count,
                "not anomaly": not_anomaly_count
            })
            window_results.append({
                "invariant_number": inv_id,
                "minimum_windowsize": min_window
            })
            
            # ── anomalies_5.csv data ───────────────────────────────────────────
            # Logic: OPEN/RUN implies flow -> OPEN/RUN and no flow implies anomaly
            # Logic: CLOSE/STOP implies no flow -> CLOSE/STOP and flow implies anomaly
            if "implies flow" in comment_base:
                anomaly_comment = comment_base.replace("implies flow", "and no flow") + " implies anomaly"
            elif "implies no flow" in comment_base:
                anomaly_comment = comment_base.replace("implies no flow", "and flow") + " implies anomaly"
            else:
                # default fallback
                anomaly_comment = comment_base.replace("implies", "and no") + " implies anomaly"
            
            anomalies_data.append({
                "Plant stage": 5,
                "Alert Code": alert_code,
                "Antecedent": antecedent,
                "Consequent": neg_cons,
                "Comments": anomaly_comment
            })

        except Exception as e:
            print(f"  Error evaluating {inv_id} ({alert_code}): {e}")
            output_df[inv_id] = "error"

    # ── Save Files ────────────────────────────────────────────────────────────
    print(f"\nFinalizing and saving {len(inv_df)} invariants results...")
    
    output_df.to_csv(OUTPUT_TEST_RESULTS, index=False)
    pd.DataFrame(count_results).to_csv(OUTPUT_COUNT, index=False)
    pd.DataFrame(window_results).to_csv(OUTPUT_WINDOWSIZE, index=False)
    pd.DataFrame(anomalies_data).to_csv(OUTPUT_ANOMALIES, index=False)
    
    with open(OUTPUT_STATEMENTS_TXT, "w") as f:
        f.write("\n".join(statements_txt))

    print("\nSuccessfully generated:")
    print(f" - {OUTPUT_DATASET}")
    print(f" - {OUTPUT_TEST_RESULTS}")
    print(f" - {OUTPUT_COUNT}")
    print(f" - {OUTPUT_WINDOWSIZE}")
    print(f" - {OUTPUT_ANOMALIES}")
    print(f" - {OUTPUT_STATEMENTS_TXT}")

if __name__ == "__main__":
    analyze_invariants()
