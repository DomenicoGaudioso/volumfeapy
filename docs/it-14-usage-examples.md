---
layout: default
title: "14 - Esempi d'Uso"
parent: Italiano
nav_order: 14
---

# 14 - Esempi d'Uso

La directory `usage_examples/` contiene script autocontenuti che coprono le
funzionalità principali.

## Esempi disponibili

| # | File | Descrizione |
|---|------|-------------|
| 01 | `01_convergence_hex8.py` | Studio di convergenza: Hex8 trazione uniassiale |
| 02 | `02_cantilever_convergence.py` | Mensola con raffinamento mesh Tet4 |

## Casi studio dalla letteratura

Un set completo di **11 casi FEM classici e didattici**
e' disponibile nella directory `casestudies/`, con documentazione
completa e immagini nel sito web. Ogni caso e' confrontato con una
soluzione analitica o semianalitica dove disponibile, oppure usato come
esempio mirato di elemento e visualizzazione.

| # | Caso | Riferimento |
|---|------|-------------|
| CS01 | Cubo in trazione uniassiale (Hex8) | Cook et al. §2 |
| CS02 | Mensola 3D (Tet4) | Euler-Bernoulli |
| CS03 | Cubo sotto pressione idrostatica | Lamé / modulo volumetrico |
| CS04 | Lastra con foro circolare (Kirsch) | K_t = 3 |
| CS05 | Cubo con peso proprio | sigma_zz = -rho g z |
| CS06 | Cubo con carico termico | Espansione libera |
| CS07 | Patch test (campo lineare) | Esatto per costruzione |
| CS08 | Confronto elementi (Hex8/Tet4/Wedge6) | Studio di convergenza |
| CS09 | Analisi modale cubo Hex8 | Frequenze naturali |
| CS10 | Elemento Pyramid5 | Esempio dedicato piramidale |
| CS11 | Modello misto 3D | Hex8, Tet4, Tet10, Wedge6, Pyramid5 |

→ [Esplora tutti i casi studio]({{ site.baseurl }}/casestudies/)

## Esecuzione esempi

```bash
cd volumfeapy
python usage_examples/01_convergence_hex8.py
```

## Esempio 01: Convergenza Hex8

Trazione uniassiale su un cubo unitario con raffinamento progressivo della mesh:

```python
from volumfeapy import Model, Material

L = 1.0
F = 1e6
E = 210e9
nu = 0.3

for n_el in [1, 2, 4, 8]:
    m = Model()
    # ... creare mesh hex n_el × n_el × n_el ...
    # ... fissare faccia inferiore, applicare trazione sulla superiore ...
    res = m.solve()
    u_max = max(res.displacement(nid, "uz") for nid in nodi_superiori)
    # ... confrontare con soluzione analitica ...
```

Output atteso:

```
Mesh  1x1x1  |  uz = 4.76e-06  |  err = 0.00%
Mesh  2x2x2  |  uz = 4.76e-06  |  err = 0.00%
Mesh  4x4x4  |  uz = 4.76e-06  |  err = 0.00%
```

Gli elementi Hex8 riproducono la tensione uniforme esattamente indipendentemente
dalla densità della mesh.

## Esempio 02: Convergenza mensola

Mensola (L=2m, b=0.1m, h=0.2m) con carico in punta P=1kN, meshata con Tet4:

```python
from volumfeapy import Model, Material

L = 2.0
P = 1000.0
E = 210e9
I = 0.1 * 0.2**3 / 12
u_esatto = P * L**3 / (3 * E * I)

for nx in [4, 8, 12, 16]:
    # ... creare mesh tet ...
    res = m.solve()
    u_punta = abs(res.displacement(nodo_punta, "uz"))
    # ... confrontare con soluzione di Eulero-Bernoulli ...
```

Gli elementi Tet4 convergono lentamente a causa della limitazione della
deformazione costante.

## Esempi base

La directory `examples/` contiene script più semplici:

| File | Descrizione |
|------|-------------|
| `ex01_uniaxial_hex8.py` | Cubo unitario in trazione uniassiale (Hex8) |
| `ex02_cantilever_tet4.py` | Mensola con mesh Tet4 |

```bash
python examples/ex01_uniaxial_hex8.py
```
