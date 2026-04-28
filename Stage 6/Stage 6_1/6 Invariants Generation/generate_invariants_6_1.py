import csv
import sys
import os
import pandas as pd

# ── Import threshold functions from compute_thresholds_6_1.py ──────────────────
_COMPUTE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "5_Computation"
)
sys.path.insert(0, os.path.abspath(_COMPUTE_DIR))

# Import needed functions from Stage 6_1 computation script
from compute_thresholds_6_1 import compute_min2, compute_max2  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 6)\Project_Steps (Stage 6_1)"
COMPONENTS_CSV = os.path.join(_BASE, "3_Graph_Generation", "stage_6_components_1.csv")
TEMPLATES_PATH = os.path.join(_BASE, "4_Templates_Generation", "templates_6_1.csv")
CONNECTIONS_PATH = os.path.join(_BASE, "3_Graph_Generation", "connections_6_1.csv")

# ── Threshold Mapping ─────────────────────────────────────────────────────────
_THRESHOLDS_CACHE = {}

def get_fit_thresholds(tag):
    """
    Calculates Tmin2 and Tmax2 for a specific FIT tag.
    Uses compute_min2 / compute_max2 as per context.
    """
    if tag in _THRESHOLDS_CACHE:
        return _THRESHOLDS_CACHE[tag]
    
    try:
        df = pd.read_csv(COMPONENTS_CSV)
        if tag in df.columns:
            fit_max = df[tag].max()
            tmin = compute_min2(fit_max)
            tmax = compute_max2(fit_max)
            _THRESHOLDS_CACHE[tag] = (tmin, tmax)
            return tmin, tmax
    except Exception as e:
        print(f"Warning: Could not compute thresholds for {tag}: {e}")
    
    return 0.0, 0.0

def get_type(tag):
    """Maps a physical tag (e.g., FIT-602) to its generic type (FIT)."""
    for t in ["FIT", "LIT", "P"]:
        if tag.startswith(t):
            return t
    return None

# ── Invariant generator ───────────────────────────────────────────────────────
def generate_instance_invariants(templates_path: str, connections_path: str) -> list[dict]:
    """
    Constructs instance-specific invariants based on templates and edges.
    Returns a list of dictionaries with columns for invariants_6_1.xlsx.
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
    # Constants from context
    RUN, STOP = 2, 1
    L, H = 100, 800

    # Iterate through connections and match templates
    # Template logic: (Source, Destination) could be (FIT, P), (LIT, P), or (P, FIT)
    for src_inst, dst_inst in connections:
        src_type = get_type(src_inst)
        dst_type = get_type(dst_inst)

        # Check for FIT <-> P connection
        if (src_type == "P" and dst_type == "FIT") or (src_type == "FIT" and dst_type == "P"):
            p_inst = src_inst if src_type == "P" else dst_inst
            fit_inst = dst_inst if src_type == "P" else src_inst
            
            # Check if either (P, FIT) or (FIT, P) is in templates
            if ("P", "FIT") in templates or ("FIT", "P") in templates:
                _append_fit_p_rows(rows, p_inst, fit_inst)

        # Check for LIT -> P connection
        elif src_type == "LIT" and dst_type == "P":
            if ("LIT", "P") in templates:
                _append_lit_p_rows(rows, src_inst, dst_inst, L)

    return rows

def _append_fit_p_rows(rows, p_inst, fit_inst):
    """Generates invariants for Pump and FIT connection."""
    tmin, tmax = get_fit_thresholds(fit_inst)
    clean_p = p_inst.replace("-", "")
    clean_fit = fit_inst.replace("-", "")

    # Rule: If P = Run, then FIT > Tmin2
    rows.append({
        "Plant stage": 6,
        "Antecedent": f"{clean_p}=2",
        "Consequent": f"{clean_fit}>{tmin:.6f}",
        "Comments": f"{clean_p} RUN implies flow on {clean_fit}"
    })
    
    # Rule: If P = Stop, then FIT < Tmax2
    rows.append({
        "Plant stage": 6,
        "Antecedent": f"{clean_p}=1",
        "Consequent": f"{clean_fit}<{tmax:.6f}",
        "Comments": f"{clean_p} STOP implies no flow on {clean_fit}"
    })

def _append_lit_p_rows(rows, lit_inst, p_inst, L):
    """Generates invariants for LIT and Pump connection."""
    clean_p = p_inst.replace("-", "")
    clean_lit = lit_inst.replace("-", "")

    # Rule: If P = Run, then LIT > L
    rows.append({
        "Plant stage": 6,
        "Antecedent": f"{clean_p}=2",
        "Consequent": f"{clean_lit}>{L}",
        "Comments": f"{clean_p} RUN implies {clean_lit} > {L}"
    })

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating instance-specific invariants for Stage 6_1...\n")
    rows = generate_instance_invariants(TEMPLATES_PATH, CONNECTIONS_PATH)

    output_path = os.path.join(os.path.dirname(__file__), "invariants_6_1.xlsx")
    
    # ── Excel Export ──────────────────────────────────────────────────────────
    if not rows:
        print("No invariants generated. Check connections and templates.")
    else:
        df_rows = pd.DataFrame(rows)
        # Assign Alert Codes
        df_rows.insert(1, "Alert Code", [f"A2-{i:02d}" for i in range(1, len(rows) + 1)])
        
        # Ensure column order
        cols = ["Plant stage", "Alert Code", "Antecedent", "Consequent", "Comments"]
        df_rows = df_rows[cols]
        
        try:
            df_rows.to_excel(output_path, index=False)
            print(f"Successfully generated {len(rows)} invariants in {output_path}")
        except PermissionError:
            output_path = output_path.replace("invariants_6_1.xlsx", "invariants_6_1_updated.xlsx")
            df_rows.to_excel(output_path, index=False)
            print(f"Warning: invariants_6_1.xlsx was locked. Generated {len(rows)} invariants in {output_path} instead.")
        
        # Display content in console format
        print("\nInvariants Content:")
        print(df_rows.to_string(index=False))
