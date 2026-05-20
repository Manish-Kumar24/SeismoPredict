# 🌍 SeismoPredict | Real-Time Earthquake Risk Estimator & Monitor

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![Scikit-learn](https://img.shields.io/badge/ML-Scikit--learn-orange?logo=scikit-learn)](https://scikit-learn.org/)
[![USGS](https://img.shields.io/badge/Data-USGS%20API-green)](https://earthquake.usgs.gov/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📖 Overview
**SeismoPredict** is a real-time web application that estimates seismic risk using machine learning and live earthquake data from the USGS. It combines spatial feature engineering, tectonic zone encoding, and historical magnitude distributions to provide probabilistic risk assessments for any given coordinates and depth.

> ⚠️ **Educational Purpose Only**: This tool demonstrates ML-based seismic pattern recognition. It **cannot predict earthquakes** in real-time. Always rely on official agencies (USGS, EMSC, local geological surveys) for emergency alerts.

---

## ✨ Features
- 🌐 **Live Earthquake Feed**: Auto-refreshing global seismic activity (M2.5+, last 24h)
- 🧠 **ML Risk Estimation**: `HistGradientBoostingRegressor` trained on 1-year USGS data
- 🗺️ **Tectonic-Aware Modeling**: Encodes plate boundary proximity & depth-log scaling
- 📱 **Responsive Dashboard**: Modern UI built with Bootstrap 5
- 🔄 **Real-Time API**: `/api/live` endpoint for JSON feeds & external integrations
- 🛡️ **Graceful Fallbacks**: Offline/local dataset support if USGS API is unavailable

---

## 🛠️ Tech Stack
| Layer | Technology |
|-------|------------|
| **Backend** | Flask, Scikit-learn, Pandas, NumPy |
| **Frontend** | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| **Data Source** | USGS Earthquake Hazards Program API |
| **ML Pipeline** | Feature engineering → Stratified balancing → HGBR → Pickle serialization |

---

## 📁 Project Structure

```text
Earthquake-Predictor/
├── app.py                 # Flask web server & routing
├── detector.py            # Model training pipeline (run first!)
├── model.pkl              # Serialized ML model (generated)
├── requirements.txt       # Python dependencies
├── dataset.csv            # Fallback/local dataset (optional)
└── templates/
    ├── index.html         # Main dashboard & prediction UI
    └── error.html         # Error handling template

```

---

## 🚀 Installation & Setup

### 1. Clone & Enter Directory
```bash
git clone https://github.com/yourusername/SeismoPredict.git
cd SeismoPredict
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Train the Model (Required Before First Run)
```bash
python detector.py
```
✅ Fetches ~10,000+ earthquakes from USGS, engineers features, balances magnitudes, and saves model.pkl.

### 4. Start the Web Server
```bash
python app.py
```
🌐 Open http://127.0.0.1:5000 in your browser.

---

## 🌐 How to Use

### 🔮 Predict Seismic Risk

1. Enter coordinates & depth  
   *(Example: Tokyo → Lat: 35.68, Lon: 139.69, Depth: 35)*

2. Click **Predict Magnitude & Risk**

3. View the categorized risk level  
   *(Minor → Severe)*

## 📡 Live Data API

Access the real-time earthquake JSON feed:

```bash
curl http://127.0.0.1:5000/api/live
```

## 🧪 Quick Test Cases

| Location              | Lat   | Lon    | Depth | Expected Risk |
|----------------------|-------|--------|--------|----------------|
| Tokyo, Japan         | 35.68 | 139.69 | 35     | 🔴 High |
| Santiago, Chile      | -33.45 | -70.67 | 25     | 🔴 High |
| Sydney, Australia    | -33.86 | 151.21 | 20     | 🟢 Low |
| Reykjavik, Iceland   | 64.14 | -21.94 | 5      | 🟡 Moderate |

---

## 📊 Model & Data Pipeline

- **Data Source:** `USGS 2.5_year.geojson` *(~10k–15k earthquake events)*

- **Features:**
  - `abs_lat`
  - `log1p(depth)`
  - `lat_lon_interaction`
  - `tectonic_zone`

- **Balancing:**  
  Oversamples `M ≥ 6.0` events **3×** to reduce regression-to-mean bias.

- **Algorithm:**  
  `HistGradientBoostingRegressor` with:
  - Early stopping
  - `300` estimators

- **Evaluation Metrics:**
  - **MAE:** `~0.45`
  - **R² Score:** `~0.68` on held-out test set

--- 

## ⚠️ Scientific Disclaimer

Earthquakes are governed by complex, non-linear tectonic stress accumulation. No current scientific method can reliably predict the exact time, location, or magnitude of future earthquakes.

This project estimates probabilistic historical patterns based on coordinates and depth. It is designed for **educational, demonstration, and research prototyping purposes only**.

For real-world hazard assessment, consult:
- **Probabilistic Seismic Hazard Analysis (PSHA)** frameworks
- Official geological and seismic monitoring agencies

---

## 🔮 Future Roadmap

- 🗺️ Interactive `Leaflet.js` map with click-to-predict & heatmap overlay

- 📊 `SQLite` / `PostgreSQL` logging for prediction history & trend analysis

- 📧 Email/SMS alert system for high-risk predictions

- 🐳 `Docker Compose` setup + `GitHub Actions` CI/CD pipeline

- 🔄 Probabilistic output: `P(M > 6 | location)` using calibrated classifiers

- 📐 Add real fault-distance features using `GPlates` / `USGS` shapefiles

--- 

## 📄 License

This project is licensed under the **MIT License**.

USGS earthquake data is in the **public domain**.  
Model outputs are intended for **educational and research purposes only**.

---

## 🤝 Contributing

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature/amazing-feature
```

3. Commit your changes
```bash
git commit -m "Add amazing feature"
```

4. Push to the branch
```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request

---

## 📬 Contact & Credits

- **Data:** USGS Earthquake Hazards Program

- **ML Framework:** Scikit-learn & Pandas

- **Web Framework:** Flask & Bootstrap 5

- **Built by:** Manish Kumar 

⭐ If you found this project helpful, consider starring the repository!

---