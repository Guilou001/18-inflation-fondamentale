#set document(title: "L'inflation fondamentale à l'épreuve du choc : le concours rejoué, la recette refaite", author: "Guillaume Vaudescal")
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
    #text(size: 18pt, weight: "bold")[L'inflation fondamentale à l'épreuve du choc : le concours rejoué, la recette refaite]
    #v(0.6em)
    #text(size: 10pt, fill: luma(70))[Guillaume Vaudescal · 2026-08-30 · #link("https://github.com/Guilou001/18-inflation-fondamentale")[Guilou001/18-inflation-fondamentale]]
  ]
]
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + luma(190))
#v(0.8em)

Les trois mesures d'inflation fondamentale de la Banque du Canada ont gagné leur place sur des données d'avant 2019 ; le choc de 2021-23 est exactement le régime qu'elles devaient filtrer. Ce dépôt rejoue le concours de Lao et Steyn à travers le choc, et reconstruit IPC-tronq et IPC-méd depuis les 55 composantes, écart mesuré à l'officiel. _English summary below._

Le même contenu en PDF : #link("rapport/rapport.pdf")[rapport/rapport.pdf].

== En bref

+ *Le podium d'avant 2019 survit au choc, et la relégation de la Banque était dans les données.* Sur le critère d'ajustement à 12 mois : IPC-tronq gagne AVANT le choc (0,77 point de pourcentage sur 1990-01 à 2015-12), sur l'échantillon complet (0,89) et sur la fenêtre récente (1,15) ; l'IPC-comm, que la Banque a déclassé en 2022, finit dernier des trois mesures officielles dans les trois fenêtres (0,85, puis 1,01, puis 1,33). Le choc n'a pas rebattu les cartes, il a juste rendu tout le monde moins précis (+48 % d'erreur pour l'IPC-tronq entre la fenêtre d'avant et la fenêtre récente). (Mesuré.)
+ *Les 55 composantes suffisent à retrouver la forme ; les décimales exigent la cuisine officielle.* Notre reconstruction (tronquage à 20 % de poids par queue, médiane pondérée) colle à l'officiel à 0,24 point d'écart absolu moyen pour IPC-tronq et 0,22 pour IPC-méd (corrélations 0,95 et 0,96 sur 439 mois), avec QUATRE approximations déclarées : pas de correction des impôts indirects, STL au lieu du X-13 officiel, panier de poids statique, et 53 à 54 composantes avant décembre 1997 (les deux séries que la table A1 marque « partiellement construites par la Banque » ne sont pas publiques ; effet borné par contrefactuel : environ 0,06 point là où il s'applique). L'écart maximal (1,7 point) tombe sur 1991 et mêle les deux premières causes : la TPS entre en vigueur (impôts indirects omis) au moment où le panier est à 53 composantes. (Mesuré.)
+ *Deux guichets, une seule vérité :* les mesures officielles publiées par StatCan (18-10-0256) et par Valet (BdC) coïncident exactement sur l'échantillon commun (contrôle croisé, #raw("results/tables/controle_valet.csv")). (Mesuré.)

== La question

En 2016, la Banque du Canada a retenu IPC-tronq, IPC-méd et IPC-comm à l'issue d'un concours (Khan, Morel et Sabourin 2013 ; Lao et Steyn 2019) couru sur des données où l'inflation dormait entre 1 et 3 %. Or 2021-23 a envoyé l'IPC total à 8 % et les mesures fondamentales au-dessus de 5 % : le régime que ces filtres devaient justement absorber. Rejouées à travers le choc, gagnent-elles encore leur propre concours ?

== Les données (100 % libres, licence ouverte de StatCan, jamais commitées)

#table(
  columns: 3,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Source*],
    [*Contenu*],
    [*Statut*],
    [StatCan 18-10-0004 (API WDS)],
    [IPC mensuel NON désaisonnalisé par produit, Canada],
    [mesuré],
    [StatCan 18-10-0007],
    [poids du panier au mois de raccord, par période de base],
    [mesuré],
    [StatCan 18-10-0256],
    [IPC-tronq, IPC-méd, IPC-comm officiels (une décimale publiée)],
    [mesuré],
    [BdC Valet #raw("CPI_TRIM, CPI_MEDIAN, CPI_COMMON")],
    [le miroir des mêmes séries],
    [mesuré],
)

La liste des 55 composantes vient de la table A1 du document méthodologique officiel (programme 2301 de StatCan, rapporté), recopiée dans #raw("components.py") et vérifiée mot à mot par la contre-vérification. Le chargeur échoue si une COLONNE manque ; la couverture TEMPORELLE est une autre affaire : deux composantes (l'astérisque de la table A1 : « séries partiellement construites par la Banque du Canada ») n'existent dans la table publique qu'à partir de 1994-12 et 1997-12. Les mois à 53 ou 54 composantes sont acceptés, JOURNALISÉS (colonne #raw("n_composantes") de #raw("reconstruction.csv")) et comptés comme la quatrième approximation ; en deçà de 53, le calcul refuse. Détail d'exhaustivité déclaré : les 55 composantes de 2016 ne couvrent plus que 99,2 % du panier de 2025 (le cannabis récréatif est hors liste) ; les poids sont renormalisés.

== Volet 1 : le concours de Lao-Steyn, rejoué à travers le choc

Les critères du papier : le biais (la moyenne de l'écart à l'IPC total), le lissage (l'écart-type des variations mensuelles) et le pouvoir prédictif (le RMSE de la régression de l'inflation totale moyenne des 12 et 24 prochains mois sur la mesure courante, pleine période comme chez Lao-Steyn, déclaré). Candidates : les trois mesures officielles, l'IPC hors alimentation et énergie, la moyenne mobile de 12 mois.

#table(
  columns: 4,
  stroke: (x, y) => if y == 0 { (bottom: 0.6pt) } else { none },
  align: left + top,
  inset: 5pt,
    [*Erreur d'ajustement à 12 mois (pp)*],
    [*Avant le choc (1990-01 à 2015-12)*],
    [*Échantillon complet (1990-01 à 2026-07)*],
    [*Fenêtre récente (2016-01 à 2026-07)*],
    [*IPC-tronq*],
    [*0,77*],
    [*0,89*],
    [*1,15*],
    [IPC-méd],
    [0,80],
    [0,94],
    [1,24],
    [IPC-comm],
    [0,85],
    [1,01],
    [1,33],
    [IPC hors aliments et énergie],
    [0,82],
    [1,00],
    [1,31],
    [Moyenne mobile 12 mois],
    [0,88],
    [1,09],
    [1,45],
)

*Lecture guidée.* Trois enseignements mesurés. L'IPC-tronq garde son premier rang dans les trois fenêtres, y compris dans celle qui s'arrête AVANT le choc : le choix de 2016 tient, et la comparaison est cette fois entre deux périodes disjointes et non entre un échantillon et l'une de ses sous-périodes. L'IPC-comm est dernier des mesures officielles partout, et la Banque l'a rétrogradé en 2022 après ses grandes révisions : sa relégation se lisait déjà dans le critère. Et TOUTES les mesures perdent de 48 à 65 % de précision entre la fenêtre d'avant et la fenêtre récente : le choc n'a pas changé le classement, il a coûté à tout le monde. Sur le lissage, l'IPC-méd est la plus stable (0,13 d'écart-type de variation mensuelle) et l'IPC hors alimentation-énergie la plus bruyante (0,30) : le filtre « fixe » exclut toujours les mêmes postes, même quand le choc vient d'ailleurs.

#figure(image("../results/figures/choc.png", width: 100%), caption: [Choc])

*Comment lire cette figure.* L'IPC total (gris) et les trois mesures officielles, bande grise sur la fourchette cible de 1 à 3 %. En 2021-23, les mesures fondamentales montent à 5-6 % : elles ont filtré le sommet de 8,1 % mais suivi le gros du choc. Le retard n'est pas le même pour les trois, et c'est mesuré : l'IPC-tronq culmine LE MÊME MOIS que l'IPC total, en 2022-06 ; l'IPC-méd retarde de quatre mois et l'IPC-comm de cinq. Un filtre de tendance n'est pas un bouclier, mais celui que la Banque a retenu ne retarde pas.

== Volet 2 : la recette refaite, et ce que l'écart enseigne

La méthode officielle (document 2301, rapporté) : 55 composantes, corrigées des impôts indirects, désaisonnalisées (44 sur 55, X-13), variations MENSUELLES, tronquage à 20 % de poids dans chaque queue ou médiane pondérée, poids au mois de raccord du panier. Notre reconstruction assume quatre approximations, toutes déclarées : pas de correction des impôts indirects, STL robuste au lieu du X-13 officiel, panier de poids statique (le plus récent), et 53 à 54 composantes avant décembre 1997 (voir la section données). Les mathématiques du tronquage et de la médiane pondérée sont, elles, exactes et testées sur cas à la main, poids partiels aux bornes compris ; la médiane suit la lettre du document officiel (la première composante dont le poids cumulé DÉPASSE 50 %).

#figure(image("../results/figures/reconstruction.png", width: 100%), caption: [Reconstruction])

*Comment lire cette figure.* L'officiel (bleu) et notre reconstruction (tirets orange) pour IPC-tronq (haut) et IPC-méd (bas). La forme est retrouvée partout : corrélations de 0,95 et 0,96, écarts absolus moyens de 0,24 et 0,22 point (#raw("results/tables/ecarts_reconstruction.csv")). Les écarts se concentrent où les approximations mordent : autour de 1991 (écart maximal de 1,7 point, où se superposent la TPS, donc l'omission des impôts indirects, ET le panier réduit à 53 composantes d'avant 1994) et pendant le choc de 2021-23 pour la tronquée (0,48 point d'écart moyen, quand la désaisonnalisation et les poids comptent le plus). Le contrefactuel mesuré sur 1998-2026, où les 55 existent : retirer les deux composantes tardives déplace le glissement de 0,056 point de pourcentage en moyenne pour la tronquée et 0,062 pour la médiane, avec un maximum de 0,22 en 2022-04, sur 343 mois de 1998-01 à 2026-07 (mesuré, #raw("results/tables/contrefactuel_composantes.csv")) : le quart environ de l'écart total. La décimale publiée exige la cuisine officielle, facteurs X-13 non publiés compris : l'écart mesuré en est le prix, et il est petit.

== Reproduire

#raw("uv sync --locked --all-extras\nuv run pytest        # 9 tests fermés, sans réseau\nuv run infc fetch    # 3 tables StatCan + Valet (~17 Mo)\nuv run infc lab      # reconstruction + concours : 6 tables, 3 figures (~3 min, STL sur 55 séries)", block: true, lang: "bash")

Les tests, tous à la main : la médiane pondérée sur cas frontière (la première composante dont le cumul DÉPASSE 50 %, la lettre du document officiel) et sur cas franc ; le tronquage avec poids partiels aux bornes ; le cas dégénéré toutes-composantes-égales ; la composition mensuelle vers le glissement annuel (1,003 puissance 12) ; la STL qui retire une saisonnalité plantée ; le concours qui préfère le vrai signal au bruit ; les 55 composantes uniques.

== Limites, avec statut

+ *Quatre approximations dans la reconstruction, chacune déclarée* : impôts indirects non corrigés, STL au lieu du programme officiel de désaisonnalisation (facteurs non publiés), panier de poids statique, et 53 à 54 composantes avant décembre 1997 (les deux séries reconstruites par la Banque ne sont pas publiques ; effet contrefactuel d'environ 0,06 point, mesuré sur 1998-2026 ; attrapée par la contre-vérification adversariale, elle manquait à la première version). L'écart de 0,22-0,24 point est leur prix total ; la décomposition complète n'est pas isolée. (Déclaré et mesuré.)
+ *Le critère prédictif est en pleine période*, comme chez Lao-Steyn : c'est une comparaison de mesures, pas un exercice de prévision en temps réel ; une version récursive serait plus dure et la suite naturelle. (Déclaré.)
+ *Les données de 18-10-0004 sont les séries COURANTES*, révisées : pas de millésimes point-in-time pour l'IPC (les révisions de l'IPC non désaisonnalisé sont rares, rapporté ; celles des mesures officielles, réelles, la Banque ayant documenté les révisions de l'IPC-comm). (Déclaré.)
+ *L'IPC-comm n'est pas reconstruit* (modèle à facteur sur glissements annuels, publié en variation seulement, déclassé par la Banque depuis 2022) : il concourt au volet 1 via sa série officielle, c'est tout. (Déclaré.)
+ *Le choc de 2021-23 n'offre qu'un cycle.* Le classement qui y survit est un constat, pas une garantie pour le prochain régime. (Déclaré.)

== Références

- Lao, H. et C. Steyn (2019), « A comprehensive evaluation of measures of core

inflation in Canada: an update », Banque du Canada, Staff Discussion Paper 2019-9.

- Khan, M., L. Morel et P. Sabourin (2013), « The common component of CPI: an

alternative measure of underlying inflation for Canada », Banque du Canada, WP 2013-35 ; et (2015), Staff Discussion Paper 2015-12.

- Banque du Canada (2016), _Renouvellement de la cible de maîtrise de l'inflation_,

document d'information.

- Statistique Canada, document méthodologique des mesures de la Banque du Canada

(programme 2301) : la méthode et la table A1 des 55 composantes.

== English summary

The Bank of Canada's three preferred core inflation measures won their 2016 selection on pre-2019 data; 2021-23 delivered exactly the regime they were built to filter. (1) We re-run the Lao-Steyn horse race THROUGH the shock: on the predictive criterion (RMSE for 12-month-ahead headline CPI), CPI-trim wins on the long sample (0.89 pt) AND on the recent window (1.15) and, crucially, on a window that STOPS BEFORE the shock (0.77); CPI-common, which the Bank demoted in 2022 after large revisions, ranks last of the three official measures in both windows (1.02, then 1.40): the demotion was already in the data. Every candidate loses 30-40 % of precision through the shock: the ranking survived, the precision did not. (2) We rebuild CPI-trim and CPI-median from the official 55-component list (Table A1, hard-coded and verified word for word): weighted 20 %-per-tail trim and weighted median (official boundary convention), with FOUR declared approximations: no indirect-tax adjustment, STL instead of the unpublished official seasonal factors, static basket weights, and 53-54 components before December 1997 (the two Bank-constructed series are not public; counterfactual effect ~0.06 pt where it applies, logged per month). Result: mean absolute gap of 0.24 pt (trim) and 0.22 pt (median) to the official series over 439 months, correlations 0.95-0.96, with the largest gap at 1991 where the GST introduction and the reduced basket overlap. StatCan and Bank of Canada (Valet) copies of the official series match exactly (cross-checked). Free data, open licence, 9 hand-computed tests.

== Licence et citation

Code sous licence MIT ; rapport et figures CC BY 4.0. Données : Statistique Canada (licence ouverte, attribution : « Source : Statistique Canada »), Banque du Canada (attribution). Citer via #raw("CITATION.cff").
