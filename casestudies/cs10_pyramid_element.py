"""Caso studio CS10 volumfeapy: elemento Pyramid5.

Esempio mirato per visualizzare l'elemento piramidale a 5 nodi. La base
quadrata e' vincolata, l'apice e' caricato verticalmente e le tensioni sono
mostrate sulle facce esterne con contour interpolato.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from volumfeapy import Material, Model
from volumfeapy import postprocess
from volumfeapy.plotting import plot_deformed, plot_mesh, plot_stress

from common import header, print_check, save_figure


def build_single_pyramid(mat: Material) -> Model:
    m = Model()
    m.add_node(1, 0.0, 0.0, 0.0)
    m.add_node(2, 1.0, 0.0, 0.0)
    m.add_node(3, 1.0, 1.0, 0.0)
    m.add_node(4, 0.0, 1.0, 0.0)
    m.add_node(5, 0.5, 0.5, 0.9)
    m.add_pyramid5(1, [1, 2, 3, 4, 5], mat)
    return m


def main() -> None:
    E, nu = 30e9, 0.22
    P = -50_000.0
    mat = Material(E=E, nu=nu)
    m = build_single_pyramid(mat)

    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    m.add_nodal_load(5, Fz=P)

    res = m.solve()
    uz = res.displacement(5, "uz")
    vm = postprocess.element_stresses(res, 1)["von_mises"]

    header("CS10 - Elemento piramidale Pyramid5")
    print(f"  Base 1.0 x 1.0 m, altezza = 0.9 m")
    print(f"  E = {E:.2e} Pa, nu = {nu}, P_apice = {P:.2e} N")
    print(f"  Volume elemento = {m.elements[1].volume():.4e} m^3")
    print_check("u_z apice", uz, None)
    print_check("von Mises elemento", vm, None)

    save_figure(plot_mesh(m, show_node_ids=True), "cs10_pyramid_mesh.png",
                title="Mesh Pyramid5 con ID nodi")
    save_figure(plot_deformed(res, scale=600), "cs10_pyramid_deformed.png",
                title="Deformata Pyramid5 (scala 600x)")
    save_figure(plot_stress(res, "von_mises", subdivisions=8),
                "cs10_pyramid_vm.png",
                title="Tensioni von Mises su facce Pyramid5")
    save_figure(plot_stress(res, "szz", subdivisions=8),
                "cs10_pyramid_szz.png",
                title="Tensione sigma_zz su facce Pyramid5")

    print("  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
