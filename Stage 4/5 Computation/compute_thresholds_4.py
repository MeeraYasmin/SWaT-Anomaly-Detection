import pandas as pd
import os

# ── Load dataset ──────────────────────────────────────────────────────────────
# Base directory for the project
base_dir = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT"
# Path to Stage 4 filtered components CSV
CSV_PATH = os.path.join(base_dir, r"Anomaly_Detection\Project_Steps (Stage 4)\3_Graph_Generation\stage_4_components.csv")

if not os.path.exists(CSV_PATH):
    print(f"Error: {CSV_PATH} not found.")
    # Fallback to local file if path fails
    CSV_PATH = "stage_4_components.csv"

df = pd.read_csv(CSV_PATH)

# ── FIT-401 Thresholds ────────────────────────────────────────────────────────
if "FIT-401" in df.columns:
    FIT_401_max = df["FIT-401"].max()

    def compute_min4(fit_max: float) -> float:
        """Returns Tmin4: minimum threshold 4 as 10% of FIT-401 max."""
        return 0.10 * fit_max

    def compute_max4(fit_max: float) -> float:
        """Returns Tmax4: maximum threshold 4 as 90% of FIT-401 max."""
        return 0.90 * fit_max

    Tmin4 = compute_min4(FIT_401_max)
    Tmax4 = compute_max4(FIT_401_max)
else:
    print("Error: FIT-401 column not found in dataset.")
    FIT_401_max = 0.0
    Tmin4 = 0.0
    Tmax4 = 0.0

# ── LIT-401 Thresholds ────────────────────────────────────────────────────────
if "LIT-401" in df.columns:
    LIT_401_min = df["LIT-401"].min()
    LIT_401_max = df["LIT-401"].max()

    def compute_min(lit_min: float) -> float:
        """Returns Tmin: minimum threshold as LIT-401 min."""
        return lit_min

    def compute_max(lit_max: float) -> float:
        """Returns Tmax: maximum threshold as LIT-401 max."""
        return lit_max

    Tmin = compute_min(LIT_401_min)
    Tmax = compute_max(LIT_401_max)
else:
    print("Error: LIT-401 column not found in dataset.")
    LIT_401_min = 0.0
    LIT_401_max = 0.0
    Tmin = 0.0
    Tmax = 0.0

# ── Output ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FIT-401 Threshold Computation Results (Stage 4)")
    print("=" * 50)
    print(f"  FIT-401 Maximum (FIT-401 Max) : {FIT_401_max:.6f}")
    print(f"  Tmin4  (10% of FIT-401 Max)   : {Tmin4:.6f}")
    print(f"  Tmax4  (90% of FIT-401 Max)   : {Tmax4:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  LIT-401 Threshold Computation Results (Stage 4)")
    print("=" * 50)
    print(f"  LIT-401 Minimum (LIT-401 Min) : {LIT_401_min:.6f}")
    print(f"  LIT-401 Maximum (LIT-401 Max) : {LIT_401_max:.6f}")
    print(f"  Tmin  (LIT-401 Min)           : {Tmin:.6f}")
    print(f"  Tmax  (LIT-401 Max)           : {Tmax:.6f}")
    print("=" * 50)

