import pandas as pd


def aggregate(rte_df, meteo_df, csv_df):
    """Agrège les données des trois sources sur le timestamp.

    Args:
        rte_df: DataFrame production RTE (timestamp, solar_production_mw)
        meteo_df: DataFrame irradiance Open-Meteo (timestamp, ghi, dni, dhi)
        csv_df: DataFrame éCO2mix (timestamp, region, solar_production_mw, consumption_mw)

    Returns:
        DataFrame unifié avec toutes les colonnes fusionnées sur le timestamp
    """
    # Normalisation des timestamps en UTC avant merge
    rte_df["timestamp"] = pd.to_datetime(rte_df["timestamp"], utc=True).dt.floor("h")
    meteo_df["timestamp"] = pd.to_datetime(meteo_df["timestamp"], utc=True).dt.floor("h")
    csv_df["timestamp"] = pd.to_datetime(csv_df["timestamp"], utc=True).dt.floor("h")

    rte_df = rte_df.groupby("timestamp").agg(
        solar_production_mw_rte=("solar_production_mw", "mean")
    ).reset_index()

    meteo_df = meteo_df.groupby("timestamp").agg(
        ghi=("ghi", "mean"),
        dni=("dni", "mean"),
        dhi=("dhi", "mean"),
    ).reset_index()
    
    csv_with_no_duplicates = csv_df.groupby(["timestamp", "region"]).agg(
        solar_production_mw=("solar_production_mw", "mean"),
        consumption_mw=("consumption_mw", "mean"),
    ).reset_index()

    csv_agg = csv_with_no_duplicates.groupby("timestamp").agg(
        solar_production_mw_csv=("solar_production_mw", "sum"),
        consumption_mw=("consumption_mw", "sum"),
    ).reset_index()

    # TODO: nettoyer les données avant le merge ?
    merged = pd.merge(rte_df, meteo_df, on="timestamp", how="outer")
    merged = pd.merge(merged, csv_agg, on="timestamp", how="outer")
    
    merged = merged.sort_values("timestamp").reset_index(drop=True)
    merged['solar_production_mw'].interpolate(method='linear', inplace=True)
    merged['consumption_mw'].interpolate(method='linear', inplace=True)
    merged['ghi'].interpolate(method='linear', inplace=True)
    merged['dni'].interpolate(method='linear', inplace=True)
    merged['dhi'].interpolate(method='linear', inplace=True)

    return merged
