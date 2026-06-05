"""Example: automatic tetrahedral mesh with Gmsh."""

from volumfeapy import Material
from volumfeapy.meshing import mesh_box_tet


mat = Material(E=210e9, nu=0.3)

# Requires: pip install -e ".[mesh]" or pip install gmsh
m = mesh_box_tet(mat, lx=1.0, ly=0.4, lz=0.3, mesh_size=0.18, order=1)

z_min = min(node.z for node in m.nodes.values())
z_max = max(node.z for node in m.nodes.values())
bottom = [nid for nid, node in m.nodes.items() if abs(node.z - z_min) < 1e-9]
top = [nid for nid, node in m.nodes.items() if abs(node.z - z_max) < 1e-9]

for nid in bottom:
    m.fix(nid)
for nid in top:
    m.add_nodal_load(nid, Fz=-1000.0 / len(top))

res = m.solve(sparse=True)
print(f"nodes={len(m.nodes)}, elements={len(m.elements)}")
print(f"max uz={min(res.displacement(nid, 'uz') for nid in top):.6e} m")

try:
    from volumfeapy.plotting import plot_deformed, plot_mesh, plot_stress

    plot_mesh(m, show_node_ids=False).show()
    plot_deformed(res, scale=200).show()
    plot_stress(res, "von_mises").show()
except ImportError:
    pass
