import argparse
import os
from datetime import date, timedelta

import pandas as pd

import config
from collectors.rte_collector import fetch_rte_production
from collectors.meteo_collector import fetch_irradiance
from collectors.csv_collector import load_eco2mix
from processing.aggregator import aggregate
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger()

def parse_args():
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = date.today().strftime("%Y-%m-%d")

    parser = argparse.ArgumentParser(
        description="SolarFlow — pipeline de collecte de données solaires"
    )
    parser.add_argument("--start-date", default=yesterday, help="Date de début YYYY-MM-DD")
    parser.add_argument("--end-date", default=today, help="Date de fin YYYY-MM-DD")
    parser.add_argument(
        "--output-format",
        choices=["csv", "json"],
        default="csv",
        help="Format de sortie (csv ou json)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.start_date > args.end_date:
        logger.info(f'La date de début ({args.start_date}) est postérieure à la date de fin ({args.end_date}).')       
        raise ValueError(f"La date de début ({args.start_date}) est postérieure à la date de fin ({args.end_date}).")

    # On vérifie que les dates sont au format YYYY-MM-DD
    try:
        date.fromisoformat(args.start_date)
        date.fromisoformat(args.end_date)
    except ValueError:
        logger.error("Les dates doivent être au format YYYY-MM-DD.")
        raise ValueError("Les dates doivent être au format YYYY-MM-DD.")
    
    # On vérifie que les dates ne sont pas dans le futur
    today_str = date.today().strftime("%Y-%m-%d")
    if args.end_date > today_str:
        logger.error("Les dates ne peuvent pas être dans le futur.")
        raise ValueError("Les dates ne peuvent pas être dans le futur.")
    
    logger.info(f"SolarFlow démarré — période : {args.start_date} → {args.end_date}")

    logger.info("Collecte RTE...")
    rte_df = fetch_rte_production(args.start_date, args.end_date)

    logger.info("Collecte Open-Meteo...")
    

    meteo_df = fetch_irradiance(
        config.SOLAR_PARK_LAT,
        config.SOLAR_PARK_LON,
        args.start_date,
        args.end_date,
    )

    logger.info("Chargement CSV éCO2mix...")
    csv_df = load_eco2mix("data/eco2mix_sample.csv", args.start_date, args.end_date)

    logger.info("Agrégation des sources...")
    result_df = aggregate(rte_df, meteo_df, csv_df)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(
        config.OUTPUT_DIR,
        f"solarflow_{args.start_date}_{args.end_date}.{args.output_format}",
    )

    if args.output_format == "csv":
        result_df.to_csv(output_path, index=False)
    else:
        result_df.to_json(output_path, orient="records", date_format="iso", indent=2)

    logger.info(f"Dataset généré : {output_path} ({len(result_df)} lignes)")


if __name__ == "__main__":
    main()
