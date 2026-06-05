---
layout: default
title: "14 - Usage Examples"
parent: English
nav_order: 14
---

# 14 - Usage Examples

The `usage_examples/` directory contains self-contained scripts covering key features.

## Available examples

| # | File | Description |
|---|------|-------------|
| 01 | `01_convergence_hex8.py` | Convergence study: Hex8 uniaxial tension |
| 02 | `02_cantilever_convergence.py` | Cantilever beam with Tet4 mesh refinement |

## Literature Case Studies

A complete set of **9 classical FEM benchmark cases** is available in
the `casestudies/` directory, with full documentation and images on the
website. Each case study is compared with an analytical reference
solution from the literature (Euler-Bernoulli beam, Lamé, Kirsch,
etc.).

| # | Case | Reference |
|---|------|-----------|
| CS01 | Cube in uniaxial tension (Hex8) | Cook et al. §2 |
| CS02 | 3D cantilever beam (Tet4) | Euler-Bernoulli |
| CS03 | Cube under hydrostatic pressure | Lamé / bulk modulus |
| CS04 | Plate with circular hole (Kirsch) | K_t = 3 |
| CS05 | Cube under self-weight (gravity) | sigma_zz = -rho g z |
| CS06 | Cube under thermal load | Free expansion |
| CS07 | Patch test (linear field) | Exact by construction |
| CS08 | Element comparison (Hex8/Tet4/Wedge6) | Convergence study |
| CS09 | Modal analysis of Hex8 cube | Natural frequencies |

→ [Browse all case studies]({{ site.baseurl }}/casestudies/)

## Running examples

```bash
cd volumfeapy
python usage_examples/01_convergence_hex8.py
```

## Example 01: Hex8 convergence

Uniaxial tension on a unit cube with progressive mesh refinement:

```python
from volumfeapy import Model, Material

L = 1.0
F = 1e6
E = 210e9
nu = 0.3

for n_el in [1, 2, 4, 8]:
    m = Model()
    # ... create n_el × n_el × n_el hex mesh ...
    # ... fix bottom face, apply tension on top ...
    res = m.solve()
    u_max = max(res.displacement(nid, "uz") for nid in top_nodes)
    # ... compare with analytical solution ...
```

Expected output:

```
Mesh  1x1x1  |  uz = 4.76e-06  |  err = 0.00%
Mesh  2x2x2  |  uz = 4.76e-06  |  err = 0.00%
Mesh  4x4x4  |  uz = 4.76e-06  |  err = 0.00%
```

Hex8 elements reproduce uniform stress exactly regardless of mesh density.

## Example 02: Cantilever convergence

Cantilever beam (L=2m, b=0.1m, h=0.2m) with tip load P=1kN, meshed with Tet4:

```python
from volumfeapy import Model, Material

L = 2.0
P = 1000.0
E = 210e9
I = 0.1 * 0.2**3 / 12
u_exact = P * L**3 / (3 * E * I)

for nx in [4, 8, 12, 16]:
    # ... create tet mesh ...
    res = m.solve()
    u_tip = abs(res.displacement(tip_node, "uz"))
    # ... compare with Euler-Bernoulli solution ...
```

Tet4 elements converge slowly due to the constant strain limitation.

## Basic examples

The `examples/` directory contains simpler scripts:

| File | Description |
|------|-------------|
| `ex01_uniaxial_hex8.py` | Unit cube in uniaxial tension (Hex8) |
| `ex02_cantilever_tet4.py` | Cantilever beam with Tet4 mesh |

```bash
python examples/ex01_uniaxial_hex8.py
```
