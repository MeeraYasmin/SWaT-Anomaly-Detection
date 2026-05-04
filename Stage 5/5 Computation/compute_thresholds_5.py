import pandas as pd

# ── Load dataset ──────────────────────────────────────────────────────────────
CSV_PATH = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%205/3%20Graph%20Generation/stage_5_components.csv"

df = pd.read_csv(CSV_PATH)

# ── FIT-501 Thresholds ────────────────────────────────────────────────────────
FIT_501_max = df["FIT-501"].max()

def compute_min1(fit_max: float) -> float:
    """Returns Tmin1: minimum threshold 1 as 10% of FIT-501 max."""
    return 0.10 * fit_max

def compute_max1(fit_max: float) -> float:
    """Returns Tmax1: maximum threshold 1 as 90% of FIT-501 max."""
    return 0.90 * fit_max

Tmin1 = compute_min1(FIT_501_max)
Tmax1 = compute_max1(FIT_501_max)

# ── FIT-502 Thresholds ────────────────────────────────────────────────────────
FIT_502_max = df["FIT-502"].max()

def compute_min2(fit_max: float) -> float:
    """Returns Tmin2: minimum threshold 2 as 10% of FIT-502 max."""
    return 0.10 * fit_max

def compute_max2(fit_max: float) -> float:
    """Returns Tmax2: maximum threshold 2 as 90% of FIT-502 max."""
    return 0.90 * fit_max

Tmin2 = compute_min2(FIT_502_max)
Tmax2 = compute_max2(FIT_502_max)

# ── FIT-503 Thresholds ────────────────────────────────────────────────────────
FIT_503_max = df["FIT-503"].max()

def compute_min3(fit_max: float) -> float:
    """Returns Tmin3: minimum threshold 3 as 10% of FIT-503 max."""
    return 0.10 * fit_max

def compute_max3(fit_max: float) -> float:
    """Returns Tmax3: maximum threshold 3 as 90% of FIT-503 max."""
    return 0.90 * fit_max

Tmin3 = compute_min3(FIT_503_max)
Tmax3 = compute_max3(FIT_503_max)

# ── Output ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  FIT-501 Threshold Computation Results")
    print("=" * 50)
    print(f"  FIT-501 Maximum (FIT-501 Max) : {FIT_501_max:.6f}")
    print(f"  Tmin1  (10% of FIT-501 Max)   : {Tmin1:.6f}")
    print(f"  Tmax1  (90% of FIT-501 Max)   : {Tmax1:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  FIT-502 Threshold Computation Results")
    print("=" * 50)
    print(f"  FIT-502 Maximum (FIT-502 Max) : {FIT_502_max:.6f}")
    print(f"  Tmin2  (10% of FIT-502 Max)   : {Tmin2:.6f}")
    print(f"  Tmax2  (90% of FIT-502 Max)   : {Tmax2:.6f}")
    print("=" * 50)

    print()
    print("=" * 50)
    print("  FIT-503 Threshold Computation Results")
    print("=" * 50)
    print(f"  FIT-503 Maximum (FIT-503 Max) : {FIT_503_max:.6f}")
    print(f"  Tmin3  (10% of FIT-503 Max)   : {Tmin3:.6f}")
    print(f"  Tmax3  (90% of FIT-503 Max)   : {Tmax3:.6f}")
    print("=" * 50)
