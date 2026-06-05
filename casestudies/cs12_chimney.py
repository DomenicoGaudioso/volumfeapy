"""Caso studio CS12: ciminiera solida rastremata con apertura.

Il caso usa una mesh Hex8 cilindrica per rappresentare il fusto di una
ciminiera in c.a. con spessore finito. La geometria e' confrontabile con il
caso CS13 di platefeapy: stessa altezza, raggi medi, spessore, legge di vento
e apertura di servizio alla base.
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


def radius_at_height(z: float, H: float, r_base: float, r_top: float) -> float:
    return r_base + (r_top - r_base) * z / H


def wind_pressure(theta: float, z: float, H: float) -> float:
    """Stessa legge del caso platefeapy CS13."""
    q_top = 500.0
    q_z = q_top * (0.35 + 0.65 * (z / H) ** 0.25)
    cp = max(0.0, np.cos(theta)) + 0.18 * max(0.0, -np.cos(theta))
    return q_z * cp


def _inside_service_opening(theta: float, z: float, H: float,
                            r_base: float, r_top: float) -> bool:
    r = radius_at_height(z, H, r_base, r_top)
    return abs(theta * r) < 1.45 and 3.0 < z < 12.0


def _quad_area(points: list[np.ndarray]) -> float:
    return (
        0.5 * np.linalg.norm(np.cross(points[1] - points[0], points[2] - points[0]))
        + 0.5 * np.linalg.norm(np.cross(points[2] - points[0], points[3] - points[0]))
    )


def build_chimney_solid(ntheta: int = 24, nz: int = 16):
    """Costruisce la ciminiera solida come mesh Hex8 cilindrica."""
    H = 60.0
    r_base = 3.0
    r_top = 2.05
    thickness = 0.40
    mat = Material(E=30e9, nu=0.20)

    theta_vals = np.linspace(-np.pi, np.pi, ntheta, endpoint=False)
    z_vals = np.linspace(0.0, H, nz + 1)

    kept_cells: list[tuple[int, int]] = []
    used_nodes: set[tuple[int, int, int]] = set()
    for j in range(nz):
        z_c = 0.5 * (z_vals[j] + z_vals[j + 1])
        for i, theta0 in enumerate(theta_vals):
            theta1 = theta_vals[(i + 1) % ntheta]
            if i == ntheta - 1:
                theta1 += 2.0 * np.pi
            theta_c = 0.5 * (theta0 + theta1)
            theta_eval = ((theta_c + np.pi) % (2.0 * np.pi)) - np.pi
            if _inside_service_opening(theta_eval, z_c, H, r_base, r_top):
                continue
            kept_cells.append((i, j))
            ip = (i + 1) % ntheta
            used_nodes.update({
                (0, i, j), (0, ip, j), (1, ip, j), (1, i, j),
                (0, i, j + 1), (0, ip, j + 1), (1, ip, j + 1), (1, i, j + 1),
            })

    m = Model()
    node_map: dict[tuple[int, int, int], int] = {}
    node_theta: dict[int, float] = {}
    nid = 1
    for key in sorted(used_nodes, key=lambda p: (p[2], p[1], p[0])):
        ir, i, j = key
        theta = theta_vals[i]
        z = z_vals[j]
        r_mid = radius_at_height(z, H, r_base, r_top)
        r = r_mid + (0.5 * thickness if ir == 1 else -0.5 * thickness)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        m.add_node(nid, x, y, z)
        node_map[key] = nid
        node_theta[nid] = theta
        nid += 1

    outer_faces: list[tuple[int, list[int], float, float]] = []
    eid = 1
    for i, j in kept_cells:
        ip = (i + 1) % ntheta
        nodes = [
            node_map[(0, i, j)],
            node_map[(0, ip, j)],
            node_map[(1, ip, j)],
            node_map[(1, i, j)],
            node_map[(0, i, j + 1)],
            node_map[(0, ip, j + 1)],
            node_map[(1, ip, j + 1)],
            node_map[(1, i, j + 1)],
        ]
        m.add_hex8(eid, nodes, mat)

        theta0 = theta_vals[i]
        theta1 = theta_vals[ip] + (2.0 * np.pi if i == ntheta - 1 else 0.0)
        theta_c = ((0.5 * (theta0 + theta1) + np.pi) % (2.0 * np.pi)) - np.pi
        z_c = 0.5 * (z_vals[j] + z_vals[j + 1])
        outer_faces.append((eid, [nodes[k] for k in [3, 2, 6, 7]], theta_c, z_c))
        eid += 1

    for nid, node in m.nodes.items():
        if abs(node.z) < 1e-12:
            m.fix(nid)

    # Pressione vento equivalente sui nodi della superficie esterna.
    load_acc: dict[int, np.ndarray] = {nid: np.zeros(3) for nid in m.nodes}
    for _, face_nodes, theta, z in outer_faces:
        pts = [m.nodes[nid].coords for nid in face_nodes]
        area = _quad_area(pts)
        normal = np.array([np.cos(theta), np.sin(theta), 0.0])
        force = -wind_pressure(theta, z, H) * normal * area
        for nid in face_nodes:
            load_acc[nid] += 0.25 * force
    for nid, f in load_acc.items():
        if np.linalg.norm(f) > 1e-12:
            m.add_nodal_load(nid, Fx=float(f[0]), Fy=float(f[1]), Fz=float(f[2]))

    return m, {
        "H": H,
        "r_base": r_base,
        "r_top": r_top,
        "thickness": thickness,
        "outer_faces": outer_faces,
        "node_theta": node_theta,
    }


def radial_displacement(result, nid: int, theta: float) -> float:
    u = result.displacements(nid)
    er = np.array([np.cos(theta), np.sin(theta), 0.0])
    return float(u @ er)


def frame_chimney_figure(fig):
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X", range=[-4.2, 4.2]),
            yaxis=dict(title="Y", range=[-4.2, 4.2]),
            zaxis=dict(title="Z", range=[0.0, 60.0]),
            aspectmode="manual",
            aspectratio=dict(x=1.0, y=1.0, z=1.45),
            camera=dict(
                projection=dict(type="orthographic"),
                eye=dict(x=1.8, y=-2.4, z=0.35),
            ),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def main() -> None:
    m, meta = build_chimney_solid()
    res = m.solve()

    outer_nodes = {
        nid for _, face_nodes, _, _ in meta["outer_faces"]
        for nid in face_nodes
    }
    radial_vals = [
        radial_displacement(res, nid, meta["node_theta"][nid])
        for nid in outer_nodes
    ]
    max_ur = max(abs(v) for v in radial_vals)
    max_u = max(float(np.linalg.norm(res.displacements(nid))) for nid in m.nodes)
    max_vm = max(
        postprocess.element_stresses(res, eid)["von_mises"]
        for eid in m.elements
    )
    total_fx = sum(load.Fx for load in m.nodal_loads)
    base_reaction_fx = sum(
        res.reactions(nid)[0]
        for nid, node in m.nodes.items()
        if abs(node.z) < 1e-12
    )

    header("CS12 - Ciminiera solida rastremata con apertura")
    print(f"  H = {meta['H']:.1f} m, r_base = {meta['r_base']:.2f} m, r_top = {meta['r_top']:.2f} m")
    print(f"  t = {meta['thickness']:.3f} m, elementi = {len(m.elements)}, nodi = {len(m.nodes)}")
    print("  Mesh: Hex8 cilindrica, apertura di servizio, base incastrata")
    print_check("max |u_radiale|", max_ur, None)
    print_check("max |u|", max_u, None)
    print_check("max von Mises", max_vm, None)
    print_check("equilibrio Fx R+F", base_reaction_fx + total_fx, 0.0, tol=0.02)

    save_figure(frame_chimney_figure(plot_mesh(m, show_node_ids=False)), "cs12_chimney_mesh.png",
                width=950, height=900, title="Mesh solida ciminiera")
    save_figure(frame_chimney_figure(plot_supports(m)), "cs12_chimney_supports.png",
                width=950, height=900, title="Vincoli ciminiera solida")
    save_figure(frame_chimney_figure(plot_deformed(res, scale=40)), "cs12_chimney_deformed.png",
                width=950, height=900, title="Deformata ciminiera solida (scala 40x)")
    save_figure(frame_chimney_figure(plot_stress(res, "von_mises", subdivisions=3)),
                "cs12_chimney_vm.png", width=950, height=900,
                title="von Mises ciminiera solida")
    save_figure(frame_chimney_figure(plot_stress(res, "sxx", subdivisions=3)),
                "cs12_chimney_sxx.png", width=950, height=900,
                title="sigma_xx ciminiera solida")
    save_figure(frame_chimney_figure(plot_reactions(res)), "cs12_chimney_reactions.png",
                width=950, height=900, title="Reazioni vincolari")
    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
