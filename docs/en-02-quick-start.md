---
layout: default
title: "02 - Quick Start"
parent: English
nav_order: 2
---

# 02 - Quick Start

Your first model: a unit cube under uniaxial tension.

```python
from volumfeapy import Model, Material

# 1. Create the model
m = Model()

# 2. Add nodes (unit cube)
m.add_node(1, 0, 0, 0)
m.add_node(2, 1, 0, 0)
m.add_node(3, 1, 1, 0)
m.add_node(4, 0, 1, 0)
m.add_node(5, 0, 0, 1)
m.add_node(6, 1, 0, 1)
m.add_node(7, 1, 1, 1)
m.add_node(8, 0, 1, 1)

# 3. Define material
mat = Material(E=210e9, nu=0.3)       # steel

# 4. Add hexahedral element
m.add_hex8(1, [1, 2, 3, 4, 5, 6, 7, 8], mat)

# 5. Apply constraints (fix bottom face)
for nid in [1, 2, 3, 4]:
    m.fix(nid)

# 6. Apply tensile load on top face
F = 1e6  # 1 MN total
for nid in [5, 6, 7, 8]:
    m.add_nodal_load(nid, Fz=F / 4.0)

# 7. Solve
res = m.solve()

# 8. Read results
print(res.displacements(5))   # [ux, uy, uz] at node 5
```

## Expected result

For uniaxial tension: `σ_zz = F/A`, `u_z = F·L/(E·A)`

```python
u_exact = F * 1.0 / (210e9 * 1.0)
print(f"uz FEM   = {res.displacement(5, 'uz'):.6e} m")
print(f"uz exact = {u_exact:.6e} m")
```

## Next steps

- [Structural Model](en-03-structural-model.md) — nodes, materials, elements
- [Element Types](en-04-element-types.md) — Hex8, Tet4, Tet10, Wedge6, Pyramid5
- [Loads](en-05-loads.md) — body forces, gravity, thermal, pressure
- [Post-Processing](en-08-post-processing.md) — stresses, von Mises, principal stresses
