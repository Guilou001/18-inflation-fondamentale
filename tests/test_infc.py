"""Le tronquage et la médiane pondérée contre des cas à la main, sans réseau."""

import numpy as np
import pandas as pd
import pytest

from infc.components import COMPOSANTES_55
from infc.mesures import (
    gap_stats,
    horse_race,
    monthly_measures,
    seasonally_adjust,
    trimmed_mean,
    weighted_median,
)


def test_components_are_55_and_unique():
    assert len(COMPOSANTES_55) == 55
    assert len(set(COMPOSANTES_55)) == 55


def test_weighted_median_hand_case():
    # cas frontière : cumuls 0,2 puis 0,5 puis 1,0 ; le document officiel prend la
    # PREMIÈRE composante dont le cumul DÉPASSE 50 % : la troisième
    assert weighted_median(np.array([1.0, 2.0, 3.0]), np.array([0.2, 0.3, 0.5])) == 3.0
    # cas franc : cumuls 0,2 puis 0,4 puis 1,0 ; le 50e percentile tombe dans la troisième
    assert weighted_median(np.array([1.0, 2.0, 3.0]), np.array([0.2, 0.2, 0.6])) == 3.0
    # poids égaux, 5 composantes : la médiane est la valeur du milieu
    assert weighted_median(np.array([5.0, 1.0, 3.0, 2.0, 4.0]), np.ones(5)) == 3.0


def test_trimmed_mean_hand_case():
    # 5 composantes de poids égal, tronquage 20 % : la première et la dernière tombent
    changes = np.array([-10.0, 1.0, 2.0, 3.0, 50.0])
    assert trimmed_mean(changes, np.ones(5), trim=0.20) == pytest.approx(2.0)


def test_trimmed_mean_partial_weight_at_the_border():
    # 2 composantes 50/50, tronquage 20 % : chacune garde 30/50 de son poids, moyenne simple
    changes = np.array([0.0, 10.0])
    assert trimmed_mean(changes, np.array([0.5, 0.5]), trim=0.20) == pytest.approx(5.0)


def test_trimmed_mean_degenerate_all_equal():
    assert trimmed_mean(np.full(55, 2.5), np.random.default_rng(0).uniform(0.1, 3, 55)) == pytest.approx(2.5)


def test_monthly_measures_compound_to_yoy():
    # 55 composantes à +0,3 %/mois exactement : tronquée = médiane = 0,3 ; glissement = 1,003^12 - 1
    idx = pd.period_range("2015-01", periods=40, freq="M")
    base = 100.0 * np.cumprod(np.full(40, 1.003))
    df = pd.DataFrame({f"c{i}": base for i in range(55)}, index=idx)
    poids = pd.Series(np.random.default_rng(1).uniform(0.5, 3.0, 55), index=df.columns)
    m = monthly_measures(df, poids)
    assert m["tronq_mm"].dropna().iloc[-1] == pytest.approx(0.3, abs=1e-9)
    attendu = (1.003**12 - 1.0) * 100.0
    assert m["tronq_glissement"].dropna().iloc[-1] == pytest.approx(attendu, abs=1e-6)
    assert m["med_glissement"].dropna().iloc[-1] == pytest.approx(attendu, abs=1e-6)


def test_stl_removes_a_planted_seasonal():
    # série log-linéaire plus saisonnalité sinusoïdale : l'ajustée doit coller à la tendance
    idx = pd.period_range("2000-01", periods=240, freq="M")
    t = np.arange(240)
    brute = 100.0 * np.exp(0.002 * t + 0.03 * np.sin(2 * np.pi * t / 12))
    df = pd.DataFrame({"x": brute}, index=idx)
    adj = seasonally_adjust(df)["x"]
    lisse = 100.0 * np.exp(0.002 * t)
    assert float(np.abs(adj.to_numpy() / lisse - 1.0).max()) < 0.01


def test_gap_stats_zero_on_identical():
    idx = pd.period_range("2010-01", periods=60, freq="M")
    s = pd.Series(np.linspace(1, 3, 60), index=idx)
    g = gap_stats(s, s.copy())
    assert g["ecart_absolu_moyen"] == 0.0 and g["correlation"] == pytest.approx(1.0)


def test_horse_race_prefers_the_true_signal():
    # l'IPC futur suit exactement la candidate A ; la candidate B est du bruit
    rng = np.random.default_rng(2)
    idx = pd.period_range("2000-01", periods=300, freq="M")
    a = pd.Series(2.0 + np.cumsum(rng.normal(0, 0.05, 300)), index=idx)
    headline = a.shift(0) + rng.normal(0, 0.01, 300)      # la cible colle à A
    b = pd.Series(rng.normal(2.0, 1.0, 300), index=idx)
    hr = horse_race(pd.DataFrame({"A": a, "B": b}), headline, horizons=(12,))
    rmse = hr.set_index("candidate")["rmse_h12"]
    assert rmse["A"] < rmse["B"] * 0.5
