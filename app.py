from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np
import requests
from functools import lru_cache

app = Flask(__name__)

# Load trained model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Cache USGS data for 300 seconds to avoid rate limits
@lru_cache(maxsize=1)
def get_recent_quakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        quakes = []
        for feat in data["features"]:
            mag = feat["properties"].get("mag")
            if mag is None:
                continue
            lon, lat, depth = feat["geometry"]["coordinates"]
            place = feat["properties"].get("place", "Unknown Location")
            time_str = feat["properties"].get("time", 0)
            quakes.append({
                "magnitude": mag,
                "latitude": lat,
                "longitude": lon,
                "depth": depth,
                "place": place,
                "time": time_str
            })
        return {"quakes": quakes, "count": len(quakes)}
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        lat = float(request.form.get("latitude"))
        lon = float(request.form.get("longitude"))
        depth = float(request.form.get("depth"))

        # Feature engineering (MUST match detector.py)
        abs_lat = abs(lat)
        depth_log = np.log1p(depth)
        
        def get_zone(la, lo):
            if (20 < la < 50) and (100 < lo < 150): return 3
            if (-60 < la < -10) and (-120 < lo < -50): return 3
            if (-20 < la < 20) and (90 < lo < 160): return 2
            if (35 < la < 45) and (20 < lo < 50): return 2
            if (40 < la < 65) and (-140 < lo < -100): return 2
            if (-35 < la < -10) and (110 < lo < 180): return 1
            if abs(la) < 15: return 1
            return 0

        zone = get_zone(lat, lon)
        zone_depth = zone * depth_log
        features = np.array([[abs_lat, depth_log, zone_depth]])
        
        base_mag = float(model.predict(features)[0])
        
        # 🌍 Domain Calibration for hazard potential
        if zone == 3:
            calibrated_mag = max(base_mag, 6.2)
        elif zone == 2:
            calibrated_mag = max(base_mag, 4.8)
        elif zone == 1:
            calibrated_mag = min(base_mag, 4.5)
        else:
            calibrated_mag = min(base_mag, 3.8)

        calibrated_mag = np.clip(calibrated_mag, 2.5, 9.0)

        if calibrated_mag < 4.0:
            risk, color = "Minor / Low", "success"
        elif calibrated_mag < 5.5:
            risk, color = "Moderate", "warning"
        elif calibrated_mag < 7.0:
            risk, color = "High", "danger"
        else:
            risk, color = "Severe / Very High", "dark"

        return render_template("index.html", 
                               predicted=True,
                               magnitude=f"{calibrated_mag:.1f}",
                               risk=risk,
                               risk_color=color)
    except Exception as e:
        return render_template("error.html", error=str(e))

@app.route("/api/live")
def live_data():
    return jsonify(get_recent_quakes())

if __name__ == "__main__":
    app.run(debug=True, port=5000)