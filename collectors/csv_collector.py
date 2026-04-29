import pandas as pd
import logging

logger = logging.getLogger(__name__)

def load_eco2mix(filepath):
    """Charge un fichier CSV éCO2mix et retourne un DataFrame normalisé.

    Args:
        filepath: chemin vers le fichier CSV éCO2mix

    Returns:
        DataFrame avec les colonnes timestamp, region, solar_production_mw, consumption_mw
    """
    df = pd.read_csv(
        filepath,
        sep=";",
        encoding="utf-8",
        na_values=["N/A", "-", "ND", ""],
        on_bad_lines="skip",
    )

    if df.empty:
        logger.error("Le fichier CSV éCO2mix est vide ou ne contient pas de données valides")
        raise ValueError("Le fichier CSV éCO2mix est vide ou ne contient pas de données valides")
    
    # Supprimer les lignes d'en-tête dupliquées insérées dans le fichier
    df = df[df["Date"] != "Date"]

    # On vérifie que les colonnes nécessaires sont présentes
    required_columns = {"Date", "Heure", "Région", "Solaire (MW)", "Consommation (MW)"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        logger.error(f"Le fichier CSV éCO2mix n'a pas les colonnes suivantes : {', '.join(missing)}")
        raise ValueError(f"Le fichier CSV éCO2mix n'a pas les colonnes suivantes : {', '.join(missing)}")

    df["timestamp"] = pd.to_datetime(df["Date"] + " " + df["Heure"], format="%Y-%m-%d %H:%M")
    df = df.rename(columns={
        "Région": "region",
        "Solaire (MW)": "solar_production_mw",
        "Consommation (MW)": "consumption_mw",
    })

    df = df[["timestamp", "region", "solar_production_mw", "consumption_mw"]]
    return df
