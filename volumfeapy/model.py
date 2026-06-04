"""Modello strutturale per elementi volumetrici 3D."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .element import Hex8, Tet4, Tet10, Wedge6, Pyramid5
from .loads import (
    DOF_INDEX,
    DOF_NAMES,
    NodalLoad,
    BodyForce,
    GravityLoad,
    ThermalLoad,
    FacePressure,
    Settlement,
)
from .material import Material
from .node import Node

ElementType = Hex8 | Tet4 | Tet10 | Wedge6 | Pyramid5


@dataclass
class Result:
    """Risultati dell'analisi."""

    model: "Model"
    U: np.ndarray
    R: np.ndarray
    element_forces: dict[int, np.ndarray]
    cases: object = None

    def displacements(self, node: int) -> np.ndarray:
        return self.U[self.model.dof_map[node]]

    def reactions(self, node: int) -> np.ndarray:
        return self.R[self.model.dof_map[node]]

    def displacement(self, node: int, dof: str) -> float:
        return float(self.U[self.model.dof_map[node][DOF_INDEX[dof.lower()]]])


@dataclass
class ModalResult:
    """Risultati dell'analisi modale."""

    model: "Model"
    omega: np.ndarray
    freq: np.ndarray
    period: np.ndarray
    phi: np.ndarray

    def mode(self, i: int) -> np.ndarray:
        return self.phi[:, i]

    def mode_shape(self, i: int, node: int) -> np.ndarray:
        return self.phi[self.model.dof_map[node], i]


class Model:
    """Modello FEM di elementi volumetrici 3D."""

    def __init__(self) -> None:
        self.nodes: dict[int, Node] = {}
        self.elements: dict[int, ElementType] = {}
        self.nodal_loads: list[NodalLoad] = []
        self.body_forces: list[BodyForce] = []
        self.gravity_loads: list[GravityLoad] = []
        self.thermal_loads: list[ThermalLoad] = []
        self.face_pressures: list[FacePressure] = []
        self.settlements: list[Settlement] = []
        self._prescribed: dict[int, float] = {}
        self._dof_map: dict[int, np.ndarray] | None = None

    def add_node(self, id: int, x: float, y: float, z: float) -> Node:
        if id in self.nodes:
            raise ValueError(f"Nodo {id} gia' presente.")
        node = Node(id, x, y, z)
        self.nodes[id] = node
        self._dof_map = None
        return node

    def add_hex8(self, id: int, node_ids: list[int], material: Material) -> Hex8:
        if id in self.elements:
            raise ValueError(f"Elemento {id} gia' presente.")
        nodes = [self.nodes[nid] for nid in node_ids]
        el = Hex8(id, nodes, material)
        self.elements[id] = el
        return el

    def add_tet4(self, id: int, node_ids: list[int], material: Material) -> Tet4:
        if id in self.elements:
            raise ValueError(f"Elemento {id} gia' presente.")
        nodes = [self.nodes[nid] for nid in node_ids]
        el = Tet4(id, nodes, material)
        self.elements[id] = el
        return el

    def add_tet10(self, id: int, node_ids: list[int], material: Material) -> Tet10:
        if id in self.elements:
            raise ValueError(f"Elemento {id} gia' presente.")
        nodes = [self.nodes[nid] for nid in node_ids]
        el = Tet10(id, nodes, material)
        self.elements[id] = el
        return el

    def add_wedge6(self, id: int, node_ids: list[int], material: Material) -> Wedge6:
        if id in self.elements:
            raise ValueError(f"Elemento {id} gia' presente.")
        nodes = [self.nodes[nid] for nid in node_ids]
        el = Wedge6(id, nodes, material)
        self.elements[id] = el
        return el

    def add_pyramid5(self, id: int, node_ids: list[int], material: Material) -> Pyramid5:
        if id in self.elements:
            raise ValueError(f"Elemento {id} gia' presente.")
        nodes = [self.nodes[nid] for nid in node_ids]
        el = Pyramid5(id, nodes, material)
        self.elements[id] = el
        return el

    @property
    def dof_map(self) -> dict[int, np.ndarray]:
        if self._dof_map is None:
            self._dof_map = {}
            for i, nid in enumerate(sorted(self.nodes)):
                self._dof_map[nid] = np.arange(3 * i, 3 * i + 3)
        return self._dof_map

    @property
    def ndof(self) -> int:
        return 3 * len(self.nodes)

    def fix(self, node: int, dofs: list[str] | None = None) -> None:
        names = DOF_NAMES if dofs is None else [d.lower() for d in dofs]
        for name in names:
            gi = self.dof_map[node][DOF_INDEX[name]]
            self._prescribed[gi] = 0.0

    def pin(self, node: int) -> None:
        self.fix(node)

    def support(self, node: int, **dofs: bool) -> None:
        active = [name for name, on in dofs.items() if on]
        self.fix(node, active)

    def add_nodal_load(self, node: int, case: str = "default", **comps: float) -> NodalLoad:
        load = NodalLoad(node, **comps)
        load.case = case
        self.nodal_loads.append(load)
        return load

    def add_body_force(self, elem: int, bx: float = 0.0, by: float = 0.0,
                       bz: float = 0.0, case: str = "default") -> BodyForce:
        load = BodyForce(elem, bx, by, bz)
        load.case = case
        self.body_forces.append(load)
        return load

    def add_gravity(self, g: float = 9.81, direction: str = "z",
                    case: str = "default") -> GravityLoad:
        load = GravityLoad(g, direction)
        load.case = case
        self.gravity_loads.append(load)
        return load

    def add_thermal_load(self, elem: int, dT: float, case: str = "default") -> ThermalLoad:
        load = ThermalLoad(elem, dT)
        load.case = case
        self.thermal_loads.append(load)
        return load

    def add_face_pressure(self, elem: int, face: int, p: float,
                          case: str = "default") -> FacePressure:
        load = FacePressure(elem, face, p)
        load.case = case
        self.face_pressures.append(load)
        return load

    def add_settlement(self, node: int, dof: str, value: float) -> Settlement:
        s = Settlement(node, dof, value)
        self.settlements.append(s)
        gi = self.dof_map[node][s.local_index]
        self._prescribed[gi] = value
        return s

    def load_cases(self) -> list[str]:
        cases = set()
        for grp in (self.nodal_loads, self.body_forces, self.gravity_loads,
                    self.thermal_loads, self.face_pressures):
            for ld in grp:
                cases.add(getattr(ld, "case", "default"))
        return sorted(cases)

    @staticmethod
    def _norm_cases(cases):
        if cases is None:
            return None
        if isinstance(cases, str):
            return {cases: 1.0}
        if isinstance(cases, dict):
            return {str(k): float(v) for k, v in cases.items()}
        return {str(c): 1.0 for c in cases}

    @staticmethod
    def _factor(load, factors) -> float:
        if factors is None:
            return 1.0
        return factors.get(getattr(load, "case", "default"), 0.0)

    def assemble_stiffness(self) -> np.ndarray:
        ndof = self.ndof
        K = np.zeros((ndof, ndof))
        for el in self.elements.values():
            ke = el.stiffness_local()
            ed = el.global_dofs(self.dof_map)
            K[np.ix_(ed, ed)] += ke
        return K

    def assemble_loads(self, cases=None) -> np.ndarray:
        factors = self._norm_cases(cases)
        ndof = self.ndof
        F = np.zeros(ndof)

        for nl in self.nodal_loads:
            fac = self._factor(nl, factors)
            if fac:
                F[self.dof_map[nl.node]] += fac * nl.vector()

        for bf in self.body_forces:
            fac = self._factor(bf, factors)
            if fac:
                el = self.elements[bf.elem]
                feq = el.equivalent_body_force(bf.bx, bf.by, bf.bz)
                F[el.global_dofs(self.dof_map)] += fac * feq

        for gl in self.gravity_loads:
            fac = self._factor(gl, factors)
            if fac:
                d = gl.direction.lower()
                for el in self.elements.values():
                    rho = el.material.rho
                    bx = -rho * gl.g if d == "x" else 0.0
                    by = -rho * gl.g if d == "y" else 0.0
                    bz = -rho * gl.g if d == "z" else 0.0
                    feq = el.equivalent_body_force(bx, by, bz)
                    F[el.global_dofs(self.dof_map)] += fac * feq

        for tl in self.thermal_loads:
            fac = self._factor(tl, factors)
            if fac:
                el = self.elements[tl.elem]
                alpha = el.material.alpha
                E = el.material.E
                nu = el.material.nu
                beta = E * alpha / (1 - 2 * nu)
                eps_th = np.array([beta * tl.dT, beta * tl.dT, beta * tl.dT, 0, 0, 0])
                D = el.material.D_matrix()
                if isinstance(el, Tet4):
                    B, vol6 = el._B_matrix()
                    feq = (vol6 / 6.0) * (B.T @ D @ np.linalg.solve(D, eps_th))
                else:
                    feq = np.zeros(el.n_dof)
                F[el.global_dofs(self.dof_map)] += fac * feq

        return F

    def solve(self, sparse: bool = False, cases=None) -> Result:
        factors = self._norm_cases(cases)
        ndof = self.ndof

        F = self.assemble_loads(factors)
        prescribed = self._prescribed
        p_idx = np.array(sorted(prescribed), dtype=int)
        if p_idx.size == 0:
            raise ValueError("Nessun vincolo: struttura labile.")
        free_mask = np.ones(ndof, dtype=bool)
        free_mask[p_idx] = False
        f_idx = np.flatnonzero(free_mask)

        U = np.zeros(ndof)
        U[p_idx] = [prescribed[i] for i in p_idx]

        K = self.assemble_stiffness()

        if sparse:
            from scipy.sparse.linalg import spsolve
            from scipy import sparse as sp
            Ksp = sp.csr_matrix(K)
            Kff = Ksp[f_idx][:, f_idx]
            Kfp = Ksp[f_idx][:, p_idx]
            rhs = F[f_idx] - Kfp @ U[p_idx]
            U[f_idx] = spsolve(Kff.tocsc(), rhs)
        else:
            Kff = K[np.ix_(f_idx, f_idx)]
            Kfp = K[np.ix_(f_idx, p_idx)]
            rhs = F[f_idx] - Kfp @ U[p_idx]
            U[f_idx] = np.linalg.solve(Kff, rhs)

        R = K @ U - F
        R[f_idx] = 0.0

        element_forces: dict[int, np.ndarray] = {}
        for el in self.elements.values():
            ed = el.global_dofs(self.dof_map)
            u_elem = U[ed]
            ke = el.stiffness_local()
            element_forces[el.id] = ke @ u_elem

        return Result(self, U, R, element_forces, cases=factors)

    def assemble_mass(self) -> np.ndarray:
        """Matrice di massa concentrata (lumped)."""
        ndof = self.ndof
        M = np.zeros(ndof)
        for el in self.elements.values():
            rho = el.material.rho
            V = el.volume()
            mass = rho * V / el.n_nodes
            for n in el.nodes:
                di = self.dof_map[n.id]
                for d in range(3):
                    M[di[d]] += mass
        return M

    def modal(self, n_modes: int = 10) -> ModalResult:
        from scipy.linalg import eigh

        K = self.assemble_stiffness()
        Mdiag = self.assemble_mass()
        ndof = self.ndof
        prescribed = self._prescribed
        free = np.array([i for i in range(ndof) if i not in prescribed], dtype=int)
        if free.size == 0:
            raise ValueError("Nessun GdL libero.")

        Kff = K[np.ix_(free, free)]
        Mff = Mdiag[free]
        massive = Mff > 1e-300
        if not np.any(massive):
            raise ValueError("Massa nulla: impostare rho nel materiale.")

        m = np.flatnonzero(massive)
        s = np.flatnonzero(~massive)
        Kmm = Kff[np.ix_(m, m)]
        if s.size:
            Kms = Kff[np.ix_(m, s)]
            Kss = Kff[np.ix_(s, s)]
            Ksm = Kff[np.ix_(s, m)]
            Kss_inv_Ksm = np.linalg.solve(Kss, Ksm)
            Kstar = Kmm - Kms @ Kss_inv_Ksm
        else:
            Kss_inv_Ksm = None
            Kstar = Kmm

        Mm = Mff[m]
        D = 1.0 / np.sqrt(Mm)
        A = (D[:, None] * Kstar) * D[None, :]
        A = 0.5 * (A + A.T)
        w2, psi = eigh(A)
        w2 = np.clip(w2, 0.0, None)
        keep = min(n_modes, len(w2))
        w2 = w2[:keep]
        psi = psi[:, :keep]

        omega = np.sqrt(w2)
        freq = omega / (2.0 * np.pi)
        with np.errstate(divide="ignore"):
            period = np.where(freq > 0, 1.0 / freq, np.inf)

        phi_m = D[:, None] * psi
        phi = np.zeros((ndof, keep))
        phi[free[m], :] = phi_m
        if s.size:
            phi[free[s], :] = -(Kss_inv_Ksm @ phi_m)

        return ModalResult(self, omega, freq, period, phi)
