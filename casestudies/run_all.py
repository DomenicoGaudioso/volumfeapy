"""Esegue tutti i casi studio volumfeapy in un unico processo Python."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main():
    print("=" * 78)
    print("  ESECUZIONE DI TUTTI I CASI STUDIO volumfeapy")
    print("=" * 78)
    print()
    total_t0 = time.time()

    cases = [
        ("CS01 - Cubo trazione uniassiale",    "cs01_cube_uniaxial"),
        ("CS02 - Mensola 3D Tet4",            "cs02_cantilever_3d"),
        ("CS03 - Cubo pressione idrostatica", "cs03_hydrostatic_cube"),
        ("CS04 - Lastra con foro (Kirsch)",   "cs04_kirsch_plate"),
        ("CS05 - Cubo con peso proprio",      "cs05_body_force"),
        ("CS06 - Cubo con thermal load",      "cs06_thermal"),
        ("CS07 - Patch test",                 "cs07_patch_test"),
        ("CS08 - Convergenza elementi",       "cs08_element_convergence"),
        ("CS09 - Analisi modale cubo",        "cs09_modal_cube"),
        ("CS10 - Elemento Pyramid5",          "cs10_pyramid_element"),
        ("CS11 - Mesh mista 3D",              "cs11_mixed_elements"),
    ]

    for label, module_name in cases:
        print()
        print("#" * 78)
        print(f"#  {label}  --  {module_name}")
        print("#" * 78)
        t0 = time.time()
        try:
            mod = __import__(module_name)
            mod.main()
        except Exception as exc:
            print(f"  !!! ERRORE in {module_name}: {exc!r}")
            import traceback
            traceback.print_exc()
        dt = time.time() - t0
        print(f"\n  >>> {label} completato in {dt:.1f} s")
        sys.stdout.flush()

    total_dt = time.time() - total_t0
    print()
    print("=" * 78)
    print(f"  TUTTI I CASI COMPLETATI in {total_dt:.1f} s")
    print(f"  Immagini salvate in: {ROOT / 'images'}")
    print("=" * 78)


if __name__ == "__main__":
    main()
