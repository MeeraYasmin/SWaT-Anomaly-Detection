import pandas as pd
import os

# ── Load dataset ──────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(os.path.dirname(script_dir), "3_Graph_Generation", "stage_6_components_1.csv")

if not os.path.exists(CSV_PATH):
    # Fallback to absolute path if joined path fails during remote execution
    CSV_PATH = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 6)\Project_Steps (Stage 6_1)\3_Graph_Generation\stage_6_components_1.csv"

df = pd.read_csv(CSV_PATH)

# ── FIT-602 Thresholds ────────────────────────────────────────────────────────
FIT_602_max = df["FIT-602"].max()

def compute_min2(fit_max: float) -> float:
    """Returns Tmin2: minimum threshold 2 as 10% of FIT-602 max."""
    return 0.10 * fit_max

def compute_max2(fit_max: float) -> float:
    """Returns Tmax2: maximum threshold 2 as 90% of FIT-602 max."""
    return 0.90 * fit_max

Tmin2 = compute_min2(FIT_602_max)
Tmax2 = compute_max2(FIT_602_max)

# ── LIT-601 Thresholds ────────────────────────────────────────────────────────
LIT_601_min = df["LIT-601"].min()
LIT_601_max = df["LIT-601"].max()

def compute_min(lit_min: float) -> float:
    """Returns Tmin: minimum threshold as LIT-601 min."""
    return lit_min

def compute_max(lit_max: float) -> float:
    """Returns Tmax: maximum threshold as LIT-601 max."""
    return lit_max

Tmin = compute_min(LIT_601_min)
Tmax = compute_max(LIT_601_max)

# ── Output ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FIT-602 Threshold Computation Results (Stage 6_1)")
    print("=" * 50)
    print(f"  FIT-602 Maximum (FIT-602 Max) : {FIT_602_max:.6f}")
    print(f"  Tmin2  (10% of FIT-602 Max)   : {Tmin2:.6f}")
    print(f"  Tmax2  (90% of FIT-602 Max)   : {Tmax2:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  LIT-601 Threshold Computation Results (Stage 6_1)")
    print("=" * 50)
    print(f"  LIT-601 Minimum (LIT-601 Min) : {LIT_601_min:.6f}")
    print(f"  LIT-601 Maximum (LIT-601 Max) : {LIT_601_max:.6f}")
    print(f"  Tmin  (LIT-601 Min)           : {Tmin:.6f}")
    print(f"  Tmax  (LIT-601 Max)           : {Tmax:.6f}")
    print("=" * 50)

