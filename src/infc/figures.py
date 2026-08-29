"""Trois figures : le choc à travers les mesures, notre reconstruction, le concours."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]


def use_style():
    import matplotlib as mpl
    from cycler import cycler
    from matplotlib.ticker import FuncFormatter

    mpl.rcParams.update({
        "figure.dpi": 200, "savefig.dpi": 200, "figure.constrained_layout.use": True,
        "font.size": 11, "axes.titlesize": 12, "axes.prop_cycle": cycler(color=OKABE_ITO),
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linewidth": 0.5,
        "legend.frameon": False, "lines.linewidth": 1.6,
    })
    return FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def fig_choc(officiel: pd.DataFrame, headline: pd.Series, dest: Path) -> None:
    """Le choc de 2021-23 vu par l'IPC total et les trois mesures fondamentales."""
    fr = use_style()
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    ts = headline.index.to_timestamp()
    ax.plot(ts, headline, color="0.6", linewidth=1.1, label="IPC total")
    for col, name, color in [("ipc_tronq", "IPC-tronq", OKABE_ITO[0]),
                             ("ipc_med", "IPC-méd", OKABE_ITO[3]),
                             ("ipc_comm", "IPC-comm", OKABE_ITO[2])]:
        if col in officiel:
            s = officiel[col]
            ax.plot(s.index.to_timestamp(), s, color=color, label=name)
    ax.axhspan(1, 3, color="0.92", zorder=0,
               label="fourchette cible de la Banque du Canada (1 % à 3 %)")
    # la fenêtre du choc occupe un septième de la largeur : sans ombrage, le titre parle d'une
    # période que le lecteur ne sait pas situer
    choc = (pd.Period("2021-01", "M").to_timestamp(), pd.Period("2023-12", "M").to_timestamp(how="end"))
    ax.axvspan(*choc, color="0.85", zorder=0)
    ax.annotate("2021-23", (choc[0], ax.get_ylim()[1]), fontsize=8.5, color="0.35",
                ha="left", va="top")
    ax.set_ylabel("Glissement annuel (%)")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=8.5, loc="upper left")
    # le titre affirmait un RETARD des trois mesures : mesuré, l'IPC-tronq culmine le même mois
    # que l'IPC total, seules les deux autres retardent
    fen = slice(pd.Period("2021-01", "M"), pd.Period("2023-12", "M"))
    sommet_total = headline.loc[fen].idxmax()
    sommets = {n: officiel[c].loc[fen].idxmax()
               for c, n in (("ipc_tronq", "IPC-tronq"), ("ipc_med", "IPC-méd"),
                            ("ipc_comm", "IPC-comm")) if c in officiel}
    tronq = officiel["ipc_tronq"].loc[fen].max()
    retard = {n: (s - sommet_total).n for n, s in sommets.items()}
    sans_retard = [n for n, d in retard.items() if d == 0]
    ax.set_title(f"Le choc de 2021-23 : les mesures amortissent le sommet "
                 f"({tronq:.1f} % contre {headline.loc[fen].max():.1f} %) sans le retarder pour "
                 f"{', '.join(sans_retard) if sans_retard else 'aucune mesure'}".replace(".", ","),
                 fontsize=11.5)
    fig.savefig(dest)
    plt.close(fig)


def fig_reconstruction(notre: pd.DataFrame, officiel: pd.DataFrame, dest: Path) -> None:
    """Notre tronquée et notre médiane contre les officielles : l'écart des approximations."""
    fr = use_style()
    fig, axes = plt.subplots(2, 1, figsize=(9.4, 6.4), sharex=True)
    for ax, (col_n, col_o, name) in zip(axes, [("tronq_glissement", "ipc_tronq", "IPC-tronq"),
                                               ("med_glissement", "ipc_med", "IPC-méd")],
                                        strict=False):
        n = notre[col_n].dropna()
        o = officiel[col_o].dropna()
        common = n.index.intersection(o.index)
        ax.plot(o.loc[common].index.to_timestamp(), o.loc[common], color=OKABE_ITO[0],
                label=f"{name} officiel")
        ax.plot(n.loc[common].index.to_timestamp(), n.loc[common], color=OKABE_ITO[3],
                linestyle="--", label="notre reconstruction (approximations déclarées)")
        mae = float((n.loc[common] - o.loc[common]).abs().mean())
        ax.set_ylabel("Glissement annuel (%)")
        ax.yaxis.set_major_formatter(fr)
        ax.legend(fontsize=8.5,
                  title=f"écart absolu moyen : {mae:.2f} point de pourcentage".replace(".", ","))
    axes[0].set_title("Les 55 composantes suffisent à retrouver la forme ; les décimales exigent la cuisine officielle")
    fig.savefig(dest)
    plt.close(fig)


def fig_concours(avant: pd.DataFrame, full: pd.DataFrame, recent: pd.DataFrame, dest: Path,
                 fenetre_avant: str, fenetre_longue: str, fenetre_recente: str) -> None:
    """Le critère d'ajustement à 12 mois, avant le choc, sur tout l'échantillon, et à travers lui.

    Les trois fenêtres sont nommées par l'appelant à partir des dates réellement estimées. Sans la
    fenêtre d'AVANT, la figure comparait l'échantillon complet à l'une de ses sous-périodes, donc
    « tout » à « une partie de tout » : elle ne pouvait pas dire si le classement a survécu.
    """
    fr = use_style()
    fig, ax = plt.subplots(figsize=(9.6, 4.8))
    noms = full["candidate"].tolist()
    x = np.arange(len(noms))
    series = [(avant, f"{fenetre_avant} (avant le choc)", OKABE_ITO[0], -0.26),
              (full, f"{fenetre_longue} (échantillon complet)", OKABE_ITO[2], 0.0),
              (recent, f"{fenetre_recente} (fenêtre récente)", OKABE_ITO[3], 0.26)]
    for df, lab, couleur, decal in series:
        ax.bar(x + decal, df.set_index("candidate").reindex(noms)["rmse_h12"], 0.25,
               color=couleur, label=lab)
    ax.set_xticks(x)
    ax.set_xticklabels(noms, rotation=15, fontsize=8.5)
    # ce n'est pas une erreur de PRÉVISION hors échantillon : c'est le résidu d'un ajustement mené
    # sur toute la fenêtre, de l'inflation totale MOYENNE des douze mois suivants sur la mesure
    ax.set_ylabel("Erreur d'ajustement à 12 mois\n(points de pourcentage)", fontsize=9.5)
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=8.5)
    # le titre affirme le classement MESURÉ, il ne pose pas la question
    premier = {nom: str(df.loc[df["rmse_h12"].idxmin(), "candidate"])
               for nom, df in (("avant", avant), ("choc", recent))}
    rmse = {nom: float(df["rmse_h12"].min()) for nom, df in (("avant", avant), ("choc", recent))}
    if premier["avant"] == premier["choc"]:
        titre = (f"Le classement d'avant le choc tient : {premier['avant']} premier avant "
                 f"({rmse['avant']:.2f}) comme pendant ({rmse['choc']:.2f})")
    else:
        titre = (f"Le choc renverse le classement : {premier['avant']} premier avant, "
                 f"{premier['choc']} pendant")
    ax.set_title(titre.replace(".", ","), fontsize=11.5)
    fig.text(0.5, -0.06, "Racine de l'erreur quadratique moyenne des résidus de la régression, DANS "
                         "l'échantillon, de l'inflation totale moyenne\ndes 12 mois suivants sur la "
                         "mesure du mois courant (mesuré). Ce n'est pas une prévision hors échantillon.",
             ha="center", fontsize=7.5, color="#444444")
    fig.savefig(dest, bbox_inches="tight")
    plt.close(fig)
