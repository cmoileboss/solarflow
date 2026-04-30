# SolarFlow

Pipeline de collecte et d'agrégation de données pour la prévision de production solaire.
Développé en interne chez **GreenWatt** pour alimenter le modèle de prévision J+1 des parcs solaires.
Le pipeline collecte des données depuis trois sources (RTE, Open-Meteo, éCO2mix), les agrège et produit un dataset horodaté prêt à l'emploi.

## Architecture

```
API RTE ──────────┐
API Open-Meteo ───┼──→ Agrégation ──→ Dataset unifié (CSV/JSON)
CSV éCO2mix ──────┘
```

- **API RTE** : production solaire réalisée et prévisions (données réseau national)
- **API Open-Meteo** : irradiance solaire horaire (GHI, DNI, DHI)
- **CSV éCO2mix** : historique régional de production par filière

## Prérequis

- **Python 3.13**
- **Credentials API RTE** : créer un compte sur [data.rte-france.com](https://data.rte-france.com), puis créer une application pour obtenir un `client_id` et un `client_secret`. L'accès à l'endpoint de production réelle est gratuit mais nécessite une validation du compte.

## Installation

```bash
winget install Python.Python.3.13
# Créer un environnement virtuel
py -3.13 -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Installer les dépendances (versions épinglées)
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env           # Linux/macOS
copy .env.example .env         # Windows
# Éditer .env et renseigner vos credentials RTE
```

## Utilisation

```bash
python main.py --start-date 2026-01-01 --end-date 2026-04-27
```

Options :
- `--start-date` : date de début (format YYYY-MM-DD, défaut : veille)
- `--end-date` : date de fin (format YYYY-MM-DD, défaut : aujourd'hui)
- `--output-format` : format de sortie `csv` ou `json` (défaut : `csv`)

Le fichier de sortie est généré dans le répertoire `output/`.

## Configuration

Copier `.env.example` vers `.env` et renseigner les variables suivantes :

| Variable | Description |
|---|---|
| `RTE_CLIENT_ID` | Client ID de l'application RTE (portail data.rte-france.com) |
| `RTE_CLIENT_SECRET` | Client Secret associé |
| `SOLAR_PARK_LAT` | Latitude du parc solaire (coordonnées GPS) |
| `SOLAR_PARK_LON` | Longitude du parc solaire |
| `OUTPUT_DIR` | Répertoire de sortie des fichiers générés |

## Sources de données

- **API RTE** : [https://data.rte-france.com](https://data.rte-france.com) — Portail open data de RTE. Nécessite une inscription et la création d'une application pour obtenir les credentials OAuth2.
- **Open-Meteo** : [https://open-meteo.com/en/docs](https://open-meteo.com/en/docs) — API météo ouverte, sans authentification. Données d'irradiance solaire au niveau horaire.
- **éCO2mix** : [https://www.data.gouv.fr](https://www.data.gouv.fr) — Rechercher "éCO2mix" pour télécharger les historiques régionaux de production électrique par filière.

## Données de test

Un fichier d'exemple `data/eco2mix_sample.csv` est fourni pour tester le pipeline sans accès réseau.

## TODO (notes du dev précédent)

- TODO: Le refresh automatique du token RTE n'est pas encore implémenté proprement, pour l'instant on utilise un token fixe (à améliorer).
- TODO: Ajouter de la gestion d'erreur sur le parsing CSV, ça plante parfois sur certains fichiers.
- TODO: Il faudrait ajouter des tests.


## Connaissances Techniques 

MW — MégaWatt. C'est une unité de puissance (1 MW = 1 000 kW = 1 000 000 W). Sur RTE, c'est la puissance instantanée injectée sur le réseau à un instant T (ou moyennée sur le pas de temps, typiquement 15 min ou 1 h). Pour avoir une énergie, il faut multiplier par le temps → MWh.
GHI — Global Horizontal Irradiance (Rayonnement Global Horizontal). C'est le rayonnement solaire total reçu sur une surface horizontale au sol, exprimé en W/m² (puissance) ou Wh/m² / kWh/m² (énergie cumulée). C'est la somme du direct et du diffus :
GHI = DNI × cos(θz) + DHI
où θz est l'angle zénithal du soleil. C'est la grandeur de référence pour estimer le potentiel d'une installation PV au sol.
DNI — Direct Normal Irradiance (Rayonnement Direct Normal). C'est uniquement la composante directe du rayonnement, mesurée perpendiculairement aux rayons du soleil (suivi du soleil). Unité : W/m². C'est la grandeur clé pour le solaire à concentration (CSP) et les trackers.
DHI — Diffuse Horizontal Irradiance (Rayonnement Diffus Horizontal). C'est la part du rayonnement diffusée par l'atmosphère (nuages, aérosols) reçue sur une surface horizontale, hors rayonnement direct. Unité : W/m². Par ciel couvert, le DHI peut représenter la quasi-totalité du GHI.
En résumé pratique : MW = ce que produit ton parc, GHI/DNI/DHI = ce que le soleil envoie (la "ressource" qui explique la production). Si tu croises les deux, tu peux calculer un performance ratio ou caler un modèle de production

## Gestion des valeurs manquantes 

Après analyse des données, la colonne solar_production_mw contient des valeurs manquantes (NaN) principalement sur la période de janvier (pour une analyse des données entre le 01.01.2026 et le 04.27.2026)
Choix retenu : Imputation par zéro (fillna(0))

Justification :
La suppression a été écartée car elle ferait perdre des plages horaires entières, faussant le calcul de production totale.
L'interpolation a été écartée car elle inventerait des valeurs de production qui n'ont peut-être jamais existé, ce qui n'est pas acceptable dans un contexte de mesure énergétique.
L'imputation à zéro a été retenue car une donnée manquante en production solaire signifie soit une absence de production (nuit, panne), soit un défaut d'enregistrement. Dans les deux cas, considérer la production comme nulle est le choix le plus conservateur et honnête.