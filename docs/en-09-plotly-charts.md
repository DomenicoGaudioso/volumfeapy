---
layout: default
title: "09 - Plotly Charts"
parent: English
nav_order: 9
---

# 09 - Plotly Charts

volumfeapy provides 6 interactive visualization functions based on Plotly.

## Installation

```bash
pip install volumfeapy[plot]
```

## Available functions

### plot_mesh(m, show_node_ids=True)

3D mesh visualization with node IDs and element edges:

```python
from volumfeapy.plotting import plot_mesh
fig = plot_mesh(m)
fig.show()
```

Draws element edges according to the element type:
- Hex8: 12 edges
- Tet4: 6 edges
- Wedge6: 9 edges
- Pyramid5: 8 edges

### plot_deformed(result, scale=1.0)

3D deformed mesh overlaid on the undeformed geometry:

```python
from volumfeapy.plotting import plot_deformed
plot_deformed(res, scale=100).show()
```

The undeformed model is drawn as a transparent reference wireframe; the
deformed mesh is colored by the real displacement norm `|u|`.

### plot_stress(result, component="von_mises", title=None, subdivisions=5, opacity=1.0, show_isolines=True)

3D stress contour map on the visible boundary faces of the mesh:

```python
from volumfeapy.plotting import plot_stress

# Von Mises stress
plot_stress(res, "von_mises").show()

# Smoother visual contour on each external element face
plot_stress(res, "von_mises", subdivisions=8).show()

# Opaque surface with contour bands separated by iso-lines
plot_stress(res, "von_mises", opacity=1.0, show_isolines=True).show()

# Normal stresses
plot_stress(res, "sxx").show()
plot_stress(res, "syy").show()
plot_stress(res, "szz").show()

# Shear stresses
plot_stress(res, "txy").show()
```

Available components: `sxx`, `syy`, `szz`, `txy`, `tyz`, `txz`, `von_mises`.

Stress values are recovered at element nodes where the element formulation
allows it, averaged at shared mesh nodes, and interpolated across the external
faces. This gives a continuous FEM-style contour on the actual mesh skin
instead of isolated center markers. The `subdivisions` parameter only refines
the display surface; the colorbar keeps the real stress values. Iso-lines are
drawn by intersecting the same sampled boundary triangles with equally spaced
stress levels, so they mark the separation between color bands.

### plot_supports(model)

Constrained nodes and active DOFs:

```python
from volumfeapy.plotting import plot_supports
plot_supports(m).show()
```

### plot_reactions(result, scale=None)

Support reaction vectors:

```python
from volumfeapy.plotting import plot_reactions
plot_reactions(res).show()
```

### plot_mode(modal_result, i=0, scale=1.0)

3D mode shape visualization:

```python
from volumfeapy.plotting import plot_mode

# First mode
plot_mode(mr, i=0, scale=100).show()

# Loop through modes
for i in range(min(6, len(mr.freq))):
    plot_mode(mr, i=i, scale=100).show()
```

## Saving figures

```python
fig = plot_stress(res, "von_mises")
fig.write_html("stress_von_mises.html", include_plotlyjs="cdn")
fig.write_image("stress_von_mises.png", width=1200, height=800)  # requires kaleido
```

## Complete example

```python
from volumfeapy import Model, Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

# Create model
m = Model()
# ... add nodes, elements, loads ...
res = m.solve()

# Visualize
plot_mesh(m).show()
plot_deformed(res, scale=100).show()
plot_stress(res, "von_mises").show()
plot_stress(res, "szz").show()
```

## Color maps

All stress plots use the `RdYlBu` colorscale:
- **Red**: high positive values
- **Blue**: low/negative values
- **Yellow/white**: near zero

The colorbar shows the value range with units.
