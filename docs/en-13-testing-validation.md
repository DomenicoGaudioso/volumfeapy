---
layout: default
title: "13 - Testing & Validation"
parent: English
nav_order: 13
---

# 13 - Testing & Validation

## Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests -v
```

## Test coverage

The test suite includes:

| Test | Description |
|------|-------------|
| `test_hex8_stiffness_symmetry` | Hex8 K matrix symmetry |
| `test_hex8_stiffness_positive_diagonal` | Hex8 K diagonal non-negative |
| `test_hex8_volume` | Hex8 unit volume computation |
| `test_hex8_uniaxial_tension` | Hex8 uniaxial tension vs analytical |
| `test_tet4_stiffness_symmetry` | Tet4 K matrix symmetry |
| `test_tet4_volume` | Tet4 volume computation |
| `test_tet4_stresses_constant` | Tet4 constant stress field |
| `test_settlement` | Imposed displacement |
| `test_gravity_load` | Gravity load application |
| `test_modal_analysis` | Modal analysis (positive frequencies) |
| `test_von_mises` | Von Mises stress computation |
| `test_principal_stresses` | Principal stress computation |
| `test_wedge6_volume` | Wedge6 volume computation |
| `test_pyramid5_volume` | Pyramid5 volume computation |

## Analytical validation

### Uniaxial tension (Hex8)

For a unit cube under uniaxial tension F:

```
σ_zz = F / A
u_z = F · L / (E · A)
```

The Hex8 element reproduces this exactly for a single-element mesh.

### Cantilever beam (Tet4)

For a cantilever beam (L × b × h) with tip load P:

```
u_tip = P · L³ / (3 · E · I)
```

where `I = b·h³/12`. Tet4 elements require a fine mesh for accuracy
(constant strain limitation).

## Validation scripts

```bash
python validation/validate_hex8_tension.py
```

This script runs a uniaxial tension test on a single Hex8 element and prints
displacements and stresses compared to the analytical solution.

## Known limitations

1. **Tet4 element**: constant strain/stress within each element. Requires very
   fine mesh for accurate results. Use Tet10 for better accuracy.

2. **Hex8 element**: trilinear interpolation. May exhibit volumetric locking
   for nearly incompressible materials (ν → 0.5).

3. **Pyramid5 element**: uses numerical differentiation for shape function
   derivatives. Accuracy may be reduced near the apex.

4. **Wedge6 element**: linear interpolation. Similar limitations to Tet4.

5. **Mesh distortion**: highly distorted elements reduce accuracy. Maintain
   aspect ratio < 5 and Jacobian > 0 everywhere.

## Comparison with literature

The element formulations follow standard FEM textbooks:

- Zienkiewicz, O.C., Taylor, R.L. (2000). *The Finite Element Method*, Vol. 1.
  Butterworth-Heinemann.
- Hughes, T.J.R. (1987). *The Finite Element Method*. Prentice-Hall.
- Bathe, K.J. (1996). *Finite Element Procedures*. Prentice-Hall.
