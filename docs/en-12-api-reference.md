---
layout: default
title: "12 - API Reference"
parent: English
nav_order: 12
---

# 12 - API Reference

Complete reference of all public functions in **volumfeapy**.

Typical import:

```python
from volumfeapy import Model, Material
from volumfeapy import postprocess
from volumfeapy.plotting import (
    plot_mesh, plot_deformed, plot_stress,
    plot_supports, plot_reactions, plot_mode,
)
from volumfeapy.meshing import mesh_box_tet
```

---

## Materials

### `Material(E, nu=0.3, alpha=0.0, G=None, rho=0.0, name="")`
Isotropic elastic material. `G` (shear modulus) is derived as
`E/(2(1+nu))` if not provided. `alpha` = thermal expansion; `rho` = density.

Methods:
- `D_matrix()` → 6×6 constitutive matrix (Voigt notation)

---

## Model

### `Model()`
FEM model container. Attributes: `nodes`, `elements`, `nodal_loads`,
`body_forces`, `gravity_loads`, `thermal_loads`, `face_pressures`, `settlements`.

### `add_node(id, x, y, z) -> Node`
Add a node (3 DOFs: `ux, uy, uz`).

### Element methods
- **`add_hex8(id, node_ids, material) -> Hex8`** — 8-node hexahedron
- **`add_tet4(id, node_ids, material) -> Tet4`** — 4-node tetrahedron
- **`add_tet10(id, node_ids, material) -> Tet10`** — 10-node tetrahedron
- **`add_wedge6(id, node_ids, material) -> Wedge6`** — 6-node wedge
- **`add_pyramid5(id, node_ids, material) -> Pyramid5`** — 5-node pyramid

### Constraints
- **`fix(node, dofs=None)`** — restrain listed DOFs; `None` = all 3 (fixed).
- **`support(node, ux=False, uy=False, uz=False)`** — selective constraint.

### `add_settlement(node, dof, value) -> Settlement`
Settlement (imposed displacement): `dof` ∈ `{ux, uy, uz}`.

---

## Loads

All `add_*` methods accept `case="..."` (load case, default `"default"`).

### `add_nodal_load(node, case="default", Fx=0, Fy=0, Fz=0) -> NodalLoad`
Concentrated force at a node (global system).

### `add_body_force(elem, bx=0, by=0, bz=0, case="default") -> BodyForce`
Uniform body force [N/m³] on an element.

### `add_gravity(g=9.81, direction="z", case="default") -> GravityLoad`
Automatic gravity from material density. `direction` ∈ `{x, y, z}`.

### `add_thermal_load(elem, dT, case="default") -> ThermalLoad`
Uniform temperature change [°C]. Produces thermal strain `ε = α·ΔT`.

### `add_face_pressure(elem, face, p, case="default") -> FacePressure`
Pressure on an element face [Pa].

---

## Solution

### `load_cases() -> list[str]`
Sorted list of load cases present in the loads.

### `solve(sparse=False, cases=None) -> Result`
Solve the system.
- `sparse`: `True` uses scipy sparse solver (large models).
- `cases`: load combination —
  - `None` = all loads (coeff 1);
  - string = a single load case;
  - list/set = combination (coeff 1 each);
  - **dict `{case: coefficient}`** = combination with multiplicative coefficients.

### `modal(n_modes=10) -> ModalResult`
Modal analysis: solves `K φ = ω² M φ`. Requires `rho > 0` in materials.

---

## Results

### `Result`
Attributes: `U` (global displacements), `R` (global reactions),
`element_forces` (nodal forces per element).

- **`displacements(node) -> ndarray(3)`** — `[ux, uy, uz]` of the node.
- **`displacement(node, dof) -> float`** — single component.
- **`reactions(node) -> ndarray(3)`** — `[Fx, Fy, Fz]` of the node.

### `ModalResult`
Attributes: `omega` [rad/s], `freq` [Hz], `period` [s], `phi` (ndof × n_modes).

- **`mode(i) -> ndarray(ndof)`** — i-th mode shape vector.
- **`mode_shape(i, node) -> ndarray(3)`** — `[ux, uy, uz]` at node.

---

## Post-processing (`volumfeapy.postprocess`)

### `element_stresses(result, elem_id) -> dict`
Stresses at element center. Returns `{sxx, syy, szz, txy, tyz, txz, von_mises}`.

### `von_mises(sigma) -> float`
Von Mises equivalent stress from 6-component stress vector.

### `principal_stresses(sigma) -> tuple[ndarray, ndarray]`
Principal stresses and directions: `(values, vectors)`.

### `element_displacements(result, elem_id) -> ndarray`
Nodal displacement vector for the element.

### `all_stresses(result) -> dict`
Stresses at center of all elements: `{elem_id: {sxx, ..., von_mises}}`.

### `max_von_mises(result) -> tuple[int, float]`
Element ID and maximum von Mises stress: `(elem_id, vm_max)`.

---

## Visualization (`volumfeapy.plotting`)

Requires the `plot` extra (`plotly`, `kaleido`). Each function returns a
`plotly.graph_objects.Figure`.

- **`plot_mesh(model, show_node_ids=True)`** — 3D mesh with edges and node IDs.
- **`plot_deformed(result, scale=1.0)`** — 3D deformed mesh.
- **`plot_stress(result, component="von_mises", subdivisions=5, opacity=1.0, show_isolines=True)`** — 3D stress contour with subdivided external faces and iso-lines.
- **`plot_supports(model)`** — constrained nodes and active DOFs.
- **`plot_reactions(result, scale=None)`** — support reaction vectors.
- **`plot_mode(modal_result, i=0, scale=1.0)`** — i-th mode shape.

---

## Meshing (`volumfeapy.meshing`)

Requires the `mesh` extra (`gmsh`). These helpers generate or import a mesh
and return a normal `Model`.

- **`mesh_box_tet(material, lx, ly, lz, mesh_size, order=1)`** — Gmsh tetrahedral box mesh (`order=1` Tet4, `order=2` Tet10).
- **`from_gmsh(material, dim=3)`** — convert the active Gmsh model mesh to supported volumetric elements.
