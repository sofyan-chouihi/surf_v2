import streamlit as st

from storage import init_db, save_spots, load_spots
from config import DEFAULT_SPOT_LIST


st.title("Surf forecast & best sessions")

@st.cache_data
def save_spots_list_db(SPOTS_LIST):
    init_db()
    save_spots(SPOTS_LIST)
    SPOTS_LIST_DB = load_spots()
    return SPOTS_LIST_DB


def spot_choice_button():
    SPOTS_LIST = save_spots_list_db(DEFAULT_SPOT_LIST)
    spot_name = [spot['name'] for spot in SPOTS_LIST]
    choose_spot= st.selectbox("Choose your surf spot in Britanny :", spot_name)
    st.write (f"The choosen spot is : {choose_spot}")
    return choose_spot

chosen_spot = spot_choice_button()






