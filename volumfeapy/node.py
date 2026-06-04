"""Nodo del modello volumetrico."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Node:
    """Nodo a 3 gradi di liberta' (ux, uy, uz)."""

    id: int
    x: float
    y: float
    z: float

    @property
    def coords(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)
