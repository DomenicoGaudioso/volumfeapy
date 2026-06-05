"""Caso studio CS11 volumfeapy: unico oggetto con tutti gli elementi 3D.

Il modello e' un unico corpo connesso, non una serie di provini separati:
un nucleo Hex8 con Pyramid5, Tet4, Tet10 e Wedge6 collegati tramite nodi
condivisi. Serve come test dimostrativo dell'assemblaggio misto e delle
visualizzazioni di vincoli e reazioni.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from volumfeapy import Material, Model, postprocess
from volumfeapy.plotting import (
    plot_deformed, plot_mesh, plot_reactions, plot_stress, plot_supports,
)

from common import header, print_check, save_figure


def _mid(m: Model, nid: int, a: int, b: int) -> int:
    ca = m.nodes[a].coords
    cb = m.nodes[b].coords
    p = 0.5 * (ca + cb)
    m.add_node(nid, p[0], p[1], p[2])
    return nid + 1


def build_mixed_model(mat: Material) -> tuple[Model, dict[str, int]]:
    m = Model()
    # Nucleo Hex8.
    coords = {
        1: (0, 0, 0), 2: (1, 0, 0), 3: (1, 1, 0), 4: (0, 1, 0),
        5: (0, 0, 1), 6: (1, 0, 1), 7: (1, 1, 1), 8: (0, 1, 1),
        9: (0.5, 0.5, 1.8),      # apice Pyramid5
        10: (1.65, 0.15, 0.35),   # apice Tet4
        11: (1.75, 0.85, 0.75),   # apice Tet10
        12: (0.0, 0.0, 1.75), 13: (1.0, 0.0, 1.75),
        14: (0.0, 1.0, 1.75),
    }
    for nid, xyz in coords.items():
        m.add_node(nid, *xyz)

    eid_by_name: dict[str, int] = {}
    m.add_hex8(1, [1, 2, 3, 4, 5, 6, 7, 8], mat)
    eid_by_name["Hex8"] = 1
    m.add_pyramid5(2, [5, 6, 7, 8, 9], mat)
    eid_by_name["Pyramid5"] = 2
    m.add_tet4(3, [2, 3, 6, 10], mat)
    eid_by_name["Tet4"] = 3

    nid = 16
    tet10_corners = [3, 6, 7, 11]
    tet10_edges = [(3, 6), (6, 7), (7, 3), (3, 11), (6, 11), (7, 11)]
    mids = []
    for a, b in tet10_edges:
        mids.append(nid)
        nid = _mid(m, nid, a, b)
    m.add_tet10(4, [*tet10_corners, *mids], mat)
    eid_by_name["Tet10"] = 4

    # Wedge6 collegato alla triangolazione della faccia superiore del nucleo.
    m.add_wedge6(5, [5, 6, 8, 12, 13, 14], mat)
    eid_by_name["Wedge6"] = 5

    return m, eid_by_name


def main() -> None:
    E, nu = 30e9, 0.22
    mat = Material(E=E, nu=nu)
    m, eid_by_name = build_mixed_model(mat)

    for nid in [1, 2, 3, 4, 12, 13]:
        m.fix(nid)
    for nid, fz in [(9, -12_000.0), (10, -6_000.0), (11, -6_000.0), (14, -4_000.0)]:
        m.add_nodal_load(nid, Fz=fz)

    res = m.solve()

    header("CS11 - Oggetto unico con tutti gli elementi volumetrici")
    print("  Elementi connessi: Hex8, Pyramid5, Tet4, Tet10, Wedge6")
    print(f"  E = {E:.2e} Pa, nu = {nu}")
    print(f"  Nodi = {len(m.nodes)}, elementi = {len(m.elements)}, vincoli = 6 nodi")
    print()
    print(f"  {'elemento':>10s}  {'id':>3s}  {'volume [m3]':>13s}  {'max |u| [m]':>12s}  {'von Mises [Pa]':>15s}")
    print("  " + "-" * 70)
    for name, eid in eid_by_name.items():
        elem = m.elements[eid]
        max_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in elem.node_ids)
        vm = postprocess.element_stresses(res, eid)["von_mises"]
        print(f"  {name:>10s}  {eid:3d}  {elem.volume():13.4e}  {max_u:12.4e}  {vm:15.4e}")

    save_figure(plot_mesh(m, show_node_ids=True), "cs11_mixed_mesh.png",
                width=1100, height=650,
                title="Oggetto unico misto: Hex8, Tet4, Tet10, Wedge6, Pyramid5")
    save_figure(plot_supports(m), "cs11_mixed_supports.png",
                width=1100, height=650,
                title="Vincoli oggetto misto")
    save_figure(plot_deformed(res, scale=350), "cs11_mixed_deformed.png",
                width=1100, height=650,
                title="Deformata oggetto misto (scala 350x)")
    save_figure(plot_stress(res, "von_mises", subdivisions=8),
                "cs11_mixed_vm.png", width=1100, height=650,
                title="von Mises su oggetto misto")
    save_figure(plot_stress(res, "szz", subdivisions=8),
                "cs11_mixed_szz.png", width=1100, height=650,
                title="sigma_zz su oggetto misto")
    save_figure(plot_reactions(res), "cs11_mixed_reactions.png",
                width=1100, height=650,
                title="Reazioni vincolari oggetto misto")

    max_global_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in m.nodes)
    print()
    print_check("max |u| globale", max_global_u, None)
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
