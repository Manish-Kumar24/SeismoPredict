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
Earthquake-Predictor/
├── app.py # Flask web server & routing
├── detector.py # Model training pipeline (run first!)
├── model.pkl # Serialized ML model (generated)
├── requirements.txt # Python dependencies
├── dataset.csv # Fallback/local dataset (optional)
└── templates/
├── index.html # Main dashboard & prediction UI
└── error.html # Error handling template