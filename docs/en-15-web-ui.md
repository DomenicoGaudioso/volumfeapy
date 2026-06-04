---
layout: default
title: "15 - Web UI"
parent: English
nav_order: 15
---

# 15 - Web UI (Streamlit)

volumfeapy includes a Streamlit web application for interactive 3D solid analysis.

## Installation

```bash
pip install volumfeapy streamlit plotly
```

## Launch

```bash
streamlit run app.py
```

The app opens in your default browser at `http://localhost:8501`.

## Interface layout

The web UI has three tabs:

### Modello (Model)

Define the 3D model through editable tables:

- **Nodi**: node ID, X, Y, Z coordinates
- **Materiali**: material name, E, nu, alpha, rho
- **Elementi**: element ID, type (hex8/tet4/tet10/wedge6/pyramid5), nodes (comma-separated), material
- **Vincoli**: node ID, Ux, Uy, Uz (boolean checkboxes)
- **Carichi nodali**: node ID, Fx, Fy, Fz, Case

Click **Applica modifiche** to rebuild the model.

### Analisi (Analysis)

Choose analysis type:

- **Statica**: solve the static problem
- **Modale**: compute natural frequencies and mode shapes

Options:
- Sparse solver (for large models)
- Number of modes (for modal analysis)

### Risultati (Results)

Visualize results:

- **Deformata**: 3D deformed mesh with scale factor
- **Stress maps**: von Mises, sxx, syy, szz
- **Nodal displacements**: table of [ux, uy, uz] per node
- **Stress table**: von Mises and stress components per element
- **Mode shapes**: 3D visualization of each mode
- **Frequency table**: natural frequencies and periods

## Example workflow

1. **Define nodes**: create 8 nodes for a unit cube
2. **Add material**: E=210e9, nu=0.3
3. **Add element**: type=hex8, nodes=1,2,3,4,5,6,7,8
4. **Apply supports**: fix bottom face (Ux=Uy=Uz=1 on nodes 1-4)
5. **Apply load**: Fz=-10000 on top nodes
6. **Run static analysis**
7. **View results**: deformed shape, von Mises stress

## Screenshots

The web UI provides:
- Interactive 3D visualization (rotate, zoom, pan)
- Editable tables with add/remove rows
- Real-time model preview
- Element type selector (dropdown)

## Limitations

- No mesh generation (manual node/element input)
- No Excel import (planned)
- No HDF5 export (planned)
- Limited to the features available in the Python API

## Programmatic access

The web UI uses the same Python API as the library:

```python
from volumfeapy import Model, Material

# The web UI builds this model from the tables
m = Model()
# ... add nodes, elements, loads ...
res = m.solve()
```
