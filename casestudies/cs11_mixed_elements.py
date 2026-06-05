"""Caso studio CS11 volumfeapy: modello con tutti gli elementi 3D.

Il modello contiene cinque provini separati, uno per ciascun tipo di
elemento volumetrico implementato: Hex8, Tet4, Tet10, Wedge6 e Pyramid5.
Ogni provino e' vincolato alla base e caricato verticalmente per produrre
una deformata e una mappa tensionale confrontabili nello stesso plot.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from volumfeapy import Material, Model
from volumfeapy import postprocess
from volumfeapy.plotting import plot_deformed, plot_mesh, plot_stress

from common import header, print_check, save_figure


def _add_node(m: Model, nid: int, x: float, y: float, z: float,
              dx: float) -> int:
    m.add_node(nid, x + dx, y, z)
    return nid + 1


def build_mixed_model(mat: Material) -> tuple[Model, dict[str, list[int]]]:
    m = Model()
    groups: dict[str, list[int]] = {}
    nid = 1
    eid = 1

    # Hex8: un cubo unitario.
    dx = 0.0
    hex_nodes = list(range(nid, nid + 8))
    for x, y, z in [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1),
    ]:
        nid = _add_node(m, nid, x, y, z, dx)
    m.add_hex8(eid, hex_nodes, mat)
    groups["Hex8"] = hex_nodes
    eid += 1

    # Tet4: tetraedro lineare.
    dx = 1.8
    tet4_nodes = list(range(nid, nid + 4))
    for x, y, z in [(0, 0, 0), (1, 0, 0), (0.15, 1, 0), (0.35, 0.35, 1.0)]:
        nid = _add_node(m, nid, x, y, z, dx)
    m.add_tet4(eid, tet4_nodes, mat)
    groups["Tet4"] = tet4_nodes
    eid += 1

    # Tet10: tetraedro quadratico con nodi intermedi sugli spigoli.
    dx = 3.6
    corners = [
        (0, 0, 0), (1, 0, 0), (0.15, 1, 0), (0.35, 0.35, 1.0),
    ]
    mids = [
        ((0, 1),), ((1, 2),), ((2, 0),),
        ((0, 3),), ((1, 3),), ((2, 3),),
    ]
    tet10_coords = corners[:]
    for ((a, b),) in mids:
        tet10_coords.append(tuple((corners[a][i] + corners[b][i]) / 2 for i in range(3)))
    tet10_nodes = list(range(nid, nid + 10))
    for x, y, z in tet10_coords:
        nid = _add_node(m, nid, x, y, z, dx)
    m.add_tet10(eid, tet10_nodes, mat)
    groups["Tet10"] = tet10_nodes
    eid += 1

    # Wedge6: prisma triangolare.
    dx = 5.4
    wedge_nodes = list(range(nid, nid + 6))
    for x, y, z in [
        (0, 0, 0), (1, 0, 0), (0.1, 0.9, 0),
        (0, 0, 1), (1, 0, 1), (0.1, 0.9, 1),
    ]:
        nid = _add_node(m, nid, x, y, z, dx)
    m.add_wedge6(eid, wedge_nodes, mat)
    groups["Wedge6"] = wedge_nodes
    eid += 1

    # Pyramid5: base quadrata e apice.
    dx = 7.2
    pyramid_nodes = list(range(nid, nid + 5))
    for x, y, z in [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
        (0.5, 0.5, 1.0),
    ]:
        nid = _add_node(m, nid, x, y, z, dx)
    m.add_pyramid5(eid, pyramid_nodes, mat)
    groups["Pyramid5"] = pyramid_nodes

    return m, groups


def main() -> None:
    E, nu = 30e9, 0.22
    P = -10_000.0
    mat = Material(E=E, nu=nu)
    m, groups = build_mixed_model(mat)

    base_nodes = []
    load_nodes = []
    for nodes in groups.values():
        z_min = min(m.nodes[nid].z for nid in nodes)
        z_max = max(m.nodes[nid].z for nid in nodes)
        base = [nid for nid in nodes if abs(m.nodes[nid].z - z_min) < 1e-12]
        top = [nid for nid in nodes if abs(m.nodes[nid].z - z_max) < 1e-12]
        base_nodes.extend(base)
        load_nodes.extend(top)
        for nid in base:
            m.fix(nid)
        for nid in top:
            m.add_nodal_load(nid, Fz=P / len(top))

    res = m.solve()

    header("CS11 - Tutti gli elementi volumetrici in un modello")
    print(f"  Elementi: {', '.join(groups.keys())}")
    print(f"  E = {E:.2e} Pa, nu = {nu}, carico verticale = {P:.2e} N per provino")
    print(f"  Nodi vincolati: {len(base_nodes)}, nodi caricati: {len(load_nodes)}")
    print()
    print(f"  {'elemento':>10s}  {'nodi':>4s}  {'volume [m3]':>13s}  {'max |u| [m]':>12s}  {'von Mises [Pa]':>15s}")
    print("  " + "-" * 64)
    for name, node_ids in groups.items():
        elem = next(el for el in m.elements.values() if list(el.node_ids) == node_ids)
        max_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in node_ids)
        vm = postprocess.element_stresses(res, elem.id)["von_mises"]
        print(f"  {name:>10s}  {len(node_ids):4d}  {elem.volume():13.4e}  {max_u:12.4e}  {vm:15.4e}")

    save_figure(plot_mesh(m, show_node_ids=False), "cs11_mixed_mesh.png",
                width=1100, height=650,
                title="Mesh mista: Hex8, Tet4, Tet10, Wedge6, Pyramid5")
    save_figure(plot_deformed(res, scale=350), "cs11_mixed_deformed.png",
                width=1100, height=650,
                title="Deformata mesh mista (scala 350x)")
    save_figure(plot_stress(res, "von_mises", subdivisions=8),
                "cs11_mixed_vm.png", width=1100, height=650,
                title="Tensioni von Mises su tutti gli elementi")
    save_figure(plot_stress(res, "szz", subdivisions=8),
                "cs11_mixed_szz.png", width=1100, height=650,
                title="Tensione sigma_zz su tutti gli elementi")

    print()
    max_global_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in m.nodes)
    print_check("max |u| globale", max_global_u, None)
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
