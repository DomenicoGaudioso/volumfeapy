"""Quadratura di Gauss-Legendre per elementi 3D."""

from __future__ import annotations

import numpy as np


def gauss_legendre_3d(nx: int, ny: int, nz: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Punti e pesi di Gauss-Legendre 3D su [-1,1]^3.

    Restituisce (xi, eta, zeta, w).
    """
    xi_i, wi = np.polynomial.legendre.leggauss(nx)
    eta_j, wj = np.polynomial.legendre.leggauss(ny)
    zeta_k, wk = np.polynomial.legendre.leggauss(nz)

    pts = []
    wts = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                pts.append((xi_i[i], eta_j[j], zeta_k[k]))
                wts.append(wi[i] * wj[j] * wk[k])

    pts = np.array(pts)
    return pts[:, 0], pts[:, 1], pts[:, 2], np.array(wts)


def gauss_tet4() -> tuple[np.ndarray, np.ndarray]:
    """Punto di Gauss singolo per tetraedro lineare.

    Restituisce (L, w) dove L = [L1, L2, L3, L4] coordinate baricentriche.
    """
    L = np.array([[0.25, 0.25, 0.25, 0.25]])
    w = np.array([1.0 / 6.0])
    return L, w


def gauss_tet4_4pt() -> tuple[np.ndarray, np.ndarray]:
    """4 punti di Gauss per tetraedro (integrazione di ordine 2).

    Coordinate baricentriche e pesi.
    """
    a = (5.0 - np.sqrt(5.0)) / 20.0
    b = (5.0 + 3.0 * np.sqrt(5.0)) / 20.0
    L = np.array([
        [a, a, a, b],
        [a, a, b, a],
        [a, b, a, a],
        [b, a, a, a],
    ])
    w = np.array([1.0 / 24.0, 1.0 / 24.0, 1.0 / 24.0, 1.0 / 24.0])
    return L, w


def gauss_wedge(n_tri: int = 3, n_z: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Punti e pesi per elemento cuneo (wedge/prisma).

    Integrazione nel triangolo (coordinate areali) x Gauss in zeta.
    """
    tri_pts = np.array([
        [1.0 / 6.0, 1.0 / 6.0, 2.0 / 3.0],
        [1.0 / 6.0, 2.0 / 3.0, 1.0 / 6.0],
        [2.0 / 3.0, 1.0 / 6.0, 1.0 / 6.0],
    ])
    tri_wts = np.array([1.0 / 6.0, 1.0 / 6.0, 1.0 / 6.0])

    zeta_g, w_z = np.polynomial.legendre.leggauss(n_z)

    pts = []
    wts = []
    for i in range(len(tri_pts)):
        for k in range(n_z):
            pts.append((tri_pts[i, 0], tri_pts[i, 1], zeta_g[k]))
            wts.append(tri_wts[i] * w_z[k])

    pts = np.array(pts)
    return pts[:, 0], pts[:, 1], pts[:, 2], np.array(wts)
