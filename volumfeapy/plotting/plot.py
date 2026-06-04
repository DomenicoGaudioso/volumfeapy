"""Visualizzazione con Plotly per elementi volumetrici."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from volumfeapy import postprocess
from volumfeapy.element import Hex8, Tet4, Tet10, Wedge6, Pyramid5


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
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
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


def _face_color(u_mag_i: float, u_mag_j: float, u_mag_k: float,
                u_min: float, u_max: float) -> str:
    """Colore RGB basato sulla magnitudine media dello spostamento."""
    avg = (u_mag_i + u_mag_j + u_mag_k) / 3.0
    rng = u_max - u_min
    if rng < 1e-30:
        t = 0.5
    else:
        t = (avg - u_min) / rng
    t = max(0.0, min(1.0, t))
    r = int(59 + t * (220 - 59))
    g = int(76 + (1.0 - abs(2 * t - 1)) * 140)
    b = int(192 + (1 - t) * (50 - 192))
    return f"rgb({r},{g},{b})"


def plot_deformed(result, scale: float = 1.0, opacity: float = 0.7) -> go.Figure:
    """Mesh deformata 3D con facce colorate e trasparenza.

    Parameters
    ----------
    result : Result
        Risultato dell'analisi.
    scale : float
        Fattore di scala per gli spostamenti.
    opacity : float
        Trasparenza delle facce (0=trasparente, 1=opaco). Default 0.7.
    """
    model = result.model
    fig = go.Figure()

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
    face_colors = []
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
        offset += len(face_global)

        u_mags = [u_magnitudes[nid] for nid in face_global]

        if len(face_global) == 3:
            all_i.append(base)
            all_j.append(base + 1)
            all_k.append(base + 2)
            face_colors.append(_face_color(u_mags[0], u_mags[1], u_mags[2],
                                           u_min, u_max))
        elif len(face_global) == 4:
            all_i.extend([base, base])
            all_j.extend([base + 1, base + 3])
            all_k.extend([base + 2, base + 2])
            c1 = _face_color(u_mags[0], u_mags[1], u_mags[2], u_min, u_max)
            c2 = _face_color(u_mags[0], u_mags[3], u_mags[2], u_min, u_max)
            face_colors.extend([c1, c2])

    if all_x:
        fig.add_trace(go.Mesh3d(
            x=all_x, y=all_y, z=all_z,
            i=all_i, j=all_j, k=all_k,
            facecolor=face_colors,
            opacity=opacity,
            flatshading=True,
            showlegend=False,
            hoverinfo="skip",
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
                    line=dict(color="rgba(0,0,0,0.5)", width=2),
                    showlegend=False, hoverinfo="skip",
                ))

    for el in model.elements.values():
        coords = el._coords()
        edges = _get_edges(el)
        for i_e, j_e in edges:
            fig.add_trace(go.Scatter3d(
                x=[coords[i_e, 0], coords[j_e, 0]],
                y=[coords[i_e, 1], coords[j_e, 1]],
                z=[coords[i_e, 2], coords[j_e, 2]],
                mode="lines",
                line=dict(color="rgba(180,180,180,0.3)", width=1, dash="dot"),
                showlegend=False, hoverinfo="skip",
            ))

    fig.update_layout(
        title=f"Deformata (scala {scale:g})",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z",
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def plot_stress(result, component: str = "von_mises",
                title: str | None = None) -> go.Figure:
    """Mappa a colori delle tensioni (valore al centro di ogni elemento)."""
    model = result.model
    fig = go.Figure()

    for el in model.elements.values():
        coords = el._coords()
        edges = _get_edges(el)
        for i, j in edges:
            fig.add_trace(go.Scatter3d(
                x=[coords[i, 0], coords[j, 0]],
                y=[coords[i, 1], coords[j, 1]],
                z=[coords[i, 2], coords[j, 2]],
                mode="lines", line=dict(color="#ccc", width=2),
                showlegend=False,
            ))

    centers_x, centers_y, centers_z, values = [], [], [], []
    for eid, el in model.elements.items():
        coords = el._coords()
        center = coords.mean(axis=0)
        s = postprocess.element_stresses(result, eid)
        centers_x.append(center[0])
        centers_y.append(center[1])
        centers_z.append(center[2])
        values.append(s[component])

    fig.add_trace(go.Scatter3d(
        x=centers_x, y=centers_y, z=centers_z,
        mode="markers",
        marker=dict(size=8, color=values, colorscale="RdYlBu",
                    colorbar=dict(title=component)),
        showlegend=False,
    ))

    fig.update_layout(
        title=title or f"Tensioni: {component}",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z",
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def plot_mode(modal_result, i: int = 0, scale: float = 1.0,
              opacity: float = 0.7) -> go.Figure:
    """Disegna la i-esima forma modale con mesh colorata e trasparenza."""
    model = modal_result.model
    phi_i = modal_result.phi[:, i]

    fig = go.Figure()

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
    face_colors = []
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
        offset += len(face_global)

        u_mags = [u_magnitudes[nid] for nid in face_global]

        if len(face_global) == 3:
            all_i.append(base)
            all_j.append(base + 1)
            all_k.append(base + 2)
            face_colors.append(_face_color(u_mags[0], u_mags[1], u_mags[2],
                                           u_min, u_max))
        elif len(face_global) == 4:
            all_i.extend([base, base])
            all_j.extend([base + 1, base + 3])
            all_k.extend([base + 2, base + 2])
            c1 = _face_color(u_mags[0], u_mags[1], u_mags[2], u_min, u_max)
            c2 = _face_color(u_mags[0], u_mags[3], u_mags[2], u_min, u_max)
            face_colors.extend([c1, c2])

    if all_x:
        fig.add_trace(go.Mesh3d(
            x=all_x, y=all_y, z=all_z,
            i=all_i, j=all_j, k=all_k,
            facecolor=face_colors,
            opacity=opacity,
            flatshading=True,
            showlegend=False,
            hoverinfo="skip",
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
                    line=dict(color="rgba(0,0,0,0.5)", width=2),
                    showlegend=False, hoverinfo="skip",
                ))

    f = modal_result.freq[i]
    fig.update_layout(
        title=f"Modo {i + 1} — f = {f:.3f} Hz" if f > 0 else f"Modo {i + 1}",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z",
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
