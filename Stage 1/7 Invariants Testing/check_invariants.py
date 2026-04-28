import sys
import pandas as pd
import os
import re
import csv
import numpy as np

# paths
_BASE_DIR = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 1)"
INVARIANTS_XLSX = os.path.join(_BASE_DIR, "6_Invariants_Generation", "invariants_updated.xlsx")
DATA_PATH = os.path.join(_BASE_DIR, "3_Graph_Generation", "stage_1_components.csv")

OUTPUT_TEST = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_results_updated.csv")
OUTPUT_COUNT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_count.csv")
OUTPUT_WINDOWSIZE = os.path.join(_BASE_DIR, "7_Invariants_Testing", "minimum_windowsize.csv")
OUTPUT_STATEMENTS_TXT = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomaly_statements.txt")
OUTPUT_ANOMALIES = os.path.join(_BASE_DIR, "7_Invariants_Testing", "anomalies.csv")
OUTPUT_DATASET = os.path.join(_BASE_DIR, "7_Invariants_Testing", "test_dataset.xlsx")

def clean_expr(expr):
    """Converts invariant strings to pandas-compatible expressions."""
    # Replace single '=' with '==' (but not '>=', '<=', '!=')
    expr = re.sub(r'(?<![<>!])=(?!=)', '==', expr)
    return expr

def negate_condition(condition):
    """Negates a mathematical condition for anomalies.csv."""
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
        print(f"Error: {INVARIANTS_XLSX} not found. Run generate_invariants.py first.")
        return

    print(f"Loading invariants from {INVARIANTS_XLSX}...")
    inv_df = pd.read_excel(INVARIANTS_XLSX)
    
    print(f"Loading dataset from {DATA_PATH}...")
    full_df = pd.read_csv(DATA_PATH)
    
    # ── Clean Dataframe ───────────────────────────────────────────────────────
    if 'P-102' in full_df.columns:
        full_df = full_df.drop(columns=['P-102'])
    full_df.columns = [c.replace("-", "") for c in full_df.columns]
    
    # Split Dataset 50/50
    split_idx = len(full_df) // 2
    train_df = full_df.iloc[:split_idx].reset_index(drop=True)
    test_df = full_df.iloc[split_idx:].reset_index(drop=True)
    
    print(f"Dataset split: Training ({len(train_df)} rows), Testing ({len(test_df)} rows)")
    
    # Save test_dataset.xlsx (using the test split only as per project flow)
    print(f"Saving testing dataset to {OUTPUT_DATASET}...")
    test_df.to_excel(OUTPUT_DATASET, index=False)
    
    output_df = test_df.copy()
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
        
        print(f"Processing {inv_id} ({alert_code})...")
        
        try:
            ant_expr = clean_expr(antecedent)
            cons_expr = clean_expr(consequent)
            
            # 1. Training Phase: Identify Window Size on train_df
            train_ant = train_df.eval(ant_expr)
            train_cons = train_df.eval(cons_expr)
            train_violation = train_ant & (~train_cons)
            
            if train_violation.any():
                # group consecutive True values
                violation_groups = (train_violation != train_violation.shift()).cumsum()
                max_consecutive = train_violation[train_violation].groupby(violation_groups).count().max()
                min_window = max_consecutive + 1
            else:
                min_window = 1
            
            print(f"  Training window size: {min_window}")
            
            # 2. Testing Phase: Detect Anomalies and False Positives on test_df
            test_ant = test_df.eval(ant_expr)
            test_cons = test_df.eval(cons_expr)
            test_violation = test_ant & (~test_cons)
            
            # Initialize markers
            # "yes" means invariant followed, "no" means true anomaly
            # We'll use a temporary column to track sample-level violation types
            v_type = np.full(len(test_df), "followed", dtype=object)
            
            if test_violation.any():
                # Identify clusters of consecutive violations
                violation_groups = (test_violation != test_violation.shift()).cumsum()
                # Get indices where test_violation is True
                indices = test_violation[test_violation].index
                # Group these indices by their group number
                grouped_violations = test_violation[test_violation].groupby(violation_groups)
                
                for group_id, group in grouped_violations:
                    v_indices = group.index
                    duration = len(v_indices)
                    
                    if duration > (min_window - 1):
                        # All samples in this block are part of an anomalous event
                        # But typically, only samples EXCEEDING the window are "Anomalies"
                        # whereas those within the window are "False Positives" (Normal delay)
                        
                        # First (min_window - 1) samples are False Positives
                        fp_count = min(len(v_indices), min_window - 1)
                        v_type[v_indices[:fp_count]] = "false_positive"
                        
                        # Samples from min_window onwards are True Anomalies
                        if len(v_indices) > (min_window - 1):
                            v_type[v_indices[fp_count:]] = "anomaly"
                    else:
                        # Event is shorter than window -> all samples are False Positives
                        v_type[v_indices] = "false_positive"
            
            # Map to output format: followed or false_positive -> "yes", anomaly -> "no"
            output_df[inv_id] = "yes"
            output_df.loc[v_type == "anomaly", inv_id] = "no"
            
            # Stats
            true_anomaly_count = (v_type == "anomaly").sum()
            false_positive_count = (v_type == "false_positive").sum()
            followed_count = (v_type == "followed").sum()
            not_anomaly_count = followed_count + false_positive_count
            
            # Anomaly Statement
            neg_cons = negate_condition(consequent)
            sample_text = "sample" if min_window == 1 else "samples"
            statement = f"INV{idx+1}: If {antecedent}, after a window of {min_window} {sample_text}, if {neg_cons} then it is an anomaly."
            statements_txt.append(statement)
            
            count_results.append({
                "invariant_number": inv_id,
                "anomaly": true_anomaly_count,
                "not anomaly": followed_count,
                "False Positives": false_positive_count
            })
            window_results.append({
                "invariant_number": inv_id,
                "minimum_windowsize": min_window
            })
            
            # anomalies.csv row
            anomaly_comment = comment_base.replace("implies", "and no") + " implies anomaly"
            if "no flow" in comment_base:
                 anomaly_comment = comment_base.replace("implies no", "and") + " implies anomaly"
            
            anomalies_data.append({
                "Plant stage": 1,
                "Alert Code": alert_code,
                "Antecedent": antecedent,
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

    print("Done. Generated files in Stage 1 testing folder.")

if __name__ == "__main__":
    analyze_invariants()
