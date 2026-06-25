"""
@author: Chouihi Sofyan - green813
Module: analysis
Description: Contient les classes de notation (via Visitor) et d'analyse des sessions.
"""

from abc import ABC, abstractmethod
import pandas as pd
from indicators import Tide, Wind, Swell



class ScoreVisitor(ABC):
    """
    Classe définissant le visiteur pour le calcul du score d'un spot.

    Permet de parcourir les différents indicateurs (Tide, Swell, Wind) d'un
    DataFrame et d'appliquer la logique de notation spécifiée
    dans les classes filles (PenfoulScoreVisitor et PetitMinouScoreVisitor).

    Args:
        df_spot: DataFrame contenant les données des indicateurs du spot.

    Attributes:
        df_spot: DataFrame contenant les données des indicateurs du spot.
        score: valeur du score calculé (défaut pd.NA).

    """
    def __init__(self,df_spot:pd.DataFrame)->None:
        self.df_spot:pd.DataFrame = df_spot
        self.score: float = pd.NA
    @abstractmethod
    def visit_tide(self,tide: Tide) -> float:
        """
        Méthode abstraite pour évaluer la condition de marée.

        :param tide: L'objet Tide à analyser.
        :return: Le score calculé pour la marée.
        """
        pass
    @abstractmethod
    def visit_swell(self,swell: Swell) -> float:
        """
        Méthode abstraite pour évaluer la condition de la houle.

        :param swell: L'objet Swell à analyser.
        :return: Le score calculé pour la houle.
        """
        pass
    @abstractmethod
    def visit_wind(self,wind: Wind) -> float:
        """
        Méthode abstraite pour évaluer la condition du vent.

        :param wind: L'objet Wind à analyser.
        :return: Le score calculé pour le vent.
        """
        pass
    def compute_score(self)-> pd.DataFrame:
        """
        Calcule le score global pour chaque créneau horaire du DataFrame.

        Itère sur toutes les lignes du DataFrame.
        Pour chaque ligne, le visiteur (self) est passé à la méthode 'accept' de chaque indicateur
        (tide, swell, wind) pour additionner leurs scores respectifs.
        Le résultat est stocké dans une nouvelle colonne 'score'.

        :return: Le DataFrame mis à jour avec la colonne 'score'
        """
        scores = []
        for i, row in self.df_spot.iterrows():
            score = row['tide'].accept(self) + row['swell'].accept(self) + row['wind'].accept(self)
            scores.append(score)
        self.df_spot['score'] = scores #Mutation en place du df_spot initial
        return self.df_spot

class PenfoulScoreVisitor(ScoreVisitor):
    """
    Visiteur spécifique pour calculer le score d'une session au spot de Penfoul.

    Applique des règles de notation personnalisées en fonction des conditions
    idéales de ce spot (mi-marée, vent offshore idéalement autour de 135°, etc..).
    """
    def visit_tide(self,tide: Tide) -> float:
        """
        Évalue les conditions de marée pour Penfoul.
        Le spot fonctionne idéalement à mi-marée.

        :param tide: L'objet Tide à analyser.
        :return: 1.0 si l'état précis est 'mid-tide', 0.0 sinon.
        """
        if tide.tide_state_precision == 'mid-tide':
            return 1
        else:
            return 0
    def visit_swell(self,swell: Swell) -> float:
        """
        Évalue les conditions de houle pour Penfoul.
        Nécessite une période supérieure à 8 secondes et une hauteur comprise
        entre 0.8m et 2m.

        :param swell: L'objet Swell à analyser.
        :return: 1.0 si les conditions sont optimales, 0.0 sinon.
        """
        if swell.swell_wave_peak_period > 8 and (swell.value > 0.8 and swell.value < 2)  :
            return 1
        else:
            return 0
    def visit_wind(self,wind: Wind) -> float:
        """
        Évalue les conditions de vent pour Penfoul.
        Le vent offshore parfait est à environ 135 degrés.

        :param wind: L'objet Wind à analyser.
        :return: 1.0 pour un vent faible et parfaitement orienté,
                 0.5 pour un vent un peu plus fort/désaxé,
                 0.0 sinon.

        """
        if wind.value < 20 and (75 < wind.wind_direction_10m < 195): #Vent offshore parfait 135 deg à Penfoul
            return 1
        elif 20 < wind.value < 35 and (195 < wind.wind_direction_10m < 255 or 15 < wind.wind_direction_10m < 75) :
            return 0.5
        else:
            return 0


class PetitMinouScoreVisitor(ScoreVisitor):
    """
    Visiteur spécifique pour calculer le score d'une session au spot du Petit Minou.

    Applique des règles de notation personnalisées en fonction des conditions
    idéales de ce spot (peak à marée basse, vent offshore idéalement autour de 45°, etc.).
    """
    def visit_tide(self, tide: Tide)->float:
        # parfait aux peaks marée basse
        """
        Évalue les conditions de marée pour le Petit Minou.
        Le spot fonctionne de manière optimale lors des peaks à marée basse.

        :param tide: L'objet Tide à analyser.
        :return: 1.0 si c'est un peak et que la marée est basse (hauteur < 0), 0.0 sinon.
        """
        if tide.tide_state_precision == 'peak' and tide.value < 0:
            return 1
        else:
            return 0

    def visit_swell(self, swell: Swell)-> float:
        """
        Évalue les conditions de houle pour le Petit Minou.
        Nécessite une période supérieure à 8 secondes et une hauteur comprise
        entre 0.8m et 2m.

        :param swell: L'objet Swell à analyser.
        :return: 1.0 si les conditions sont optimales, 0.0 sinon.
        """
        if swell.swell_wave_peak_period > 8 and (swell.value > 0.8 and swell.value < 2):
            return 1
        else:
            return 0

    def visit_wind(self, wind: Wind)-> float:
        """
        Évalue les conditions de vent pour le Petit Minou.
        Le vent offshore parfait est à environ 45 degrés.

        :param wind: L'objet Wind à analyser.
        :return: 1.0 pour un vent faible (<20 km/h) et parfaitement orienté (15° à 90°),
                 0.5 pour un vent modéré ou légèrement désaxé,
                 0.0 sinon.
        """
        # Vent offshore parfait 45 deg au Petit Minou
        if wind.value < 20 and (15 < wind.wind_direction_10m < 90):
            return 1
        elif 20 < wind.value < 35 and ( 0 < wind.wind_direction_10m < 15 or 90 < wind.wind_direction_10m < 105):
            return 0.5
        else:
            return 0

class BestSession:
    """
    Filtre les sessions d'un spot en fonction de leur score global.
    Args:
        df_scored: DataFrame contenant les indicateurs et la colonne 'score'.
    Attributes:
        df_scored: DataFrame initial contenant les scores.
        df_filtered: DataFrame filtré avec les meilleures sessions.
    """
    def __init__(self, df_scored: pd.DataFrame)-> None :
        self.df_scored: pd.DataFrame = df_scored
        self.df_filtred: pd.DataFrame = df_scored
    def filtering(self, score_min: float = 1.5) -> pd.DataFrame:
        """
        Applique un masque booléen pour ne conserver que les sessions
        ayant un score supérieur ou égal au score minimum requis.

        :param score_min: Le score minimum pour qu'une session soit validée (défaut: 1.5).
        :return: Le DataFrame contenant uniquement les meilleures sessions.

        """
        self.df_filtred = self.df_scored[self.df_scored['score'] >= score_min]#masque booleen
        return self.df_filtred

class ForecastAnalyzer:
    """
    Orchestre l'analyse des prévisions pour un spot donné.
    Combine le calcul des scores via un visiteur et le filtrage des meilleures sessions.

    Args:
        df_spot: DataFrame brut contenant les indicateurs marins.
        visitor: L'objet visiteur (ex: PenfoulScoreVisitor) pour calculer le score.

    Attributes:
        df_spot: DataFrame brut contenant les indicateurs marins.
        df_spot_filtered: DataFrame mis à jour contenant les meilleures sessions.
        visitor: Le visiteur instancié pour la notation du spot.
    Note : le df_spot est modifié dynamiquement par mutation en place lors du calcul du score.
    """
    def __init__(self,df_spot:pd.DataFrame,visitor:ScoreVisitor)-> None :
        self.df_spot: pd.DataFrame = df_spot
        self.df_spot_filtered:pd.DataFrame = df_spot
        self.visitor: ScoreVisitor = visitor
    def get_best_session(self)-> pd.DataFrame :
        """
        Calcule les scores de toutes les sessions prévues via le visiteur,
        puis filtre et retourne les meilleures sessions.

        :return: Un DataFrame avec les meilleures sessions trouvées.
        """
        score = self.visitor.compute_score()
        best_session = BestSession(score).filtering()
        return best_session

