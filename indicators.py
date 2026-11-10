"""
@author: Chouihi Sofyan - green813
Module: indicators
Description: Contient les classes pour les indicateurs marins.
"""

from abc import ABC, abstractmethod
import pandas as pd


class MarineIndicator(ABC):
    """
    Construit un moule d'objet d'indicateur marin.
    Args:
        hour: l'heure de la mesure.
        value: valeur numérique (ex : 2 m, 3 km/h, etc.).

    Attributes:
        hour: Heure précise de la mesure.
        value: Stockage de la donnée numérique de l'indicateur.
    """

    def __init__(self, hour: pd.Timestamp, value: float) -> None:
        self.hour: pd.Timestamp = hour
        self.value: float = value

    @abstractmethod
    def accept(self, visitor: object) -> float:
        """
        Point d'entrée pour le Design Pattern Visiteur, en abstract ici.

        Permet à ScoreVisitor et à ses classes filles (PenfoulScoreVisitor, PetitMinouScoreVisitor)
        d'exécuter le calcul du score sur MarineIndicator et ses classes filles (Tide, Swell et Wind)
        sans avoir à modifier leurs structures. L'objet se passe lui-même en argument
        à la méthode dédiée du visiteur.

        :param visitor: Le visiteur qui vient analyser l'objet.
        :return: Le score calculé par le visiteur.
        """
        pass


class Tide(MarineIndicator):
    """
    Indicateur spécifique pour le niveau de la mer (Marée).
    Args:
        hour: Heure de la mesure de la marée.
        value: Hauteur d'eau en mètres (par rapport au MeanSeaLevel).

    Attributes:
        hour: Heure de la mesure de la marée.
        value: Hauteur d'eau en mètres (par rapport au MeanSeaLevel).
        tide_speed: Vitesse de variation de la marée en m/h.
        tide_state: État de la marée ("montante", "descendante" ou pd.NA).
        tide_state_precision: État précis de la marée ("peak" ou "mid-tide")

    """

    def __init__(self, hour: pd.Timestamp, value: float) -> None:
        super().__init__(hour, value)
        self.tide_speed: float = 0
        self.tide_state: str = pd.NA
        self.tide_state_precision: str = pd.NA

    def association(self, sea_level_height_msl: float) -> float:
        """
        Associe la valeur de hauteur d'eau à l'attribut de l'objet Tide.
        :param sea_level_height_msl: hauteur d'eau
        :return: hauteur d'eau associée
        """
        self.value: float = sea_level_height_msl
        return sea_level_height_msl

    def accept(self, visitor: object) -> float:
        """
        Point d'entrée du visiteur spécifique à Tide.
        Redirige l'exécution vers la méthode visit_tide du visiteur.

        :param visitor: Le visiteur qui vient analyser l'objet.
        :return: Le score calculé par le visiteur
        """
        return visitor.visit_tide(self)

    def __str__(self) -> str:
        """
        Établit l'impression syntaxique de l'objet Tide via ses arguments.
        :return : impression syntaxique.
        """
        return f"Tide({self.hour},sea_level_height_msl:{self.value} m,tide_speed:{self.tide_speed} m/h,tide_state:{self.tide_state},tide_state_precision:{self.tide_state_precision})"

    __repr__ = __str__  # __repr__ surcharge la representation du df par la surcharge de __str__


class Swell(MarineIndicator):
    """
    Indicateur spécifique pour la houle (Swell).
    Args:
        hour: Heure de la mesure de houle.
        value_1: Hauteur des vagues en mètres.
        value_2: Période de la houle au max en secondes.
        value_3: Direction de la houle en degrés.

    Attributes:
        hour: Heure de la mesure de houle.
        value: Hauteur des vagues en mètres.
        swell_wave_peak_period: Période de la houle au max en secondes.
        swell_wave_direction: Direction de la houle en degrés

    """

    def __init__(
        self, hour: pd.Timestamp, value_1: float, value_2: float, value_3: float
    ) -> None:
        super().__init__(hour, value_1)
        self.swell_wave_peak_period: float = value_2
        self.swell_wave_direction: float = value_3

    def association(self, swell_wave_height: float) -> float:
        """
        Associe la valeur hauteur de vague à l'attribut de l'objet Swell.
        :param swell_wave_height: hauteur de vague
        :return: hauteur de vague associée
        """
        self.value: float = swell_wave_height
        return swell_wave_height

    def accept(self, visitor: object) -> float:
        """
        Point d'entrée du visiteur spécifique à Swell.
        Redirige l'exécution vers la méthode visit_swell du visiteur.

        :param visitor: Le visiteur qui vient analyser l'objet.
        :return: Le score calculé par le visiteur
        """
        return visitor.visit_swell(self)

    def __str__(self) -> str:
        """
        Établit l'impression syntaxique de l'objet Swell via ses arguments.
        :return : impression syntaxique.
        """
        return f"Swell({self.hour},swell_wave_height:{self.value}m,swell_wave_peak_period:{self.swell_wave_peak_period}s,swell_wave_direction:{self.swell_wave_direction}deg)"

    __repr__ = __str__


class Wind(MarineIndicator):
    """
    Indicateur spécifique pour le vent (Wind).

    Args:
        hour: Heure de la mesure de vent.
        value_1: Vitesse du vent en km/h.
        value_2: Direction du vent à 10m d'altitude en degrés
    Attributes:
        hour: Heure de la mesure.
        value: Vitesse du vent en km/h.
        wind_direction_10m: Direction du vent à 10m d'altitude en degrés.
    """

    def __init__(self, hour: pd.Timestamp, value_1: float, value_2: float) -> None:
        super().__init__(hour, value_1)
        self.wind_direction_10m: float = value_2

    def accept(self, visitor: object) -> float:
        """
        Point d'entrée du visiteur spécifique à Wind.
        Redirige l'exécution vers la méthode visit_wind du visiteur.

        :param visitor: Le visiteur qui vient analyser l'objet.
        :return: Le score calculé par le visiteur
        """
        return visitor.visit_wind(self)

    def __str__(self) -> str:
        """
        Établit l'impression syntaxique de l'objet Wind via ses arguments.
        :return : impression syntaxique
        """
        return f"Wind({self.hour}, wind_speed:{self.value}km/h, wind_direction:{self.wind_direction_10m}deg)"

    __repr__ = __str__
