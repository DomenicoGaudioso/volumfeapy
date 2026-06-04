"""Post-processing per elementi volumetrici: tensioni, deformazioni, von Mises."""

from __future__ import annotations

import numpy as np


def element_stresses(result, elem_id: int) -> dict[str, np.ndarray]:
    """Tensioni al centro dell'elemento (punto medio nel dominio naturale).

    Restituisce dict con: sxx, syy, szz, txy, tyz, txz, von_mises.
    """
    model = result.model
    el = model.elements[elem_id]
    ed = el.global_dofs(model.dof_map)
    u_elem = result.U[ed]

    from .element import Hex8, Tet4, Tet10, Wedge6, Pyramid5
    if isinstance(el, Hex8):
        sigma = el.stress_at(0.0, 0.0, 0.0, u_elem)
    elif isinstance(el, Tet4):
        sigma = el.stress_at(None, None, None, u_elem)
    elif isinstance(el, Tet10):
        sigma = el.stress_at(0.25, 0.25, 0.25, 0.25, u_elem)
    elif isinstance(el, Wedge6):
        sigma = el.stress_at(1 / 3, 1 / 3, 1 / 3, 0.0, u_elem)
    elif isinstance(el, Pyramid5):
        sigma = el.stress_at(0.0, 0.0, 0.0, u_elem)
    else:
        sigma = np.zeros(6)

    vm = von_mises(sigma)
    return {
        "sxx": sigma[0], "syy": sigma[1], "szz": sigma[2],
        "txy": sigma[3], "tyz": sigma[4], "txz": sigma[5],
        "von_mises": vm,
    }


def von_mises(sigma: np.ndarray) -> float:
    """Tensione equivalente di von Mises.

    sigma = [sxx, syy, szz, txy, tyz, txz]
    """
    sxx, syy, szz, txy, tyz, txz = sigma
    vm = np.sqrt(0.5 * ((sxx - syy)**2 + (syy - szz)**2 + (szz - sxx)**2 +
                         6 * (txy**2 + tyz**2 + txz**2)))
    return float(vm)


def principal_stresses(sigma: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Tensioni principali e direzioni.

    Restituisce (valori, vettori) ordinati per valore decrescente.
    """
    sxx, syy, szz, txy, tyz, txz = sigma
    S = np.array([
        [sxx, txy, txz],
        [txy, syy, tyz],
        [txz, tyz, szz],
    ])
    vals, vecs = np.linalg.eigh(S)
    idx = np.argsort(vals)[::-1]
    return vals[idx], vecs[:, idx]


def element_displacements(result, elem_id: int) -> np.ndarray:
    """Spostamenti nodali dell'elemento."""
    model = result.model
    el = model.elements[elem_id]
    ed = el.global_dofs(model.dof_map)
    return result.U[ed]


def all_stresses(result) -> dict[int, dict]:
    """Tensioni al centro di tutti gli elementi."""
    stresses = {}
    for eid in result.model.elements:
        stresses[eid] = element_stresses(result, eid)
    return stresses


def max_von_mises(result) -> tuple[int, float]:
    """Elemento con la massima tensione di von Mises."""
    max_vm = -1.0
    max_eid = -1
    for eid in result.model.elements:
        s = element_stresses(result, eid)
        if s["von_mises"] > max_vm:
            max_vm = s["von_mises"]
            max_eid = eid
    return max_eid, max_vm
