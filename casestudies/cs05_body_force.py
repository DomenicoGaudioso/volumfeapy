"""Caso studio CS05 volumfeapy: Cubo con body force (gravita').

Caso classico FEM. Un cubo [0,L]^3 soggetto alla forza di volume
(peso proprio) con densita' rho e accelerazione di gravita' g
diretta in -z. Si confronta lo spostamento verticale del centro di
ogni faccia orizzontale con la soluzione di compressione uniassiale:

    sigma_zz(z) = rho * g * (L - z)
    u_z(z) = (rho g L^2) / (2 E) * (1 - (z/L)^2 - 2 nu (1 - z/L)) -- con vincoli SS

Caso semplificato con vincoli solo di supporto sulla faccia inferiore
(sigma_zz = 0 a z = 0, spostamento libero laterale):

    sigma_zz(z) = -rho g z  (compressione crescente con la profondita')
    u_z(z) = -(rho g) / E * z^2 / 2
    u_z(L) = -(rho g L^2) / (2 E)
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
    rho = 7850.0
    g = 9.81
    E, nu = 210e9, 0.3
    mat = Material(E=E, nu=nu, rho=rho)
    sigma_max = rho * g * L
    u_max = rho * g * L ** 2 / (2.0 * E)

    header("CS05 - Cubo con peso proprio (body force)")
    print(f"  L = {L} m, rho = {rho} kg/m^3, g = {g} m/s^2")
    print(f"  E = {E:.2e} Pa, nu = {nu}")
    print(f"  sigma_zz(0) = -rho g L = {sigma_max:.2e} Pa (massima compressione al suolo)")
    print(f"  u_z(L) = -rho g L^2 / (2 E) = {u_max:.4e} m")
    print()

    print(f"  {'mesh':>10s}  {'u_z(L) FEM':>14s}  {'err %':>8s}  "
          f"{'sigma_zz(0) medio':>16s}  {'err %':>8s}")
    print("  " + "-" * 72)

    for n in (2, 4, 6, 8):
        m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
        m.add_gravity(g=g, direction="z", case="default")
        for nid in bottom_ids:
            m.fix(nid, ["ux", "uy", "uz"])
        res = m.solve()
        top_mid = top_ids[(n + 1) // 2 * (n + 1) + (n + 1) // 2]
        u_z_fem = abs(res.displacement(top_mid, "uz"))
        err_u = abs(u_z_fem - u_max) / u_max * 100

        from volumfeapy import postprocess
        sigmas = []
        for eid, el in m.elements.items():
            coords = el._coords()
            cz = coords[:, 2].mean()
            if cz < L / n:
                s = postprocess.element_stresses(res, eid)
                sigmas.append(s["szz"])
        szz_mean = sum(sigmas) / len(sigmas)
        err_s = abs(szz_mean - (-sigma_max)) / sigma_max * 100
        print(f"  {n:>3d}x{n}x{n:<3d}  {u_z_fem:14.4e}  {err_u:7.3f}%  "
              f"{szz_mean:16.4e}  {err_s:7.3f}%")

    n = 4
    m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
    m.add_gravity(g=g, direction="z", case="default")
    for nid in bottom_ids:
        m.fix(nid, ["ux", "uy", "uz"])
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs05_mesh_{n}.png",
                title=f"Mesh cubo Hex8 {n}^3")
    save_figure(plot_deformed(res, scale=20000), f"cs05_deformed_{n}.png",
                title="Deformata cubo sotto peso proprio (scala 20000×)")
    save_figure(plot_stress(res, "szz"), f"cs05_szz_{n}.png",
                title="sigma_zz [Pa] - lineare in z (max compressione al suolo)")
    save_figure(plot_stress(res, "von_mises"), f"cs05_vm_{n}.png",
                title="von Mises [Pa]")

    top_mid = top_ids[(n + 1) // 2 * (n + 1) + (n + 1) // 2]
    u_z_fem = abs(res.displacement(top_mid, "uz"))
    print_check("u_z(L) FEM", u_z_fem, u_max, tol=0.20)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
