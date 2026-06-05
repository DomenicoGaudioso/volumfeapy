"""Caso studio CS02 volumfeapy: Mensola 3D con Tet4 - confronto Euler-Bernoulli.

Caso classico FEM. Trave a sbalzo di dimensioni L x b x h con carico
concentrato P in punta (asse z). Si confronta la freccia in punta con la
soluzione di trave Euler-Bernoulli:

    u_z(L) = P L^3 / (3 E I)  con I = b h^3 / 12

Per Tet4 (CST a 4 nodi, deformazione costante), la convergenza e'
lineare e richiede mesh sufficientemente fini per accuratezza < 5%.

Caso: L = 2.0 m, b = 0.1 m, h = 0.2 m, P = 1000 N, E = 210 GPa.
I = 0.1 * 0.2^3 / 12 = 6.667e-5 m^4
u_z(L)_EB = 1000 * 2^3 / (3 * 210e9 * 6.667e-5) = 1.905e-3 m
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from volumfeapy import Model, Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

from common import (
    build_cantilever_tet4, save_figure,
    euler_bernoulli_tip_deflection, print_check, header,
)


def main() -> None:
    L = 2.0
    b = 0.1
    h = 0.2
    P = -1000.0
    E, nu = 210e9, 0.3
    I = b * h ** 3 / 12.0
    mat = Material(E=E, nu=nu)
    u_eb = euler_bernoulli_tip_deflection(P, L, E, I)

    header("CS02 - Mensola 3D (Tet4) sotto carico in punta")
    print(f"  L = {L} m, b = {b} m, h = {h} m, P = {P} N, E = {E:.2e} Pa, nu = {nu}")
    print(f"  I = b h^3 / 12 = {I:.4e} m^4")
    print(f"  u_z(L) Euler-Bernoulli = P L^3 / (3 E I) = {u_eb:.6e} m")
    print()

    print(f"  {'nx':>4s}  {'ny':>4s}  {'nz':>4s}  {'n_tet':>6s}  "
          f"{'u_z(L) FEM':>12s}  {'err %':>8s}")
    print("  " + "-" * 56)

    for nx, ny, nz in [(4, 2, 2), (8, 2, 4), (12, 4, 4), (16, 4, 6), (20, 4, 8), (30, 4, 10)]:
        m, fixed, tip = build_cantilever_tet4(L, b, h, nx, ny, nz, mat)
        for nid in fixed:
            m.fix(nid)
        per_node = P / len(tip)
        for nid in tip:
            m.add_nodal_load(nid, Fz=per_node)
        res = m.solve()
        tip_mid = tip[len(tip) // 2]
        u_z_fem = abs(res.displacement(tip_mid, "uz"))
        err = abs(u_z_fem - u_eb) / u_eb * 100
        n_tet = 6 * nx * ny * nz
        print(f"  {nx:>4d}  {ny:>4d}  {nz:>4d}  {n_tet:>6d}  {u_z_fem:12.4e}  {err:7.3f}%")

    nx, ny, nz = 20, 4, 8
    m, fixed, tip = build_cantilever_tet4(L, b, h, nx, ny, nz, mat)
    for nid in fixed:
        m.fix(nid)
    per_node = P / len(tip)
    for nid in tip:
        m.add_nodal_load(nid, Fz=per_node)
    res = m.solve()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs02_mesh_{nx}x{ny}x{nz}.png",
                title=f"Mesh Tet4: {6*nx*ny*nz} tetraedri")
    save_figure(plot_deformed(res, scale=50), f"cs02_deformed_{nx}x{ny}x{nz}.png",
                title=f"Deformata mensola Tet4 (scala 50×) — u_z punta = {u_eb*1e3:.2f} mm")
    save_figure(plot_stress(res, "von_mises"), f"cs02_vm_{nx}x{ny}x{nz}.png",
                title="von Mises [Pa] — massimo vicino all'incastro")
    save_figure(plot_stress(res, "sxx"), f"cs02_sxx_{nx}x{ny}x{nz}.png",
                title="sigma_xx [Pa] — trazione sopra l'asse neutro")
    save_figure(plot_stress(res, "szz"), f"cs02_szz_{nx}x{ny}x{nz}.png",
                title="sigma_zz [Pa] — taglio vicino all'incastro")

    tip_mid = tip[len(tip) // 2]
    u_z_fem = abs(res.displacement(tip_mid, "uz"))
    print_check("u_z(L) FEM vs EB", u_z_fem, u_eb, tol=0.10)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
