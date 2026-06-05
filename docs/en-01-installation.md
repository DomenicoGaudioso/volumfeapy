---
layout: default
title: "01 - Installation"
parent: English
nav_order: 1
---

# 01 - Installation

## Requirements

- Python ≥ 3.9
- numpy ≥ 1.24
- scipy ≥ 1.10

## Installation

### From source (development)

```bash
git clone https://github.com/DomenicoGaudioso/volumfeapy.git
cd volumfeapy
pip install -e ".[all]"
```

### Base dependencies only (numpy + scipy)

```bash
pip install -e .
```

## Extras

| Extra | Packages | Description |
|-------|----------|-------------|
| `plot` | plotly, kaleido | Interactive Plotly charts |
| `mesh` | gmsh | Automatic mesh generation |
| `all` | plotly, kaleido, gmsh | Everything |
| `dev` | plotly, kaleido, gmsh, pytest | Development + tests |

Example:

```bash
pip install -e ".[all]"       # everything
pip install -e ".[plot]"      # charts only
pip install -e ".[mesh]"      # Gmsh meshing only
```

## Verify installation

```python
import volumfeapy
print(volumfeapy.__version__)  # 0.1.0
```

## Running tests

```bash
pip install -e ".[dev]"
python -m pytest tests -q
```

## Troubleshooting

### ImportError: plotly not found

The `plot` extra is not installed. Run:

```bash
pip install -e ".[all]"
```

### ImportError: gmsh not found

The `mesh` extra is not installed. Run:

```bash
pip install -e ".[mesh]"
```

### ValueError: Jacobian singular

Check that element nodes are not coplanar or degenerate. Hexahedral elements
require 8 non-coplanar nodes forming a valid hexahedron.
