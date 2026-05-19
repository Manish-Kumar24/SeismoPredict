import pandas as pd
import numpy as np
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
import pickle
from datetime import datetime, timedelta
import os

USGS_API = "https://earthquake.usgs.gov/fdsnws/event/1/query"

print("🌍 Fetching recent global earthquake data...")
try:
    params = {
        "format": "geojson",
        "starttime": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        "minmagnitude": 2.5,
        "limit": 15000,
        "orderby": "time"
    }
    headers = {"User-Agent": "Earthquake-Predictor/1.0 (Educational)"}
    
    res = requests.get(USGS_API, params=params, headers=headers, timeout=30)
    res.raise_for_status()
    
    if "json" not in res.headers.get("Content-Type", ""):
        raise ValueError(f"Invalid response format")
        
    data = res.json()
    if "features" not in data:
        raise ValueError("No earthquake data in response")

    records = []
    for feat in data["features"]:
        mag = feat["properties"].get("mag")
        if mag is None: continue
        lon, lat, depth = feat["geometry"]["coordinates"]
        records.append({"lat": lat, "lon": lon, "depth": depth, "mag": mag})

    df = pd.DataFrame(records)
    print(f"✅ Successfully loaded {len(df)} earthquakes.")

except Exception as e:
    print(f"⚠️ API fetch failed: {e}")
    if os.path.exists("dataset.csv"):
        print("📦 Falling back to local dataset.csv...")
        df = pd.read_csv("dataset.csv")
    else:
        raise SystemExit("❌ No data available. Exiting.")

# 🔧 SAFE Feature Engineering
df["depth"] = df["depth"].fillna(0).clip(lower=0)  # ✅ Fixes log1p warning
df["abs_lat"] = df["lat"].abs()
df["depth_log"] = np.log1p(df["depth"])
df["lat_lon_interaction"] = df["lat"] * df["lon"]

def get_zone(row):
    if (row["lat"] > -60 and row["lat"] < 60) and ((row["lon"] > 120) or (row["lon"] < -100)):
        return 3  # Pacific Ring of Fire
    elif 20 < row["lat"] < 50 and -10 < row["lon"] < 120:
        return 2  # Alpine-Himalayan Belt
    else:
        return 1  # Stable/Other zones

df["tectonic_zone"] = df.apply(get_zone, axis=1)

X = df[["abs_lat", "depth_log", "lat_lon_interaction", "tectonic_zone"]]
y = df["mag"]

# 🔁 Balance high-magnitude events
high_mask = y >= 6.0
if high_mask.sum() > 0:
    X_bal = pd.concat([X, X[high_mask].sample(n=min(len(X[high_mask])*2, 500), replace=True, random_state=42)])
    y_bal = pd.concat([y, y[high_mask].sample(n=min(len(y[high_mask])*2, 500), replace=True, random_state=42)])
    X_train, X_test, y_train, y_test = train_test_split(X_bal, y_bal, test_size=0.2, random_state=42)
else:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🧠 Train Model (Fixed parameter)
model = HistGradientBoostingRegressor(
    max_depth=6, 
    learning_rate=0.05, 
    max_iter=300,          # ✅ FIXED: was n_estimators
    random_state=42,
    early_stopping=True,
    validation_fraction=0.1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = model.score(X_test, y_test)
print(f"✅ Training Complete | MAE: {mae:.2f} | R²: {r2:.2f}")

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
print("💾 Model saved as model.pkl. Run `python app.py` to start.")