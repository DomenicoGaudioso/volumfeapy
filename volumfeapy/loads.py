"""Carichi per elementi volumetrici: forze di volume, nodali, termici, pressione."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DOF_NAMES = ["ux", "uy", "uz"]
DOF_INDEX = {name: i for i, name in enumerate(DOF_NAMES)}


@dataclass
class NodalLoad:
    """Forza concentrata applicata a un nodo (sistema globale)."""

    node: int
    Fx: float = 0.0
    Fy: float = 0.0
    Fz: float = 0.0

    def vector(self) -> np.ndarray:
        return np.array([self.Fx, self.Fy, self.Fz], float)


@dataclass
class BodyForce:
    """Forza di volume uniforme (gravita', accelerazione, ecc.).

    Parametri
    ---------
    elem : int
        Id dell'elemento.
    bx, by, bz : float
        Componenti della forza di volume [N/m^3].
    """

    elem: int
    bx: float = 0.0
    by: float = 0.0
    bz: float = 0.0


@dataclass
class GravityLoad:
    """Carico gravitazionale automatico (rho * g).

    Parametri
    ---------
    g : float
        Accelerazione di gravita' (default 9.81 m/s^2).
    direction : str
        Direzione della gravita': 'x', 'y', o 'z' (default 'z').
    """

    g: float = 9.81
    direction: str = "z"


@dataclass
class ThermalLoad:
    """Carico termico uniforme su un elemento.

    Parametri
    ---------
    elem : int
        Id dell'elemento.
    dT : float
        Variazione di temperatura uniforme.
    """

    elem: int
    dT: float


@dataclass
class FacePressure:
    """Pressione su una faccia di un elemento.

    Parametri
    ---------
    elem : int
        Id dell'elemento.
    face : int
        Indice della faccia (dipende dal tipo di elemento).
    p : float
        Pressione (positiva verso l'interno, normale entrante).
    """

    elem: int
    face: int
    p: float


@dataclass
class Settlement:
    """Cedimento nodale: spostamento imposto a un grado di liberta'.

    Parametri
    ---------
    node : int
        Id del nodo.
    dof : str
        Uno tra 'ux', 'uy', 'uz'.
    value : float
        Valore imposto.
    """

    node: int
    dof: str
    value: float

    def __post_init__(self) -> None:
        self.dof = self.dof.lower()
        if self.dof not in DOF_INDEX:
            raise ValueError(f"dof non valido: {self.dof}")

    @property
    def local_index(self) -> int:
        return DOF_INDEX[self.dof]
