import os
import pandas as pd
        
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, root_mean_squared_error


class ScikitLearn:
    """Classe d'entraînement d'un modèle de régression linéaire pour prédire la production solaire à partir des données d'irradiance.
    Les données d'entraînement sont chargées depuis les fichiers CSV générés par le pipeline de collecte. Les fichiers doivent être nommés "solarflow_YYYY-MM-DD.csv" et contenir au moins les colonnes timestamp, ghi, dni, dhi, solar_production_mw_csv et être au format csv."""
    
    def __init__(self):
        self.prepare_data()
    

    def prepare_data(self):
        """Prépare les données d'entraînement en chargeant les fichiers CSV, nettoyant les données et séparant en ensembles d'entraînement et de test."""
        self.charge_data()
        self.clean_zero_data() # on enlève les données de nuit où ghi, dni, dhi sont à 0
        self.input = self.data[["ghi", "dni", "dhi"]]
        self.output = self.data["solar_production_mw_csv"]
        self.separate_train_test()

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

    def train_linear_regression(self):
        """Entraîne un modèle de régression linéaire sur les données d'entraînement préparées"""
        self.model = LinearRegression()
        self.model.fit(self.X_train, self.y_train)

    def prediction_linear_regression(self):
        """Fait des prédictions sur l'ensemble de test et retourne les résultats"""
        self.y_pred = self.model.predict(self.X_test)
        return self.y_pred
    
    def get_metrics(self):
        """Retourne les métriques d'évaluation du modèle sur l'ensemble de test"""
        mae = mean_absolute_error(self.y_test, self.y_pred)
        mse = mean_squared_error(self.y_test, self.y_pred)
        rmse = root_mean_squared_error(self.y_test, self.y_pred)
        r2 = r2_score(self.y_test, self.y_pred)
        return {"MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2}


scikit = ScikitLearn()
scikit.train_linear_regression()
predictions = scikit.prediction_linear_regression()
metrics = scikit.get_metrics()
print("Métriques :", metrics)