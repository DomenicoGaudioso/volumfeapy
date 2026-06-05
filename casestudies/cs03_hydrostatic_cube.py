"""Caso studio CS03 volumfeapy: Cubo sotto pressione idrostatica (Lamé-like).

Caso classico FEM. Cubo [0,L]^3 soggetto a pressione uniforme p su tutte
e 6 le facce. La soluzione esatta in campo elastico lineare e':

    sigma_xx = sigma_yy = sigma_zz = -p  (compressione idrostatica)
    u_x = -p * x / (K_bulk),  con K_bulk = E / [3 (1 - 2 nu)]
    u_y, u_z analoghi

Il cubo si contrae uniformemente verso il suo centro. Per simmetria,
possiamo modellare solo 1/8 del cubo con opportune condizioni di
simmetria, ma in questo caso studio usiamo il cubo completo per
semplicita'.

Caso: L = 1 m, p = 1 MPa, E = 210 GPa, nu = 0.3.
K_bulk = E / (3(1-2 nu)) = 210e9 / 1.2 = 1.75e11 Pa
u_x(L/2) = -p * (L/2) / K_bulk = -1e6 * 0.5 / 1.75e11 = -2.857e-6 m
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from volumfeapy import Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

from common import build_cube_hex8, save_figure, print_check, header


def apply_face_pressure_uniform(model, L: float, n: int, p: float) -> None:
    """Applica pressione uniforme p su tutte e 6 le facce del cubo.

    Forza per nodo = p * A_nodo, dove A_nodo dipende dalla posizione del
    nodo sulla faccia (angolo, spigolo, interno).
    """
    cell = L / n

    def _node_area_on_face(node, face_axis: str) -> float:
        """Area di influenza di un nodo su una data faccia."""
        x_on = node.x in (0.0, L)
        y_on = node.y in (0.0, L)
        z_on = node.z in (0.0, L)
        if face_axis == "x":
            on_count = sum([x_on, y_on, z_on])
            if on_count == 1:
                return (cell / 2.0) ** 2
            elif on_count == 2:
                return (cell / 2.0) * cell
            else:
                return cell * cell
        elif face_axis == "y":
            on_count = sum([x_on, y_on, z_on])
            if on_count == 1:
                return (cell / 2.0) ** 2
            elif on_count == 2:
                return cell * (cell / 2.0)
            else:
                return cell * cell
        elif face_axis == "z":
            on_count = sum([x_on, y_on, z_on])
            if on_count == 1:
                return (cell / 2.0) ** 2
            elif on_count == 2:
                return cell * (cell / 2.0)
            else:
                return cell * cell

    for nid, node in model.nodes.items():
        if node.x == L:
            model.add_nodal_load(nid, Fx=p * _node_area_on_face(node, "x"))
        if node.x == 0.0:
            model.add_nodal_load(nid, Fx=-p * _node_area_on_face(node, "x"))
        if node.y == L:
            model.add_nodal_load(nid, Fy=p * _node_area_on_face(node, "y"))
        if node.y == 0.0:
            model.add_nodal_load(nid, Fy=-p * _node_area_on_face(node, "y"))
        if node.z == L:
            model.add_nodal_load(nid, Fz=p * _node_area_on_face(node, "z"))
        if node.z == 0.0:
            model.add_nodal_load(nid, Fz=-p * _node_area_on_face(node, "z"))


def main() -> None:
    L = 1.0
    p = 1.0e6
    E, nu = 210e9, 0.3
    K_bulk = E / (3.0 * (1.0 - 2.0 * nu))
    mat = Material(E=E, nu=nu)
    u_ex = p * (L / 2.0) / K_bulk

    header("CS03 - Cubo sotto pressione idrostatica (Hex8)")
    print(f"  L = {L} m, p = {p:.2e} Pa, E = {E:.2e} Pa, nu = {nu}")
    print(f"  K_bulk = E / (3(1-2 nu)) = {K_bulk:.4e} Pa")
    print(f"  sigma_xx = sigma_yy = sigma_zz = -p (compressione uniforme)")
    print(f"  u_max (al centro di una faccia) atteso = {u_ex:.4e} m")
    print()

    print(f"  {'mesh':>10s}  {'u_x centro faccia':>18s}  {'err %':>8s}  "
          f"{'sigma_xx medio':>14s}  {'err %':>8s}")
    print("  " + "-" * 76)

    for n in (2, 4, 6, 8):
        m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)

        apply_face_pressure_uniform(m, L, n, p)

        m.fix(1, ["ux", "uy", "uz"])

        res = m.solve()
        target = top_ids[(n + 1) // 2 * (n + 1) + (n + 1) // 2]
        u_x_fem = abs(res.displacement(target, "ux"))

        from volumfeapy import postprocess
        sigmas = []
        for eid in m.elements:
            s = postprocess.element_stresses(res, eid)
            sigmas.append(s["sxx"])
        sxx_mean = sum(sigmas) / len(sigmas)

        err_u = abs(u_x_fem - u_ex) / u_ex * 100
        err_s = abs(sxx_mean - (-p)) / p * 100
        print(f"  {n:>3d}x{n}x{n:<3d}  {u_x_fem:18.4e}  {err_u:7.3f}%  "
              f"{sxx_mean:14.4e}  {err_s:7.3f}%")

    n = 4
    m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
    apply_face_pressure_uniform(m, L, n, p)
    m.fix(1, ["ux", "uy", "uz"])
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs03_mesh_{n}.png",
                title=f"Mesh cubo Hex8 {n}^3")
    save_figure(plot_deformed(res, scale=2000), f"cs03_deformed_{n}.png",
                title="Cubo sotto pressione idrostatica (scala 2000×) — contrazione uniforme")
    save_figure(plot_stress(res, "sxx"), f"cs03_sxx_{n}.png",
                title="sigma_xx [Pa] - uniforme = -p")
    save_figure(plot_stress(res, "von_mises"), f"cs03_vm_{n}.png",
                title="von Mises = 0 (stato idrostatico)")

    target = top_ids[(n + 1) // 2 * (n + 1) + (n + 1) // 2]
    u_x_fem = abs(res.displacement(target, "ux"))
    print_check("u_x centro faccia", u_x_fem, u_ex, tol=0.05)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
