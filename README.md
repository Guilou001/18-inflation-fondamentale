# Quelles mesures montrent le mieux la tendance des prix ?

L'essence peut monter très vite pendant que beaucoup d'autres prix changent peu. L'inflation totale mélange ces mouvements. Les mesures d'inflation fondamentale cherchent à faire ressortir la tendance plus générale.

Ce projet compare les mesures canadiennes et reconstruit deux d'entre elles à partir des prix de 55 catégories de produits.

**La mesure tronquée garde le meilleur résultat au critère étudié, mais les erreurs augmentent dans la période récente.**

## Trois façons de regarder les mêmes prix

La mesure tronquée retire les mouvements extrêmes de chaque mois. La médiane retient le mouvement au milieu du panier pondéré. La mesure commune cherche une tendance partagée entre les composantes.

![Inflation totale et mesures de tendance pendant la hausse de 2021 à 2023](results/figures/choc.png)

Toutes les courbes sont des variations annuelles de prix. La zone de 1 % à 3 % sert de repère. Les mesures de tendance atténuent certains mouvements, sans effacer une hausse qui touche de nombreux produits.

| Mesure | Erreur sur 1990–2015 | Erreur sur la fenêtre récente à partir de 2016 |
|---|---:|---:|
| Tronquée | 0,77 | 1,15 |
| Médiane | 0,80 | 1,24 |
| Commune | 0,85 | 1,34 |

Les erreurs sont en points de pourcentage. Une valeur plus basse est meilleure. Le calcul relie chaque mesure à l'inflation totale moyenne des douze mois suivants. Les données vont jusqu'en juillet 2026, ce qui limite les dernières dates évaluables. [Fenêtre ancienne](results/tables/concours_avant_choc.csv) et [fenêtre récente](results/tables/concours_2016_2025.csv).

## Retrouver le calcul derrière les séries

Le programme recompose la mesure tronquée et la médiane à partir des catégories de prix. Elles suivent les séries officielles, avec des écarts absolus moyens d'environ 0,24 et 0,22 point de pourcentage.

La différence vient notamment des poids du panier, des ajustements saisonniers et des impôts indirects que cette reconstruction ne reproduit pas exactement.

## Ce que le classement ne prouve pas

Les régressions sont ajustées sur chaque période complète et utilisent les séries révisées. Ce n'est pas un test de prévisions réellement disponibles à l'époque.

La période récente contient aussi d'autres changements que le choc de 2021–2023. La hausse des erreurs ne peut pas être attribuée intégralement à cet épisode.

## Refaire les calculs

```bash
uv sync --locked --all-extras
uv run pytest
uv run infc fetch
uv run infc lab
```

Les commandes de téléchargement accèdent aux sources externes. Les tableaux et figures publiés restent consultables sans lancer les calculs.

## Pour aller plus loin

[Méthodes, résultats complets et références](docs/ETUDE_DETAILLEE.md) · [Présentation en PDF](rapport/rapport.pdf) · [Citer le projet](CITATION.cff) · [Licence](LICENSE).

## English summary

Canadian core inflation measures are compared on revised data, and CPI-trim and CPI-median are reconstructed from component prices. CPI-trim ranks first under the chosen full-sample criterion; this is not a real-time forecasting test.
