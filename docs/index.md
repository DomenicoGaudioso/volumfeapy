---
layout: default
title: Home
nav_order: 1
---

# volumfeapy

<div align="center">
  <img src="img/Logo_VolumfeaPy.png" alt="volumfeapy Logo" width="216">
</div>

A Python finite-element solver for the **static and modal analysis** of **3D solid structures** using hexahedral, tetrahedral, wedge and pyramid elements.

## Quick Start

```python
from volumfeapy import Model, Material

m = Model()
m.add_node(1, 0, 0, 0)
m.add_node(2, 1, 0, 0)
m.add_node(3, 1, 1, 0)
m.add_node(4, 0, 1, 0)
m.add_node(5, 0, 0, 1)
m.add_node(6, 1, 0, 1)
m.add_node(7, 1, 1, 1)
m.add_node(8, 0, 1, 1)

mat = Material(E=210e9, nu=0.3)
m.add_hex8(1, [1,2,3,4,5,6,7,8], mat)

for nid in range(1, 5):
    m.fix(nid)

m.add_nodal_load(6, Fz=-10000)
res = m.solve()
print(res.displacements(6))
```

## Features

- **Hex8** (8-node hexahedron/brick, trilinear, 2x2x2 Gauss integration)
- **Tet4** (4-node tetrahedron, linear, constant strain)
- **Tet10** (10-node tetrahedron, quadratic, 4-point Gauss)
- **Wedge6** (6-node wedge/prism, triangular base × linear extrusion)
- **Pyramid5** (5-node pyramid, quadrilateral base + apex)
- **Body forces** (uniform volume forces)
- **Gravity loads** (automatic from density)
- **Thermal loads** (uniform temperature change)
- **Face pressures** (pressure on element faces)
- **Nodal settlements** (imposed displacements)
- **Modal analysis** (natural frequencies and mode shapes)
- **Post-processing**: stresses (σxx, σyy, σzz, τxy, τyz, τxz), von Mises, principal stresses
- **Plotly visualization**: mesh, deformed shape, stress maps, mode shapes
