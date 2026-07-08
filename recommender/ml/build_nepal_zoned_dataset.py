import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# Base profiles (treated as "Hill" baseline -- Nepal's most agriculturally
# average zone). Terai and Mountain variants are derived by applying
# realistic climate/fertility shifts on top of this baseline per crop.
# N, P, K are representative soil-fertility index values (same convention as
# before); rice/maize/wheat NPK anchored to NARC/CIMMYT 2022-2023
# site-specific fertilizer recommendations.
BASE_PROFILES = {
    "rice":       [95, 42, 43, 26, 82, 6.0, 250],
    "maize":      [85, 55, 45, 24, 65, 6.2, 110],
    "wheat":      [100, 50, 32, 18, 55, 6.5, 60],
    "potato":     [100, 80, 100, 18, 70, 5.5, 90],
    "lentil":     [20, 40, 20, 18, 55, 6.5, 45],
    "chickpea":   [20, 45, 20, 20, 50, 7.0, 40],
    "blackgram":  [20, 35, 20, 27, 70, 6.5, 90],
    "mustard":    [60, 30, 20, 20, 55, 6.5, 40],
    "millet":     [40, 25, 25, 22, 60, 5.8, 100],
    "barley":     [50, 30, 20, 16, 50, 6.8, 45],
    "sugarcane":  [120, 60, 60, 28, 75, 6.5, 150],
    "soybean":    [25, 50, 30, 25, 65, 6.3, 100],
    "banana":     [100, 60, 150, 27, 80, 6.0, 120],
    "mango":      [50, 40, 60, 27, 60, 6.2, 90],
    "ginger":     [80, 50, 90, 23, 80, 5.8, 180],
}

# Which agro-ecological zones each crop is actually cultivated in across Nepal.
CROP_ZONES = {
    "rice":      ["terai", "hill"],
    "maize":     ["terai", "hill", "mountain"],
    "wheat":     ["terai", "hill"],
    "potato":    ["terai", "hill", "mountain"],
    "lentil":    ["terai", "hill"],
    "chickpea":  ["terai", "hill"],
    "blackgram": ["terai", "hill"],
    "mustard":   ["terai", "hill"],
    "millet":    ["hill", "mountain"],
    "barley":    ["hill", "mountain"],
    "sugarcane": ["terai"],
    "soybean":   ["terai", "hill"],
    "banana":    ["terai", "hill"],
    "mango":     ["terai"],
    "ginger":    ["hill"],
}

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Zone adjustments applied on top of the Hill baseline profile.
ZONE_ADJUST = {
    "terai":    {"temp_delta": 4,  "humidity_delta": 8,  "rainfall_mult": 1.3, "ph_delta": -0.1, "npk_mult": 1.0},
    "hill":     {"temp_delta": 0,  "humidity_delta": 0,  "rainfall_mult": 1.0, "ph_delta": 0.0,  "npk_mult": 1.0},
    "mountain": {"temp_delta": -7, "humidity_delta": -10,"rainfall_mult": 0.7, "ph_delta": -0.2, "npk_mult": 0.85},
}

NOISE_FRAC = {
    "N": 0.12, "P": 0.15, "K": 0.15,
    "temperature": 0.10, "humidity": 0.08,
    "ph": 0.06, "rainfall": 0.15,
}

SAMPLES_PER_ZONE = 40


def apply_zone(base_values, zone):
    adj = ZONE_ADJUST[zone]
    N, P, K, temp, hum, ph, rain = base_values
    return [
        N * adj["npk_mult"],
        P * adj["npk_mult"],
        K * adj["npk_mult"],
        temp + adj["temp_delta"],
        hum + adj["humidity_delta"],
        ph + adj["ph_delta"],
        rain * adj["rainfall_mult"],
    ]


def generate_row(zone_values):
    row = {}
    for col, val in zip(FEATURE_COLS, zone_values):
        noise = rng.normal(0, NOISE_FRAC[col] * abs(val) if val != 0 else 1)
        new_val = val + noise
        if col in ("N", "P", "K"):
            new_val = max(0, round(new_val, 1))
        elif col == "temperature":
            new_val = round(new_val, 1)
        elif col == "humidity":
            new_val = round(min(100, max(10, new_val)), 1)
        elif col == "ph":
            new_val = round(min(9.5, max(3.5, new_val)), 2)
        elif col == "rainfall":
            new_val = round(max(10, new_val), 1)
        row[col] = new_val
    return row


def build_dataset():
    rows = []
    for crop, base in BASE_PROFILES.items():
        for zone in CROP_ZONES[crop]:
            zone_values = apply_zone(base, zone)
            for _ in range(SAMPLES_PER_ZONE):
                row = generate_row(zone_values)
                row["label"] = crop
                row["zone"] = zone  # metadata only -- not used as a model feature
                rows.append(row)
    df = pd.DataFrame(rows)
    return df[FEATURE_COLS + ["label", "zone"]]


if __name__ == "__main__":
    df = build_dataset()
    df.to_csv("Nepal_crop_recommendation_zoned.csv", index=False)
    print(f"Generated {len(df)} rows across {df['label'].nunique()} crops and {df['zone'].nunique()} zones")
    print(df.groupby(["label", "zone"]).size())
