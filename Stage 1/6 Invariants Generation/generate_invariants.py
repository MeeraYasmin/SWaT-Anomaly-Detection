import csv
import sys
import os
import pandas as pd

# ── Import threshold functions from compute_thresholds.py ─────────────────────
_COMPUTE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "5_Computation"
)
sys.path.insert(0, os.path.abspath(_COMPUTE_DIR))

from compute_thresholds import compute_min1, compute_max1, compute_min2, compute_max2  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
CSV_PATH = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%201/3%20Graph%20Generation/stage_1_components.csv"
TEMPLATES_PATH = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%201/4%20Templates%20Generation/templates.csv"
CONNECTIONS_PATH = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%201/3%20Graph%20Generation/connections.csv"

# ── Threshold Mapping ─────────────────────────────────────────────────────────
_THRESHOLDS_CACHE = {}

def get_fit_thresholds(tag):
    """
    Calculates Tmin and Tmax for a specific FIT tag.
    FIT-101 -> compute_min1 / compute_max1  (Tmin1 / Tmax1)
    FIT-201 -> compute_min2 / compute_max2  (Tmin2 / Tmax2)
    """
    if tag in _THRESHOLDS_CACHE:
        return _THRESHOLDS_CACHE[tag]
    
    try:
        df = pd.read_csv(CSV_PATH)
        if tag in df.columns:
            fit_max = df[tag].max()
            if tag == "FIT-101":
                tmin = compute_min1(fit_max)
                tmax = compute_max1(fit_max)
            else:  # FIT-201 or any other FIT
                tmin = compute_min2(fit_max)
                tmax = compute_max2(fit_max)
            _THRESHOLDS_CACHE[tag] = (tmin, tmax)
            return tmin, tmax
    except Exception as e:
        print(f"Warning: Could not compute thresholds for {tag}: {e}")
    
    return 0.0, 0.0

def get_type(tag):
    """Maps a physical tag (e.g., FIT-101) to its generic type (FIT)."""
    for t in ["FIT", "LIT", "MV", "P"]:
        if tag.startswith(t):
            return t
    return None

# ── Invariant generator ───────────────────────────────────────────────────────
def generate_instance_invariants(templates_path: str, connections_path: str) -> list[dict]:
    """
    Constructs instance-specific invariants.
    Returns a list of dictionaries with columns for invariants.csv.
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
    ws = "after windowSize"
    L, H = 500, 800

    for src_inst, dst_inst in connections:
        # User constraint: Exclude P-102
        if "P-102" in [src_inst, dst_inst]:
            continue

        src_type = get_type(src_inst)
        dst_type = get_type(dst_inst)

        if (src_type, dst_type) in templates:
            _append_rows(rows, src_inst, src_type, dst_inst, dst_type, ws, L, H)

    return rows

def _append_rows(rows, src, src_type, dst, dst_type, ws, L, H):
    """
    Helper to generate specific rows based on type pairs.
    """
    # Helper to remove hyphens
    clean = lambda s: s.replace("-", "")
    
    # Terminology based on type
    def get_terms(tag_type):
        if tag_type == "MV":
            return "OPEN", "CLOSE"
        else: # P
            return "RUN", "STOP"

    # ── FIT -> MV / FIT -> P ──────────────────────────────────────────────────
    if src_type == "FIT" and (dst_type == "MV" or dst_type == "P"):
        tmin, tmax = get_fit_thresholds(src)
        on_term, off_term = get_terms(dst_type)
        # Rule 1: MV/P Open/Running -> FIT > Tmin1
        rows.append({
            "Plant stage": 1,
            "Antecedent": f"{clean(dst)}=2",
            "Consequent": f"{clean(src)}>{tmin:.6f}",
            "Comments": f"{clean(dst)} {on_term} implies flow on {clean(src)}"
        })
        # Rule 2: MV/P Close/Stop -> FIT < Tmax1
        rows.append({
            "Plant stage": 1,
            "Antecedent": f"{clean(dst)}=1",
            "Consequent": f"{clean(src)}<{tmax:.6f}",
            "Comments": f"{clean(dst)} {off_term} implies no flow on {clean(src)}"
        })

    # ── LIT -> P ──────────────────────────────────────────────────────────────
    elif src_type == "LIT" and dst_type == "P":
        on_term, _ = get_terms(dst_type)
        # Rule: P = Running -> LIT > L
        rows.append({
            "Plant stage": 1,
            "Antecedent": f"{clean(dst)}=2",
            "Consequent": f"{clean(src)}>{L}",
            "Comments": f"{clean(dst)} {on_term} implies {clean(src)} > {L}"
        })

    # ── MV -> FIT / P -> FIT ──────────────────────────────────────────────────
    elif (src_type == "MV" or src_type == "P") and dst_type == "FIT":
        tmin, tmax = get_fit_thresholds(dst)
        on_term, off_term = get_terms(src_type)
        # Rule 1: MV/P Open/Running -> FIT > Tmin2
        rows.append({
            "Plant stage": 1,
            "Antecedent": f"{clean(src)}=2",
            "Consequent": f"{clean(dst)}>{tmin:.6f}",
            "Comments": f"{clean(src)} {on_term} implies flow on {clean(dst)}"
        })
        # Rule 2: MV/P Close/Stop -> FIT < Tmax2
        rows.append({
            "Plant stage": 1,
            "Antecedent": f"{clean(src)}=1",
            "Consequent": f"{clean(dst)}<{tmax:.6f}",
            "Comments": f"{clean(src)} {off_term} implies no flow on {clean(dst)}"
        })

    # ── MV -> LIT ─────────────────────────────────────────────────────────────
    elif src_type == "MV" and dst_type == "LIT":
        on_term, off_term = get_terms(src_type)
        # Rule 1: MV = Open -> LIT < L
        rows.append({
            "Plant stage": 1,
            "Antecedent": f"{clean(src)}=2",
            "Consequent": f"{clean(dst)}<{L}",
            "Comments": f"{clean(src)} {on_term} implies {clean(dst)} < {L}"
        })
        # Rule 2: MV = Close -> LIT > H
        rows.append({
            "Plant stage": 1,
            "Antecedent": f"{clean(src)}=1",
            "Consequent": f"{clean(dst)}>{H}",
            "Comments": f"{clean(src)} {off_term} implies {clean(dst)} > {H}"
        })

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating instance-specific invariants based on graph edges...\n")
    rows = generate_instance_invariants(TEMPLATES_PATH, CONNECTIONS_PATH)

    # Assign Alert Codes and output to Excel
    output_path = os.path.join(os.path.dirname(__file__), "invariants_updated.xlsx")
    
    # ── Excel Export ──────────────────────────────────────────────────────────
    df_rows = pd.DataFrame(rows)
    # Assign Alert Codes
    df_rows.insert(1, "Alert Code", [f"A2-{i:02d}" for i in range(1, len(rows) + 1)])
    
    try:
        df_rows.to_excel(output_path, index=False)
        print(f"Successfully generated {len(rows)} invariants in {output_path}")
    except PermissionError:
        print(f"Error: Could not write to {output_path}. Please close the file if it is open.")
    
    # Optional: Display content in console format
    print("\nInvariants Content:")
    print(df_rows.to_string(index=False))
