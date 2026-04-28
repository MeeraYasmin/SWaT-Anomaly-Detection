import csv
import sys
import os
import pandas as pd

# ── Import threshold functions from compute_thresholds_3.py ─────────────────────
_COMPUTE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "5_Computation"
)
sys.path.insert(0, os.path.abspath(_COMPUTE_DIR))

from compute_thresholds_3 import compute_min3, compute_max3  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 3)"
CSV_PATH = os.path.join(_BASE, "3_Graph_Generation", "stage_3_components.csv")
TEMPLATES_PATH = os.path.join(_BASE, "4_Templates_Generation", "templates_3.csv")
CONNECTIONS_PATH = os.path.join(_BASE, "3_Graph_Generation", "connections_3.csv")

# ── Threshold Mapping ─────────────────────────────────────────────────────────
_THRESHOLDS_CACHE = {}

def get_fit_thresholds(tag):
    """
    Calculates Tmin and Tmax for a specific FIT tag.
    FIT-301 -> compute_min3 / compute_max3  (Tmin3 / Tmax3)
    """
    if tag in _THRESHOLDS_CACHE:
        return _THRESHOLDS_CACHE[tag]
    
    try:
        df = pd.read_csv(CSV_PATH)
        if tag in df.columns:
            fit_max = df[tag].max()
            tmin = compute_min3(fit_max)
            tmax = compute_max3(fit_max)
            _THRESHOLDS_CACHE[tag] = (tmin, tmax)
            return tmin, tmax
    except Exception as e:
        print(f"Warning: Could not compute thresholds for {tag}: {e}")
    
    return 0.0, 0.0

def get_type(tag):
    """Maps a physical tag (e.g., FIT-301) to its generic type (FIT)."""
    for t in ["FIT", "LIT", "MV", "P"]:
        if tag.startswith(t):
            return t
    return None

# ── Invariant generator ───────────────────────────────────────────────────────
def generate_instance_invariants(templates_path: str, connections_path: str) -> list[dict]:
    """
    Constructs instance-specific invariants.
    Returns a list of dictionaries with columns for invariants_3.xlsx.
    """
    templates = set()
    with open(templates_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            templates.add((row["Source"].strip(), row["Destination"].strip()))

    connections = []
    if os.path.exists(connections_path):
        with open(connections_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                connections.append((row["source"].strip(), row["destination"].strip()))

    rows = []
    ws = "after windowSize"
    L, H = 800, 1000

    for src_inst, dst_inst in connections:
        src_type = get_type(src_inst)
        dst_type = get_type(dst_inst)

        if (src_type, dst_type) in templates:
            # Rule selection based on pairs according to Invariants_Context_3.txt
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
        # Rule 1: MV/P Open/Running -> FIT > Tmin3
        rows.append({
            "Plant stage": 3,
            "Antecedent": f"{clean(dst)}=2",
            "Consequent": f"{clean(src)}>{tmin:.6f}",
            "Comments": f"{clean(dst)} {on_term} implies flow on {clean(src)}"
        })
        # Rule 2: MV/P Close/Stop -> FIT < Tmax3
        rows.append({
            "Plant stage": 3,
            "Antecedent": f"{clean(dst)}=1",
            "Consequent": f"{clean(src)}<{tmax:.6f}",
            "Comments": f"{clean(dst)} {off_term} implies no flow on {clean(src)}"
        })

    # ── LIT -> P ──────────────────────────────────────────────────────────────
    elif src_type == "LIT" and dst_type == "P":
        on_term, _ = get_terms(dst_type)
        # Rule: P = Running -> LIT > L (800)
        rows.append({
            "Plant stage": 3,
            "Antecedent": f"{clean(dst)}=2",
            "Consequent": f"{clean(src)}>{L}",
            "Comments": f"{clean(dst)} {on_term} implies {clean(src)} > {L}"
        })

    # ── MV -> FIT / P -> FIT ──────────────────────────────────────────────────
    elif (src_type == "MV" or src_type == "P") and dst_type == "FIT":
        tmin, tmax = get_fit_thresholds(dst)
        on_term, off_term = get_terms(src_type)
        # Rule 1: MV/P Open/Running -> FIT > Tmin3
        rows.append({
            "Plant stage": 3,
            "Antecedent": f"{clean(src)}=2",
            "Consequent": f"{clean(dst)}>{tmin:.6f}",
            "Comments": f"{clean(src)} {on_term} implies flow on {clean(dst)}"
        })
        # Rule 2: MV/P Close/Stop -> FIT < Tmax3
        rows.append({
            "Plant stage": 3,
            "Antecedent": f"{clean(src)}=1",
            "Consequent": f"{clean(dst)}<{tmax:.6f}",
            "Comments": f"{clean(src)} {off_term} implies no flow on {clean(dst)}"
        })

    # ── MV -> LIT ─────────────────────────────────────────────────────────────
    elif src_type == "MV" and dst_type == "LIT":
        on_term, off_term = get_terms(src_type)
        # Rule 1: MV = Open -> LIT < L
        rows.append({
            "Plant stage": 3,
            "Antecedent": f"{clean(src)}=2",
            "Consequent": f"{clean(dst)}<{L}",
            "Comments": f"{clean(src)} {on_term} implies {clean(dst)} < {L}"
        })
        # Rule 2: MV = Close -> LIT > H
        rows.append({
            "Plant stage": 3,
            "Antecedent": f"{clean(src)}=1",
            "Consequent": f"{clean(dst)}>{H}",
            "Comments": f"{clean(src)} {off_term} implies {clean(dst)} > {H}"
        })

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating instance-specific invariants based on graph edges...\n")
    rows = generate_instance_invariants(TEMPLATES_PATH, CONNECTIONS_PATH)

    # Assign Alert Codes and output to Excel
    output_path = os.path.join(os.path.dirname(__file__), "invariants_3.xlsx")
    
    # ── Excel Export ──────────────────────────────────────────────────────────
    if rows:
        df_rows = pd.DataFrame(rows)
        # Assign Alert Codes
        df_rows.insert(1, "Alert Code", [f"A2-{i:02d}" for i in range(1, len(rows) + 1)])
        
        try:
            df_rows.to_excel(output_path, index=False)
            print(f"Successfully generated {len(rows)} invariants in {output_path}")
        except PermissionError:
            output_path = output_path.replace("invariants_3.xlsx", "invariants_updated_3.xlsx")
            df_rows.to_excel(output_path, index=False)
            print(f"Warning: invariants_3.xlsx was locked. Generated {len(rows)} invariants in {output_path} instead.")
        
        # Optional: Display content in console format
        print("\nInvariants Content:")
        print(df_rows.to_string(index=False))
    else:
        print("No invariants generated.")
