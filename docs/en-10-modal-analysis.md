---
layout: default
title: "10 - Modal Analysis"
parent: English
nav_order: 10
---

# 10 - Modal Analysis

## Natural frequencies and mode shapes

```python
mr = m.modal(n_modes=6)

for i in range(len(mr.freq)):
    print(f"Mode {i+1}: f = {mr.freq[i]:.3f} Hz, T = {mr.period[i]:.3f} s")
```

`modal()` solves the eigenvalue problem `K φ = ω² M φ` on free DOFs.

## Mass matrix

The mass matrix is **lumped** (diagonal) and computed from element density:

```python
M = m.assemble_mass()    # diagonal mass vector (ndof,)
```

Mass per node:

```
m_node = ρ · V_element / n_nodes
```

where `V_element` is the element volume and `n_nodes` is the number of nodes.

## Result object

```python
mr = m.modal(n_modes=10)

mr.omega          # angular frequencies [rad/s]
mr.freq           # natural frequencies [Hz]
mr.period         # periods [s]
mr.phi            # mode shapes (ndof × n_modes)

# Single mode
mr.mode(i)                    # mode shape vector (ndof,)
mr.mode_shape(i, node)        # [ux, uy, uz] at node
```

## Visualization

```python
from volumfeapy.plotting import plot_mode

# First mode
plot_mode(mr, i=0, scale=100).show()

# Loop through modes
for i in range(min(6, len(mr.freq))):
    plot_mode(mr, i=i, scale=100).show()
```

## Analytical comparison

For a cantilever beam (L × b × h), the first bending frequency is:

```
f_1 = (1.875² / (2π·L²)) · √(E·I / (ρ·A))
```

where `I = b·h³/12` and `A = b·h`.

### Example: steel cantilever

```python
import numpy as np

L = 2.0
b = 0.1
h = 0.2
E = 210e9
rho = 7850.0

I = b * h**3 / 12
A = b * h

f_1 = (1.875**2 / (2 * np.pi * L**2)) * np.sqrt(E * I / (rho * A))
print(f"f_1 analytical = {f_1:.3f} Hz")

# Compare with FEM
mr = m.modal(n_modes=1)
print(f"f_1 FEM        = {mr.freq[0]:.3f} Hz")
```

## Requirements

- Material must have `rho > 0` (density)
- Sufficient constraints to prevent rigid body modes
- Free DOFs without mass are eliminated by static condensation

If `rho = 0`, `modal()` raises:
```
ValueError: Massa nulla: impostare rho nel materiale.
```
