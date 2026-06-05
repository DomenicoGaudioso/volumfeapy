"""Elementi volumetrici 3D: Hex8, Tet4, Tet10, Wedge6, Pyramid5.

Tutti gli elementi hanno 3 GdL per nodo (ux, uy, uz).
La matrice costitutiva D e' 6x6 (notazione di Voigt):
    [sxx, syy, szz, txy, tyz, txz]

La matrice B (6 x n_dof) mappa gli spostamenti nodali nelle deformazioni:
    eps = B @ u_elem
"""

from __future__ import annotations

import numpy as np

from .material import Material
from .node import Node


class Hex8:
    """Elemento esaedrico (brick) a 8 nodi, trilineare.

    24 GdL totali (3 per nodo). Integrazione 2x2x2.
    Nodi numerati secondo la convenzione standard:
        1---2       bottom face (zeta=-1): 1,2,3,4
       /|  /|       top face (zeta=+1): 5,6,7,8
      4---3 |
      | 5-|-6
      |/  |/
      8---7
    """

    n_dof = 24
    n_nodes = 8

    def __init__(self, id: int, nodes: list[Node], material: Material) -> None:
        if len(nodes) != 8:
            raise ValueError(f"Elemento {id}: servono 8 nodi per Hex8.")
        self.id = id
        self.nodes = nodes
        self.material = material

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords(self) -> np.ndarray:
        return np.array([[n.x, n.y, n.z] for n in self.nodes], dtype=float)

    @staticmethod
    def _shape_functions(xi: float, eta: float, zeta: float) -> np.ndarray:
        """Funzioni di forma trilineari N1..N8."""
        return 0.125 * np.array([
            (1 - xi) * (1 - eta) * (1 - zeta),
            (1 + xi) * (1 - eta) * (1 - zeta),
            (1 + xi) * (1 + eta) * (1 - zeta),
            (1 - xi) * (1 + eta) * (1 - zeta),
            (1 - xi) * (1 - eta) * (1 + zeta),
            (1 + xi) * (1 - eta) * (1 + zeta),
            (1 + xi) * (1 + eta) * (1 + zeta),
            (1 - xi) * (1 + eta) * (1 + zeta),
        ])

    @staticmethod
    def _shape_derivatives(xi: float, eta: float, zeta: float) -> np.ndarray:
        """Derivate dN/d(xi,eta,zeta): shape (3, 8)."""
        dNdxi = 0.125 * np.array([
            -(1 - eta) * (1 - zeta), (1 - eta) * (1 - zeta),
            (1 + eta) * (1 - zeta), -(1 + eta) * (1 - zeta),
            -(1 - eta) * (1 + zeta), (1 - eta) * (1 + zeta),
            (1 + eta) * (1 + zeta), -(1 + eta) * (1 + zeta),
        ])
        dNdeta = 0.125 * np.array([
            -(1 - xi) * (1 - zeta), -(1 + xi) * (1 - zeta),
            (1 + xi) * (1 - zeta), (1 - xi) * (1 - zeta),
            -(1 - xi) * (1 + zeta), -(1 + xi) * (1 + zeta),
            (1 + xi) * (1 + zeta), (1 - xi) * (1 + zeta),
        ])
        dNdzeta = 0.125 * np.array([
            -(1 - xi) * (1 - eta), -(1 + xi) * (1 - eta),
            -(1 + xi) * (1 + eta), -(1 - xi) * (1 + eta),
            (1 - xi) * (1 - eta), (1 + xi) * (1 - eta),
            (1 + xi) * (1 + eta), (1 - xi) * (1 + eta),
        ])
        return np.vstack([dNdxi, dNdeta, dNdzeta])

    def _B_matrix(self, xi: float, eta: float, zeta: float) -> tuple[np.ndarray, float]:
        """Matrice B (6x24) e determinante dello Jacobiano."""
        coords = self._coords()
        dNdxi_eta_zeta = self._shape_derivatives(xi, eta, zeta)
        J = dNdxi_eta_zeta @ coords
        detJ = float(np.linalg.det(J))
        if abs(detJ) < 1e-30:
            raise ValueError(f"Elemento {self.id}: Jacobiano singolare.")
        Jinv = np.linalg.inv(J)
        dNdxyz = Jinv @ dNdxi_eta_zeta

        B = np.zeros((6, 24))
        for i in range(8):
            c = 3 * i
            dNdx = dNdxyz[0, i]
            dNdy = dNdxyz[1, i]
            dNdz = dNdxyz[2, i]
            B[0, c] = dNdx
            B[1, c + 1] = dNdy
            B[2, c + 2] = dNdz
            B[3, c] = dNdy
            B[3, c + 1] = dNdx
            B[4, c + 1] = dNdz
            B[4, c + 2] = dNdy
            B[5, c] = dNdz
            B[5, c + 2] = dNdx
        return B, detJ

    def stiffness_local(self) -> np.ndarray:
        """Matrice di rigidezza 24x24 con integrazione 2x2x2."""
        from .integration import gauss_legendre_3d
        K = np.zeros((24, 24))
        D = self.material.D_matrix()
        xi_g, eta_g, zeta_g, w_g = gauss_legendre_3d(2, 2, 2)
        for xi, eta, zeta, w in zip(xi_g, eta_g, zeta_g, w_g):
            B, detJ = self._B_matrix(xi, eta, zeta)
            K += w * (B.T @ D @ B) * abs(detJ)
        return K

    def volume(self) -> float:
        from .integration import gauss_legendre_3d
        V = 0.0
        xi_g, eta_g, zeta_g, w_g = gauss_legendre_3d(2, 2, 2)
        for xi, eta, zeta, w in zip(xi_g, eta_g, zeta_g, w_g):
            _, detJ = self._B_matrix(xi, eta, zeta)
            V += w * abs(detJ)
        return V

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def equivalent_body_force(self, bx: float, by: float, bz: float) -> np.ndarray:
        """Forze nodali equivalenti per forze di volume (bx, by, bz)."""
        from .integration import gauss_legendre_3d
        f = np.zeros(24)
        b = np.array([bx, by, bz])
        xi_g, eta_g, zeta_g, w_g = gauss_legendre_3d(2, 2, 2)
        for xi, eta, zeta, w in zip(xi_g, eta_g, zeta_g, w_g):
            N = self._shape_functions(xi, eta, zeta)
            _, detJ = self._B_matrix(xi, eta, zeta)
            for i in range(8):
                f[3 * i:3 * i + 3] += w * N[i] * b * abs(detJ)
        return f

    def equivalent_thermal_load(self, dT: float) -> np.ndarray:
        """Forze nodali equivalenti per un incremento termico uniforme dT.

        f_th = integral_V B^T D eps_th dV  con  eps_th = alpha dT (1,1,1,0,0,0)^T
        """
        from .integration import gauss_legendre_3d
        alpha = self.material.alpha
        if alpha == 0.0:
            return np.zeros(24)
        D = self.material.D_matrix()
        eps_th = alpha * dT * np.array([1.0, 1.0, 1.0, 0.0, 0.0, 0.0])
        f = np.zeros(24)
        xi_g, eta_g, zeta_g, w_g = gauss_legendre_3d(2, 2, 2)
        for xi, eta, zeta, w in zip(xi_g, eta_g, zeta_g, w_g):
            B, detJ = self._B_matrix(xi, eta, zeta)
            f += w * (B.T @ D @ eps_th) * abs(detJ)
        return f

    def stress_at(self, xi: float, eta: float, zeta: float,
                  u_elem: np.ndarray) -> np.ndarray:
        """Tensioni [sxx, syy, szz, txy, tyz, txz] al punto (xi, eta, zeta)."""
        D = self.material.D_matrix()
        B, _ = self._B_matrix(xi, eta, zeta)
        return D @ B @ u_elem


class Tet4:
    """Elemento tetraedrico a 4 nodi, lineare.

    12 GdL totali (3 per nodo). Integrazione esatta con 1 punto.
    """

    n_dof = 12
    n_nodes = 4

    def __init__(self, id: int, nodes: list[Node], material: Material) -> None:
        if len(nodes) != 4:
            raise ValueError(f"Elemento {id}: servono 4 nodi per Tet4.")
        self.id = id
        self.nodes = nodes
        self.material = material

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords(self) -> np.ndarray:
        return np.array([[n.x, n.y, n.z] for n in self.nodes], dtype=float)

    def volume(self) -> float:
        """Volume del tetraedro: V = |det([x2-x1, x3-x1, x4-x1])| / 6."""
        c = self._coords()
        J = np.column_stack([c[1] - c[0], c[2] - c[0], c[3] - c[0]])
        return abs(float(np.linalg.det(J))) / 6.0

    def _B_matrix(self) -> tuple[np.ndarray, float]:
        """Matrice B (6x12) costante per Tet4 e volume 6V."""
        c = self._coords()
        J = np.column_stack([c[1] - c[0], c[2] - c[0], c[3] - c[0]])
        detJ = float(np.linalg.det(J))
        Jinv = np.linalg.inv(J)

        dNdL = np.array([
            [-1, -1, -1],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ], dtype=float)

        dNdxyz = dNdL @ Jinv

        B = np.zeros((6, 12))
        for i in range(4):
            col = 3 * i
            dNdx = dNdxyz[i, 0]
            dNdy = dNdxyz[i, 1]
            dNdz = dNdxyz[i, 2]
            B[0, col] = dNdx
            B[1, col + 1] = dNdy
            B[2, col + 2] = dNdz
            B[3, col] = dNdy
            B[3, col + 1] = dNdx
            B[4, col + 1] = dNdz
            B[4, col + 2] = dNdy
            B[5, col] = dNdz
            B[5, col + 2] = dNdx
        return B, abs(detJ)

    def stiffness_local(self) -> np.ndarray:
        """Matrice di rigidezza 12x12 (integrazione esatta, B costante)."""
        B, vol6 = self._B_matrix()
        D = self.material.D_matrix()
        return (vol6 / 6.0) * (B.T @ D @ B)

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def equivalent_body_force(self, bx: float, by: float, bz: float) -> np.ndarray:
        """Forze nodali equivalenti per forze di volume (ripartite equamente)."""
        V = self.volume()
        f = np.zeros(12)
        b = np.array([bx, by, bz])
        for i in range(4):
            f[3 * i:3 * i + 3] = b * V / 4.0
        return f

    def stress_at(self, xi, eta, zeta, u_elem: np.ndarray) -> np.ndarray:
        """Tensioni (costanti nel Tet4)."""
        D = self.material.D_matrix()
        B, _ = self._B_matrix()
        return D @ B @ u_elem


class Tet10:
    """Elemento tetraedrico a 10 nodi, quadratico.

    30 GdL totali (3 per nodo). Integrazione con 4 punti di Gauss.
    Nodi: 4 ai vertici + 6 ai punti medi degli spigoli.
    Ordinamento spigoli: (1-2), (2-3), (3-1), (1-4), (2-4), (3-4).
    """

    n_dof = 30
    n_nodes = 10

    def __init__(self, id: int, nodes: list[Node], material: Material) -> None:
        if len(nodes) != 10:
            raise ValueError(f"Elemento {id}: servono 10 nodi per Tet10.")
        self.id = id
        self.nodes = nodes
        self.material = material

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords(self) -> np.ndarray:
        return np.array([[n.x, n.y, n.z] for n in self.nodes], dtype=float)

    def volume(self) -> float:
        c = self._coords()
        J = np.column_stack([c[1] - c[0], c[2] - c[0], c[3] - c[0]])
        return abs(float(np.linalg.det(J))) / 6.0

    @staticmethod
    def _shape_functions(L1, L2, L3, L4) -> np.ndarray:
        """Funzioni di forma quadratiche in coordinate baricentriche."""
        N = np.array([
            L1 * (2 * L1 - 1),
            L2 * (2 * L2 - 1),
            L3 * (2 * L3 - 1),
            L4 * (2 * L4 - 1),
            4 * L1 * L2,
            4 * L2 * L3,
            4 * L3 * L1,
            4 * L1 * L4,
            4 * L2 * L4,
            4 * L3 * L4,
        ])
        return N

    @staticmethod
    def _shape_derivatives(L1, L2, L3, L4) -> np.ndarray:
        """Derivate dN/dL (10x4) in coordinate baricentriche."""
        dNdL = np.zeros((10, 4))
        L = [L1, L2, L3, L4]
        for i in range(4):
            for j in range(4):
                if i == j:
                    dNdL[i, j] = 4 * L[i] - 1
                else:
                    dNdL[i, j] = 0
        edge_pairs = [(0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3)]
        for k, (a, b) in enumerate(edge_pairs):
            for j in range(4):
                if j == a:
                    dNdL[4 + k, j] = 4 * L[b]
                elif j == b:
                    dNdL[4 + k, j] = 4 * L[a]
        return dNdL

    def _B_matrix(self, L1, L2, L3, L4) -> tuple[np.ndarray, float]:
        """Matrice B (6x30) e determinante Jacobiano."""
        c = self._coords()
        J = np.column_stack([c[1] - c[0], c[2] - c[0], c[3] - c[0]])
        detJ = float(np.linalg.det(J))
        Jinv = np.linalg.inv(J)

        dNdL = self._shape_derivatives(L1, L2, L3, L4)
        grad_l234 = Jinv
        grad_l1 = -np.sum(grad_l234, axis=0)
        grad_l = np.vstack([grad_l1, grad_l234])
        dNdxyz = dNdL @ grad_l

        B = np.zeros((6, 30))
        for i in range(10):
            col = 3 * i
            dNdx = dNdxyz[i, 0]
            dNdy = dNdxyz[i, 1]
            dNdz = dNdxyz[i, 2]
            B[0, col] = dNdx
            B[1, col + 1] = dNdy
            B[2, col + 2] = dNdz
            B[3, col] = dNdy
            B[3, col + 1] = dNdx
            B[4, col + 1] = dNdz
            B[4, col + 2] = dNdy
            B[5, col] = dNdz
            B[5, col + 2] = dNdx
        return B, abs(detJ)

    def stiffness_local(self) -> np.ndarray:
        """Matrice di rigidezza 30x30 con 4 punti di Gauss."""
        from .integration import gauss_tet4_4pt
        K = np.zeros((30, 30))
        D = self.material.D_matrix()
        L_gauss, w_gauss = gauss_tet4_4pt()
        for L, w in zip(L_gauss, w_gauss):
            B, detJ = self._B_matrix(L[0], L[1], L[2], L[3])
            K += w * (B.T @ D @ B) * detJ
        return K

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def equivalent_body_force(self, bx: float, by: float, bz: float) -> np.ndarray:
        """Forze nodali equivalenti per forze di volume."""
        from .integration import gauss_tet4_4pt
        f = np.zeros(30)
        b = np.array([bx, by, bz])
        L_gauss, w_gauss = gauss_tet4_4pt()
        for L, w in zip(L_gauss, w_gauss):
            N = self._shape_functions(L[0], L[1], L[2], L[3])
            _, detJ = self._B_matrix(L[0], L[1], L[2], L[3])
            for i in range(10):
                f[3 * i:3 * i + 3] += w * N[i] * b * detJ
        return f

    def stress_at(self, L1, L2, L3, L4, u_elem: np.ndarray) -> np.ndarray:
        D = self.material.D_matrix()
        B, _ = self._B_matrix(L1, L2, L3, L4)
        return D @ B @ u_elem


class Wedge6:
    """Elemento cuneo (wedge/prisma) a 6 nodi.

    18 GdL totali (3 per nodo). Base triangolare x estrusione lineare.
    Nodi: 1,2,3 bottom (zeta=-1); 4,5,6 top (zeta=+1).
    """

    n_dof = 18
    n_nodes = 6

    def __init__(self, id: int, nodes: list[Node], material: Material) -> None:
        if len(nodes) != 6:
            raise ValueError(f"Elemento {id}: servono 6 nodi per Wedge6.")
        self.id = id
        self.nodes = nodes
        self.material = material

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords(self) -> np.ndarray:
        return np.array([[n.x, n.y, n.z] for n in self.nodes], dtype=float)

    def volume(self) -> float:
        c = self._coords()
        A_tri = 0.5 * abs(float(np.linalg.det(
            np.column_stack([c[1, :2] - c[0, :2], c[2, :2] - c[0, :2]])
        )))
        h = float(np.mean(c[3:6, 2] - c[0:3, 2]))
        return A_tri * abs(h)

    @staticmethod
    def _shape_functions(L1, L2, L3, zeta) -> np.ndarray:
        """Funzioni di forma: lineari nel triangolo x lineari in zeta."""
        return np.array([
            L1 * (1 - zeta) / 2,
            L2 * (1 - zeta) / 2,
            L3 * (1 - zeta) / 2,
            L1 * (1 + zeta) / 2,
            L2 * (1 + zeta) / 2,
            L3 * (1 + zeta) / 2,
        ])

    def _B_matrix(self, L1, L2, L3, zeta) -> tuple[np.ndarray, float]:
        """Matrice B (6x18) e determinante Jacobiano."""
        c = self._coords()
        N = self._shape_functions(L1, L2, L3, zeta)

        dNdL = np.array([
            [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [1, 0, 0], [0, 1, 0], [0, 0, 1],
        ], dtype=float)

        dNdL[0:3, :] *= (1 - zeta) / 2
        dNdL[3:6, :] *= (1 + zeta) / 2

        dNdzeta = np.array([
            -L1 / 2, -L2 / 2, -L3 / 2,
            L1 / 2, L2 / 2, L3 / 2,
        ])

        dNdxi = np.zeros((3, 6))
        J_tri = np.column_stack([c[1] - c[0], c[2] - c[0]])
        if J_tri.shape == (3, 2):
            for i in range(6):
                dNdxi[:, i] = (dNdL[i, 1] - dNdL[i, 0]) * (c[1] - c[0]) + \
                              (dNdL[i, 2] - dNdL[i, 0]) * (c[2] - c[0])
                dNdxi[:, i] += dNdzeta[i] * (c[i % 3 + 3] - c[i % 3]) / 2

        J_full = np.zeros((3, 3))
        for i in range(6):
            J_full[:, 0] += dNdL[i, 1] * c[i] - dNdL[i, 0] * c[i]
            J_full[:, 1] += dNdL[i, 2] * c[i] - dNdL[i, 0] * c[i]
            J_full[:, 2] += dNdzeta[i] * c[i]

        detJ = float(np.linalg.det(J_full))
        if abs(detJ) < 1e-30:
            detJ = 1e-30
        Jinv = np.linalg.inv(J_full)

        dNdxyz = np.zeros((6, 3))
        for i in range(6):
            dNd_nat = np.array([
                dNdL[i, 1] - dNdL[i, 0],
                dNdL[i, 2] - dNdL[i, 0],
                dNdzeta[i],
            ])
            dNdxyz[i] = Jinv @ dNd_nat

        B = np.zeros((6, 18))
        for i in range(6):
            col = 3 * i
            dNdx = dNdxyz[i, 0]
            dNdy = dNdxyz[i, 1]
            dNdz = dNdxyz[i, 2]
            B[0, col] = dNdx
            B[1, col + 1] = dNdy
            B[2, col + 2] = dNdz
            B[3, col] = dNdy
            B[3, col + 1] = dNdx
            B[4, col + 1] = dNdz
            B[4, col + 2] = dNdy
            B[5, col] = dNdz
            B[5, col + 2] = dNdx
        return B, abs(detJ)

    def stiffness_local(self) -> np.ndarray:
        """Matrice di rigidezza 18x18."""
        from .integration import gauss_wedge
        K = np.zeros((18, 18))
        D = self.material.D_matrix()
        L1_g, L2_g, zeta_g, w_g = gauss_wedge(3, 2)
        for L1, L2, zeta, w in zip(L1_g, L2_g, zeta_g, w_g):
            L3 = 1.0 - L1 - L2
            B, detJ = self._B_matrix(L1, L2, L3, zeta)
            K += w * (B.T @ D @ B) * detJ
        return K

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def equivalent_body_force(self, bx: float, by: float, bz: float) -> np.ndarray:
        f = np.zeros(18)
        b = np.array([bx, by, bz])
        V = self.volume()
        for i in range(6):
            f[3 * i:3 * i + 3] = b * V / 6.0
        return f

    def stress_at(self, L1, L2, L3, zeta, u_elem: np.ndarray) -> np.ndarray:
        D = self.material.D_matrix()
        B, _ = self._B_matrix(L1, L2, L3, zeta)
        return D @ B @ u_elem


class Pyramid5:
    """Elemento piramidale a 5 nodi.

    15 GdL totali (3 per nodo). Base quadrilatera + apice.
    Nodi: 1,2,3,4 base (zeta=-1); 5 apice (zeta=+1).
    """

    n_dof = 15
    n_nodes = 5

    def __init__(self, id: int, nodes: list[Node], material: Material) -> None:
        if len(nodes) != 5:
            raise ValueError(f"Elemento {id}: servono 5 nodi per Pyramid5.")
        self.id = id
        self.nodes = nodes
        self.material = material

    @property
    def node_ids(self) -> list[int]:
        return [n.id for n in self.nodes]

    def _coords(self) -> np.ndarray:
        return np.array([[n.x, n.y, n.z] for n in self.nodes], dtype=float)

    def volume(self) -> float:
        c = self._coords()
        base_area = 0.5 * abs(float(np.linalg.det(
            np.column_stack([c[1, :2] - c[0, :2], c[3, :2] - c[0, :2]])
        )))
        h = float(abs(c[4, 2] - np.mean(c[0:4, 2])))
        return base_area * h / 3.0

    @staticmethod
    def _shape_functions(xi, eta, zeta) -> np.ndarray:
        """Funzioni di forma per piramide a 5 nodi."""
        if abs(1 - zeta) < 1e-12:
            return np.array([0.0, 0.0, 0.0, 0.0, 1.0])
        f = 1.0 / (1.0 - zeta) if abs(1 - zeta) > 1e-12 else 0.0
        N = np.array([
            0.25 * (1 - xi * f) * (1 - eta * f) * (1 - zeta),
            0.25 * (1 + xi * f) * (1 - eta * f) * (1 - zeta),
            0.25 * (1 + xi * f) * (1 + eta * f) * (1 - zeta),
            0.25 * (1 - xi * f) * (1 + eta * f) * (1 - zeta),
            0.5 * (1 + zeta),
        ])
        return N

    def _B_matrix_numerical(self, xi, eta, zeta) -> tuple[np.ndarray, float]:
        """Matrice B (6x15) con derivazione numerica."""
        h = 1e-6
        c = self._coords()

        def _N_at(xi_, eta_, zeta_):
            return self._shape_functions(xi_, eta_, zeta_)

        dNdxi = (_N_at(xi + h, eta, zeta) - _N_at(xi - h, eta, zeta)) / (2 * h)
        dNdeta = (_N_at(xi, eta + h, zeta) - _N_at(xi, eta - h, zeta)) / (2 * h)
        dNdzeta = (_N_at(xi, eta, zeta + h) - _N_at(xi, eta, zeta - h)) / (2 * h)

        dNd_nat = np.vstack([dNdxi, dNdeta, dNdzeta])
        J = dNd_nat @ c
        detJ = float(np.linalg.det(J))
        if abs(detJ) < 1e-30:
            detJ = 1e-30
        Jinv = np.linalg.inv(J)
        dNdxyz = Jinv @ dNd_nat

        B = np.zeros((6, 15))
        for i in range(5):
            col = 3 * i
            dNdx = dNdxyz[0, i]
            dNdy = dNdxyz[1, i]
            dNdz = dNdxyz[2, i]
            B[0, col] = dNdx
            B[1, col + 1] = dNdy
            B[2, col + 2] = dNdz
            B[3, col] = dNdy
            B[3, col + 1] = dNdx
            B[4, col + 1] = dNdz
            B[4, col + 2] = dNdy
            B[5, col] = dNdz
            B[5, col + 2] = dNdx
        return B, abs(detJ)

    def stiffness_local(self) -> np.ndarray:
        """Matrice di rigidezza 15x15."""
        from .integration import gauss_legendre_3d
        K = np.zeros((15, 15))
        D = self.material.D_matrix()
        xi_g, eta_g, zeta_g, w_g = gauss_legendre_3d(2, 2, 2)
        for xi, eta, zeta, w in zip(xi_g, eta_g, zeta_g, w_g):
            B, detJ = self._B_matrix_numerical(xi, eta, zeta)
            K += w * (B.T @ D @ B) * detJ
        return K

    def global_dofs(self, dof_map: dict[int, np.ndarray]) -> np.ndarray:
        return np.concatenate([dof_map[n.id] for n in self.nodes])

    def equivalent_body_force(self, bx: float, by: float, bz: float) -> np.ndarray:
        f = np.zeros(15)
        b = np.array([bx, by, bz])
        V = self.volume()
        for i in range(5):
            f[3 * i:3 * i + 3] = b * V / 5.0
        return f

    def stress_at(self, xi, eta, zeta, u_elem: np.ndarray) -> np.ndarray:
        D = self.material.D_matrix()
        B, _ = self._B_matrix_numerical(xi, eta, zeta)
        return D @ B @ u_elem
