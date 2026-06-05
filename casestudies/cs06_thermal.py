"""Caso studio CS06 volumfeapy: Cubo con thermal load (espansione libera).

Caso classico FEM. Cubo [0,L]^3 soggetto a un incremento di temperatura
uniforme dT su tutto il volume. In assenza di vincoli, il cubo si
espande liberamente:

    epsilon_xx = epsilon_yy = epsilon_zz = alpha dT
    sigma_xx = sigma_yy = sigma_zz = 0
    u_x = alpha dT * x,  u_y = alpha dT * y,  u_z = alpha dT * z

Con un vincolo che impedisce la traslazione rigida (es. nodo 1 fissato
su tutti i 3 GdL), il campo di spostamento relativo a tale nodo e':

    u(x,y,z) = alpha dT * (x, y, z)

In assenza di vincoli, il cubo si espande di:

    Delta_L = alpha dT L
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


def main() -> None:
    L = 1.0
    dT = 100.0
    alpha = 1.2e-5
    E, nu = 210e9, 0.3
    mat = Material(E=E, nu=nu, alpha=alpha)
    delta_L = alpha * dT * L

    header("CS06 - Cubo con thermal load (espansione libera)")
    print(f"  L = {L} m, dT = {dT} K, alpha = {alpha:.2e} 1/K")
    print(f"  E = {E:.2e} Pa, nu = {nu}")
    print(f"  Espansione attesa Delta_L = alpha dT L = {delta_L:.4e} m")
    print()

    print(f"  {'mesh':>10s}  {'u_z(L) FEM':>14s}  {'err %':>8s}  "
          f"{'sigma_zz medio':>14s}  {'err %':>8s}")
    print("  " + "-" * 68)

    for n in (2, 4, 6, 8):
        m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
        m.fix(1)
        for eid in m.elements:
            m.add_thermal_load(eid, dT)
        res = m.solve()
        top_mid = top_ids[(n + 1) // 2 * (n + 1) + (n + 1) // 2]
        u_z_fem = res.displacement(top_mid, "uz")
        err_u = abs(u_z_fem - delta_L) / delta_L * 100

        from volumfeapy import postprocess
        sigmas = []
        for eid in m.elements:
            s = postprocess.element_stresses(res, eid)
            sigmas.append(s["szz"])
        szz_mean = sum(sigmas) / len(sigmas)
        err_s = abs(szz_mean - 0.0)
        print(f"  {n:>3d}x{n}x{n:<3d}  {u_z_fem:14.4e}  {err_u:7.3f}%  "
              f"{szz_mean:14.4e}  {err_s:7.3e}")

    n = 4
    m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
    m.fix(1)
    for eid in m.elements:
        m.add_thermal_load(eid, dT)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs06_mesh_{n}.png",
                title=f"Mesh cubo Hex8 {n}^3 - carico termico dT = {dT} K")
    save_figure(plot_deformed(res, scale=1e6), f"cs06_deformed_{n}.png",
                title=f"Espansione termica (scala 10^6×) - Delta_L = {delta_L:.2e} m")
    save_figure(plot_stress(res, "szz"), f"cs06_szz_{n}.png",
                title="sigma_zz [Pa] - atteso ~ 0 (espansione libera)")
    save_figure(plot_stress(res, "von_mises"), f"cs06_vm_{n}.png",
                title="von Mises [Pa] - atteso ~ 0")

    top_mid = top_ids[(n + 1) // 2 * (n + 1) + (n + 1) // 2]
    u_z_fem = res.displacement(top_mid, "uz")
    print_check("u_z(L) FEM", u_z_fem, delta_L, tol=0.05)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
