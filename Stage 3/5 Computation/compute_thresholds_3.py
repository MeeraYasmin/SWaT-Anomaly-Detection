import pandas as pd
import os

# ── Load dataset ──────────────────────────────────────────────────────────────
# Base directory for the project
base_dir = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT"
# Path to Stage 3 filtered components CSV
CSV_PATH = os.path.join(base_dir, r"Anomaly_Detection\Project_Steps (Stage 3)\3_Graph_Generation\stage_3_components.csv")

if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found.")
    # Fallback to current directory for relative testing if needed
    CSV_PATH = "stage_3_components.csv"

df = pd.read_csv(CSV_PATH)

# ── FIT-301 Thresholds ────────────────────────────────────────────────────────
if "FIT-301" in df.columns:
    FIT_301_max = df["FIT-301"].max()

    def compute_min3(fit_max: float) -> float:
        """Returns Tmin3: minimum threshold 3 as 10% of FIT-301 max."""
        return 0.10 * fit_max

    def compute_max3(fit_max: float) -> float:
        """Returns Tmax3: maximum threshold 3 as 90% of FIT-301 max."""
        return 0.90 * fit_max

    Tmin3 = compute_min3(FIT_301_max)
    Tmax3 = compute_max3(FIT_301_max)
else:
    print("Error: FIT-301 column not found in dataset.")
    FIT_301_max = 0.0
    Tmin3 = 0.0
    Tmax3 = 0.0

# ── LIT-301 Thresholds ────────────────────────────────────────────────────────
if "LIT-301" in df.columns:
    LIT_301_min = df["LIT-301"].min()
    LIT_301_max = df["LIT-301"].max()

    def compute_min(lit_min: float) -> float:
        """Returns Tmin: minimum threshold as LIT-301 min."""
        return lit_min

    def compute_max(lit_max: float) -> float:
        """Returns Tmax: maximum threshold as LIT-301 max."""
        return lit_max

    Tmin = compute_min(LIT_301_min)
    Tmax = compute_max(LIT_301_max)
else:
    print("Error: LIT-301 column not found in dataset.")
    LIT_301_min = 0.0
    LIT_301_max = 0.0
    Tmin = 0.0
    Tmax = 0.0

# ── Output ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FIT-301 Threshold Computation Results (Stage 3)")
    print("=" * 50)
    print(f"  FIT-301 Maximum (FIT-301 Max) : {FIT_301_max:.6f}")
    print(f"  Tmin3  (10% of FIT-301 Max)   : {Tmin3:.6f}")
    print(f"  Tmax3  (90% of FIT-301 Max)   : {Tmax3:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  LIT-301 Threshold Computation Results (Stage 3)")
    print("=" * 50)
    print(f"  LIT-301 Minimum (LIT-301 Min) : {LIT_301_min:.6f}")
    print(f"  LIT-301 Maximum (LIT-301 Max) : {LIT_301_max:.6f}")
    print(f"  Tmin  (LIT-301 Min)           : {Tmin:.6f}")
    print(f"  Tmax  (LIT-301 Max)           : {Tmax:.6f}")
    print("=" * 50)

