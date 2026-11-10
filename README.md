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

<img width="1280" height="811" alt="1787930353652" src="https://github.com/user-attachments/assets/ca700cfc-8aed-4134-97cc-1c411e141ae4" />

## How to Run
```bash
pip install -r requirements.txt
streamlit run dashboard.py

