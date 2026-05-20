import pandas as pd
import numpy as np
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os

# ✅ Use working USGS endpoints + add headers to avoid blocking
USGS_MONTHLY = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
USGS_QUERY = "https://earthquake.usgs.gov/fdsnws/event/1/query"

HEADERS = {
    "User-Agent": "SeismoPredict/1.0 (Educational Project; contact: your@email.com)"
}

def fetch_usgs_data():
    """Fetch earthquake data with fallback strategies"""
    
    # Strategy 1: Try monthly summary (reliable, ~10k events)
    try:
        print("🌍 Fetching from USGS monthly summary...")
        res = requests.get(USGS_MONTHLY, headers=HEADERS, timeout=20)
        res.raise_for_status()
        data = res.json()
        if "features" in data and len(data["features"]) > 100:
            print(f"✅ Loaded {len(data['features'])} events from monthly feed")
            return data
    except Exception as e:
        print(f"⚠️ Monthly fetch failed: {e}")

    # Strategy 2: Try query API for last 90 days, magnitude >= 2.5
    try:
        print("🔄 Trying USGS query API for 90-day data...")
        params = {
            "format": "geojson",
            "starttime": "2025-02-20",  # 90 days ago from May 2026
            "endtime": "2026-05-20",
            "minmagnitude": 2.5,
            "limit": 20000,
            "orderby": "time"
        }
        res = requests.get(USGS_QUERY, headers=HEADERS, params=params, timeout=30)
        res.raise_for_status()
        # Check if response is actually JSON
        if "application/json" in res.headers.get("Content-Type", ""):
            data = res.json()
            if "features" in data and len(data["features"]) > 100:
                print(f"✅ Loaded {len(data['features'])} events from query API")
                return data
    except Exception as e:
        print(f"⚠️ Query API failed: {e}")

    # Strategy 3: Fallback to local CSV
    if os.path.exists("dataset.csv"):
        print("📦 Using local dataset.csv as fallback")
        df = pd.read_csv("dataset.csv")
        # Convert to pseudo-geojson structure for compatibility
        return {
            "features": [
                {
                    "geometry": {"coordinates": [row["Longitude"], row["Latitude"], row["Depth"]]},
                    "properties": {"mag": row["Magnitude"]}
                }
                for _, row in df.iterrows()
            ]
        }
    
    raise RuntimeError("❌ No data source available. Please add dataset.csv or check internet connection.")

# Fetch data
data = fetch_usgs_data()

# Parse into DataFrame
records = []
for feat in data["features"]:
    mag = feat["properties"].get("mag")
    if mag is None: continue
    coords = feat["geometry"]["coordinates"]
    if len(coords) < 3: continue
    lon, lat, depth = coords[0], coords[1], coords[2]
    records.append({"lat": lat, "lon": lon, "depth": depth, "mag": mag})

df = pd.DataFrame(records)
print(f"✅ Final dataset: {len(df)} valid earthquakes")

if len(df) < 50:
    raise ValueError("⚠️ Too few records. Add more data to dataset.csv")

# 🌋 Tectonic Zone Proxy
def get_seismic_zone(lat, lon):
    if (20 < lat < 50) and (100 < lon < 150): return 3      # Himalayas / Japan
    if (-60 < lat < -10) and (-120 < lon < -50): return 3   # Andes / Chile
    if (-20 < lat < 20) and (90 < lon < 160): return 2      # Indonesia
    if (35 < lat < 45) and (20 < lon < 50): return 2        # Turkey / Med
    if (40 < lat < 65) and (-140 < lon < -100): return 2    # Alaska
    if (-35 < lat < -10) and (110 < lon < 180): return 1    # NZ / Fiji
    if abs(lat) < 15: return 1                              # Equatorial
    return 0                                                # Stable interiors

df["zone"] = df.apply(lambda r: get_seismic_zone(r["lat"], r["lon"]), axis=1)

# 🔧 Feature Engineering
df["abs_lat"] = df["lat"].abs()
df["depth_log"] = np.log1p(df["depth"])
df["zone_depth"] = df["zone"] * df["depth_log"]

# 🎯 Train Regressor
X = df[["abs_lat", "depth_log", "zone_depth"]]
y = df["mag"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = HistGradientBoostingRegressor(max_depth=6, learning_rate=0.05, max_iter=300, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"✅ Training Complete | MAE: {mae:.2f} | R²: {r2:.2f}")

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
print("💾 Model saved as model.pkl")