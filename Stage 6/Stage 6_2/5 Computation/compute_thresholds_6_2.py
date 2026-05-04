import pandas as pd
import os

# ── Load dataset ──────────────────────────────────────────────────────────────
CSV_PATH = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%206/Stage%206_2/3%20Graph%20Generation/stage_6_components_2.csv"
df = pd.read_csv(CSV_PATH)

# ── FIT-601 Thresholds ────────────────────────────────────────────────────────
FIT_601_max = df["FIT-601"].max()

def compute_min1(fit_max: float) -> float:
    """Returns Tmin1: minimum threshold 1 as 10% of FIT-601 max."""
    return 0.10 * fit_max

def compute_max1(fit_max: float) -> float:
    """Returns Tmax1: maximum threshold 1 as 90% of FIT-601 max."""
    return 0.90 * fit_max

Tmin1 = compute_min1(FIT_601_max)
Tmax1 = compute_max1(FIT_601_max)

# ── LIT-602 Thresholds ────────────────────────────────────────────────────────
LIT_602_min = df["LIT-602"].min()
LIT_602_max = df["LIT-602"].max()

def compute_min(lit_min: float) -> float:
    """Returns Tmin: minimum threshold as LIT-602 min."""
    return lit_min

def compute_max(lit_max: float) -> float:
    """Returns Tmax: maximum threshold as LIT-602 max."""
    return lit_max

Tmin = compute_min(LIT_602_min)
Tmax = compute_max(LIT_602_max)

# ── Output ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FIT-601 Threshold Computation Results (Stage 6_2)")
    print("=" * 50)
    print(f"  FIT-601 Maximum (FIT-601 Max) : {FIT_601_max:.6f}")
    print(f"  Tmin1  (10% of FIT-601 Max)   : {Tmin1:.6f}")
    print(f"  Tmax1  (90% of FIT-601 Max)   : {Tmax1:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  LIT-602 Threshold Computation Results (Stage 6_2)")
    print("=" * 50)
    print(f"  LIT-602 Minimum (LIT-602 Min) : {LIT_602_min:.6f}")
    print(f"  LIT-602 Maximum (LIT-602 Max) : {LIT_602_max:.6f}")
    print(f"  Tmin  (LIT-602 Min)           : {Tmin:.6f}")
    print(f"  Tmax  (LIT-602 Max)           : {Tmax:.6f}")
    print("=" * 50)

