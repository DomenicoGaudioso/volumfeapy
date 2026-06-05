"""Caso studio CS01 volumfeapy: Cubo in trazione uniassiale con Hex8.

Caso classico (Cook, Malkus & Plesha, "Concepts and Applications of
Finite Element Analysis", 3rd ed., Cap. 2). Cubo unitario [0,1]^3 con
carico di trazione uniassiale sigma_zz = q applicato sulla faccia
superiore. La soluzione esatta in campo elastico lineare e':

    sigma_zz = q,  sigma_xx = sigma_yy = 0
    u_z(z) = q * z / E
    u_x = u_y = 0

Il vincolo minimo e' l'incastro della faccia inferiore (z = 0) per
tutti i gradi di liberta' (u_x = u_y = u_z = 0).

Il carico viene applicato come forze nodali equivalenti distribuite
sulla faccia superiore (z = 1), ciascuna pari a q * A_nodo dove A_nodo
e' l'area di influenza del nodo (angolo L^2/(4n^2), spigolo L^2/(2n^2),
interno L^2/n^2).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from volumfeapy import Model, Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

from common import build_cube_hex8, save_figure, print_check, header


def apply_face_pressure_z(model, n: int, L: float, q: float) -> None:
    """Applica una pressione uniforme q sulla faccia z = L (forze nodali).

    Forza per nodo: F_nodo = q * A_nodo, dove A_nodo dipende dalla
    posizione del nodo sulla faccia (angolo, spigolo, interno).
    """
    cell = L / n
    for nid, node in model.nodes.items():
        if abs(node.z - L) > 1e-12:
            continue
        is_corner = (node.x in (0.0, L)) and (node.y in (0.0, L))
        is_edge = (node.x in (0.0, L)) or (node.y in (0.0, L))
        if is_corner:
            area = (cell / 2.0) ** 2
        elif is_edge:
            area = (cell / 2.0) * cell
        else:
            area = cell * cell
        model.add_nodal_load(nid, Fz=q * area)


def main() -> None:
    L = 1.0
    q = 1.0e6
    E, nu = 210e9, 0.3
    mat = Material(E=E, nu=nu)

    header("CS01 - Cubo in trazione uniassiale (Hex8)")
    print(f"  L = {L} m, q = {q:.2e} Pa, E = {E:.2e} Pa, nu = {nu}")
    print(f"  Soluzione esatta: sigma_zz = q = {q:.2e} Pa")
    print(f"                     u_z(L) = q L / E = {q * L / E:.4e} m")
    print()

    print(f"  {'mesh':>10s}  {'u_z tip FEM':>14s}  {'err %':>8s}  "
          f"{'sigma_zz medio':>14s}  {'err %':>8s}")
    print("  " + "-" * 72)

    for n in (2, 4, 6, 8):
        m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
        for nid in bottom_ids:
            m.fix(nid)

        apply_face_pressure_z(m, n, L, q)

        res = m.solve()
        u_z_tip = res.displacement(top_ids[len(top_ids) // 2], "uz")
        u_z_ex = q * L / E

        from volumfeapy import postprocess
        sigmas = []
        for eid in m.elements:
            s = postprocess.element_stresses(res, eid)
            sigmas.append(s["szz"])
        szz_mean = sum(sigmas) / len(sigmas)
        szz_ex = q

        err_u = abs(u_z_tip - u_z_ex) / u_z_ex * 100
        err_s = abs(szz_mean - szz_ex) / szz_ex * 100
        print(f"  {n:>3d}x{n}x{n:<3d}  {u_z_tip:14.4e}  {err_u:7.3f}%  "
              f"{szz_mean:14.4e}  {err_s:7.3f}%")

    n = 4
    m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
    for nid in bottom_ids:
        m.fix(nid)
    apply_face_pressure_z(m, n, L, q)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs01_mesh_{n}.png",
                title=f"Mesh cubo Hex8 {n}^3 = {n*n*n} elementi")
    save_figure(plot_deformed(res, scale=200), f"cs01_deformed_{n}.png",
                title="Deformata cubo trazione (scala 200×)")
    save_figure(plot_stress(res, "szz"), f"cs01_szz_{n}.png",
                title="sigma_zz [Pa] - uniforme = q")
    save_figure(plot_stress(res, "von_mises"), f"cs01_vonmises_{n}.png",
                title="von Mises [Pa] = |q| uniforme")
    save_figure(plot_stress(res, "sxx"), f"cs01_sxx_{n}.png",
                title="sigma_xx [Pa] - atteso ~ 0 (effetto Poisson trascurabile)")

    u_z_tip = res.displacement(top_ids[len(top_ids) // 2], "uz")
    print_check("u_z(L)", u_z_tip, q * L / E, tol=0.05)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
