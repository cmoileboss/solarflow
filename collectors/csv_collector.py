import pandas as pd
import logging

logger = logging.getLogger(__name__)

def load_eco2mix(filepath, start_date=None, end_date=None):
    """Charge un fichier CSV éCO2mix et retourne un DataFrame normalisé.

    Args:
        filepath: chemin vers le fichier CSV éCO2mix
        start_date: date de début (str YYYY-MM-DD ou None)
        end_date: date de fin inclusive (str YYYY-MM-DD ou None)

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
    required_columns = {"Date - Heure", "Région", "Solaire (MW)", "Consommation (MW)"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        logger.error(f"Le fichier CSV éCO2mix n'a pas les colonnes suivantes : {', '.join(missing)}")
        raise ValueError(f"Le fichier CSV éCO2mix n'a pas les colonnes suivantes : {', '.join(missing)}")

    df["timestamp"] = pd.to_datetime(df["Date - Heure"], utc=True)
    df = df.rename(columns={
        "Région": "region",
        "Solaire (MW)": "solar_production_mw",
        "Consommation (MW)": "consumption_mw",
    })

    df = df[["timestamp", "region", "solar_production_mw", "consumption_mw"]]

    for col in ("solar_production_mw", "consumption_mw"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].where(df[col] >= 0, other=None)

    if start_date is not None:
        df = df[df["timestamp"] >= pd.Timestamp(start_date, tz="UTC")]
    if end_date is not None:
        df = df[df["timestamp"] < pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)]

    return df
