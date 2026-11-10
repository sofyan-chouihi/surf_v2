"""
@author: Chouihi Sofyan - green813
Module: extraction
Description: Gère la construction et l'appel à l'API Open-Meteo pour récupérer les données.
"""


import streamlit as st
import pandas as pd

from storage import load_spots, init_db, save_spots
from config import DEFAULT_SPOT_LIST, MARINE_INDICATORS_LIST, WIND_INDICATORS_LIST
from spots import SpotBuilder
from analysis import ForecastAnalyzer, PenfoulScoreVisitor, PetitMinouScoreVisitor


st.set_page_config(layout="wide", page_title="Surf Forecast App", page_icon="🌊")


@st.cache_data
def load_and_init_db(spots_list):
    init_db()
    save_spots(spots_list)
    return load_spots()


def parse_objects_to_display(df_objects):
    rows = []
    for _, row in df_objects.iterrows():
        t, s, w = row['tide'], row['swell'], row['wind']
        score = row.get('score', 0)
        vent_nds = w.value / 1.852 if pd.notna(w.value) else 0
        dirs = ['↓', '↙', '←', '↖', '↑', '↗', '→', '↘']
        ix = int((w.wind_direction_10m + 22.5) // 45) % 8
        local_hour = t.hour.tz_convert('Europe/Paris')

        rows.append({
            "Date": local_hour.strftime("%d/%m"),
            "Time": local_hour.strftime("%H:00"),
            "Tide (m)": round(t.value, 2),
            "Swell (m)": round(s.value, 2),
            "Period (s)": round(s.swell_wave_peak_period, 1) if pd.notna(s.swell_wave_peak_period) else 0,
            "Wind (kts)": round(vent_nds, 1),
            "Direction": dirs[ix],
            "Score": score
        })
    return pd.DataFrame(rows)


st.title("🌊️ Surf Forecast Analyzer")
st.markdown("Algorithmic forecasts and session scoring in Brittany.")

SPOTS_LIST = load_and_init_db(DEFAULT_SPOT_LIST)
spot_names = [spot['name'] for spot in SPOTS_LIST]

chosen_spot_name = st.sidebar.selectbox("🎯 Select a spot", spot_names)
spot_dict = next(item for item in SPOTS_LIST if item["name"] == chosen_spot_name)

with st.spinner('Analyzing conditions...'):
    builder = SpotBuilder(**spot_dict)
    spot = builder.construct_with_api(MARINE_INDICATORS_LIST, WIND_INDICATORS_LIST)
    df_raw = spot.marine_indicators

    visitor = PenfoulScoreVisitor(df_raw) if chosen_spot_name == "Penfoul" else PetitMinouScoreVisitor(df_raw)
    analyzer = ForecastAnalyzer(df_raw, visitor)
    df_best = analyzer.get_best_session()

    df_all_display = parse_objects_to_display(analyzer.df_spot)
    df_best_display = parse_objects_to_display(df_best)


st.markdown("### 🥇 Next Optimal Session")

now = pd.Timestamp.now(tz='Europe/Paris')

futures_sessions = df_best[df_best['tide'].apply(lambda tide_obj: tide_obj.hour >= now)]

if not futures_sessions.empty:
    prochaine_session_brute = futures_sessions.head(1)

    top_session = parse_objects_to_display(prochaine_session_brute).iloc[0]

    col1, col2 = st.columns(2)
    col1.metric("When?", f"{top_session['Date']} at {top_session['Time']}")
    col2.metric("Score", f"{top_session['Score']} / 3")

    st.markdown("<br>", unsafe_allow_html=True)  # Un petit espace

    col3, col4, col5 = st.columns(3)
    col3.metric("Swell", f"{top_session['Swell (m)']} m")
    col4.metric("Period", f"{top_session['Period (s)']} s")
    col5.metric("Wind", f"{top_session['Wind (kts)']} kts {top_session['Direction']}")

else:
    st.info("No optimal session forecast in the coming hours. Time to rest!")

st.divider()

st.markdown("### 📈 72h Trends")

df_chart = df_all_display.copy()
df_chart['Datetime'] = df_chart['Date'] + " " + df_chart['Time']
df_chart = df_chart.set_index('Datetime')

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.caption("Tide (m)")
    st.line_chart(df_chart['Tide (m)'], color="#1f77b4")

with row1_col2:
    st.caption("Swell Height (m)")
    st.area_chart(df_chart['Swell (m)'], color="#2ca02c")

st.markdown("<br>", unsafe_allow_html=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.caption("Swell Period (s)")
    st.area_chart(df_chart['Period (s)'], color="#ff7f0e")

with row2_col2:
    st.caption("Score")
    st.bar_chart(df_chart['Score'], color="#ff0000")

st.markdown("### 📊 Detailed Data")
tab1, tab2 = st.tabs(["🔥 Best Sessions", "📅 All Forecasts"])

with tab1:
    st.dataframe(df_best_display, use_container_width=True, hide_index=True)
with tab2:
    st.dataframe(df_all_display, use_container_width=True, hide_index=True)