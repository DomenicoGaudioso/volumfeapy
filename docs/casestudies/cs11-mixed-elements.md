---
layout: default
title: "CS11 - Mesh mista 3D"
parent: Casi studio - volumfeapy
nav_order: 61
permalink: /casestudies/cs11-mixed-elements/
---

# CS11 - Tutti gli elementi volumetrici in un modello

## Obiettivo

Questo caso studio costruisce un unico modello con tutti gli elementi
volumetrici implementati in **volumfeapy**:

- **Hex8**
- **Tet4**
- **Tet10**
- **Wedge6**
- **Pyramid5**

I cinque provini sono separati nello spazio per rendere leggibili le geometrie.
Ogni provino e' vincolato alla base e caricato verticalmente in sommità. Il
risultato e' utile come esempio di API e come controllo visivo delle routine di
plot per mesh eterogenee.

## Visualizzazione

| Mesh mista | Deformata |
|------------|-----------|
| ![Mesh mista](images/cs11_mixed_mesh.png) | ![Deformata mesh mista](images/cs11_mixed_deformed.png) |

| von Mises | sigma_zz |
|-----------|----------|
| ![von Mises mesh mista](images/cs11_mixed_vm.png) | ![sigma_zz mesh mista](images/cs11_mixed_szz.png) |

Il contour tensionale usa i valori nodali recuperati e li interpola sulle
facce esterne. Per Tet10 vengono usati anche i nodi intermedi della faccia,
quindi il plot segue la logica quadratica dell'elemento.

## Modello

```python
from volumfeapy import Material, Model

mat = Material(E=30e9, nu=0.22)
m = Model()

# In un solo modello:
m.add_hex8(...)
m.add_tet4(...)
m.add_tet10(...)
m.add_wedge6(...)
m.add_pyramid5(...)

# Ogni provino ha base vincolata e carico verticale in sommità.
res = m.solve()
```

## Risultati

| Elemento | Nodi | Volume [m3] | max \|u\| [m] | von Mises [Pa] |
|----------|------|-------------|---------------|----------------|
| Hex8 | 8 | 1.0000e+00 | 3.2730e-07 | 9.0761e+03 |
| Tet4 | 4 | 1.6667e-01 | 1.7518e-06 | 4.3077e+04 |
| Tet10 | 10 | 1.6667e-01 | 5.2791e-06 | 6.2355e+04 |
| Wedge6 | 6 | 4.5000e-01 | 7.2941e-07 | 2.0304e+04 |
| Pyramid5 | 5 | 1.6667e-01 | 2.9197e-07 | 7.1795e+03 |

## Script

`casestudies/cs11_mixed_elements.py`
