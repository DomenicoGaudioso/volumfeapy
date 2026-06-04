"""Materiale elastico isotropo 3D."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Material:
    """Materiale elastico lineare isotropo 3D.

    Parametri
    ---------
    E : float
        Modulo di Young.
    nu : float
        Coefficiente di Poisson.
    alpha : float
        Coefficiente di dilatazione termica lineare (1/grado). Default 0.
    G : float, opzionale
        Modulo di taglio. Se non fornito: G = E / (2 (1 + nu)).
    rho : float
        Densita' di massa.
    name : str
        Etichetta opzionale.
    """

    E: float
    nu: float = 0.3
    alpha: float = 0.0
    G: float | None = None
    rho: float = 0.0
    name: str = ""

    def __post_init__(self) -> None:
        if self.G is None:
            self.G = self.E / (2.0 * (1.0 + self.nu))

    def D_matrix(self) -> np.ndarray:
        """Matrice costitutiva 6x6 (Voigt: [sxx, syy, szz, txy, tyz, txz])."""
        E = self.E
        nu = self.nu
        c = E / ((1.0 + nu) * (1.0 - 2.0 * nu))
        D = c * np.array([
            [1 - nu, nu, nu, 0, 0, 0],
            [nu, 1 - nu, nu, 0, 0, 0],
            [nu, nu, 1 - nu, 0, 0, 0],
            [0, 0, 0, (1 - 2 * nu) / 2, 0, 0],
            [0, 0, 0, 0, (1 - 2 * nu) / 2, 0],
            [0, 0, 0, 0, 0, (1 - 2 * nu) / 2],
        ])
        return D
