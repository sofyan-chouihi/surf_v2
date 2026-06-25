"""
@author: Chouihi Sofyan - green813
Module: config
Description: Paramètres de configuration du projet (spots, indicateurs et chemin base de données ).
"""

DB_PATH: str = "spots.db"

MARINE_INDICATORS_LIST: list[str] = [
    "sea_level_height_msl",
    "swell_wave_height",
    "swell_wave_peak_period",
    "swell_wave_direction"
]

WIND_INDICATORS_LIST: list[str] = [
    "wind_speed_10m",
    "wind_direction_10m"
]

DEFAULT_SPOT_LIST: list[dict[str, float | str]] = [
    {"name": "Penfoul", "lat": 48.53088223489344, "long": -4.748379916062399},
    {"name": "Petit Minou", "lat": 48.34091784235447, "long": -4.6152373332512555},
]