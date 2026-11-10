"""
@author: Chouihi Sofyan - green813
Module: extraction
Description: Gère la construction et l'appel à l'API Open-Meteo pour récupérer les données.
"""

import pandas as pd
import openmeteo_requests

openmeteo = openmeteo_requests.Client()


class Extraction:
    """
    Extrait les données d'UN indicateur marin à un spot donné,
    caractérisé par sa latitude et longitude.
    Pour ce faire, construit l'API à appeler via les informations susmentionnées,
    puis l'appelle et stocke le tout dans un dataframe.
    Args:
        lat: Latitude du spot.
        long: Longitude du spot.
        marine_indicator_name: Nom de l'indicateur (ex: "wave_height")
    Attributes:
        lat: Latitude du spot.
        long: Longitude du spot.
        marine_indicator_name: Nom de l'indicateur (ex: "wave_height")
        url: brique url de base pour la construction de l'api

    """
    def __init__(self, lat: float, long: float, marine_indicator_name: str )-> None:
        self.lat: float= lat
        self.long: float = long
        self.marine_indicator_name: str = marine_indicator_name
        self.url: str = "https://marine-api.open-meteo.com/v1/marine"
    def api_construction(self)-> dict:
        """
        Récupère les arguments de l'objet créé pour les mettre dans un dictionnaire qui
        permettra ensuite d'appeler l'API de l'indicateur marin au spot voulu.

        :return: params: le dictionnaire contenant toutes les informations qui vont
        bien pour appeler l'API, soit la latitude, la longitude, le nom de l'indicateur marin
        et le début et la fin de la période voulue (ici, on restera que sur le forecast maximum
        gratuit, soit 7 jours).
        """
        params ={
            "latitude": self.lat,
            "longitude": self.long,
            "hourly" : self.marine_indicator_name,
            "past_days":0,
            "forecast_days":3, #Forecast limité par le nombre de jour ou peak_wave_period est fourni
        }
        return params
    def api_call(self, params: dict)-> tuple[object, pd.DataFrame]:
        """
        Récupère le dictionnaire params de la méthode "api_construction", construit et appelle l'API
        et renvoie les données d'OpenMeteo sous forme brute et sous forme rangée dans un DataFrame.
        :param params: Paramètres générés par api_construction
        :return: response: les données brutes de l'indicateur marin voulu au spot voulu
        d'OpenMeteo sous forme de liste.
        hourly_marine_indicator_dataframe: stockage des différentes données de la liste brute
        dans un DataFrame, les données sont triées via la librairie spécialisée d'OpenMeteo.

        """
        response = openmeteo.weather_api(self.url, params=params) #[<WeatherApiResponse>, <WeatherApiResponse>] #liste avec un objet par location
        response = response[0] #récupère le premier objet (API conçu pour le multi localisation)
        hourly = response.Hourly() #récupère-les datas par heures de forecast # d'un objet : VariablesWithTime
        #séparer par heure
        hourly_marine_indicator_value = hourly.Variables(0).ValuesAsNumpy()  #numpy.ndarray
        # Récupère l'indicateur marin unique (index 0) spécifié dans les paramètres de la requête
        # Extrait l'ensemble des données prévisionnelles sur la période et les convertit en tableau NumPy
        hourly_data = {"date": pd.date_range(
            # Convertit les Timestamps UNIX (secondes) de l'API en dates UTC lisibles
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            # Applique l'intervalle de temps défini par l'API (ex: 3600s pour des données horaires)
            freq=pd.Timedelta(seconds=hourly.Interval()),
            # Exclut la borne temporelle de fin pour éviter une ligne excédentaire (remplace 'closed="left"')
            inclusive="left" #closed="left" ?
            ),
            # Associe le tableau de valeurs NumPy à la clé correspondant au nom de l'indicateur marin
            self.marine_indicator_name: hourly_marine_indicator_value
        }

        #template transfo en df

        hourly_marine_indicator_dataframe = pd.DataFrame(data=hourly_data)

        hourly_marine_indicator_dataframe = hourly_marine_indicator_dataframe.fillna(0)

        return response, hourly_marine_indicator_dataframe

class WindExtraction(Extraction):
    """
    Extraction spécifique aux indicateurs de vent qui ne se trouvent pas à la même API.
    Args:
        lat: Latitude du spot.
        long: Longitude du spot.
        marine_indicator_name: Nom de l'indicateur (ex: "wave_height")
    Attributes:
        url: brique url de base pour la construction de l'api
    """
    def __init__(self,lat:float,long:float,marine_indicator_name:str)-> None:
        super().__init__(lat,long,marine_indicator_name)
        self.url: str= "https://api.open-meteo.com/v1/forecast"