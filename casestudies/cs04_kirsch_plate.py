"""Caso studio CS04 volumfeapy: Lastra piana con foro centrale - Kirsch.

Caso classico FEM (Kirsch, 1898). Lastra piana indefinita (o grande
rispetto al foro) con un foro circolare centrale di raggio a, soggetta
a trazione lontana sigma_0. Lo stato tensionale in coordinate polari
e' la soluzione di Kirsch.

Al bordo del foro (r = a, theta = 0, punto piu' sollecitato):
    sigma_tt_max = 3 sigma_0

(fattore di concentrazione K_t = 3 per lastra infinita).

In questo caso studio modelliamo 1/4 del dominio (per doppia simmetria
rispetto ai piani y=0 e z=0). Il dominio computazionale e':

    [0, W] x [0, t] x [0, H]  (1/4 della lastra)

con il foro modellato come un cilindro di raggio a centrato in
(0, t/2, H/2). Il dominio viene "forato" rimuovendo gli elementi il
cui baricentro cade dentro il cilindro. La trazione sigma_0 viene
applicata sulla faccia x = W.

Vincoli:
  * y = 0: piano di simmetria, u_y = 0
  * z = 0: piano di simmetria, u_z = 0
  * x = 0 (a parte il foro): libero
  * un nodo per evitare moti rigidi: u_x = 0 in un nodo dell'asse x
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from volumfeapy import Model, Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

from common import save_figure, print_check, header


def main() -> None:
    a = 1.0
    W = 6.0
    t = 1.0
    H = 1.0
    sigma_0 = 1.0e6
    E, nu = 210e9, 0.3
    mat = Material(E=E, nu=nu)

    header("CS04 - Lastra piana con foro (Kirsch) - modello 3D")
    print(f"  a = {a} m (raggio foro), W = {W} m, t = {t} m, H = {H} m")
    print(f"  sigma_0 = {sigma_0:.2e} Pa")
    print(f"  K_t atteso (Kirsch, lastra infinita) = 3.0")
    print()

    nx, ny, nz = 16, 4, 4
    cell = W / nx

    m = Model()
    nid = 1
    nodes = {}
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                m.add_node(nid, i * cell, j * t / ny, k * H / nz)
                nodes[(i, j, k)] = nid
                nid += 1

    eid = 1
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n1 = nodes[(i, j, k)]
                n2 = nodes[(i + 1, j, k)]
                n3 = nodes[(i + 1, j + 1, k)]
                n4 = nodes[(i, j + 1, k)]
                n5 = nodes[(i, j, k + 1)]
                n6 = nodes[(i + 1, j, k + 1)]
                n7 = nodes[(i + 1, j + 1, k + 1)]
                n8 = nodes[(i, j + 1, k + 1)]
                m.add_hex8(eid, [n1, n2, n3, n4, n5, n6, n7, n8], mat)
                eid += 1

    elements_to_remove = []
    for eid, el in m.elements.items():
        coords = el._coords()
        cx = coords[:, 0].mean()
        cy = coords[:, 1].mean()
        cz = coords[:, 2].mean()
        if (cx - 0) ** 2 + (cy - t / 2) ** 2 + (cz - H / 2) ** 2 < a ** 2:
            elements_to_remove.append(eid)
    for eid in elements_to_remove:
        del m.elements[eid]

    print(f"  Elementi totali iniziali: {nx * ny * nz}")
    print(f"  Elementi rimossi (foro): {len(elements_to_remove)}")
    print(f"  Elementi finali: {len(m.elements)}")
    print()

    for nid, node in m.nodes.items():
        if abs(node.y) < 1e-12:
            m.fix(nid, ["uy"])
        if abs(node.z) < 1e-12:
            m.fix(nid, ["uz"])
    m.fix(nodes[(0, ny // 2, nz // 2)], ["ux"])

    hole_node_ids = set()
    for eid in elements_to_remove:
        for nid in m.elements.get(eid, type('X', (), {'node_ids': []})()).node_ids if eid in m.elements else []:
            hole_node_ids.add(nid)
    el_with_node = {}
    for eid, el in m.elements.items():
        for nid in el.node_ids:
            el_with_node.setdefault(nid, []).append(eid)
    for nid in list(m.nodes.keys()):
        coords = m.nodes[nid].coords if hasattr(m.nodes[nid], 'coords') else (m.nodes[nid].x, m.nodes[nid].y, m.nodes[nid].z)
        x, y, z = coords
        if x ** 2 + (y - t / 2) ** 2 + (z - H / 2) ** 2 < (a + 0.5 * cell) ** 2:
            if nid not in el_with_node or len(el_with_node[nid]) == 0:
                m.fix(nid, ["ux", "uy", "uz"])

    cell_y = t / ny
    cell_z = H / nz
    for nid, node in m.nodes.items():
        if abs(node.x - W) < 1e-9:
            m.add_nodal_load(nid, Fx=sigma_0 * cell_y * cell_z)

    res = m.solve()

    from volumfeapy import postprocess
    sig_at_hole = []
    for eid, el in m.elements.items():
        coords = el._coords()
        cx = coords[:, 0].mean()
        cy = coords[:, 1].mean()
        cz = coords[:, 2].mean()
        if cx < a + 1.5 * cell and abs(cy - t / 2) < 0.2 and abs(cz - H / 2) < 0.2:
            s = postprocess.element_stresses(res, eid)
            sig_at_hole.append((cx, s["syy"]))
    sig_at_hole.sort(key=lambda p: p[0])

    if sig_at_hole:
        max_syy = max(s for _, s in sig_at_hole)
        print(f"  sigma_yy vicino al bordo del foro (lato x ~ a):")
        for x, syy in sig_at_hole[:5]:
            print(f"    x = {x:.3f} m, sigma_yy = {syy:.3e} Pa")
        print()
        print_check("K_t FEM (sigma_yy max / sigma_0)", max_syy / sigma_0, 3.0, tol=0.50)
    print()

    save_figure(plot_mesh(m, show_node_ids=False), "cs04_mesh.png",
                title=f"Mesh lastra con foro (1/4 dominio), elementi rimossi: {len(elements_to_remove)}")
    save_figure(plot_deformed(res, scale=200), "cs04_deformed.png",
                title="Deformata lastra con foro (scala 200×)")
    save_figure(plot_stress(res, "syy"), "cs04_syy.png",
                title="sigma_yy [Pa] - concentrazione al bordo del foro (K_t ~ 3)")
    save_figure(plot_stress(res, "von_mises"), "cs04_vm.png",
                title="von Mises [Pa]")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
