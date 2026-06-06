"""Caso studio CS11 volumfeapy: spalla/plinto con tutti gli elementi 3D.

Il modello e' un unico oggetto connesso, non una serie di provini separati:
un corpo principale Hex8, una rampa Wedge6, una copertura Pyramid5 e due
contrafforti laterali Tet4/Tet10 condividono nodi e facce del plinto.
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

try:
    from .common import header, print_check, save_figure
except ImportError:  # pragma: no cover - standalone execution
    from common import header, print_check, save_figure


def _mid(m: Model, nid: int, a: int, b: int) -> int:
    ca = m.nodes[a].coords
    cb = m.nodes[b].coords
    p = 0.5 * (ca + cb)
    m.add_node(nid, p[0], p[1], p[2])
    return nid + 1


def build_mixed_model(mat: Material) -> tuple[Model, dict[str, int]]:
    """Costruisce un piccolo plinto/spalla in c.a. con mesh mista."""
    m = Model()
    coords = {
        # Blocco principale 4.0 x 2.0 x 0.8 m.
        1: (0.0, 0.0, 0.0), 2: (4.0, 0.0, 0.0),
        3: (4.0, 2.0, 0.0), 4: (0.0, 2.0, 0.0),
        5: (0.0, 0.0, 0.8), 6: (4.0, 0.0, 0.8),
        7: (4.0, 2.0, 0.8), 8: (0.0, 2.0, 0.8),
        # Rampa/prisma triangolare lato destro.
        9: (5.35, 0.0, 0.0), 10: (5.35, 2.0, 0.0),
        11: (5.35, 2.0, 0.35),
        # Copertura piramidale.
        12: (2.0, 1.0, 1.75),
        # Contrafforti laterali.
        13: (2.0, -0.95, 0.35),
        14: (2.0, 2.95, 0.45),
    }
    for nid, xyz in coords.items():
        m.add_node(nid, *xyz)

    eid_by_name: dict[str, int] = {}
    m.add_hex8(1, [1, 2, 3, 4, 5, 6, 7, 8], mat)
    eid_by_name["Hex8"] = 1

    m.add_wedge6(2, [2, 3, 10, 6, 7, 11], mat)
    eid_by_name["Wedge6"] = 2

    m.add_pyramid5(3, [5, 6, 7, 8, 12], mat)
    eid_by_name["Pyramid5"] = 3

    m.add_tet4(4, [1, 2, 6, 13], mat)
    eid_by_name["Tet4"] = 4

    nid = 15
    tet10_corners = [4, 8, 7, 14]
    tet10_edges = [(4, 8), (8, 7), (7, 4), (4, 14), (8, 14), (7, 14)]
    mids = []
    for a, b in tet10_edges:
        mids.append(nid)
        nid = _mid(m, nid, a, b)
    m.add_tet10(5, [*tet10_corners, *mids], mat)
    eid_by_name["Tet10"] = 5

    return m, eid_by_name


def main() -> None:
    E, nu = 30e9, 0.22
    mat = Material(E=E, nu=nu)
    m, eid_by_name = build_mixed_model(mat)

    for nid, node in m.nodes.items():
        if abs(node.z) < 1e-12:
            m.fix(nid)

    loads = {
        12: -18_000.0,  # copertura/piastra d'appoggio
        11: -6_000.0,   # estremita' rampa
        13: -4_000.0,   # contrafforte sinistro
        14: -4_000.0,   # contrafforte destro
    }
    for nid, fz in loads.items():
        m.add_nodal_load(nid, Fz=fz)

    res = m.solve()

    header("CS11 - Spalla/plinto con mesh mista 3D")
    print("  Oggetto unico: blocco, rampa, copertura piramidale e contrafforti")
    print("  Elementi connessi: Hex8, Wedge6, Pyramid5, Tet4, Tet10")
    print(f"  E = {E:.2e} Pa, nu = {nu}")
    print(f"  Nodi = {len(m.nodes)}, elementi = {len(m.elements)}, vincoli alla base")
    print()
    print(f"  {'elemento':>10s}  {'id':>3s}  {'volume [m3]':>13s}  {'max |u| [m]':>12s}  {'von Mises [Pa]':>15s}")
    print("  " + "-" * 70)
    for name, eid in eid_by_name.items():
        elem = m.elements[eid]
        max_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in elem.node_ids)
        vm = postprocess.element_stresses(res, eid)["von_mises"]
        print(f"  {name:>10s}  {eid:3d}  {elem.volume():13.4e}  {max_u:12.4e}  {vm:15.4e}")

    save_figure(plot_mesh(m, show_node_ids=False), "cs11_mixed_mesh.png",
                width=1100, height=720,
                title="Spalla/plinto con Hex8, Wedge6, Pyramid5, Tet4, Tet10")
    save_figure(plot_supports(m), "cs11_mixed_supports.png",
                width=1100, height=720,
                title="Vincoli spalla/plinto misto")
    save_figure(plot_deformed(res, scale=350), "cs11_mixed_deformed.png",
                width=1100, height=720,
                title="Deformata spalla/plinto misto (scala 350x)")
    save_figure(plot_stress(res, "von_mises", subdivisions=8),
                "cs11_mixed_vm.png", width=1100, height=720,
                title="von Mises su spalla/plinto misto")
    save_figure(plot_stress(res, "szz", subdivisions=8),
                "cs11_mixed_szz.png", width=1100, height=720,
                title="sigma_zz su spalla/plinto misto")
    save_figure(plot_reactions(res), "cs11_mixed_reactions.png",
                width=1100, height=720,
                title="Reazioni vincolari spalla/plinto misto")

    max_global_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in m.nodes)
    print()
    print_check("max |u| globale", max_global_u, None)
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
