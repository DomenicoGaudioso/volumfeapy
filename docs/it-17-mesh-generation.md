---
layout: default
title: "17 - Generazione Mesh"
parent: Italiano
nav_order: 17
---

# 17 - Generazione Mesh

`volumfeapy` puo' usare l'API Python ufficiale di Gmsh come meshatore
opzionale. Installa l'extra `mesh` prima di usare questi helper:

```bash
pip install -e ".[mesh]"
```

Gmsh e' un generatore di mesh FEM 3D con API Python per creare geometrie,
generare mesh ed estrarre nodi/elementi. `volumfeapy` incapsula la parte di
conversione e trasforma gli elementi 3D supportati in un `Model`.

## Mesh tetraedrica di un parallelepipedo

```python
from volumfeapy import Material
from volumfeapy.meshing import mesh_box_tet

mat = Material(E=210e9, nu=0.3)
m = mesh_box_tet(
    mat,
    lx=1.0,
    ly=0.4,
    lz=0.3,
    mesh_size=0.15,
    order=1,        # 1 = Tet4, 2 = Tet10
)
```

L'oggetto restituito e' un normale `Model`, quindi vincoli, carichi, soluzione
e post-processing funzionano come per le mesh definite manualmente.

## Risolvere la mesh generata

```python
z_min = min(node.z for node in m.nodes.values())
z_max = max(node.z for node in m.nodes.values())

bottom = [nid for nid, n in m.nodes.items() if abs(n.z - z_min) < 1e-9]
top = [nid for nid, n in m.nodes.items() if abs(n.z - z_max) < 1e-9]

for nid in bottom:
    m.fix(nid)
for nid in top:
    m.add_nodal_load(nid, Fz=-1000.0 / len(top))

res = m.solve(sparse=True)
```

## Elementi importati supportati

`from_gmsh(material)` converte la mesh attiva del modello Gmsh in elementi
`volumfeapy` quando i tipi Gmsh corrispondono:

| Elemento Gmsh | Elemento volumfeapy |
|---------------|---------------------|
| Tet4 | `Tet4` |
| Tet10 | `Tet10` |
| Hex8 | `Hex8` |
| Prism/Wedge6 | `Wedge6` |
| Pyramid5 | `Pyramid5` |

Gli elementi non supportati vengono saltati. Se non viene trovato alcun
elemento 3D supportato, l'importer solleva `ValueError`.

## Salvare la mesh Gmsh

```python
m = mesh_box_tet(
    mat,
    lx=1.0,
    ly=0.4,
    lz=0.3,
    mesh_size=0.15,
    save_msh="box.msh",
)
```

## Script di esempio

Esegui l'esempio completo:

```bash
python examples/ex03_gmsh_box_tet.py
```
