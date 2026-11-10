# Surf Forecast Analyzer

Demo : https://www.youtube.com/watch?v=LJ_qfxctM_Y

A Python-based web application that automates marine weather forecasting and algorithmic session scoring for surf spots in Brittany.

## Tech Stack
* **Core:** Python, Pandas, NumPy
* **Architecture:** Object-Oriented Programming (Builder & Visitor patterns)
* **Frontend:** Streamlit
* **Data & Storage:** Open-Meteo APIs, SQLite

## Key Features
* **Vectorized Computations:** Fast tide speed and peak calculations using Pandas `diff()` and boolean masking.
* **Dynamic Scoring:** Custom algorithms evaluating swell period, wave height, and precise offshore wind angles per spot.
* **Interactive Dashboard:** 72-hour visual trend analysis and "next best session" detection.

## How to Run
```bash
pip install -r requirements.txt
streamlit run dashboard.py
