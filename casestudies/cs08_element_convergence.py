"""Caso studio CS08 volumfeapy: Convergenza elementi su mensola 3D.

Caso classico FEM. Si confrontano diversi elementi finiti 3D
(Hex8, Tet4, Tet10, Wedge6, Pyramid5) sulla stessa struttura: una
mensola 3D caricata in punta, confrontando la freccia in punta con
la soluzione di trave Euler-Bernoulli.

Per ciascun tipo di elemento, si misura l'errore relativo rispetto
alla soluzione esatta. Hex8 e Tet10 sono elementi del secondo ordine
(di base), Tet4 e' lineare, Wedge6 e Pyramid5 hanno ordine
intermedio.

Struttura: L x b x h = 2.0 x 0.2 x 0.4 m, P = 1 kN in punta,
E = 210 GPa, nu = 0.3.
I = 0.2 * 0.4^3 / 12 = 1.067e-3 m^4
u_z(L) EB = P L^3 / (3 E I) = 1000 * 8 / (3 * 210e9 * 1.067e-3) = 1.190e-5 m
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from volumfeapy import Model, Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

from common import (
    save_figure,
    euler_bernoulli_tip_deflection, print_check, header,
)


def build_hex8_cantilever(L, b, h, nx, ny, nz, mat):
    m = Model()
    nid = 1
    nodes = {}
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                m.add_node(nid, i * L / nx, j * b / ny, k * h / nz)
                nodes[(i, j, k)] = nid
                nid += 1
    eid = 1
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n1 = nodes[(i, j, k)]
                n2 = nodes[(i + 1, j, k)]
                n3 = nodes[(i + 1, j + 1, k)]
                n4 = nodes[(i, j + 1, k)]
                n5 = nodes[(i, j, k + 1)]
                n6 = nodes[(i + 1, j, k + 1)]
                n7 = nodes[(i + 1, j + 1, k + 1)]
                n8 = nodes[(i, j + 1, k + 1)]
                m.add_hex8(eid, [n1, n2, n3, n4, n5, n6, n7, n8], mat)
                eid += 1
    return m, nodes


def build_tet4_cantilever(L, b, h, nx, ny, nz, mat):
    m = Model()
    nid = 1
    nodes = {}
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                m.add_node(nid, i * L / nx, j * b / ny, k * h / nz)
                nodes[(i, j, k)] = nid
                nid += 1
    eid = 1
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n1 = nodes[(i, j, k)]
                n2 = nodes[(i + 1, j, k)]
                n3 = nodes[(i + 1, j + 1, k)]
                n4 = nodes[(i, j + 1, k)]
                n5 = nodes[(i, j, k + 1)]
                n6 = nodes[(i + 1, j, k + 1)]
                n7 = nodes[(i + 1, j + 1, k + 1)]
                n8 = nodes[(i, j + 1, k + 1)]
                m.add_tet4(eid, [n1, n2, n4, n5], mat); eid += 1
                m.add_tet4(eid, [n2, n3, n4, n7], mat); eid += 1
                m.add_tet4(eid, [n2, n5, n6, n7], mat); eid += 1
                m.add_tet4(eid, [n4, n5, n7, n8], mat); eid += 1
                m.add_tet4(eid, [n2, n4, n5, n7], mat); eid += 1
                m.add_tet4(eid, [n2, n4, n7, n6], mat); eid += 1
    return m, nodes


def build_wedge6_cantilever(L, b, h, nx, ny, nz, mat):
    """Mensola discretizzata con Wedge6: celle esaedriche divise in 2 cunei
    ciascuna (sezione in y triangolare). Per semplicita', dividiamo ogni
    cella in 6 cunei disposti sui 3 assi (non ideale, ma dimostrativo)."""
    m = Model()
    nid = 1
    nodes = {}
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                m.add_node(nid, i * L / nx, j * b / ny, k * h / nz)
                nodes[(i, j, k)] = nid
                nid += 1
    eid = 1
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n1 = nodes[(i, j, k)]
                n2 = nodes[(i + 1, j, k)]
                n3 = nodes[(i + 1, j + 1, k)]
                n4 = nodes[(i, j + 1, k)]
                n5 = nodes[(i, j, k + 1)]
                n6 = nodes[(i + 1, j, k + 1)]
                n7 = nodes[(i + 1, j + 1, k + 1)]
                n8 = nodes[(i, j + 1, k + 1)]
                m.add_wedge6(eid, [n1, n2, n4, n5, n6, n8], mat); eid += 1
                m.add_wedge6(eid, [n2, n4, n3, n6, n8, n7], mat); eid += 1
                m.add_wedge6(eid, [n2, n3, n7, n6, n7, n7], mat); eid += 1
                m.add_wedge6(eid, [n4, n3, n7, n8, n7, n7], mat); eid += 1
                m.add_wedge6(eid, [n5, n6, n8, n5, n6, n8], mat); eid += 1
                m.add_wedge6(eid, [n6, n8, n7, n6, n8, n7], mat); eid += 1
    return m, nodes


def apply_load_and_solve(m, nodes, L, b, h, nx, ny, nz, P, E, I, mat):
    """Applica incastro sul lato x=0 e carico in punta. Ritorna u_z_tip FEM."""
    for k in range(nz + 1):
        for j in range(ny + 1):
            nid = nodes[(0, j, k)]
            m.fix(nid)
    tip_count = 0
    for k in range(nz + 1):
        for j in range(ny + 1):
            tip_count += 1
    per_node = P / tip_count
    for k in range(nz + 1):
        for j in range(ny + 1):
            nid = nodes[(nx, j, k)]
            m.add_nodal_load(nid, Fz=per_node)
    res = m.solve()
    tip_mid = nodes[(nx, ny // 2, nz // 2)]
    return abs(res.displacement(tip_mid, "uz"))


def main() -> None:
    L, b, h = 2.0, 0.2, 0.4
    P = -1000.0
    E, nu = 210e9, 0.3
    I = b * h ** 3 / 12.0
    mat = Material(E=E, nu=nu)
    u_eb = euler_bernoulli_tip_deflection(P, L, E, I)

    header("CS08 - Convergenza elementi su mensola 3D")
    print(f"  L = {L} m, b = {b} m, h = {h} m, P = {P} N")
    print(f"  E = {E:.2e} Pa, nu = {nu}, I = {I:.4e} m^4")
    print(f"  u_z(L) Euler-Bernoulli = P L^3 / (3 E I) = {u_eb:.4e} m")
    print()

    print(f"  {'elemento':>12s}  {'mesh':>12s}  {'n_el':>6s}  "
          f"{'u_z FEM':>12s}  {'err %':>8s}")
    print("  " + "-" * 60)

    nx, ny, nz = 8, 2, 4
    m, nodes = build_hex8_cantilever(L, b, h, nx, ny, nz, mat)
    u = apply_load_and_solve(m, nodes, L, b, h, nx, ny, nz, P, E, I, mat)
    err = abs(u - u_eb) / u_eb * 100
    n_el = nx * ny * nz
    print(f"  {'Hex8':>12s}  {nx:>3d}x{ny}x{nz:<3d}      {n_el:>6d}  {u:12.4e}  {err:7.3f}%")

    nx, ny, nz = 8, 2, 4
    m, nodes = build_tet4_cantilever(L, b, h, nx, ny, nz, mat)
    u = apply_load_and_solve(m, nodes, L, b, h, nx, ny, nz, P, E, I, mat)
    err = abs(u - u_eb) / u_eb * 100
    n_el = 6 * nx * ny * nz
    print(f"  {'Tet4':>12s}  {nx:>3d}x{ny}x{nz:<3d}      {n_el:>6d}  {u:12.4e}  {err:7.3f}%")

    nx, ny, nz = 6, 2, 3
    m, nodes = build_wedge6_cantilever(L, b, h, nx, ny, nz, mat)
    n_el_real = len(m.elements)
    try:
        u = apply_load_and_solve(m, nodes, L, b, h, nx, ny, nz, P, E, I, mat)
        err = abs(u - u_eb) / u_eb * 100
        print(f"  {'Wedge6':>12s}  {nx:>3d}x{ny}x{nz:<3d}      {n_el_real:>6d}  {u:12.4e}  {err:7.3f}%")
    except Exception as exc:
        print(f"  {'Wedge6':>12s}  errore: {exc!r}")

    print()
    nx, ny, nz = 8, 2, 4
    m, nodes = build_hex8_cantilever(L, b, h, nx, ny, nz, mat)
    u = apply_load_and_solve(m, nodes, L, b, h, nx, ny, nz, P, E, I, mat)

    save_figure(plot_mesh(m, show_node_ids=False), f"cs08_mesh_hex8_{nx}.png",
                title=f"Mesh Hex8 mensola: {nx*ny*nz} elementi")
    save_figure(plot_deformed(m.solve(), scale=50000), f"cs08_deformed_hex8_{nx}.png",
                title="Deformata mensola Hex8 (scala 50000×)")

    print_check("u_z(L) Hex8 vs EB", u, u_eb, tol=0.10)
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
