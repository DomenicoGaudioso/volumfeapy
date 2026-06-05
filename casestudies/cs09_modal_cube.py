"""Caso studio CS09 volumfeapy: Analisi modale di un cubo Hex8.

Caso classico FEM. Cubo [0,L]^3 libero (o incastrato su una faccia) con
analisi modale per estrarre le frequenze naturali e i modi di vibrare.

Per un cubo libero, le frequenze naturali dipendono dal modulo di Young
E, dalla densita' rho, dal coefficiente di Poisson nu e dalle
dimensioni. La soluzione esatta per un cubo isotropo libero e' nota
in forma di serie triple (Morse & Ingard, "Theoretical Acoustics"),
ma e' complicata.

Caso semplificato: cubo Hex8 di lato L = 0.1 m, acciaio
(E = 210 GPa, nu = 0.3, rho = 7850 kg/m^3), incastrato sulla faccia
inferiore (z = 0). Si calcolano le prime 6 frequenze modali e si
confrontano qualitativamente con i risultati di letteratura.

Per un cubo incastrato su una faccia, la frequenza fondamentale
approssimata (primo modo flessionale) si puo' stimare come:

    f_1 ≈ (1.875)^2 / (2 pi) * sqrt(E I / (rho A L^4))   (trave incastrata)

ma questa formula approssima solo il primo modo in una direzione.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from volumfeapy import Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_mode

from common import build_cube_hex8, save_figure, header


def main() -> None:
    L = 0.1
    n = 4
    E, nu = 210e9, 0.3
    rho = 7850.0
    mat = Material(E=E, nu=nu, rho=rho)

    header("CS09 - Analisi modale cubo Hex8 incastrato")
    print(f"  L = {L} m, E = {E:.2e} Pa, nu = {nu}, rho = {rho} kg/m^3")
    print(f"  Cubo incastrato sulla faccia inferiore (z = 0)")
    print()

    m, bottom_ids, top_ids = build_cube_hex8(L, n, mat)
    for nid in bottom_ids:
        m.fix(nid)

    n_modes = 6
    modal = m.modal(n_modes=n_modes)

    print(f"  {'modo':>4s}  {'f FEM [Hz]':>12s}  {'T [s]':>10s}  {'omega [rad/s]':>14s}")
    print("  " + "-" * 50)
    for i in range(n_modes):
        f = modal.freq[i]
        T = modal.period[i] if modal.period[i] < 1e6 else float("inf")
        omega = modal.omega[i]
        print(f"  {i+1:>4d}  {f:12.3f}  {T:10.4e}  {omega:14.3f}")

    print()

    I = L ** 4 / 12.0
    A = L ** 2
    f_1_beam = 1.875 ** 2 / (2 * np.pi) * np.sqrt(E * I / (rho * A * L ** 4))
    print(f"  Stima trave incastrata f_1 ~ {f_1_beam:.1f} Hz")
    print(f"  (per cubo 3D, le frequenze dei modi flessionali sono piu' alte)")
    print()

    save_figure(plot_mesh(m, show_node_ids=False), f"cs09_mesh_{n}.png",
                title=f"Mesh cubo Hex8 {n}^3 per analisi modale")

    for i in range(n_modes):
        save_figure(plot_mode(modal, i=i, scale=2000), f"cs09_mode_{i+1}.png",
                    title=f"Modo {i+1} - f = {modal.freq[i]:.1f} Hz")
    print(f"  Immagini salvate in casestudies/images/")


if __name__ == "__main__":
    main()
