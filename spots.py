"""
@author: Chouihi Sofyan - green813
Module: spots
Description: Contient les classes Spot et SpotBuilder pour assembler les données maritimes.
"""

import pandas as pd
import time
from extraction import Extraction, WindExtraction
from indicators import Tide, Wind, Swell

class Spot:
    """
    Construit un objet Spot à partir de son nom, de ses coordonnées et des objets indicateurs marins voulus (ex. : Swell, Tide, etc.).

    Args:
        name: Le nom du spot.
        lat: La latitude.
        long: La longitude.

    Attributes:
        name: Nom du spot.
        lat: Latitude.
        long: Longitude.
        marine_indicators: DataFrame stockant les objets indicateurs (Swell, Tide, etc.).
    """
    def __init__(self,name: str, lat: float,long: float)-> None:
        self.name: str = name
        self.lat: float = lat
        self.long: float = long
        self.marine_indicators: pd.DataFrame = pd.DataFrame()

    def add_indicator(self, marine_indicator: object)->None:
        """
        Ajoute l'objet marine_indicator à l'attribut de l'objet Spot stockant le df d'indicateur marin comme ça :
                                                      tide                                              swell
        1  Tide(2026-05-09 00:00:00+00:00,sea_level_heigh...  Swell(2026-05-09 00:00:00+00:00,wave_height:0....
        2  Tide(2026-05-09 01:00:00+00:00,sea_level_heigh...  Swell(2026-05-09 01:00:00+00:00,wave_height:0....
        3  Tide(2026-05-09 02:00:00+00:00,sea_level_heigh...  Swell(2026-05-09 02:00:00+00:00,wave_height:0....
        4  Tide(2026-05-09 03:00:00+00:00,sea_level_heigh...  Swell(2026-05-09 03:00:00+00:00,wave_height:0....
        5  Tide(2026-05-0
        9 04:00:00+00:00,sea_level_heigh...  Swell(2026-05-09 04:00:00+00:00,wave_height:0....
        :param marine_indicator: objet de l'indicateur marin voulu
        :return : None
        """

        col_name = type(marine_indicator).__name__.lower()
        if self.marine_indicators.empty :
            self.marine_indicators[col_name] = pd.Series(dtype=object)
            idx = self.marine_indicators[col_name].count()

            self.marine_indicators.loc[idx+1, col_name] = marine_indicator
        elif col_name in self.marine_indicators.columns:
            idx = self.marine_indicators[col_name].count()
            self.marine_indicators.loc[idx+1, col_name] = marine_indicator

        else :
            if col_name not in self.marine_indicators.columns:
                self.marine_indicators[col_name] = pd.Series(dtype=object)
            idx = self.marine_indicators[col_name].count()
            self.marine_indicators.loc[idx+1, col_name] = marine_indicator

    def compute_tide_speed_vectorial(self) -> None:
        """
        Calcule la vitesse de marée en utilisant une approche vectorielle, soit la méthode diff() qui
        permet de faire une pente avec la valeur dans la case de l'indice précédent dans la même colonne

        :return: None
        """
        values =[obj.value for obj in self.marine_indicators['tide']]
        speeds = pd.Series(values).diff().fillna(0)
        for i,obj in enumerate(self.marine_indicators['tide']):
            obj.tide_speed = speeds[i]

    def compute_tide_speed_non_vectorial(self) -> None:
        """
        Calcule la vitesse de marée en utilisant une approche non vectorielle,
        soit en bouclant sur la colonne du DataFrame, en faisant (valeur_n - valeur_(n-1)) [m.h^{-1}] / 1 [h])

        :return: None
        """
        values = [obj.value for obj in self.marine_indicators['tide']]
        speeds = pd.Series([0.0]*len(values))
        for i in range(1,len(self.marine_indicators['tide'])):
            speeds[i] = (values[i]-values[i-1])/1

    def benchmark_tide_speed(self)-> None :
        """
        Calcule et print les vitesses de calcul des méthodes vectorielle et non vectorielle de calcul des vitesses de marées
        :return: None
        """
        start = time.time()
        self.compute_tide_speed_vectorial()
        t_vectorial = time.time() - start

        start = time.time()
        self.compute_tide_speed_non_vectorial()
        t_non_vectorial = time.time() - start

        print(f"Vectoriel : {t_vectorial:.6f}s")
        print(f"Non vectoriel : {t_non_vectorial:.6f}s")

    def state_tide(self)-> None:
        """
        Calcule l'état de la marée, si montante ou descendante.
        :return: None
        """
        for _, obj in enumerate(self.marine_indicators['tide']):
            if obj.tide_speed < 0:
                obj.tide_state = "descendante"
            elif obj.tide_speed > 0:
                obj.tide_state = "montante"
            else:
                obj.tide_state = pd.NA

    def compute_mid_tide(self)-> None:
        """
        Calcule par méthode vectorielle l'état précis de la marée, à savoir si elle est en peak
        ou à mi-marée.

        La méthode consiste à créer deux vecteurs avec les vitesses et les horaires de marées.
        On part du principe que le peak dure 2h, là où la marée passe de montante à descendante.
        L'on identifie la fenêtre du peak de deux heures par deux produits (v_H * v_(H-1)) et (v_H * v_(H+1))
        qui doivent par définition toujours être négatifs. La fenêtre ainsi identifiée sert de masque booléen.
        Ce masque booléen est créé en pipant (equivalent OR) les deux conditions et appliqué sur le vecteur horaire,
        ne capturant que les rows répondant favorablement aux conditions du masque.
        On boucle ensuite en calculant la distance entre l'heure de l'élément en cours de la boucle et les 2h de peak :
        si nulle alors c'est un peak, si non nulle alors c'est une mi-marée.

        :return: None
        """
        tide_objects = self.marine_indicators['tide'] #pd.Series
        tide_speeds = pd.Series([obj.tide_speed for obj in tide_objects])
        tide_times = pd.Series([obj.hour for obj in tide_objects])
        is_before_crossing = (tide_speeds.shift(-1) * tide_speeds < 0).fillna(False)
        is_after_crossing = (tide_speeds.shift(1)*tide_speeds <=0).fillna(False)#fillNan*Nan en False pour les 1ere cases #booleen #shift -> décalage d'une case de la colonne vers le bas
        is_2h_peak = is_before_crossing | is_after_crossing # | : pipe \eq or
        peak_timestamps = tide_times[is_2h_peak] #masquage booleen sur le vecteur tide_times
        #pd.Series indépendant (recréée)
        for obj in tide_objects:
            distance_to_peak=abs(peak_timestamps-obj.hour).min() #pour variation du courant proche des pic
            #slacking -> eau bouge peu, dead mid tide eau bouge le plus vite (regle des 12e) , préciser l'algo un jour
            if distance_to_peak == pd.Timedelta(hours=0):
                obj.tide_state_precision = "peak"
            else:
                obj.tide_state_precision = "mid-tide"



class SpotBuilder:
    """
    Construit l'objet Spot à partir du nom et coords et y ajoute les objets indicateurs marins en extrayant les données
    via l'appel à l'api construite par l'objet d'extraction
    Args :
        name: nom du spot
        lat : latitude du spot
        long: longitude du spot
    Attributes:
        spot: stockage de l'objet Spot avec les paramètres name, lat, long.
    """

    def __init__(self, name: str, lat: float, long: float)-> None:

        self.spot: object = Spot(name, lat, long)

    def construct_with_api(self, marine_indicators_list: list[str],wind_indicators_list: list[str]) -> object :
        """
        Construit l'objet Spot à partir du nom et coords et y ajoute les objets indicateurs marins en extrayant les données
        via l'appel à l'api construite par l'objet d'extraction
        :param marine_indicators_list: liste des indicateurs marins
        :param wind_indicators_list: liste des indicateurs de vent
        :return: l'objet Spot mis à jour avec les indicateurs marins voulu.
        """
        self._build_marine_indicator(marine_indicators_list)
        self._build_wind_indicator(wind_indicators_list)
        return self.spot
    def _build_marine_indicator(self, marine_indicators_list:list) -> None:
        """
        Extrait les données de houle et de marée via l'appel à l'API et les injecte dans l'objet Spot.

        Pour la houle (car 3 valeurs à récupérer), la méthode consiste à utiliser un dictionnaire tampon (swell_buffer).
        Comme l'API nous renvoie la hauteur, la période et la direction de manière séparée,
        on capture les rows et on les stocke par heure dans le buffer. Une fois la boucle
        d'extraction terminée, on itère sur ce buffer pour assembler nos objets Swell avec
        les trois paramètres qui vont bien.
        L'indicateur de marée (Tide) étant unique, il est instancié directement.

        :param marine_indicators_list: liste des indicateurs marins à extraire
        :return: None
        """

        swell_buffer = {}
        for indicator in marine_indicators_list: #appel un df heure et valeur indicator
            extraction = Extraction(self.spot.lat, self.spot.long, indicator)
            params = extraction.api_construction()
            _, df = extraction.api_call(params)
            for _, row in df.iterrows():
                if indicator == "swell_wave_height":
                    if row['date'] not in swell_buffer: #row['date'] intérieur de la case
                        swell_buffer[row['date']] = {}  #swell_buffer[row['date']] : pose un dic dans la valeur de la clé row['date'] du dit swell buffer
                    swell_buffer[row['date']]['swell_wave_height'] = row[indicator] #ouvre la valeur de la clé 'swell_wave_height'
                    # elle meme sous clé de la clé row['date'] dont la valeur est le dic avec pour clé 'swell_wave_height'

                if indicator == "swell_wave_peak_period":
                    swell_buffer[row['date']]['swell_wave_peak_period'] = row[indicator]
                if indicator == "swell_wave_direction":
                    swell_buffer[row['date']]['swell_wave_direction'] = row[indicator]

                if indicator == "sea_level_height_msl":
                    object_tide = Tide(hour=row['date'], value=row[indicator])
                    self.spot.add_indicator(object_tide)
        for date, vals in swell_buffer.items():
            object_swell = Swell(hour=date, value_1=vals["swell_wave_height"], value_2=vals["swell_wave_peak_period"],
                                 value_3=vals["swell_wave_direction"])
            self.spot.add_indicator(object_swell)
        self.spot.compute_tide_speed_vectorial()
        self.spot.state_tide()
        self.spot.compute_mid_tide()
    def _build_wind_indicator(self,wind_indicators_list:list)-> None:
        """
        Extrait les données météo du vent via l'appel à l'API et les ajoute au Spot sur le même principe
        que pour la houle.

        :param wind_indicators_list: liste des indicateurs de vent à extraire
        :return: None
        """
        wind_buffer = {}
        for indicator in wind_indicators_list:
            wind_extraction = WindExtraction(self.spot.lat, self.spot.long, indicator)
            params = wind_extraction.api_construction()
            _, df = wind_extraction.api_call(params)
            for _, row in df.iterrows():
                if indicator == "wind_speed_10m":
                    if row['date'] not in wind_buffer:
                        wind_buffer[row['date']] = {}
                    wind_buffer[row['date']]["wind_speed_10m"] = row[indicator]
                if indicator == "wind_direction_10m":
                    wind_buffer[row['date']]["wind_direction_10m"] = row[indicator]
        for date, vals in wind_buffer.items():
            object_wind = Wind(hour=date, value_1=vals["wind_speed_10m"], value_2=vals["wind_direction_10m"])
            self.spot.add_indicator(object_wind)

