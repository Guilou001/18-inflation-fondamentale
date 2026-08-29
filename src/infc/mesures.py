"""La reconstruction d'IPC-tronq et IPC-méd, et les critères du concours de Lao-Steyn.

La méthode officielle (document 2301 de StatCan, rapporté) : 55 composantes, corrigées des
impôts indirects, désaisonnalisées (44 sur 55), variations MENSUELLES, tronquage à 20 %
de poids dans chaque queue (IPC-tronq) ou 50e percentile pondéré (IPC-méd), poids du
panier au mois de raccord. Notre reconstruction approxime trois maillons et le DÉCLARE :
pas de correction des impôts indirects, désaisonnalisation STL sur les 55 (les facteurs
X-13 officiels ne sont pas publiés), poids du panier le plus récent applicable à chaque
date. L'écart à la mesure officielle, publiée à une décimale, est MESURÉ : il est le
produit de ces trois approximations, et c'est le résultat du volet.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def seasonally_adjust(indices: pd.DataFrame) -> pd.DataFrame:
    """STL par composante (période 12, robuste) : tendance + résidu, saisonnalité retirée."""
    from statsmodels.tsa.seasonal import STL

    out = {}
    for col in indices.columns:
        s = indices[col].dropna()
        if len(s) < 36:
            out[col] = indices[col]
            continue
        stl = STL(np.log(s.to_numpy()), period=12, robust=True).fit()
        adj = np.exp(stl.trend + stl.resid)
        out[col] = pd.Series(adj, index=s.index)
    return pd.DataFrame(out).reindex(indices.index)


def weighted_median(changes: np.ndarray, weights: np.ndarray) -> float:
    """La variation de la PREMIÈRE composante dont le poids cumulé DÉPASSE 50 %.

    C'est la lettre du document officiel (« the first component for which the cumulative
    weight is greater than 50 per cent ») ; sur les données réelles, aucun mois ne tombe
    sur la borne exacte (mesuré par la contre-vérification : 0 sur 462).
    """
    order = np.argsort(changes)
    c, w = changes[order], weights[order]
    cum = np.cumsum(w) / w.sum()
    return float(c[np.searchsorted(cum, 0.5, side="right")])


def trimmed_mean(changes: np.ndarray, weights: np.ndarray, trim: float = 0.20) -> float:
    """La moyenne pondérée après tronquage de `trim` de POIDS dans chaque queue.

    Les composantes à cheval sur une borne sont retenues pour leur poids résiduel
    (convention officielle : le tronquage porte sur le poids, pas sur le compte).
    """
    order = np.argsort(changes)
    c, w = changes[order], weights[order] / weights.sum()
    cum = np.concatenate([[0.0], np.cumsum(w)])
    lo, hi = trim, 1.0 - trim
    kept = np.minimum(cum[1:], hi) - np.maximum(cum[:-1], lo)
    kept = np.maximum(kept, 0.0)
    return float(np.sum(c * kept) / kept.sum())


def monthly_measures(sa_indices: pd.DataFrame, weights: pd.Series) -> pd.DataFrame:
    """IPC-tronq et IPC-méd mensuels (variations m/m, %), puis composés en glissement annuel."""
    changes = sa_indices.pct_change() * 100.0
    w = weights.reindex(sa_indices.columns).to_numpy(dtype=float)
    rows = {}
    for p, row in changes.iterrows():
        v = row.to_numpy(dtype=float)
        ok = np.isfinite(v)
        # deux composantes (astérisque de la table A1, « partly constructed by the Bank
        # of Canada ») manquent des données publiques avant 1994-12 et 1997-12 : les mois
        # à 53 ou 54 composantes sont acceptés, JOURNALISÉS, et déclarés au README ;
        # en deçà de 53, on refuse de calculer
        if ok.sum() < 53:
            continue
        rows[p] = {"tronq_mm": trimmed_mean(v[ok], w[ok]),
                   "med_mm": weighted_median(v[ok], w[ok]),
                   "n_composantes": int(ok.sum())}
    mm = pd.DataFrame.from_dict(rows, orient="index").sort_index()
    for c in ("tronq", "med"):
        idx = (1.0 + mm[f"{c}_mm"] / 100.0).cumprod()
        mm[f"{c}_glissement"] = (idx / idx.shift(12) - 1.0) * 100.0
    return mm


def gap_stats(notre: pd.Series, officiel: pd.Series) -> dict[str, float]:
    """L'écart à la mesure officielle (publiée à une décimale) : moyenne absolue, max, corrélation."""
    common = notre.dropna().index.intersection(officiel.dropna().index)
    d = (notre.loc[common] - officiel.loc[common]).astype(float)
    return {"ecart_absolu_moyen": float(d.abs().mean()),
            "ecart_max": float(d.abs().max()),
            "correlation": float(notre.loc[common].corr(officiel.loc[common])),
            "n_mois": float(len(common))}


def horse_race(candidates: pd.DataFrame, headline: pd.Series,
               horizons: tuple[int, ...] = (12, 24)) -> pd.DataFrame:
    """Les trois critères de Lao-Steyn : biais, lissage, pouvoir prédictif de l'IPC total.

    Biais : moyenne (candidate - IPC total) sur l'échantillon. Lissage : écart-type des
    variations mensuelles de la candidate. Prédictif : RMSE de la régression (pleine
    période, comme Lao-Steyn) de l'inflation totale moyenne des h prochains mois sur la
    candidate courante.
    """
    rows = []
    for col in candidates.columns:
        x = candidates[col]
        common = x.dropna().index.intersection(headline.dropna().index)
        x_c, h_c = x.loc[common], headline.loc[common]
        row = {"candidate": col,
               "biais": float((x_c - h_c).mean()),
               "volatilite": float(x_c.diff().std())}
        for h in horizons:
            cible = headline.rolling(h).mean().shift(-h)
            ok = x.dropna().index.intersection(cible.dropna().index)
            xx, yy = x.loc[ok].to_numpy(), cible.loc[ok].to_numpy()
            beta = np.polyfit(xx, yy, 1)
            resid = yy - np.polyval(beta, xx)
            row[f"rmse_h{h}"] = float(np.sqrt(np.mean(resid**2)))
            row[f"n_h{h}"] = len(ok)
        rows.append(row)
    return pd.DataFrame(rows)
