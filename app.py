<<<<<<< HEAD
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

        # Feature engineering must match detector.py
        abs_lat = abs(lat)
        depth_log = np.log1p(depth)
        lat_lon_int = lat * lon
        
        def get_zone(la, lo):
            if (la > -60 and la < 60) and ((lo > 120) or (lo < -100)): return 3
            elif 20 < la < 50 and -10 < lo < 120: return 2
            else: return 1

        zone = get_zone(lat, lon)
        features = np.array([[abs_lat, depth_log, lat_lon_int, zone]])
        
        pred_mag = model.predict(features)[0]
        pred_mag = np.clip(pred_mag, 2.5, 9.0)  # Clamp to realistic range

        # Risk categorization
        if pred_mag < 4.0:
            risk, color = "Minor / Low Risk", "success"
        elif pred_mag < 6.0:
            risk, color = "Moderate Risk", "warning"
        elif pred_mag < 7.5:
            risk, color = "High Risk", "danger"
        else:
            risk, color = "Severe / Very High Risk", "dark"

        return render_template("index.html", 
                               predicted=True,
                               magnitude=f"{pred_mag:.1f}",
                               risk=risk,
                               risk_color=color)
    except Exception as e:
        return render_template("error.html", error=str(e))

@app.route("/api/live")
def live_data():
    return jsonify(get_recent_quakes())

if __name__ == "__main__":
=======
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

        # Feature engineering must match detector.py
        abs_lat = abs(lat)
        depth_log = np.log1p(depth)
        lat_lon_int = lat * lon
        
        def get_zone(la, lo):
            if (la > -60 and la < 60) and ((lo > 120) or (lo < -100)): return 3
            elif 20 < la < 50 and -10 < lo < 120: return 2
            else: return 1

        zone = get_zone(lat, lon)
        features = np.array([[abs_lat, depth_log, lat_lon_int, zone]])
        
        pred_mag = model.predict(features)[0]
        pred_mag = np.clip(pred_mag, 2.5, 9.0)  # Clamp to realistic range

        # Risk categorization
        if pred_mag < 4.0:
            risk, color = "Minor / Low Risk", "success"
        elif pred_mag < 6.0:
            risk, color = "Moderate Risk", "warning"
        elif pred_mag < 7.5:
            risk, color = "High Risk", "danger"
        else:
            risk, color = "Severe / Very High Risk", "dark"

        return render_template("index.html", 
                               predicted=True,
                               magnitude=f"{pred_mag:.1f}",
                               risk=risk,
                               risk_color=color)
    except Exception as e:
        return render_template("error.html", error=str(e))

@app.route("/api/live")
def live_data():
    return jsonify(get_recent_quakes())

if __name__ == "__main__":
>>>>>>> d99af0c5591eebdea886b909914a22b25ab07a80
    app.run(debug=True, port=5000)