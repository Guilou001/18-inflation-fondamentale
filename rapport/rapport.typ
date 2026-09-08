#set document(title: "Quelles mesures montrent le mieux la tendance des prix ?", author: "Guillaume Vaudescal")
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.4cm),
  numbering: "1 / 1",
  footer: context [
    #set text(size: 8pt, fill: luma(90))
    #grid(columns: (1fr, auto), align: (left, right),
      [inflation-fondamentale], [#counter(page).display("1 / 1", both: true)])
  ],
)
#set text(font: ("Helvetica", "Arial", "DejaVu Sans"), size: 10pt, lang: "fr")
#set par(justify: true, leading: 0.68em, spacing: 1.1em)
#set heading(numbering: none)
#show heading.where(level: 2): it => block(above: 1.6em, below: 0.8em, text(size: 13pt, it))
#show heading.where(level: 3): it => block(above: 1.2em, below: 0.6em, text(size: 11pt, it))
#show raw.where(block: true): it => block(
  fill: luma(246), inset: 8pt, radius: 3pt, width: 100%, text(size: 8.5pt, it))
#show raw.where(block: false): it => text(size: 9pt, fill: rgb("#1a3f66"), it)
#show quote.where(block: true): it => block(
  inset: (left: 10pt), stroke: (left: 1.5pt + luma(180)),
  text(style: "italic", fill: luma(45), it.body))
// la table NE DOIT PAS être enfermée dans un par() : Typst 0.15 la supprime alors
// entièrement, sans erreur. Le réglage se pose donc dans la portée du bloc.
#show table: it => block(above: 1.1em, below: 1.1em,
  [#set par(justify: false); #text(size: 8.8pt, it)])
#show figure: it => block(above: 1.4em, below: 1.4em, it)
#show figure.caption: it => text(size: 8.5pt, fill: luma(70), it)
#show link: it => text(fill: rgb("#0072B2"), it)

#align(center)[
  #block(width: 100%)[
    #text(size: 18pt, weight: "bold")[Quelles mesures montrent le mieux la tendance des prix ?]
    #v(0.6em)
    #text(size: 10pt, fill: luma(70))[Guillaume Vaudescal · 2026-09-08 · #link("https://github.com/Guilou001/18-inflation-fondamentale")[Guilou001/18-inflation-fondamentale]]
  ]
]
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + luma(190))
#v(0.8em)

L'essence peut monter très vite pendant que beaucoup d'autres prix changent peu. L'inflation totale mélange ces mouvements. Les mesures d'inflation fondamentale cherchent à faire ressortir la tendance plus générale.

Ce projet compare les mesures canadiennes et reconstruit deux d'entre elles à partir des prix de 55 catégories de produits.

*La mesure tronquée garde le meilleur résultat au critère étudié, mais les erreurs augmentent dans la période récente.*

== Trois façons de regarder les mêmes prix

La mesure tronquée retire les mouvements extrêmes de chaque mois. La médiane retient le mouvement au milieu du panier pondéré. La mesure commune cherche une tendance partagée entre les composantes.

#figure(image("../results/figures/choc.png", width: 100%), caption: [Inflation totale et mesures de tendance pendant la hausse de 2021 à 2023])

Toutes les courbes sont des variations annuelles de prix. La zone de 1 % à 3 % sert de repère. Les mesures de tendance atténuent certains mouvements, sans effacer une hausse qui touche de nombreux produits.

#table(
  columns: 3,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Mesure*],
    [*Erreur sur 1990–2015*],
    [*Erreur sur la fenêtre récente à partir de 2016*],
    [Tronquée],
    [0,77],
    [1,15],
    [Médiane],
    [0,80],
    [1,24],
    [Commune],
    [0,85],
    [1,34],
)

Les erreurs sont en points de pourcentage. Une valeur plus basse est meilleure. Le calcul relie chaque mesure à l'inflation totale moyenne des douze mois suivants. Les données vont jusqu'en juillet 2026, ce qui limite les dernières dates évaluables. #link("results/tables/concours_avant_choc.csv")[Fenêtre ancienne] et #link("results/tables/concours_2016_2025.csv")[fenêtre récente].

== Retrouver le calcul derrière les séries

Le programme recompose la mesure tronquée et la médiane à partir des catégories de prix. Elles suivent les séries officielles, avec des écarts absolus moyens d'environ 0,24 et 0,22 point de pourcentage.

La différence vient notamment des poids du panier, des ajustements saisonniers et des impôts indirects que cette reconstruction ne reproduit pas exactement.

== Ce que le classement ne prouve pas

Les régressions sont ajustées sur chaque période complète et utilisent les séries révisées. Ce n'est pas un test de prévisions réellement disponibles à l'époque.

La période récente contient aussi d'autres changements que le choc de 2021–2023. La hausse des erreurs ne peut pas être attribuée intégralement à cet épisode.

== Refaire les calculs

#raw("uv sync --locked --all-extras\nuv run pytest\nuv run infc fetch\nuv run infc lab", block: true, lang: "bash")

Les commandes de téléchargement accèdent aux sources externes. Les tableaux et figures publiés restent consultables sans lancer les calculs.

== Pour aller plus loin

#link("docs/ETUDE_DETAILLEE.md")[Méthodes, résultats complets et références] · #link("rapport/rapport.pdf")[Présentation en PDF] · #link("CITATION.cff")[Citer le projet] · #link("LICENSE")[Licence].

== English summary

Canadian core inflation measures are compared on revised data, and CPI-trim and CPI-median are reconstructed from component prices. CPI-trim ranks first under the chosen full-sample criterion; this is not a real-time forecasting test.
