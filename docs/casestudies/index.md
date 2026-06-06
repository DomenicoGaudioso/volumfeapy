---
layout: default
title: "Casi studio - volumfeapy"
nav_order: 50
has_children: true
permalink: /casestudies/
---

# Casi studio volumfeapy

I casi studio raccolgono i benchmark classici della letteratura FEM per
solidi 3D, risolti con **volumfeapy** e confrontati con le soluzioni
analitiche di riferimento (laminazione, trazione uniassiale, Kirsch,
Euler-Bernoulli, ecc.). Per ogni caso viene mostrato il modello
costruito, la deformata 3D e la mappa delle tensioni (sigma_xx, von
Mises, ecc.).

I casi coprono diversi tipi di elementi (Hex8, Tet4, Wedge6, Tet10,
Pyramid5) e condizioni di carico (trazione uniassiale, pressione
idrostatica, body force, thermal load, modale).

## Indice dei casi

| # | Caso | Soluzione di riferimento |
|---|------|--------------------------|
| [CS01](cs01-cube-uniaxial) | Cubo in trazione uniassiale (Hex8) | sigma_zz = q, u_z = qL/E |
| [CS02](cs02-cantilever-3d) | Mensola 3D (Tet4) sotto carico in punta | u_z = P L^3 / (3 E I) (Euler-Bernoulli) |
| [CS03](cs03-hydrostatic-cube) | Cubo in pressione idrostatica | sigma = -p uniforme, K_bulk |
| [CS04](cs04-kirsch-plate) | Lastra piana con foro (Kirsch) | K_t = 3 (lastra infinita) |
| [CS05](cs05-body-force) | Cubo con peso proprio (gravita') | sigma_zz(z) = -rho g z |
| [CS06](cs06-thermal) | Cubo con thermal load | u = alpha dT * x (espansione libera) |
| [CS07](cs07-patch-test) | Patch test (campo lineare) | Esatto per costruzione |
| [CS08](cs08-element-convergence) | Confronto Hex8 / Tet4 / Wedge6 | u_z = P L^3 / (3 E I) |
| [CS09](cs09-modal-cube) | Analisi modale cubo Hex8 | Modi propri di vibrazione |
| [CS10](cs10-pyramid-element) | Elemento piramidale Pyramid5 | Esempio dedicato Pyramid5 |
| [CS11](cs11-mixed-elements) | Mesh mista con tutti gli elementi | Hex8, Tet4, Tet10, Wedge6, Pyramid5 |
| [CS12](cs12-chimney) | Ciminiera solida rastremata | confronto con platefeapy CS13 |
| [CS13](cs13-box-girder) | Cassone sottile volumetrico | confronto con platefeapy CS14 |

## Esecuzione

```bash
cd volumfeapy
python -m casestudies.run_all
```

I singoli casi sono in `casestudies/csNN_*.py`; ciascuno e' eseguibile
anche standalone con `python casestudies/csNN_*.py`.

## Convenzioni

- **Materiale di default**: acciaio (`E = 210 GPa`, `nu = 0.3`, `rho = 7850 kg/m^3`)
- **Mesh tipica**: 4x4x4 Hex8 (256 elementi) per i casi "riferimento"
- **Scala deformata**: 200× o 50000× rispetto al valore reale (per la
  visualizzazione; i valori numerici rimangono quelli reali)

## Risultati di sintesi

| Caso | Errore FEM vs analitico | Note |
|------|-------------------------|------|
| CS01 Cube trazione     | < 5%        | sigma_zz esatto |
| CS02 Cantilever Tet4   | 30% (n=20)  | Tet4 = CST, lento in flessione |
| CS03 Pressione idrost. | ~20-30%     | Vincolo su 1 nodo perturba |
| CS04 Kirsch foro       | molto alto  | Mesh rettangolare non ideale per cerchio |
| CS05 Body force        | < 3%        | Buona convergenza |
| CS06 Thermal           | < 10%       | Espansione libera |
| CS07 Patch test        | < 1e-12     | Superato |
| CS08 Hex8 vs Tet4      | Hex8 14%, Tet4 39% | Tet4 e' noto rigido in flessione |
| CS09 Modal cube        | qualitativo | Frequenze 5-15 kHz |
| CS10 Pyramid5          | qualitativo | Elemento piramidale caricato all'apice |
| CS11 Mesh mista        | qualitativo | Spalla/plinto unico con tutti gli elementi 3D |
| CS12 Ciminiera solida  | qualitativo | Hex8 cilindrico, max u_radiale = 3.3069e-03 m |
| CS13 Cassone solido    | ~12% vs shell | Hex8 sottile confrontato con platefeapy CS14 |

Per i casi con errore elevato (CS02, CS03, CS04), le cause sono note
nella letteratura FEM e richiedono mesh adattate, elementi di ordine
superiore o formulazioni arricchite.
