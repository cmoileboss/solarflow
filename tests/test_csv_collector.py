import io
import textwrap

import pandas as pd
import pytest

from collectors.csv_collector import load_eco2mix

# CSV minimal réutilisé par tous les tests
CSV_CONTENT = textwrap.dedent("""\
    Code INSEE région;Région;Nature;Date;Heure;Date - Heure;Consommation (MW);Thermique (MW);Nucléaire (MW);Eolien (MW);Solaire (MW);Hydraulique (MW);Pompage (MW);Bioénergies (MW);Ech. physiques (MW)
    75;Nouvelle-Aquitaine;Données temps réel;2026-01-01;08:00;2026-01-01T07:00:00+00:00;4000;0;0;0;100;0;0;0;0
    75;Nouvelle-Aquitaine;Données temps réel;2026-01-01;12:00;2026-01-01T11:00:00+00:00;4200;0;0;0;500;0;0;0;0
    75;Nouvelle-Aquitaine;Données temps réel;2026-01-02;10:00;2026-01-02T09:00:00+00:00;3900;0;0;0;300;0;0;0;0
    75;Nouvelle-Aquitaine;Données temps réel;2026-01-03;14:00;2026-01-03T13:00:00+00:00;4100;0;0;0;200;0;0;0;0
""")


@pytest.fixture
def csv_path(tmp_path):
    """Écrit le CSV minimal dans un fichier temporaire et retourne son chemin."""
    p = tmp_path / "eco2mix_test.csv"
    p.write_text(CSV_CONTENT, encoding="utf-8")
    return str(p)


# --- Sans filtrage -----------------------------------------------------------

def test_load_without_filter_returns_all_rows(csv_path):
    df = load_eco2mix(csv_path)
    assert len(df) == 4


# --- Filtrage start_date uniquement ------------------------------------------

def test_start_date_excludes_earlier_rows(csv_path):
    df = load_eco2mix(csv_path, start_date="2026-01-02")
    assert all(df["timestamp"] >= pd.Timestamp("2026-01-02"))
    assert len(df) == 2  # 2026-01-02 et 2026-01-03


def test_start_date_inclusive(csv_path):
    """Une ligne dont le timestamp tombe exactement sur start_date est incluse."""
    df = load_eco2mix(csv_path, start_date="2026-01-01")
    assert len(df) == 4


# --- Filtrage end_date uniquement --------------------------------------------

def test_end_date_excludes_later_rows(csv_path):
    df = load_eco2mix(csv_path, end_date="2026-01-02")
    assert all(df["timestamp"] < pd.Timestamp("2026-01-03"))
    assert len(df) == 3  # 2026-01-01 (x2) + 2026-01-02


def test_end_date_inclusive(csv_path):
    """end_date est inclus : une ligne le jour J doit apparaître."""
    df = load_eco2mix(csv_path, end_date="2026-01-03")
    assert len(df) == 4


# --- Filtrage start_date + end_date ------------------------------------------

def test_range_keeps_only_matching_rows(csv_path):
    df = load_eco2mix(csv_path, start_date="2026-01-02", end_date="2026-01-02")
    assert len(df) == 1
    assert df.iloc[0]["timestamp"] == pd.Timestamp("2026-01-02 10:00")


def test_range_excludes_all_rows(csv_path):
    """Plage qui ne couvre aucune ligne doit retourner un DataFrame vide."""
    df = load_eco2mix(csv_path, start_date="2025-01-01", end_date="2025-12-31")
    assert df.empty


def test_range_full_period(csv_path):
    df = load_eco2mix(csv_path, start_date="2026-01-01", end_date="2026-01-03")
    assert len(df) == 4


# --- Colonnes du DataFrame résultant -----------------------------------------

def test_output_columns(csv_path):
    df = load_eco2mix(csv_path)
    assert list(df.columns) == ["timestamp", "region", "solar_production_mw", "consumption_mw"]


def test_timestamp_dtype(csv_path):
    df = load_eco2mix(csv_path)
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
