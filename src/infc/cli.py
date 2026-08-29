"""Ligne de commande : télécharger, reconstruire les mesures, rejouer le concours."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(help="Inflation fondamentale canadienne : IPC-tronq et IPC-méd reconstruits "
                       "depuis les 55 composantes (écart mesuré), et le concours de Lao-Steyn "
                       "rejoué à travers le choc de 2021-23.")


def _normalise(s: str) -> str:
    return s.replace("’", "'").strip().lower()


@app.callback()
def main() -> None:
    """Sous-commandes nommées."""


@app.command()
def fetch() -> None:
    """Les trois tables StatCan et le miroir Valet."""
    from infc import data

    data.fetch()
    off = data.load_official()
    typer.echo(f"mesures officielles : {off.index[0]} -> {off.index[-1]}, colonnes {list(off.columns)}")


@app.command()
def lab(out: Path = Path("results")) -> None:
    """Reconstruction, écarts, concours : cinq tables, trois figures (~3 min, STL sur 55 séries)."""
    import pandas as pd

    from infc import data, figures, mesures
    from infc.components import COMPOSANTES_55

    indices = data.load_indices()
    weights_all = data.load_weights()
    officiel = data.load_official()
    valet = data.load_valet()

    tables, figs = out / "tables", out / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    # appariement des 55 composantes (apostrophes normalisées) : échec BRUYANT si absente
    par_nom = {_normalise(c): c for c in indices.columns}
    manquantes = [c for c in COMPOSANTES_55 if _normalise(c) not in par_nom]
    if manquantes:
        raise SystemExit(f"composantes introuvables dans 18-10-0004 : {manquantes}")
    cols = [par_nom[_normalise(c)] for c in COMPOSANTES_55]
    ipc55 = indices[cols].loc["1988-01":]

    # poids : le panier le plus récent qui couvre les 55 (approximation déclarée : statique)
    w_par_nom = {_normalise(c): c for c in weights_all.columns}
    w_cols = [w_par_nom[_normalise(c)] for c in COMPOSANTES_55 if _normalise(c) in w_par_nom]
    if len(w_cols) != 55:
        absents = [c for c in COMPOSANTES_55 if _normalise(c) not in w_par_nom]
        raise SystemExit(f"poids introuvables dans 18-10-0007 : {absents}")
    w_rows = weights_all[w_cols].dropna()
    poids = w_rows.iloc[-1]
    poids.index = cols
    panier = str(w_rows.index[-1])
    pd.DataFrame({"composante": cols, "poids_pct": poids.to_numpy()}
                 ).to_csv(tables / "composantes_poids.csv", index=False)

    # volet B : reconstruction
    sa = mesures.seasonally_adjust(ipc55)
    notre = mesures.monthly_measures(sa, poids)
    notre.round(4).to_csv(tables / "reconstruction.csv")
    ecarts = []
    for col_n, col_o in [("tronq_glissement", "ipc_tronq"), ("med_glissement", "ipc_med")]:
        for fen, a, b in [("1990-2026", "1990-01", None), ("2016-2025", "2016-01", "2025-12"),
                          ("choc 2021-2023", "2021-01", "2023-12")]:
            n = notre[col_n].loc[pd.Period(a, "M"): pd.Period(b, "M") if b else None]
            g = mesures.gap_stats(n, officiel[col_o])
            ecarts.append({"mesure": col_o, "fenetre": fen, **g})
    pd.DataFrame(ecarts).round(3).to_csv(tables / "ecarts_reconstruction.csv", index=False)
    figures.fig_reconstruction(notre, officiel, figs / "reconstruction.png")

    # le contrefactuel de la QUATRIÈME approximation, calculé ici et non cité de mémoire : on
    # refait la reconstruction SANS les deux composantes que la Banque construit elle-même et qui
    # n'entrent dans la table publique qu'en 1994-12 et 1997-12, sur la fenêtre où les 55 existent
    tardives = ["Other owned accommodation expenses", "Leasing of passenger vehicles"]
    col_tardives = [par_nom[_normalise(c)] for c in tardives]
    sa_53 = sa.drop(columns=col_tardives)
    notre_53 = mesures.monthly_measures(sa_53, poids.drop(index=col_tardives))
    debut_55 = pd.Period("1998-01", "M")
    lignes_cf = []
    for col, nom in (("tronq_glissement", "IPC-tronq"), ("med_glissement", "IPC-méd")):
        a = notre[col].loc[debut_55:].dropna()
        b = notre_53[col].loc[debut_55:].dropna()
        com = a.index.intersection(b.index)
        d = (a.loc[com] - b.loc[com]).abs()
        lignes_cf.append({"mesure": nom, "fenetre": f"{com[0]} à {com[-1]}",
                          "deplacement_moyen_pp": float(d.mean()),
                          "deplacement_max_pp": float(d.max()),
                          "mois_du_max": str(d.idxmax()), "n_mois": int(len(com))})
    cf_table = pd.DataFrame(lignes_cf)
    cf_table.round(4).to_csv(tables / "contrefactuel_composantes.csv", index=False)

    # contrôle croisé Valet vs StatCan (les mêmes séries publiées par deux guichets)
    controle = []
    for a, b in [("ipc_tronq", "cpi_trim"), ("ipc_med", "cpi_median"), ("ipc_comm", "cpi_common")]:
        if a in officiel and b in valet:
            common = officiel[a].dropna().index.intersection(valet[b].dropna().index)
            controle.append({"mesure": a,
                             "ecart_max_valet": float((officiel[a].loc[common] - valet[b].loc[common]).abs().max()),
                             "n": len(common)})
    pd.DataFrame(controle).to_csv(tables / "controle_valet.csv", index=False)

    # volet A : le concours
    headline = (indices["All-items"] / indices["All-items"].shift(12) - 1.0) * 100.0
    sans_ae = (indices["All-items excluding food and energy"]
               / indices["All-items excluding food and energy"].shift(12) - 1.0) * 100.0
    candidates = pd.DataFrame({
        "IPC-tronq": officiel["ipc_tronq"],
        "IPC-méd": officiel["ipc_med"],
        "IPC-comm": officiel.get("ipc_comm"),
        "IPC hors aliments et énergie": sans_ae,
        "moyenne mobile 12 mois": headline.rolling(12).mean(),
    })
    # chaque horizon perd ses propres derniers mois : tronquer les candidates à index[-1] - 24
    # retirait douze mois à l'horizon 12 sans raison. horse_race intersecte déjà chaque cible avec
    # les dates disponibles, le nombre d'observations effectif est publié dans les colonnes n_h*.
    fin = headline.dropna().index[-1]
    debut_long, debut_choc = pd.Period("1990-01", "M"), pd.Period("2016-01", "M")
    fin_avant = pd.Period("2015-12", "M")
    full = mesures.horse_race(candidates.loc[debut_long:fin], headline)
    recent = mesures.horse_race(candidates.loc[debut_choc:fin], headline)
    # une VRAIE fenêtre d'avant le choc : sans elle, la figure comparait « tout » à « une partie
    # de tout » et ne pouvait pas dire si le classement a survécu
    avant = mesures.horse_race(candidates.loc[debut_long:fin_avant], headline)
    full.round(3).to_csv(tables / "concours_long.csv", index=False)
    recent.round(3).to_csv(tables / "concours_2016_2025.csv", index=False)
    avant.round(3).to_csv(tables / "concours_avant_choc.csv", index=False)
    figures.fig_concours(avant, full, recent, figs / "concours.png",
                         f"{debut_long} à {fin_avant}", f"{debut_long} à {fin}",
                         f"{debut_choc} à {fin}")
    figures.fig_choc(officiel, headline.loc[pd.Period("1990-01", "M"):], figs / "choc.png")

    typer.echo(f"panier de poids : {panier} (statique, déclaré) ; somme {poids.sum():.2f} %")
    typer.echo(pd.DataFrame(ecarts).round(2).to_string(index=False))
    typer.echo("contrefactuel des deux composantes tardives :")
    typer.echo(cf_table.round(3).to_string(index=False))
    typer.echo("concours avant le choc (1990-2015) :")
    typer.echo(avant.round(2).to_string(index=False))
    typer.echo("concours échantillon complet :")
    typer.echo(full.round(2).to_string(index=False))
    typer.echo("concours 2016-2025 :")
    typer.echo(recent.round(2).to_string(index=False))


if __name__ == "__main__":
    app()
