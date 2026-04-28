import csv
import sys
import os
import pandas as pd

# ── Import threshold functions from compute_thresholds_5.py ───────────────────
_COMPUTE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "5_Computation"
)
sys.path.insert(0, os.path.abspath(_COMPUTE_DIR))

try:
    from compute_thresholds_5 import (
        compute_min1, compute_max1, 
        compute_min2, compute_max2, 
        compute_min3, compute_max3
    )
except ImportError:
    print("Warning: Could not import compute_thresholds_5. Ensure the file exists.")

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 5)"
CSV_PATH = os.path.join(_BASE, "3_Graph_Generation", "stage_5_components.csv")
TEMPLATES_PATH = os.path.join(_BASE, "4_Templates_Generation", "templates_5.csv")
CONNECTIONS_PATH = os.path.join(_BASE, "3_Graph_Generation", "connections_5.csv")

# ── Threshold Mapping ─────────────────────────────────────────────────────────
_THRESHOLDS_CACHE = {}

def get_fit_thresholds(tag):
    """
    Calculates Tmin and Tmax for a specific FIT tag in Stage 5.
    FIT-501 -> compute_min1 / compute_max1 (Tmin1 / Tmax1)
    FIT-502 -> compute_min2 / compute_max2 (Tmin2 / Tmax2)
    FIT-503 -> compute_min3 / compute_max3 (Tmin3 / Tmax3)
    """
    if tag in _THRESHOLDS_CACHE:
        return _THRESHOLDS_CACHE[tag]
    
    try:
        df = pd.read_csv(CSV_PATH)
        if tag in df.columns:
            fit_max = df[tag].max()
            if tag == "FIT-501":
                tmin = compute_min1(fit_max)
                tmax = compute_max1(fit_max)
            elif tag == "FIT-502":
                tmin = compute_min2(fit_max)
                tmax = compute_max2(fit_max)
            elif tag == "FIT-503":
                tmin = compute_min3(fit_max)
                tmax = compute_max3(fit_max)
            else:
                tmin, tmax = 0.0, 0.0
            
            _THRESHOLDS_CACHE[tag] = (tmin, tmax)
            return tmin, tmax
    except Exception as e:
        print(f"Warning: Could not compute thresholds for {tag}: {e}")
    
    return 0.0, 0.0

def get_type(tag):
    """Maps a physical tag (e.g., FIT-501) to its generic type (FIT)."""
    for t in ["FIT", "LIT", "MV", "P"]:
        if tag.startswith(t):
            return t
    return None

# ── Invariant generator ───────────────────────────────────────────────────────
def generate_instance_invariants(templates_path: str, connections_path: str) -> list[dict]:
    """
    Constructs instance-specific invariants.
    Returns a list of dictionaries with columns for invariants_5.xlsx.
    """
    templates = set()
    with open(templates_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            templates.add((row["Source"].strip(), row["Destination"].strip()))

    connections = []
    with open(connections_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            connections.append((row["source"].strip(), row["destination"].strip()))

    rows = []
    ws = "after windowSize seconds"

    for src_inst, dst_inst in connections:
        src_type = get_type(src_inst)
        dst_type = get_type(dst_inst)

        if (src_type, dst_type) in templates:
            # Stage 5 specific rules mapped by (src_type, dst_type)
            _append_rows(rows, src_inst, src_type, dst_inst, dst_type, ws)

    return rows

def _append_rows(rows, src, src_type, dst, dst_type, ws):
    """
    Helper to generate specific rows based on Stage 5 type pairs.
    """
    # Helper to remove hyphens
    clean = lambda s: s.replace("-", "")
    
    # Terminology based on type
    def get_terms(tag_type):
        if tag_type == "MV":
            return "OPEN", "CLOSE"
        else: # P
            return "RUN", "STOP"

    # ── FIT -> P ──────────────────────────────────────────────────────────────
    if src_type == "FIT" and dst_type == "P":
        tmin, tmax = get_fit_thresholds(src)
        on_term, off_term = get_terms(dst_type)
        # Rule: If P = Run (2), then FIT > Tmin
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(dst)}=2",
            "Consequent": f"{clean(src)}>{tmin:.6f}",
            "Comments": f"{clean(dst)} {on_term} implies flow on {clean(src)}"
        })
        # Rule: If P = Stop (1), then FIT < Tmax
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(dst)}=1",
            "Consequent": f"{clean(src)}<{tmax:.6f}",
            "Comments": f"{clean(dst)} {off_term} implies no flow on {clean(src)}"
        })

    # ── FIT -> MV ─────────────────────────────────────────────────────────────
    elif src_type == "FIT" and dst_type == "MV":
        tmin, tmax = get_fit_thresholds(src)
        on_term, off_term = get_terms(dst_type)
        # Rule: If MV = Open (2), then FIT > Tmin
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(dst)}=2",
            "Consequent": f"{clean(src)}>{tmin:.6f}",
            "Comments": f"{clean(dst)} {on_term} implies flow on {clean(src)}"
        })
        # Rule: If MV = Close (1), then FIT < Tmax
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(dst)}=1",
            "Consequent": f"{clean(src)}<{tmax:.6f}",
            "Comments": f"{clean(dst)} {off_term} implies no flow on {clean(src)}"
        })

    # ── P -> FIT ──────────────────────────────────────────────────────────────
    elif src_type == "P" and dst_type == "FIT":
        tmin, tmax = get_fit_thresholds(dst)
        on_term, off_term = get_terms(src_type)
        # Rule: If P = Run (2), then FIT > Tmin
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(src)}=2",
            "Consequent": f"{clean(dst)}>{tmin:.6f}",
            "Comments": f"{clean(src)} {on_term} implies flow on {clean(dst)}"
        })
        # Rule: If P = Stop (1), then FIT < Tmax
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(src)}=1",
            "Consequent": f"{clean(dst)}<{tmax:.6f}",
            "Comments": f"{clean(src)} {off_term} implies no flow on {clean(dst)}"
        })

    # ── MV -> FIT (Standard logic, though not in Stage 5 connections) ─────────
    elif src_type == "MV" and dst_type == "FIT":
        tmin, tmax = get_fit_thresholds(dst)
        on_term, off_term = get_terms(src_type)
        # Rule: If MV = Open (2), then FIT > Tmin
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(src)}=2",
            "Consequent": f"{clean(dst)}>{tmin:.6f}",
            "Comments": f"{clean(src)} {on_term} implies flow on {clean(dst)}"
        })
        # Rule: If MV = Close (1), then FIT < Tmax
        rows.append({
            "Plant stage": 5,
            "Antecedent": f"{clean(src)}=1",
            "Consequent": f"{clean(dst)}<{tmax:.6f}",
            "Comments": f"{clean(src)} {off_term} implies no flow on {clean(dst)}"
        })

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating instance-specific invariants for Stage 5 based on graph edges...\n")
    rows = generate_instance_invariants(TEMPLATES_PATH, CONNECTIONS_PATH)

    # Output to invariants_5.xlsx
    output_path = os.path.join(os.path.dirname(__file__), "invariants_5.xlsx")
    
    # ── Excel Export ──────────────────────────────────────────────────────────
    if rows:
        df_rows = pd.DataFrame(rows)
        # Assign Alert Codes
        df_rows.insert(1, "Alert Code", [f"A2-{i:02d}" for i in range(1, len(rows) + 1)])
        
        try:
            df_rows.to_excel(output_path, index=False)
            print(f"Successfully generated {len(rows)} invariants in {output_path}")
        except PermissionError:
            output_path = output_path.replace("invariants_5.xlsx", "invariants_5_updated.xlsx")
            df_rows.to_excel(output_path, index=False)
            print(f"Warning: invariants_5.xlsx was locked. Generated {len(rows)} invariants in {output_path} instead.")
        
        # Optional: Display content in console format
        print("\nInvariants Content:")
        print(df_rows.to_string(index=False))
    else:
        print("No invariants generated. Check templates and connections.")
