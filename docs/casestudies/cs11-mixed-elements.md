---
layout: default
title: "CS11 - Spalla/plinto misto 3D"
parent: Casi studio - volumfeapy
nav_order: 61
permalink: /casestudies/cs11-mixed-elements/
---

# CS11 - Spalla/plinto con tutti gli elementi volumetrici

## Obiettivo

Questo caso studio costruisce un piccolo oggetto ingegneristico in calcestruzzo:
una spalla/plinto con corpo principale, rampa laterale, copertura piramidale e
contrafforti. Non e' una collezione di provini separati: tutti gli elementi
condividono nodi o facce e vengono assemblati nella stessa matrice globale.

Gli elementi usati nello stesso modello sono:

- **Hex8** per il blocco principale;
- **Wedge6** per la rampa/prisma laterale;
- **Pyramid5** per la copertura rastremata;
- **Tet4** per un contrafforte laterale lineare;
- **Tet10** per un contrafforte laterale quadratico.

## Visualizzazione

| Mesh mista | Deformata |
|------------|-----------|
| ![Mesh mista](images/cs11_mixed_mesh.png) | ![Deformata mesh mista](images/cs11_mixed_deformed.png) |

| Vincoli | Reazioni |
|---------|----------|
| ![Vincoli oggetto misto](images/cs11_mixed_supports.png) | ![Reazioni oggetto misto](images/cs11_mixed_reactions.png) |

| von Mises | sigma_zz |
|-----------|----------|
| ![von Mises mesh mista](images/cs11_mixed_vm.png) | ![sigma_zz mesh mista](images/cs11_mixed_szz.png) |

Il contour tensionale usa i valori nodali recuperati e li interpola sulle facce
esterne. Per Tet10 vengono usati anche i nodi intermedi della faccia, quindi il
plot segue la logica quadratica dell'elemento. Le iso-linee aiutano a leggere
le fasce di tensione anche con superfici opache.

## Modello

```python
mat = Material(E=30e9, nu=0.22)
m, eid_by_name = build_mixed_model(mat)

for nid, node in m.nodes.items():
    if abs(node.z) < 1e-12:
        m.fix(nid)

m.add_nodal_load(12, Fz=-18_000)
m.add_nodal_load(11, Fz=-6_000)
m.add_nodal_load(13, Fz=-4_000)
m.add_nodal_load(14, Fz=-4_000)
res = m.solve()
```

## Risultati

| Elemento | Volume [m3] | max \|u\| [m] | von Mises [Pa] |
|----------|-------------|---------------|----------------|
| Hex8 | 6.4000e+00 | 4.1297e-07 | 4.4317e+03 |
| Wedge6 | 8.7750e-01 | 5.7537e-07 | 6.0996e+03 |
| Pyramid5 | 1.2667e+00 | 5.3223e-07 | 3.8336e+03 |
| Tet4 | 5.0667e-01 | 1.0183e-06 | 1.3553e+04 |
| Tet10 | 5.0667e-01 | 5.7773e-05 | 2.0929e+04 |

## Script

`casestudies/cs11_mixed_elements.py`
