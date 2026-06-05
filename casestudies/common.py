"""Helper condivisi per i casi studio volumfeapy.

Fornisce:
- save_figure(fig, name): esporta un plotly figure in PNG (kaleido)
- build_cube_hex8: cubo unitario Hex8 meshato uniformemente
- build_cantilever_tet4: trave a sbalzo con elementi Tet4
- euler_bernoulli_tip_deflection: formula classica trave a sbalzo
- print_check(label, fem, exact, tol): stampa confronto
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np

CASESTUDIES_DIR = Path(__file__).resolve().parent
IMAGES_DIR = CASESTUDIES_DIR / "images"
DOC_IMAGES_DIR = CASESTUDIES_DIR.parent / "docs" / "casestudies" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DOC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def save_figure(fig, name: str, width: int = 800, height: int = 600,
                scale: int = 1, title: str | None = None) -> Path:
    """Salva una figura Plotly come PNG in casestudies/images/."""
    if title is not None:
        fig.update_layout(title=title)
    fig.update_layout(width=width, height=height)
    out = IMAGES_DIR / name
    fig.write_image(str(out), scale=scale)
    shutil.copy2(out, DOC_IMAGES_DIR / name)
    return out


def build_cube_hex8(L: float, n: int, mat):
    """Cubo [0,L]^3 meshato uniformemente con n^3 Hex8.

    Ritorna (model, boundary_node_ids_z0, top_node_ids_zL).
    """
    from volumfeapy import Model
    m = Model()
    nid = 1
    for k in range(n + 1):
        for j in range(n + 1):
            for i in range(n + 1):
                m.add_node(nid, i * L / n, j * L / n, k * L / n)
                nid += 1
    eid = 1
    for k in range(n):
        for j in range(n):
            for i in range(n):
                base = k * (n + 1) ** 2 + j * (n + 1) + i + 1
                n1 = base
                n2 = base + 1
                n3 = base + (n + 1) + 1
                n4 = base + (n + 1)
                n5 = n1 + (n + 1) ** 2
                n6 = n2 + (n + 1) ** 2
                n7 = n3 + (n + 1) ** 2
                n8 = n4 + (n + 1) ** 2
                m.add_hex8(eid, [n1, n2, n3, n4, n5, n6, n7, n8], mat)
                eid += 1
    bottom_ids = []
    top_ids = []
    for nid, node in m.nodes.items():
        if abs(node.z) < 1e-12:
            bottom_ids.append(nid)
        if abs(node.z - L) < 1e-12:
            top_ids.append(nid)
    return m, bottom_ids, top_ids


def build_cantilever_tet4(L: float, b: float, h: float, nx: int, ny: int, nz: int, mat):
    """Trave a sbalzo di dimensioni L x b x h, con nx*ny*nz celle esaedriche,
    ciascuna divisa in 6 Tet4.

    Ritorna (model, fixed_node_ids, tip_node_ids).
    """
    from volumfeapy import Model
    m = Model()
    nid = 1
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                m.add_node(nid, i * L / nx, j * b / ny, k * h / nz)
                nid += 1

    eid = 1
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n_base = k * (nx + 1) * (ny + 1) + j * (nx + 1) + i + 1
                n1 = n_base
                n2 = n_base + 1
                n3 = n_base + (nx + 1) + 1
                n4 = n_base + (nx + 1)
                n5 = n1 + (nx + 1) * (ny + 1)
                n6 = n2 + (nx + 1) * (ny + 1)
                n7 = n3 + (nx + 1) * (ny + 1)
                n8 = n4 + (nx + 1) * (ny + 1)
                m.add_tet4(eid, [n1, n2, n4, n5], mat); eid += 1
                m.add_tet4(eid, [n2, n3, n4, n7], mat); eid += 1
                m.add_tet4(eid, [n2, n5, n6, n7], mat); eid += 1
                m.add_tet4(eid, [n4, n5, n7, n8], mat); eid += 1
                m.add_tet4(eid, [n2, n4, n5, n7], mat); eid += 1
                m.add_tet4(eid, [n2, n4, n7, n6], mat); eid += 1

    fixed = []
    for k in range(nz + 1):
        for j in range(ny + 1):
            nid = k * (nx + 1) * (ny + 1) + j * (nx + 1) + 1
            fixed.append(nid)

    tip = []
    for k in range(nz + 1):
        for j in range(ny + 1):
            nid = k * (nx + 1) * (ny + 1) + j * (nx + 1) + nx + 1
            tip.append(nid)
    return m, fixed, tip


def euler_bernoulli_tip_deflection(P: float, L: float, E: float, I: float) -> float:
    """Freccia in punta di trave a sbalzo caricata in punta con forza P.

    delta = P L^3 / (3 E I)
    """
    return abs(P) * L ** 3 / (3.0 * E * I)


def euler_bernoulli_tip_deflection_distributed(q: float, L: float, E: float, I: float) -> float:
    """Freccia in punta di trave a sbalzo con carico distribuito q.

    delta = q L^4 / (8 E I)
    """
    return abs(q) * L ** 4 / (8.0 * E * I)


def lame_radial_stress(r: float, a: float, b: float, p_i: float, p_o: float = 0.0) -> float:
    """Soluzione di Lamé: sigma_radiale in un cilindro spesso in pressione interna.

    a = raggio interno, b = raggio esterno, p_i = pressione interna, p_o = pressione esterna.
    """
    return (a ** 2 * p_i - b ** 2 * p_o - (p_i - p_o) * a ** 2 * b ** 2 / r ** 2) / (b ** 2 - a ** 2)


def lame_hoop_stress(r: float, a: float, b: float, p_i: float, p_o: float = 0.0) -> float:
    """Soluzione di Lamé: sigma_circonferenziale in un cilindro spesso in pressione interna."""
    return (a ** 2 * p_i - b ** 2 * p_o + (p_i - p_o) * a ** 2 * b ** 2 / r ** 2) / (b ** 2 - a ** 2)


def lame_radial_displacement(r: float, a: float, b: float, p_i: float, p_o: float, E: float, nu: float) -> float:
    """Soluzione di Lamé: spostamento radiale u(r).

    u = (1/E) * [ (1-nu^2)/((b^2-a^2)*(1+nu)*(...)) ... ]

    Forma chiusa (Timoshenko, Theory of Elasticity, §124):
        u(r) = (1/E) * [(1-nu)/(b^2-a^2)] * [a^2 p_i - b^2 p_o] * r
                  + (1/E) * [(1+nu)/(b^2-a^2)] * [a^2 b^2 (p_i - p_o) / r]
    """
    A = (1.0 - nu) / (b ** 2 - a ** 2)
    B = (1.0 + nu) / (b ** 2 - a ** 2)
    return (1.0 / E) * (A * (a ** 2 * p_i - b ** 2 * p_o) * r
                        + B * a ** 2 * b ** 2 * (p_i - p_o) / r)


def kirsch_stress_concentration(plate_width: float, hole_radius: float, sigma_0: float) -> float:
    """Fattore di concentrazione di tensioni per piastra di larghezza finita
    con foro centrale in trazione (Howland, 1929):

    K_t = 2 + (1 - rho)^3  dove rho = a/(W/2) = 2a/W.

    In alternativa per piastra larga (W >> a), K_t = 3 (soluzione di Kirsch).
    """
    rho = 2.0 * hole_radius / plate_width
    if rho < 1e-6:
        return 3.0
    return 2.0 + (1.0 - rho) ** 3


def saint_venant_torsion_polar_moment(radius: float) -> float:
    """Momento di inerzia polare per sezione circolare piena."""
    return np.pi * radius ** 4 / 2.0


def print_check(label: str, fem, exact, tol: float = 0.10) -> None:
    """Stampa un confronto fem vs esatto."""
    if exact is None or exact == 0:
        print(f"  {label:<30s} FEM = {fem:.6e}")
        return
    err = abs(fem - exact) / abs(exact) * 100.0
    flag = "OK " if err < tol * 100 else "WARN"
    print(f"  [{flag}] {label:<30s} FEM = {fem:.6e}  esatto = {exact:.6e}  err = {err:6.2f}%")


def header(title: str, char: str = "=") -> None:
    line = char * 72
    print(line)
    print(f"  {title}")
    print(line)
