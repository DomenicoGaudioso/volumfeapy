---
layout: default
title: "17 - Mesh Generation"
parent: English
nav_order: 17
---

# 17 - Mesh Generation

`volumfeapy` can use the official Gmsh Python API as an optional mesher.
Install the `mesh` extra before using these helpers:

```bash
pip install -e ".[mesh]"
```

Gmsh is a 3D finite-element mesh generator with a Python API for creating
geometry, generating meshes, and extracting nodes/elements. `volumfeapy`
wraps the extraction step and converts supported 3D elements into a `Model`.

## Box tetrahedral mesh

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

The returned object is a normal `Model`, so constraints, loads, solve and
post-processing work exactly like manually defined meshes.

## Solve generated mesh

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

## Supported imported elements

`from_gmsh(material)` converts the active Gmsh model mesh into `volumfeapy`
elements when Gmsh element types match:

| Gmsh element | volumfeapy element |
|--------------|--------------------|
| Tet4 | `Tet4` |
| Tet10 | `Tet10` |
| Hex8 | `Hex8` |
| Prism/Wedge6 | `Wedge6` |
| Pyramid5 | `Pyramid5` |

Unsupported element types are skipped. If no supported 3D elements are found,
the importer raises `ValueError`.

## Save the Gmsh mesh

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

## Example script

Run the complete example:

```bash
python examples/ex03_gmsh_box_tet.py
```
