import pandas as pd

# ── Load dataset ──────────────────────────────────────────────────────────────
CSV_PATH = r"c:\Users\itrust\Downloads\Telegram Desktop\SWaT\Anomaly_Detection\Project_Steps (Stage 1)\3_Graph_Generation\stage_1_components.csv"

df = pd.read_csv(CSV_PATH)

# ── FIT-101 Thresholds ────────────────────────────────────────────────────────
FIT_101_max = df["FIT-101"].max()

def compute_min1(fit_max: float) -> float:
    """Returns Tmin1: minimum threshold 1 as 10% of FIT-101 max."""
    return 0.10 * fit_max

def compute_max1(fit_max: float) -> float:
    """Returns Tmax1: maximum threshold 1 as 90% of FIT-101 max."""
    return 0.90 * fit_max

Tmin1 = compute_min1(FIT_101_max)
Tmax1 = compute_max1(FIT_101_max)

# ── FIT-201 Thresholds ────────────────────────────────────────────────────────
FIT_201_max = df["FIT-201"].max()

def compute_min2(fit_max: float) -> float:
    """Returns Tmin2: minimum threshold 2 as 10% of FIT-201 max."""
    return 0.10 * fit_max

def compute_max2(fit_max: float) -> float:
    """Returns Tmax2: maximum threshold 2 as 90% of FIT-201 max."""
    return 0.90 * fit_max

Tmin2 = compute_min2(FIT_201_max)
Tmax2 = compute_max2(FIT_201_max)

# ── LIT-101 Thresholds ────────────────────────────────────────────────────────
LIT_101_min = df["LIT-101"].min()
LIT_101_max = df["LIT-101"].max()

def compute_min3(lit_min: float) -> float:
    """Returns Tmin3: minimum threshold 3 as LIT-101 min."""
    return lit_min

def compute_max3(lit_max: float) -> float:
    """Returns Tmax3: maximum threshold 3 as LIT-101 max."""
    return lit_max

Tmin3 = compute_min3(LIT_101_min)
Tmax3 = compute_max3(LIT_101_max)

# ── Output ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FIT-101 Threshold Computation Results")
    print("=" * 50)
    print(f"  FIT-101 Maximum (FIT-101 Max) : {FIT_101_max:.6f}")
    print(f"  Tmin1  (10% of FIT-101 Max)   : {Tmin1:.6f}")
    print(f"  Tmax1  (90% of FIT-101 Max)   : {Tmax1:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  FIT-201 Threshold Computation Results")
    print("=" * 50)
    print(f"  FIT-201 Maximum (FIT-201 Max) : {FIT_201_max:.6f}")
    print(f"  Tmin2  (10% of FIT-201 Max)   : {Tmin2:.6f}")
    print(f"  Tmax2  (90% of FIT-201 Max)   : {Tmax2:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  LIT-101 Threshold Computation Results")
    print("=" * 50)
    print(f"  LIT-101 Minimum (LIT-101 Min) : {LIT_101_min:.6f}")
    print(f"  LIT-101 Maximum (LIT-101 Max) : {LIT_101_max:.6f}")
    print(f"  Tmin3  (LIT-101 Min)          : {Tmin3:.6f}")
    print(f"  Tmax3  (LIT-101 Max)          : {Tmax3:.6f}")
    print("=" * 50)

