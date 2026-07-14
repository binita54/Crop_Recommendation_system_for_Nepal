"""
Collect a REAL Nepal crop-recommendation dataset.

For each sampled point across Nepal we pull:
  - soil N / P / K / pH  -> from NARC Digital Soil Map API (real measured Nepal soil)
  - temperature/humidity/rainfall -> from Open-Meteo (real climate)
Zone (Terai/Hill/Mountain) is derived from the API's elevation.
Crop labels come from CROP_ZONES (which crops grow in that Nepal agro-ecological zone).

Output: Nepal_crop_recommendation_real.csv  (columns match FEATURE_COLS + label + zone)
Units (IMPORTANT, document in report/UI):
  N = total nitrogen (%)
  P = P2O5 (kg/ha)
  K = potassium (kg/ha)
  temperature (C), humidity (%), rainfall (mm), ph
"""
import csv
import json
import sys
import time
import urllib.request

NARC_URL = "https://soil.narc.gov.np/soil/api/?lat={}&lon={}"
METEO_URL = ("https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}"
             "&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto")

# which crops grow in which Nepal agro-ecological zone (real agronomy)
CROP_ZONES = {
    "rice": ["terai", "hill"], "maize": ["terai", "hill", "mountain"],
    "wheat": ["terai", "hill"], "potato": ["terai", "hill", "mountain"],
    "lentil": ["terai", "hill"], "chickpea": ["terai", "hill"],
    "blackgram": ["terai", "hill"], "mustard": ["terai", "hill"],
    "millet": ["hill", "mountain"], "barley": ["hill", "mountain"],
    "sugarcane": ["terai"], "soybean": ["terai", "hill"],
    "banana": ["terai", "hill"], "mango": ["terai"], "ginger": ["hill"],
}

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def num(s):
    if s is None:
        return None
    s = str(s).strip()
    for unit in (" kg/ha", " ppm", " %", "%", "kg/ha", "ppm"):
        s = s.replace(unit, "")
    try:
        return float(s)
    except ValueError:
        return None


def zone_from_elevation(elev):
    if elev is None:
        return "hill"
    if elev < 1000:
        return "terai"
    if elev < 3000:
        return "hill"
    return "mountain"


def narc_soil(lat, lon):
    try:
        with urllib.request.urlopen(NARC_URL.format(lat, lon), timeout=15) as r:
            d = json.load(r)
        if "result" in d:          # "Please select the crop land"
            return None
        return d
    except Exception:
        return None


def meteo(lat, lon):
    try:
        with urllib.request.urlopen(METEO_URL.format(lat, lon), timeout=15) as r:
            c = json.load(r).get("current", {})
        return (c.get("temperature_2m"), c.get("relative_humidity_2m"),
                c.get("precipitation"))
    except Exception:
        return (None, None, None)


def collect(max_points=9999):
    rows = []
    # grid across Nepal's bounding box
    lats = [round(26.3 + 0.35 * i, 4) for i in range(0, 10)]   # 26.3 - 29.4
    lons = [round(80.0 + 0.35 * j, 4) for j in range(0, 25)]   # 80.0 - 88.25
    points = [(la, lo) for la in lats for lo in lons]

    out = "Nepal_crop_recommendation_real.csv"          # labels by CROP_ZONES (rule-based)
    out_narc = "Nepal_crop_recommendation_narc.csv"      # labels = NARC's own recommended crops
    with open(out, "w", newline="") as f, open(out_narc, "w", newline="") as fn:
        w = csv.writer(f)
        w.writerow(FEATURE_COLS + ["label", "zone"])
        wn = csv.writer(fn)
        wn.writerow(FEATURE_COLS + ["label", "zone"])
        seen = 0
        seen_n = 0
        for lat, lon in points:
            if seen >= max_points and seen_n >= max_points:
                break
            d = narc_soil(lat, lon)
            if not d:
                time.sleep(0.3)
                continue
            n = num(d.get("total_nitrogen"))
            p = num(d.get("p2o5"))
            k = num(d.get("potassium"))
            ph = num(d.get("ph"))
            if None in (n, p, k, ph):
                time.sleep(0.3)
                continue
            t, h, rf = meteo(lat, lon)
            if None in (t, h, rf):
                t, h, rf = 25.0, 70.0, 150.0   # fallback (documented)
            zone = zone_from_elevation(num(d.get("coord", {}).get("elevation")))
            # --- rule-based labels (CROP_ZONES) ---
            if seen < max_points:
                for crop, zones in CROP_ZONES.items():
                    if zone in zones:
                        w.writerow([n, p, k, t, h, ph, rf, crop, zone])
                        rows.append(crop)
                seen += 1
            # --- NARC's own recommended crops (real, tied to this location) ---
            if seen_n < max_points:
                narc_crops = list(d.get("fertilizer", {}).keys())
                for crop in narc_crops:
                    wn.writerow([n, p, k, t, h, ph, rf, crop, zone])
                seen_n += 1
                print(f"  point {lat},{lon} -> {zone}, NARC crops: {narc_crops}")
            time.sleep(0.4)   # be gentle on the public API

    print(f"\nDone. {len(rows)} labeled rows written to {out}")
    from collections import Counter
    for crop, c in Counter(rows).most_common():
        print(f"  {crop}: {c}")


if __name__ == "__main__":
    cap = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    collect(cap)
