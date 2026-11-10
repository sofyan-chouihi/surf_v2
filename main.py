"""
@author: Chouihi Sofyan - green813
Module: main
Description: Orchestre les différentes classes pour établir les différents DataFrames de spot et best session
"""

from spots import SpotBuilder
from analysis import ForecastAnalyzer, PenfoulScoreVisitor, PetitMinouScoreVisitor
from config import MARINE_INDICATORS_LIST, WIND_INDICATORS_LIST, DEFAULT_SPOT_LIST
from storage import init_db, save_spots, load_spots

if __name__ == "__main__":

    # INFORMATION  : --- Initialisation et chargement des spots depuis SQLite ---
    init_db()
    save_spots(DEFAULT_SPOT_LIST)
    SPOT_LIST = load_spots()

    # INFORMATION : --- Construction du spot sélectionné (0 pour Penfoul, 1 pour PetitMinou) ---
    builder = SpotBuilder(
        **SPOT_LIST[1]
    )  # ** <=> déballage : SpotBuilder(name="Penfoul", lat=48.53, long=-4.74)
    spot = builder.construct_with_api(MARINE_INDICATORS_LIST, WIND_INDICATORS_LIST)
    marine_indicator_df = spot.marine_indicators
    print(f"\n### Spot : {spot.name} ###")
    print(marine_indicator_df.head())

    # for row in marine_indicator_df['tide']:
    # print(row.value)

    # print(marine_indicator_df['tide'].iloc[0])

    # INFORMATION :  --- Analyse, notation et extraction des meilleure session ---
    visitor = PetitMinouScoreVisitor(marine_indicator_df)
    forecast_analyzer = ForecastAnalyzer(marine_indicator_df, visitor)
    best_df = forecast_analyzer.get_best_session()
    print(
        f"\n### Meilleures sessions -> {len(best_df)} créneaux sur les 72 prochaines heures ###"
    )
    print(best_df.head())

    # INFORMATION :  --- Benchmark calcul vectoriel vs non-vectoriel ---
    print(f"\n### Benchmark vitesse de marée###")
    spot.benchmark_tide_speed()
