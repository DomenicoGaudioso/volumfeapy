"""Visualizzazione con Plotly per elementi volumetrici."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from volumfeapy import postprocess
from volumfeapy.element import Hex8, Tet4, Tet10, Wedge6, Pyramid5


def _padded_range(values, pad_fraction: float = 0.08) -> list[float]:
    arr = np.asarray(values, dtype=float)
    v_min = float(arr.min())
    v_max = float(arr.max())
    span = v_max - v_min
    if span < 1e-12:
        span = max(abs(v_min), 1.0)
    pad = span * pad_fraction
    return [v_min - pad, v_max + pad]


def _contour_levels(v_min: float, v_max: float, count: int) -> list[float]:
    if count <= 0 or v_max - v_min < 1e-30:
        return []
    return np.linspace(v_min, v_max, count + 2)[1:-1].tolist()


def _edge_level_point(pa: np.ndarray, pb: np.ndarray, va: float, vb: float,
                      level: float) -> np.ndarray | None:
    da = va - level
    db = vb - level
    if abs(da) < 1e-30 and abs(db) < 1e-30:
        return None
    if da * db > 0:
        return None
    if abs(vb - va) < 1e-30:
        return None
    t = (level - va) / (vb - va)
    if t < -1e-12 or t > 1.0 + 1e-12:
        return None
    return pa + np.clip(t, 0.0, 1.0) * (pb - pa)


def _triangle_isoline_points(points: list[np.ndarray], values: list[float],
                             level: float) -> tuple[np.ndarray, np.ndarray] | None:
    intersections = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        point = _edge_level_point(points[a], points[b], values[a], values[b], level)
        if point is not None:
            intersections.append(point)
    unique = []
    for point in intersections:
        if not any(np.linalg.norm(point - other) < 1e-10 for other in unique):
            unique.append(point)
    if len(unique) < 2:
        return None
    return unique[0], unique[1]


def _add_isoline_trace_3d(fig: go.Figure, x: list[float], y: list[float],
                          z: list[float], i: list[int], j: list[int],
                          k: list[int], values: list[float],
                          levels: list[float],
                          color: str = "rgba(0,0,0,0.90)",
                          width: float = 4.0) -> None:
    line_x, line_y, line_z = [], [], []
    coords = [np.array([xv, yv, zv], dtype=float) for xv, yv, zv in zip(x, y, z)]
    for level in levels:
        for ia, ib, ic in zip(i, j, k):
            segment = _triangle_isoline_points(
                [coords[ia], coords[ib], coords[ic]],
                [values[ia], values[ib], values[ic]],
                level,
            )
            if segment is None:
                continue
            p0, p1 = segment
            line_x.extend([float(p0[0]), float(p1[0]), None])
            line_y.extend([float(p0[1]), float(p1[1]), None])
            line_z.extend([float(p0[2]), float(p1[2]), None])
    if line_x:
        fig.add_trace(go.Scatter3d(
            x=line_x, y=line_y, z=line_z,
            mode="lines",
            line=dict(color=color, width=width),
            name="Iso-linee",
            showlegend=False,
            hoverinfo="skip",
        ))


_HEX8_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]

_TET4_EDGES = [
    (0, 1), (1, 2), (2, 0),
    (0, 3), (1, 3), (2, 3),
]

_WEDGE6_EDGES = [
    (0, 1), (1, 2), (2, 0),
    (3, 4), (4, 5), (5, 3),
    (0, 3), (1, 4), (2, 5),
]

_PYRAMID5_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (0, 4), (1, 4), (2, 4), (3, 4),
]


def _get_edges(el) -> list[tuple[int, int]]:
    if isinstance(el, Hex8):
        return _HEX8_EDGES
    elif isinstance(el, (Tet4, Tet10)):
        return _TET4_EDGES
    elif isinstance(el, Wedge6):
        return _WEDGE6_EDGES
    elif isinstance(el, Pyramid5):
        return _PYRAMID5_EDGES
    return []


def plot_mesh(model, show_node_ids: bool = True) -> go.Figure:
    """Disegna la mesh 3D."""
    fig = go.Figure()
    for el in model.elements.values():
        coords = el._coords()
        edges = _get_edges(el)
        for i, j in edges:
            fig.add_trace(go.Scatter3d(
                x=[coords[i, 0], coords[j, 0]],
                y=[coords[i, 1], coords[j, 1]],
                z=[coords[i, 2], coords[j, 2]],
                mode="lines", line=dict(color="#444", width=3),
                showlegend=False,
            ))

    xs = [n.x for n in model.nodes.values()]
    ys = [n.y for n in model.nodes.values()]
    zs = [n.z for n in model.nodes.values()]
    text = [str(n.id) for n in model.nodes.values()] if show_node_ids else None
    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers+text" if show_node_ids else "markers",
        marker=dict(size=3, color="#1f77b4"),
        text=text, textposition="top center",
        showlegend=False,
    ))
    fig.update_layout(
        title="Mesh 3D",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z",
                   aspectmode="data",
                   camera=dict(eye=dict(x=2.45, y=-2.2, z=1.55))),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


_HEX8_FACES = [
    (0, 1, 2, 3), (4, 7, 6, 5),
    (0, 4, 5, 1), (1, 5, 6, 2),
    (2, 6, 7, 3), (3, 7, 4, 0),
]

_TET4_FACES = [
    (0, 1, 2), (0, 1, 3), (1, 2, 3), (0, 2, 3),
]

_TET10_FACE_NODES = {
    (0, 1, 2): (0, 1, 2, 4, 5, 6),
    (0, 1, 3): (0, 1, 3, 4, 8, 7),
    (1, 2, 3): (1, 2, 3, 5, 9, 8),
    (0, 2, 3): (0, 2, 3, 6, 9, 7),
}

_WEDGE6_FACES = [
    (0, 1, 2), (3, 4, 5),
    (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5),
]

_PYRAMID5_FACES = [
    (0, 1, 2, 3),
    (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4),
]


def _get_faces(el) -> list[tuple]:
    if isinstance(el, Hex8):
        return _HEX8_FACES
    elif isinstance(el, (Tet4, Tet10)):
        return _TET4_FACES
    elif isinstance(el, Wedge6):
        return _WEDGE6_FACES
    elif isinstance(el, Pyramid5):
        return _PYRAMID5_FACES
    return []


def _find_boundary_faces(model) -> list[tuple[int, tuple]]:
    """Trova le facce esterne (appartenenti a un solo elemento).

    Restituisce lista di (elem_id, face_local_nodes).
    """
    face_count: dict[tuple, list] = {}
    for eid, el in model.elements.items():
        faces = _get_faces(el)
        for face in faces:
            global_face = tuple(sorted(el.node_ids[f] for f in face))
            if global_face not in face_count:
                face_count[global_face] = []
            face_count[global_face].append((eid, face))

    boundary = []
    for gf, entries in face_count.items():
        if len(entries) == 1:
            boundary.append(entries[0])
    return boundary


def _stress_component_value(sigma: np.ndarray, component: str) -> float:
    keys = ("sxx", "syy", "szz", "txy", "tyz", "txz")
    if component == "von_mises":
        return postprocess.von_mises(sigma)
    if component not in keys:
        raise KeyError(f"Componente tensionale non valida: {component}")
    return float(sigma[keys.index(component)])


def _element_stress_at_local_node(el, local_idx: int, u_elem: np.ndarray,
                                  component: str) -> float:
    """Valore tensionale nel nodo locale, con fallback al centro elemento."""
    try:
        if isinstance(el, Hex8):
            natural = [
                (-1.0, -1.0, -1.0), (1.0, -1.0, -1.0),
                (1.0, 1.0, -1.0), (-1.0, 1.0, -1.0),
                (-1.0, -1.0, 1.0), (1.0, -1.0, 1.0),
                (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0),
            ]
            sigma = el.stress_at(*natural[local_idx], u_elem)
        elif isinstance(el, Tet4):
            sigma = el.stress_at(None, None, None, u_elem)
        elif isinstance(el, Tet10):
            natural = [
                (1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0),
                (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0),
                (0.5, 0.5, 0.0, 0.0), (0.0, 0.5, 0.5, 0.0),
                (0.5, 0.0, 0.5, 0.0), (0.5, 0.0, 0.0, 0.5),
                (0.0, 0.5, 0.0, 0.5), (0.0, 0.0, 0.5, 0.5),
            ]
            sigma = el.stress_at(*natural[local_idx], u_elem)
        elif isinstance(el, Wedge6):
            natural = [
                (1.0, 0.0, 0.0, -1.0), (0.0, 1.0, 0.0, -1.0),
                (0.0, 0.0, 1.0, -1.0), (1.0, 0.0, 0.0, 1.0),
                (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0),
            ]
            sigma = el.stress_at(*natural[local_idx], u_elem)
        elif isinstance(el, Pyramid5):
            natural = [
                (-1.0, -1.0, -1.0), (1.0, -1.0, -1.0),
                (1.0, 1.0, -1.0), (-1.0, 1.0, -1.0),
                (0.0, 0.0, 0.95),
            ]
            sigma = el.stress_at(*natural[local_idx], u_elem)
        else:
            return 0.0
    except Exception:
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
    return _stress_component_value(sigma, component)


def _nodal_stress_values(result, component: str) -> dict[int, float]:
    """Media nodale dei valori tensionali calcolati dagli elementi adiacenti."""
    sums: dict[int, float] = {}
    counts: dict[int, int] = {}
    model = result.model

    for eid, el in model.elements.items():
        ed = el.global_dofs(model.dof_map)
        u_elem = result.U[ed]
        for local_idx, nid in enumerate(el.node_ids):
            value = _element_stress_at_local_node(el, local_idx, u_elem, component)
            sums[nid] = sums.get(nid, 0.0) + value
            counts[nid] = counts.get(nid, 0) + 1

    return {nid: sums[nid] / counts[nid] for nid in sums}


def _quad_shape(s: float, t: float) -> np.ndarray:
    return np.array([
        0.25 * (1.0 - s) * (1.0 - t),
        0.25 * (1.0 + s) * (1.0 - t),
        0.25 * (1.0 + s) * (1.0 + t),
        0.25 * (1.0 - s) * (1.0 + t),
    ])


def _tri6_shape(l1: float, l2: float, l3: float) -> np.ndarray:
    return np.array([
        l1 * (2.0 * l1 - 1.0),
        l2 * (2.0 * l2 - 1.0),
        l3 * (2.0 * l3 - 1.0),
        4.0 * l1 * l2,
        4.0 * l2 * l3,
        4.0 * l3 * l1,
    ])


def _hex8_shape(xi: float, eta: float, zeta: float) -> np.ndarray:
    signs = np.array([
        (-1.0, -1.0, -1.0), (1.0, -1.0, -1.0),
        (1.0, 1.0, -1.0), (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0), (1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0),
    ])
    return 0.125 * (
        (1.0 + signs[:, 0] * xi)
        * (1.0 + signs[:, 1] * eta)
        * (1.0 + signs[:, 2] * zeta)
    )


def _hex8_face_natural(face_local: tuple[int, ...], s: float,
                       t: float) -> tuple[float, float, float]:
    if face_local == (0, 1, 2, 3):
        return s, t, -1.0
    if face_local == (4, 7, 6, 5):
        return s, t, 1.0
    if face_local == (0, 4, 5, 1):
        return s, -1.0, t
    if face_local == (1, 5, 6, 2):
        return 1.0, s, t
    if face_local == (2, 6, 7, 3):
        return s, 1.0, t
    if face_local == (3, 7, 4, 0):
        return -1.0, s, t
    raise ValueError(f"Faccia Hex8 non riconosciuta: {face_local}")


def _linear_face_sample(el, face_nodes: tuple[int, ...],
                        weights: np.ndarray,
                        nodal_values: dict[int, float]) -> tuple[np.ndarray, float]:
    coords = el._coords()[list(face_nodes)]
    values = np.array([nodal_values[el.node_ids[i]] for i in face_nodes])
    return weights @ coords, float(weights @ values)


def _stress_face_sample(el, face_local: tuple[int, ...], sample: tuple[float, ...],
                        nodal_values: dict[int, float]) -> tuple[np.ndarray, float]:
    coords = el._coords()
    values = np.array([nodal_values[nid] for nid in el.node_ids])

    if isinstance(el, Hex8):
        s, t = sample
        xi, eta, zeta = _hex8_face_natural(face_local, s, t)
        weights = _hex8_shape(xi, eta, zeta)
        return weights @ coords, float(weights @ values)

    if isinstance(el, Tet10):
        face_nodes = _TET10_FACE_NODES[tuple(face_local)]
        l1, l2, l3 = sample
        weights = _tri6_shape(l1, l2, l3)
        return _linear_face_sample(el, face_nodes, weights, nodal_values)

    if len(face_local) == 4:
        s, t = sample
        weights = _quad_shape(s, t)
        return _linear_face_sample(el, face_local, weights, nodal_values)

    l1, l2, l3 = sample
    weights = np.array([l1, l2, l3])
    return _linear_face_sample(el, face_local, weights, nodal_values)


def _add_quad_contour_face(el, face_local: tuple[int, ...], subdivisions: int,
                           nodal_values: dict[int, float],
                           all_x: list, all_y: list, all_z: list,
                           all_i: list, all_j: list, all_k: list,
                           face_values: list) -> None:
    grid: list[list[int]] = []
    for a in range(subdivisions + 1):
        row = []
        s = -1.0 + 2.0 * a / subdivisions
        for b in range(subdivisions + 1):
            t = -1.0 + 2.0 * b / subdivisions
            point, value = _stress_face_sample(el, face_local, (s, t),
                                               nodal_values)
            row.append(len(all_x))
            all_x.append(float(point[0]))
            all_y.append(float(point[1]))
            all_z.append(float(point[2]))
            face_values.append(value)
        grid.append(row)

    for a in range(subdivisions):
        for b in range(subdivisions):
            p00 = grid[a][b]
            p10 = grid[a + 1][b]
            p11 = grid[a + 1][b + 1]
            p01 = grid[a][b + 1]
            all_i.extend([p00, p00])
            all_j.extend([p10, p11])
            all_k.extend([p11, p01])


def _add_tri_contour_face(el, face_local: tuple[int, ...], subdivisions: int,
                          nodal_values: dict[int, float],
                          all_x: list, all_y: list, all_z: list,
                          all_i: list, all_j: list, all_k: list,
                          face_values: list) -> None:
    nodes: dict[tuple[int, int], int] = {}
    for i in range(subdivisions + 1):
        for j in range(subdivisions + 1 - i):
            l1 = i / subdivisions
            l2 = j / subdivisions
            l3 = 1.0 - l1 - l2
            point, value = _stress_face_sample(el, face_local, (l1, l2, l3),
                                               nodal_values)
            nodes[(i, j)] = len(all_x)
            all_x.append(float(point[0]))
            all_y.append(float(point[1]))
            all_z.append(float(point[2]))
            face_values.append(value)

    for i in range(subdivisions):
        for j in range(subdivisions - i):
            p = nodes[(i, j)]
            pi = nodes[(i + 1, j)]
            pj = nodes[(i, j + 1)]
            all_i.append(p)
            all_j.append(pi)
            all_k.append(pj)
            if j < subdivisions - i - 1:
                pij = nodes[(i + 1, j + 1)]
                all_i.append(pi)
                all_j.append(pij)
                all_k.append(pj)


def plot_deformed(result, scale: float = 1.0, opacity: float = 1.0) -> go.Figure:
    """Mesh deformata 3D colorata con riferimento trasparente.

    Parameters
    ----------
    result : Result
        Risultato dell'analisi.
    scale : float
        Fattore di scala per gli spostamenti.
    opacity : float
        Trasparenza delle facce (0=trasparente, 1=opaco). Default 1.0.
    """
    model = result.model
    fig = go.Figure()

    for el in model.elements.values():
        coords = el._coords()
        for i_e, j_e in _get_edges(el):
            fig.add_trace(go.Scatter3d(
                x=[coords[i_e, 0], coords[j_e, 0]],
                y=[coords[i_e, 1], coords[j_e, 1]],
                z=[coords[i_e, 2], coords[j_e, 2]],
                mode="lines",
                line=dict(color="rgba(70,70,70,0.24)", width=2, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            ))

    deformed_coords: dict[int, np.ndarray] = {}
    u_magnitudes: dict[int, float] = {}
    for nid, node in model.nodes.items():
        di = model.dof_map[nid]
        u = result.U[di]
        deformed_coords[nid] = node.coords + scale * u
        u_magnitudes[nid] = float(np.linalg.norm(u))

    u_vals = list(u_magnitudes.values())
    u_min = min(u_vals) if u_vals else 0.0
    u_max = max(u_vals) if u_vals else 1.0

    boundary = _find_boundary_faces(model)

    all_x, all_y, all_z = [], [], []
    all_i, all_j, all_k = [], [], []
    vertex_intensity = []
    offset = 0

    for eid, face_local in boundary:
        el = model.elements[eid]
        local_node_ids = el.node_ids
        face_global = [local_node_ids[f] for f in face_local]

        base = offset
        for nid in face_global:
            dc = deformed_coords[nid]
            all_x.append(dc[0])
            all_y.append(dc[1])
            all_z.append(dc[2])
            vertex_intensity.append(u_magnitudes[nid])
        offset += len(face_global)

        if len(face_global) == 3:
            all_i.append(base)
            all_j.append(base + 1)
            all_k.append(base + 2)
        elif len(face_global) == 4:
            all_i.extend([base, base])
            all_j.extend([base + 1, base + 3])
            all_k.extend([base + 2, base + 2])

    if all_x:
        fig.add_trace(go.Mesh3d(
            x=all_x, y=all_y, z=all_z,
            i=all_i, j=all_j, k=all_k,
            intensity=vertex_intensity,
            colorscale="RdYlBu",
            cmin=u_min,
            cmax=u_max if u_max - u_min > 1e-30 else u_min + 1.0,
            colorbar=dict(title="|u| [m]"),
            opacity=opacity,
            flatshading=True,
            showlegend=False,
            hovertemplate="x=%{x:.3g}<br>y=%{y:.3g}<br>z=%{z:.3g}<br>|u|=%{customdata:.3e} m<extra></extra>",
            customdata=vertex_intensity,
            lighting=dict(ambient=0.6, diffuse=0.4, specular=0.1),
        ))

    edge_set: set[tuple] = set()
    for eid, face_local in boundary:
        el = model.elements[eid]
        local_node_ids = el.node_ids
        face_global = [local_node_ids[f] for f in face_local]
        nf = len(face_global)
        for ii in range(nf):
            jj = (ii + 1) % nf
            a, b = face_global[ii], face_global[jj]
            edge = (min(a, b), max(a, b))
            if edge not in edge_set:
                edge_set.add(edge)
                da = deformed_coords[a]
                db = deformed_coords[b]
                fig.add_trace(go.Scatter3d(
                    x=[da[0], db[0]], y=[da[1], db[1]], z=[da[2], db[2]],
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0.30)", width=1),
                    showlegend=False, hoverinfo="skip",
                ))

    ref_x = [node.x for node in model.nodes.values()]
    ref_y = [node.y for node in model.nodes.values()]
    ref_z = [node.z for node in model.nodes.values()]

    fig.update_layout(
        title=f"Deformata (scala {scale:g})",
        scene=dict(
            xaxis=dict(title="X", range=_padded_range([*ref_x, *all_x])),
            yaxis=dict(title="Y", range=_padded_range([*ref_y, *all_y])),
            zaxis=dict(title="Z", range=_padded_range([*ref_z, *all_z])),
            aspectmode="data",
            camera=dict(
                projection=dict(type="orthographic"),
                eye=dict(x=1.55, y=-1.65, z=1.1),
            ),
        ),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_stress(result, component: str = "von_mises",
                title: str | None = None, subdivisions: int = 5,
                opacity: float = 1.0, show_isolines: bool = True,
                n_isolines: int = 9) -> go.Figure:
    """Mappa a colori delle tensioni sulle facce esterne della mesh.

    Le facce sono suddivise in triangoli di visualizzazione e colorate
    interpolando i valori tensionali nodali. La legenda resta nei valori reali.
    Le iso-linee separano fasce di uguale componente tensionale.
    """
    model = result.model
    fig = go.Figure()

    subdivisions = max(1, int(subdivisions))
    nodal_values = _nodal_stress_values(result, component)
    values = list(nodal_values.values())
    v_min = min(values) if values else 0.0
    v_max = max(values) if values else 1.0
    if v_max - v_min < 1e-30:
        v_max = v_min + 1.0

    boundary = _find_boundary_faces(model)
    all_x, all_y, all_z = [], [], []
    all_i, all_j, all_k = [], [], []
    face_values = []

    for eid, face_local in boundary:
        el = model.elements[eid]
        if len(face_local) == 4:
            _add_quad_contour_face(
                el, face_local, subdivisions, nodal_values,
                all_x, all_y, all_z, all_i, all_j, all_k, face_values,
            )
        else:
            _add_tri_contour_face(
                el, face_local, subdivisions, nodal_values,
                all_x, all_y, all_z, all_i, all_j, all_k, face_values,
            )

    if all_x:
        fig.add_trace(go.Mesh3d(
            x=all_x, y=all_y, z=all_z,
            i=all_i, j=all_j, k=all_k,
            intensity=face_values,
            colorscale="RdYlBu",
            cmin=v_min,
            cmax=v_max,
            colorbar=dict(title=component),
            opacity=float(np.clip(opacity, 0.0, 1.0)),
            flatshading=False,
            showlegend=False,
            customdata=face_values,
            hovertemplate=(
                "x=%{x:.3g}<br>y=%{y:.3g}<br>z=%{z:.3g}<br>"
                f"{component}=%{{customdata:.3e}}<extra></extra>"
            ),
            lighting=dict(ambient=0.65, diffuse=0.35, specular=0.05),
        ))
        if show_isolines:
            _add_isoline_trace_3d(
                fig, all_x, all_y, all_z, all_i, all_j, all_k, face_values,
                _contour_levels(v_min, v_max, n_isolines),
            )

    edge_set: set[tuple] = set()
    for eid, face_local in boundary:
        el = model.elements[eid]
        local_node_ids = el.node_ids
        coords = el._coords()
        face_global = [local_node_ids[f] for f in face_local]
        nf = len(face_global)
        for ii in range(nf):
            jj = (ii + 1) % nf
            a, b = face_global[ii], face_global[jj]
            edge = (min(a, b), max(a, b))
            if edge in edge_set:
                continue
            edge_set.add(edge)
            local_a = face_local[ii]
            local_b = face_local[jj]
            fig.add_trace(go.Scatter3d(
                x=[coords[local_a, 0], coords[local_b, 0]],
                y=[coords[local_a, 1], coords[local_b, 1]],
                z=[coords[local_a, 2], coords[local_b, 2]],
                mode="lines",
                line=dict(color="rgba(0,0,0,0.28)", width=1),
                showlegend=False,
                hoverinfo="skip",
            ))

    fig.update_layout(
        title=title or f"Tensioni: {component}",
        scene=dict(
            xaxis=dict(title="X", range=_padded_range(all_x)),
            yaxis=dict(title="Y", range=_padded_range(all_y)),
            zaxis=dict(title="Z", range=_padded_range(all_z)),
            aspectmode="data",
            camera=dict(
                projection=dict(type="orthographic"),
                eye=dict(x=1.55, y=-1.65, z=1.1),
            ),
        ),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def plot_mode(modal_result, i: int = 0, scale: float = 1.0,
              opacity: float = 1.0) -> go.Figure:
    """Disegna la i-esima forma modale con riferimento trasparente."""
    model = modal_result.model
    phi_i = modal_result.phi[:, i]

    fig = go.Figure()

    for el in model.elements.values():
        coords = el._coords()
        for i_e, j_e in _get_edges(el):
            fig.add_trace(go.Scatter3d(
                x=[coords[i_e, 0], coords[j_e, 0]],
                y=[coords[i_e, 1], coords[j_e, 1]],
                z=[coords[i_e, 2], coords[j_e, 2]],
                mode="lines",
                line=dict(color="rgba(70,70,70,0.24)", width=2, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            ))

    deformed_coords: dict[int, np.ndarray] = {}
    u_magnitudes: dict[int, float] = {}
    for nid, node in model.nodes.items():
        di = model.dof_map[nid]
        u = phi_i[di]
        deformed_coords[nid] = node.coords + scale * u
        u_magnitudes[nid] = float(np.linalg.norm(u))

    u_vals = list(u_magnitudes.values())
    u_min = min(u_vals) if u_vals else 0.0
    u_max = max(u_vals) if u_vals else 1.0

    boundary = _find_boundary_faces(model)

    all_x, all_y, all_z = [], [], []
    all_i, all_j, all_k = [], [], []
    vertex_intensity = []
    offset = 0

    for eid, face_local in boundary:
        el = model.elements[eid]
        local_node_ids = el.node_ids
        face_global = [local_node_ids[f] for f in face_local]

        base = offset
        for nid in face_global:
            dc = deformed_coords[nid]
            all_x.append(dc[0])
            all_y.append(dc[1])
            all_z.append(dc[2])
            vertex_intensity.append(u_magnitudes[nid])
        offset += len(face_global)

        if len(face_global) == 3:
            all_i.append(base)
            all_j.append(base + 1)
            all_k.append(base + 2)
        elif len(face_global) == 4:
            all_i.extend([base, base])
            all_j.extend([base + 1, base + 3])
            all_k.extend([base + 2, base + 2])

    max_mode = max(vertex_intensity) if vertex_intensity else 1.0
    if max_mode < 1e-30:
        max_mode = 1.0
    modal_index = [v / max_mode for v in vertex_intensity]

    if all_x:
        fig.add_trace(go.Mesh3d(
            x=all_x, y=all_y, z=all_z,
            i=all_i, j=all_j, k=all_k,
            intensity=modal_index,
            colorscale="RdYlBu",
            cmin=0.0,
            cmax=1.0,
            colorbar=dict(title="|phi| / max"),
            opacity=opacity,
            flatshading=True,
            showlegend=False,
            hovertemplate="x=%{x:.3g}<br>y=%{y:.3g}<br>z=%{z:.3g}<br>|phi|/max=%{customdata:.3f}<extra></extra>",
            customdata=modal_index,
            lighting=dict(ambient=0.6, diffuse=0.4, specular=0.1),
        ))

    edge_set: set[tuple] = set()
    for eid, face_local in boundary:
        el = model.elements[eid]
        local_node_ids = el.node_ids
        face_global = [local_node_ids[f] for f in face_local]
        nf = len(face_global)
        for ii in range(nf):
            jj = (ii + 1) % nf
            a, b = face_global[ii], face_global[jj]
            edge = (min(a, b), max(a, b))
            if edge not in edge_set:
                edge_set.add(edge)
                da = deformed_coords[a]
                db = deformed_coords[b]
                fig.add_trace(go.Scatter3d(
                    x=[da[0], db[0]], y=[da[1], db[1]], z=[da[2], db[2]],
                    mode="lines",
                    line=dict(color="rgba(0,0,0,0.30)", width=1),
                    showlegend=False, hoverinfo="skip",
                ))

    ref_x = [node.x for node in model.nodes.values()]
    ref_y = [node.y for node in model.nodes.values()]
    ref_z = [node.z for node in model.nodes.values()]

    f = modal_result.freq[i]
    mode_scene = dict(
        xaxis=dict(title="X", range=_padded_range([*ref_x, *all_x])),
        yaxis=dict(title="Y", range=_padded_range([*ref_y, *all_y])),
        zaxis=dict(title="Z", range=_padded_range([*ref_z, *all_z])),
        aspectmode="data",
        camera=dict(
            projection=dict(type="orthographic"),
            eye=dict(x=1.55, y=-1.65, z=1.1),
        ),
    )
    mode_margin = dict(l=20, r=20, t=50, b=20)
    fig.update_layout(
        title=f"Modo {i + 1} — f = {f:.3f} Hz" if f > 0 else f"Modo {i + 1}",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z",
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    fig.update_layout(scene=mode_scene, margin=mode_margin)
    return fig
