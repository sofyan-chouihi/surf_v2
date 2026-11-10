"""
@author: Chouihi Sofyan - green813
Module: storage
Description: Gère l'enregistrement des données des spots via une base de données SQLite.
"""

from config import DB_PATH
import sqlite3


def init_db(db_path: str = DB_PATH) -> None:
    """
    Crée la base de donnée si elle n'existe pas.
    :param db_path: chemin de la base de données
    :return: None
    """
    connect = sqlite3.connect(db_path)
    pen = connect.cursor()
    pen.execute("""
                CREATE TABLE IF NOT EXISTS spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lat REAL NOT NULL,
            long REAL NOT NULL
        )
        """)
    connect.commit()
    connect.close()


def save_spots(
    spots_list: list[dict[str, str | float]], db_path: str = DB_PATH
) -> None:
    """
    Enregistre les spots dans la base de données si ils n'y existent pas.
    :param spots_list: liste des dictionnaires des spots contenant name,lat,long.
    :param db_path: chemin de la base de données
    :return: None
    """
    connect = sqlite3.connect(db_path)
    pen = connect.cursor()

    for spot in spots_list:
        pen.execute(
            "SELECT id FROM spots WHERE name = ? AND lat = ? AND long = ?",
            (spot["name"], spot["lat"], spot["long"]),
        )
        if pen.fetchone() is None:
            pen.execute(
                "INSERT INTO spots (name, lat, long) VALUES (?, ?, ?)",
                (spot["name"], spot["lat"], spot["long"]),
            )

    connect.commit()
    connect.close()


def load_spots(db_path: str = DB_PATH) -> list[dict[str, str | float]]:
    """
    Fonction retourne la liste de dictionnaire des spots contenant name,lat,long par extraction de
    la base de donnée.
    :param db_path: chemin de la base de données
    :return: spots_list
    """

    connect = sqlite3.connect(db_path)
    pen = connect.cursor()
    pen.execute("SELECT name, lat, long FROM spots")
    rows = pen.fetchall()
    connect.close()
    spots_list = []
    for row in rows:
        spot_propre = {"name": row[0], "lat": row[1], "long": row[2]}
        spots_list.append(spot_propre)
    return spots_list
