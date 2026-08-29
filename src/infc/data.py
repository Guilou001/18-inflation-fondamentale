"""Trois tables StatCan (licence ouverte, attribution) et le groupe Valet de la BdC.

18-10-0004 : IPC mensuel NON désaisonnalisé par produit (Canada retenu seulement) ;
18-10-0007 : poids du panier par période de base ; 18-10-0256 : les mesures officielles
(IPC-tronq et IPC-méd en indice et en glissement annuel, IPC-comm en glissement annuel
seulement, une décimale publiée, mesuré). Les zips sont téléchargés par l'API WDS
getFullTableDownloadCSV, jamais commités.
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAW = Path("data/raw")

WDS = "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{pid}/en"
TABLES = {"18100004": "ipc_produits.zip", "18100007": "poids_panier.zip",
          "18100256": "mesures_officielles.zip"}
VALET = ("https://www.bankofcanada.ca/valet/observations/CPI_TRIM,CPI_MEDIAN,CPI_COMMON/json"
         "?start_date=1989-01-01")

UA = {"User-Agent": "infc laboratoire pedagogique (github.com/Guilou001/18-inflation-fondamentale)"}


def fetch() -> None:
    """Télécharge les trois zips StatCan et le json Valet (jamais commités)."""
    RAW.mkdir(parents=True, exist_ok=True)
    for pid, name in TABLES.items():
        meta = requests.get(WDS.format(pid=pid), headers=UA, timeout=120).json()
        if meta.get("status") != "SUCCESS":
            raise RuntimeError(f"WDS a refusé {pid} : {meta}")
        r = requests.get(meta["object"], headers=UA, timeout=600)
        r.raise_for_status()
        (RAW / name).write_bytes(r.content)
    r = requests.get(VALET, headers=UA, timeout=120)
    r.raise_for_status()
    (RAW / "valet_mesures.json").write_bytes(r.content)


def _read_zip(name: str, usecols: list[str]) -> pd.DataFrame:
    """Lit le premier CSV du zip par morceaux, en ne gardant que le Canada."""
    with zipfile.ZipFile(RAW / name) as z:
        csv_name = [n for n in z.namelist() if n.endswith(".csv") and "Metadata" not in n][0]
        chunks = []
        with z.open(csv_name) as f:
            for chunk in pd.read_csv(io.TextIOWrapper(f, encoding="utf-8"),
                                     usecols=usecols, chunksize=200_000):
                chunks.append(chunk[chunk["GEO"] == "Canada"])
    return pd.concat(chunks, ignore_index=True)


def load_indices() -> pd.DataFrame:
    """Les indices mensuels NSA par produit (colonnes), Canada, 1914-2026."""
    df = _read_zip("ipc_produits.zip",
                   ["REF_DATE", "GEO", "Products and product groups", "VALUE"])
    piv = df.pivot_table(index="REF_DATE", columns="Products and product groups",
                         values="VALUE", aggfunc="first")
    piv.index = pd.PeriodIndex(piv.index, freq="M")
    return piv.sort_index()


def load_weights() -> pd.DataFrame:
    """Les poids du panier (part en %), par période de base du panier, au mois de raccord."""
    df = _read_zip("poids_panier.zip",
                   ["REF_DATE", "GEO", "Products and product groups",
                    "Price period of weight", "Geographic distribution of weight", "VALUE"])
    df = df[(df["Price period of weight"] == "Weight at basket link month prices")
            & (df["Geographic distribution of weight"] == "Distribution to selected geographies")]
    piv = df.pivot_table(index="REF_DATE", columns="Products and product groups",
                         values="VALUE", aggfunc="first")
    return piv.sort_index()


def load_official() -> pd.DataFrame:
    """Les mesures officielles en glissement annuel (%), une décimale publiée."""
    df = _read_zip("mesures_officielles.zip",
                   ["REF_DATE", "GEO", "Alternative measures", "UOM", "VALUE"])
    df = df[df["UOM"].str.contains("Percent", case=False, na=False)]
    piv = df.pivot_table(index="REF_DATE", columns="Alternative measures",
                         values="VALUE", aggfunc="first")
    piv.index = pd.PeriodIndex(piv.index, freq="M")
    colonnes = {}
    for c in piv.columns:
        lc = c.lower()
        if "trim" in lc:
            colonnes[c] = "ipc_tronq"
        elif "median" in lc:
            colonnes[c] = "ipc_med"
        elif "common" in lc:
            colonnes[c] = "ipc_comm"
    return piv.rename(columns=colonnes).sort_index()


def load_valet() -> pd.DataFrame:
    """Le miroir Valet des trois mesures (contrôle croisé)."""
    d = json.loads((RAW / "valet_mesures.json").read_text())
    rows = {}
    for o in d["observations"]:
        p = pd.Period(o["d"][:7], freq="M")
        rows[p] = {k.lower(): float(v["v"]) for k, v in o.items()
                   if k != "d" and v.get("v") not in (None, "")}
    return pd.DataFrame.from_dict(rows, orient="index").sort_index()
