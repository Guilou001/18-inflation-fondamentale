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
    ax.axhspan(1, 3, color="0.92", zorder=0, label="fourchette cible de la BdC")
    ax.set_ylabel("Glissement annuel (%)")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=8.5, loc="upper left")
    ax.set_title("2021-23, le régime que ces mesures devaient filtrer : elles ont suivi le choc, en retard")
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
        ax.legend(fontsize=8.5, title=f"écart absolu moyen : {mae:.2f} pt".replace(".", ","))
    axes[0].set_title("Les 55 composantes suffisent à retrouver la forme ; les décimales exigent la cuisine officielle")
    fig.savefig(dest)
    plt.close(fig)


def fig_concours(full: pd.DataFrame, recent: pd.DataFrame, dest: Path) -> None:
    """Le critère prédictif à 12 mois, avant et à travers le choc."""
    fr = use_style()
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    noms = full["candidate"].tolist()
    x = np.arange(len(noms))
    ax.bar(x - 0.18, full["rmse_h12"], 0.36, color=OKABE_ITO[0], label="échantillon long")
    ax.bar(x + 0.18, recent["rmse_h12"], 0.36, color=OKABE_ITO[3], label="2016-2025 (le choc)")
    ax.set_xticks(x)
    ax.set_xticklabels(noms, rotation=15, fontsize=8.5)
    ax.set_ylabel("RMSE de prévision de l'IPC total à 12 mois (pt)")
    ax.yaxis.set_major_formatter(fr)
    ax.legend(fontsize=9)
    ax.set_title("Le concours de Lao-Steyn rejoué : le classement d'avant 2019 survit-il au choc ?")
    fig.savefig(dest)
    plt.close(fig)
