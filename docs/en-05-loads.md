---
layout: default
title: "05 - Loads"
parent: English
nav_order: 5
---

# 05 - Loads

volumfeapy supports all major load types for static analysis of 3D solids.

## Nodal loads

Forces applied directly at nodes (global system):

```python
m.add_nodal_load(node, Fx=1000, Fy=-5000, Fz=0, case="G")
```

All parameters are optional except the node. Components are in global coordinates.

## Body forces

Uniform volume forces (e.g., inertia, electromagnetic):

```python
# Body force on one element
m.add_body_force(elem, bx=0, by=0, bz=-9810)    # e.g., fluid weight

# Apply to all elements
for eid in m.elements:
    m.add_body_force(eid, bz=-9810)
```

Body forces are converted to equivalent nodal forces via numerical integration:

```
f_i = ∫ N_i · b dV
```

## Gravity loads

Automatic gravity from material density:

```python
# Gravity in -Z direction (default)
m.add_gravity(g=9.81, direction="z")

# Gravity in -Y direction
m.add_gravity(g=9.81, direction="y")
```

The body force is computed as `b = -ρ · g` in the specified direction.
Requires `rho > 0` in the material definition.

## Thermal loads

Uniform temperature change:

```python
m.add_thermal_load(elem, dT=50.0)    # 50°C increase
```

The thermal strain is:

```
ε_th = α · ΔT · [1, 1, 1, 0, 0, 0]
```

This produces thermal stresses when the deformation is constrained.

## Face pressures

Pressure on element faces (not yet fully implemented):

```python
m.add_face_pressure(elem, face=0, p=-1e6)    # 1 MPa on face 0
```

## Settlements

Imposed displacements at nodes:

```python
m.add_settlement(node, "uz", -0.005)    # 5 mm downward
m.add_settlement(node, "ux", 0.001)     # 1 mm in X
```

The DOF can be: `ux`, `uy`, `uz`.

## Assignment to Load Cases

Each load can have a `case`:

```python
m.add_nodal_load(2, Fz=-10000, case="G")          # permanent
m.add_body_force(1, bz=-9810, case="G")            # permanent
m.add_nodal_load(5, Fx=30000, case="Q")             # variable
m.add_thermal_load(3, dT=30.0, case="T")             # thermal

m.load_cases()                    # → ['G', 'Q', 'T']
res = m.solve(cases=["G", "Q"])    # combination
res = m.solve(cases="G")           # single case
res = m.solve()                     # all loads
```

## Combinations with coefficients

```python
res = m.solve(cases={"G": 1.35, "Q": 1.5})        # ULS combination
res = m.solve(cases={"G": 1.0, "Q": 0.3})          # SLS combination
```

All results (displacements, reactions, stresses) respect the coefficients.

## Illustrated examples

**Cantilever beam under self-weight:**

```python
m = Model()
# ... create mesh ...
mat = Material(E=210e9, nu=0.3, rho=7850.0)
# ... add elements ...
m.add_gravity(g=9.81, direction="z")
for nid in fixed_nodes:
    m.fix(nid)
res = m.solve()
```

**Pressurized vessel:**

```python
# Internal pressure on faces
for eid, face in internal_faces:
    m.add_face_pressure(eid, face=face, p=1e6)
```

See [Usage Examples](en-14-usage-examples.md) for complete scripts.
