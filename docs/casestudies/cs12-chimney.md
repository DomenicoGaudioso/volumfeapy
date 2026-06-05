---
layout: default
title: "CS12 - Ciminiera solida"
parent: Casi studio - volumfeapy
nav_order: 62
permalink: /casestudies/cs12-chimney/
---

# CS12 - Ciminiera solida rastremata con apertura

## Obiettivo

Questo caso studio modella una ciminiera in cemento armato come fusto solido
cilindrico rastremato con elementi **Hex8**. La geometria riprende il caso
CS13 di platefeapy:

- altezza `H = 60 m`;
- raggio medio alla base `3.00 m`;
- raggio medio in sommita' `2.05 m`;
- spessore `0.40 m`;
- apertura di servizio alla base;
- bordo inferiore incastrato;
- vento variabile in altezza e lungo la circonferenza.

Il carico del vento viene trasformato in forze nodali equivalenti sui nodi della
superficie esterna. Questa scelta rende il caso robusto anche senza dipendere da
una numerazione delle facce per pressioni locali su mesh cilindriche.

## Modello

```python
m, meta = build_chimney_solid(ntheta=12, nz=12)
res = m.solve()
```

| Grandezza | Valore |
|-----------|--------|
| Elementi Hex8 | 142 |
| Nodi | 312 |
| max \|u_radiale\| | 3.0069e-03 m |
| max \|u\| | 3.0114e-03 m |
| max von Mises | 2.4009e+05 Pa |
| Equilibrio `R_x + F_x` | 2.3020e-06 N |

## Visualizzazione

| Mesh | Deformata |
|------|-----------|
| ![Mesh ciminiera solida](images/cs12_chimney_mesh.png) | ![Deformata ciminiera solida](images/cs12_chimney_deformed.png) |

| Vincoli | Reazioni |
|---------|----------|
| ![Vincoli ciminiera solida](images/cs12_chimney_supports.png) | ![Reazioni ciminiera solida](images/cs12_chimney_reactions.png) |

| von Mises | sigma_xx |
|-----------|----------|
| ![von Mises ciminiera solida](images/cs12_chimney_vm.png) | ![sigma_xx ciminiera solida](images/cs12_chimney_sxx.png) |

## Confronto con platefeapy

Il caso platefeapy CS13 usa gli stessi parametri geometrici e la stessa legge di
vento, ma lavora sullo sviluppo piano equivalente della parete.

| Modello | Idealizzazione | Elementi | Nodi | Spostamento di confronto |
|---------|----------------|----------|------|--------------------------|
| platefeapy CS13 | sviluppo piano equivalente Q4 | 624 | 684 | max \|w\| = 1.6183 m |
| volumfeapy CS12 | solido cilindrico Hex8 | 142 | 312 | max \|u_radiale\| = 3.0069e-03 m |

Il modello solido e' molto piu' rigido perche' conserva la geometria cilindrica
chiusa e quindi attiva la rigidezza circonferenziale/membranale. Il modello
plate resta utile come esempio di mesh generica sviluppata in piano, ma non va
interpretato come una shell cilindrica completa.

## Script

`casestudies/cs12_chimney.py`
