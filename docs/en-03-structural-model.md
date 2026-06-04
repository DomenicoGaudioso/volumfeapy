---
layout: default
title: "03 - Structural Model"
parent: English
nav_order: 3
---

# 03 - Structural Model

## Nodes

Each node has 3 degrees of freedom (DOFs): `[ux, uy, uz]`.

```python
m.add_node(id, x, y, z)   # id = integer identifier, coordinates in meters
```

Example:
```python
m.add_node(1, 0, 0, 0)    # origin
m.add_node(2, 5, 0, 0)    # 5 m along X
m.add_node(3, 5, 3, 0)    # 5 m in X, 3 m in Y
m.add_node(4, 0, 0, 4)    # 4 m in Z (vertical)
```

## Materials

```python
mat = Material(E=210e9, nu=0.3, alpha=1.2e-5)   # steel
mat = Material(E=30e9, nu=0.2, alpha=1.0e-5)       # concrete
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `E` | Young's modulus [Pa] | required |
| `nu` | Poisson's ratio | 0.3 |
| `alpha` | Thermal expansion coefficient [1/°C] | 0.0 |
| `G` | Shear modulus [Pa] | computed from E and nu |
| `rho` | Density [kg/m³] | 0.0 |

### Constitutive matrix

The material provides the 6×6 constitutive matrix D (Voigt notation):

```python
D = mat.D_matrix()
# [σxx, σyy, σzz, τxy, τyz, τxz] = D @ [εxx, εyy, εzz, γxy, γyz, γxz]
```

## Elements

### Adding elements

```python
# Hexahedron (8 nodes)
m.add_hex8(id, [n1, n2, n3, n4, n5, n6, n7, n8], material)

# Tetrahedron (4 nodes)
m.add_tet4(id, [n1, n2, n3, n4], material)

# Tetrahedron (10 nodes, quadratic)
m.add_tet10(id, [n1, ..., n10], material)

# Wedge (6 nodes)
m.add_wedge6(id, [n1, n2, n3, n4, n5, n6], material)

# Pyramid (5 nodes)
m.add_pyramid5(id, [n1, n2, n3, n4, n5], material)
```

See [Element Types](en-04-element-types.md) for node ordering and details.

## Supports

```python
m.fix(node)                              # fixed: all 3 DOFs restrained
m.support(node, ux=True, uy=True)        # custom: only specified DOFs
```

| Method | Restrained DOFs | Typical use |
|--------|-----------------|-------------|
| `fix(n)` | ux, uy, uz | Fixed support |
| `support(n,...)` | custom | Roller, symmetry, etc. |

Examples:
```python
# Fixed support
m.fix(1)

# Symmetry plane (ux=0)
m.support(2, ux=True)

# Roller (uy=0, uz=0)
m.support(3, uy=True, uz=True)
```

## Solution

```python
res = m.solve()                   # dense solver (default)
res = m.solve(sparse=True)        # sparse solver (large models)
res = m.solve(cases=["G", "Q"])    # specific load cases
```

See [Solution](en-07-solution.md) for details.
