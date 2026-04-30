import os
import pandas as pd
        
from sklearn.model_selection import train_test_split


class ScikitLearn:
    """Classe d'entraînement d'un modèle de régression linéaire pour prédire la production solaire à partir des données d'irradiance.
    Les données d'entraînement sont chargées depuis les fichiers CSV générés par le pipeline de collecte. Les fichiers doivent être nommés "solarflow_YYYY-MM-DD.csv" et contenir au moins les colonnes timestamp, ghi, dni, dhi, solar_production_mw_csv et être au format csv."""
    def __init__(self):
        self.charge_data()
        self.clean_zero_data() # on enlève les données de nuit où ghi, dni, dhi sont à 0
        self.input = self.data[["ghi", "dni", "dhi"]]
        self.output = self.data["solar_production_mw_csv"]

    def charge_data(self):
        """Charge les données d'entraînement depuis les fichiers CSV générés par le pipeline de collecte.
         Les fichiers doivent être nommés "solarflow_YYYY-MM-DD.csv" et contenir au moins les colonnes timestamp, ghi, dni, dhi, solar_production_mw_csv"""
        folder = "output"
        data = pd.DataFrame()
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath) and filename.startswith("solarflow_") and filename.endswith(".csv"):
                print(f"Chargement des données d'entraînement depuis {filepath}...")
                df = pd.read_csv(filepath, parse_dates=["timestamp"])
                df = df[["ghi", "dni", "dhi", "solar_production_mw_csv"]].dropna()
                data = pd.concat([data, df], ignore_index=True)
        self.data = data

    def clean_zero_data(self):
        """Nettoie les données d'entraînement en supprimant les valeurs ghi, dni, dhi à 0"""
        self.data = self.data[~((self.data["ghi"] == 0) & (self.data["dni"] == 0) & (self.data["dhi"] == 0))]

    def separate_train_test(self):
        """Sépare les données d'entraînement en un ensemble d'entraînement (80%) et un ensemble de test (20%)"""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.input, self.output, test_size=0.2, random_state=42
        )
    

        

    