---
layout: default
title: "06 - Supports & Constraints"
parent: English
nav_order: 6
---

# 06 - Supports & Constraints

## Support types

### Fixed

All 3 DOFs restrained: `ux = 0`, `uy = 0`, `uz = 0`.

```python
m.fix(node)
```

Typical use: built-in supports, clamped boundaries.

### Custom support

Selective DOF restraint:

```python
m.support(node, ux=True, uy=True, uz=False)
```

## Common boundary conditions

| Condition | Code | Physical meaning |
|-----------|------|------------------|
| Fixed | `m.fix(n)` | ux=0, uy=0, uz=0 |
| Symmetry (x=const) | `m.support(n, ux=True)` | ux=0 |
| Symmetry (y=const) | `m.support(n, uy=True)` | uy=0 |
| Symmetry (z=const) | `m.support(n, uz=True)` | uz=0 |
| Roller (XY plane) | `m.support(n, uz=True)` | uz=0, ux/uy free |
| Free | (nothing) | No restraints |

## Symmetry conditions

For a solid with symmetry about the X-Y plane (at z=0):

```python
# On the symmetry plane: uz = 0
for nid in symmetry_nodes:
    m.support(nid, uz=True)
```

For symmetry about the X-Z plane (at y=0):

```python
for nid in symmetry_nodes:
    m.support(nid, uy=True)
```

For symmetry about the Y-Z plane (at x=0):

```python
for nid in symmetry_nodes:
    m.support(nid, ux=True)
```

## Settlements

Imposed displacements (non-zero prescribed values):

```python
m.add_settlement(node, "uz", -0.005)    # 5 mm downward
m.add_settlement(node, "ux", 0.001)     # 1 mm in X direction
```

Settlements are applied during the solution phase and affect the load vector.

## Stability requirements

The model must have sufficient constraints to prevent rigid body motion:

- **Minimum**: at least 3 non-collinear nodes with all 3 DOFs restrained, or equivalent
- **Recommended**: proper boundary conditions on all constrained surfaces

If the stiffness matrix is singular, `solve()` raises a `ValueError`.
