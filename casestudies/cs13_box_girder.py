"""Caso studio CS13: cassone sottile volumetrico Hex8 a mensola."""
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


def _add_node_unique(m: Model, node_map: dict[tuple[float, float, float], int],
                     xyz: tuple[float, float, float]) -> int:
    key = tuple(round(v, 10) for v in xyz)
    if key not in node_map:
        nid = len(node_map) + 1
        m.add_node(nid, *key)
        node_map[key] = nid
    return node_map[key]


def _add_hex_block(m: Model, node_map: dict, mat: Material, eid: int,
                   xs, ys, zs) -> int:
    ids = {}
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            for k, z in enumerate(zs):
                ids[(i, j, k)] = _add_node_unique(m, node_map, (x, y, z))
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            for k in range(len(zs) - 1):
                nodes = [
                    ids[(i, j, k)], ids[(i + 1, j, k)],
                    ids[(i + 1, j + 1, k)], ids[(i, j + 1, k)],
                    ids[(i, j, k + 1)], ids[(i + 1, j, k + 1)],
                    ids[(i + 1, j + 1, k + 1)], ids[(i, j + 1, k + 1)],
                ]
                m.add_hex8(eid, nodes, mat)
                eid += 1
    return eid


def build_box_girder_solid(nx: int = 18, n_width: int = 3, n_height: int = 3):
    """Costruisce un cassone rettangolare sottile con pareti Hex8."""
    L = 6.0
    b = 1.20
    h = 0.90
    t = 0.06
    E = 210e9
    nu = 0.30
    P = -25_000.0
    mat = Material(E=E, nu=nu)

    m = Model()
    node_map: dict[tuple[float, float, float], int] = {}
    xs = np.linspace(0.0, L, nx + 1)
    ys_full = np.linspace(-b / 2, b / 2, n_width + 1)
    zs_side = np.linspace(-h / 2 + t, h / 2 - t, n_height + 1)
    eid = 1

    # Soletta inferiore e superiore.
    eid = _add_hex_block(m, node_map, mat, eid, xs, ys_full, [-h / 2, -h / 2 + t])
    eid = _add_hex_block(m, node_map, mat, eid, xs, ys_full, [h / 2 - t, h / 2])
    # Anime laterali, senza sovrapporre lo spessore delle solette.
    eid = _add_hex_block(m, node_map, mat, eid, xs, [-b / 2, -b / 2 + t], zs_side)
    eid = _add_hex_block(m, node_map, mat, eid, xs, [b / 2 - t, b / 2], zs_side)

    fixed_nodes = [nid for nid, node in m.nodes.items() if abs(node.x) < 1e-12]
    tip_nodes = [nid for nid, node in m.nodes.items() if abs(node.x - L) < 1e-12]
    for nid in fixed_nodes:
        m.fix(nid)
    for nid in tip_nodes:
        m.add_nodal_load(nid, Fz=P / len(tip_nodes))

    meta = {
        "L": L, "b": b, "h": h, "t": t, "E": E, "nu": nu, "P": P,
        "fixed_nodes": fixed_nodes, "tip_nodes": tip_nodes,
    }
    return m, meta


def frame_box_figure(fig):
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X", range=[-0.2, 6.4]),
            yaxis=dict(title="Y", range=[-0.95, 0.95]),
            zaxis=dict(title="Z", range=[-0.75, 0.75]),
            aspectmode="manual",
            aspectratio=dict(x=3.4, y=1.0, z=1.0),
            camera=dict(projection=dict(type="orthographic"), eye=dict(x=1.7, y=-2.0, z=0.9)),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def main() -> None:
    m, meta = build_box_girder_solid()
    res = m.solve()
    tip_w = float(np.mean([res.displacement(nid, "uz") for nid in meta["tip_nodes"]]))
    max_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in m.nodes)
    max_vm = max(postprocess.element_stresses(res, eid)["von_mises"] for eid in m.elements)

    header("CS13 - Cassone sottile volumetrico Hex8 a mensola")
    print(f"  L = {meta['L']:.2f} m, b = {meta['b']:.2f} m, h = {meta['h']:.2f} m, t = {meta['t']:.3f} m")
    print(f"  Elementi Hex8 = {len(m.elements)}, nodi = {len(m.nodes)}")
    print(f"  Carico verticale in estremita' P = {meta['P']:.1f} N")
    print_check("w medio in punta", tip_w, -2.595807e-04, tol=0.20)
    print_check("max |u|", max_u, None)
    print_check("max von Mises", max_vm, None)

    save_figure(frame_box_figure(plot_mesh(m, show_node_ids=False)),
                "cs13_box_solid_mesh.png", width=1100, height=720,
                title="Cassone volumetrico Hex8 - mesh")
    save_figure(frame_box_figure(plot_supports(m)),
                "cs13_box_solid_supports.png", width=1100, height=720,
                title="Cassone volumetrico Hex8 - vincoli")
    save_figure(frame_box_figure(plot_deformed(res, scale=180)),
                "cs13_box_solid_deformed.png", width=1100, height=720,
                title="Cassone volumetrico Hex8 - deformata (scala 180x)")
    save_figure(frame_box_figure(plot_stress(res, "von_mises", subdivisions=3)),
                "cs13_box_solid_vm.png", width=1100, height=720,
                title="Cassone volumetrico Hex8 - von Mises")
    save_figure(frame_box_figure(plot_reactions(res)),
                "cs13_box_solid_reactions.png", width=1100, height=720,
                title="Cassone volumetrico Hex8 - reazioni")
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
