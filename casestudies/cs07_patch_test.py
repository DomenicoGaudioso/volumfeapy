"""Caso studio CS07 volumfeapy: Patch test (campo di spostamento lineare).

Caso classico FEM (Taylor, "The Finite Element Method", Vol. 1, Cap. 6).
Per ogni elemento finito, il patch test verifica che, sotto un campo di
spostamento lineare imposto a livello nodale, lo stato tensionale
risultante sia esatto.

Per un singolo elemento Hex8 (o un patch di Hex8) con un campo di
spostamento lineare:

    u(x,y,z) = (a + b*x, c + d*y, e + f*z)

le deformazioni sono costanti:

    eps_xx = b,  eps_yy = d,  eps_zz = f,  eps_xy = eps_yz = eps_xz = 0

e le tensioni risultanti:

    sigma_xx = D_00 b + D_01 d + D_02 f
    sigma_yy = D_10 b + D_11 d + D_12 f
    ...

Se il patch test passa, applicando un campo di spostamento lineare
impresso a tutti i nodi, il FEM riproduce esattamente il campo di
spostamento (errore < 1e-10) e le tensioni sono costanti su tutto il
dominio.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from volumfeapy import Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

from common import build_cube_hex8, save_figure, header


def main() -> None:
    L = 1.0
    n = 4
    E, nu = 210e9, 0.3
    mat = Material(E=E, nu=nu)

    header("CS07 - Patch test (campo spostamento lineare) - Hex8")
    print(f"  L = {L} m, E = {E:.2e} Pa, nu = {nu}, mesh = {n}^3")
    print()

    m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)

    bx, by, bz = 1.0e-4, 2.0e-4, -3.0e-4
    a0, c0, e0 = 0.0, 0.0, 0.0
    for nid, node in m.nodes.items():
        m.add_settlement(nid, "ux", a0 + bx * node.x)
        m.add_settlement(nid, "uy", c0 + by * node.y)
        m.add_settlement(nid, "uz", e0 + bz * node.z)

    res = m.solve()

    err_max = 0.0
    for nid, node in m.nodes.items():
        u_ex = np.array([a0 + bx * node.x, c0 + by * node.y, e0 + bz * node.z])
        u_fem = res.displacements(nid)
        err_max = max(err_max, float(np.max(np.abs(u_fem - u_ex))))

    print(f"  Campo imposto: u(x,y,z) = ({bx}*x, {by}*y, {bz}*z)")
    print(f"  Errore max spostamento: {err_max:.3e} m")
    if err_max < 1e-12:
        print(f"  [OK] Patch test SUPERATO (errore < 1e-12)")
    else:
        print(f"  [WARN] Patch test FALLITO: errore {err_max:.3e}")

    from volumfeapy import postprocess
    sxx_values = []
    syy_values = []
    szz_values = []
    for eid in m.elements:
        s = postprocess.element_stresses(res, eid)
        sxx_values.append(s["sxx"])
        syy_values.append(s["syy"])
        szz_values.append(s["szz"])

    sxx_var = max(sxx_values) - min(sxx_values)
    syy_var = max(syy_values) - min(syy_values)
    szz_var = max(szz_values) - min(szz_values)
    print(f"  Variazione sigma_xx sul dominio: {sxx_var:.3e} Pa (atteso 0)")
    print(f"  Variazione sigma_yy sul dominio: {syy_var:.3e} Pa (atteso 0)")
    print(f"  Variazione sigma_zz sul dominio: {szz_var:.3e} Pa (atteso 0)")
    print()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs07_mesh_{n}.png",
                title=f"Mesh cubo Hex8 {n}^3 - campo spostamento lineare imposto")
    save_figure(plot_deformed(res, scale=10000), f"cs07_deformed_{n}.png",
                title="Deformata (campo lineare) - scala 10000× per visualizzare")
    save_figure(plot_stress(res, "sxx"), f"cs07_sxx_{n}.png",
                title="sigma_xx [Pa] - atteso uniforme")
    save_figure(plot_stress(res, "von_mises"), f"cs07_vm_{n}.png",
                title="von Mises [Pa] - atteso uniforme")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
