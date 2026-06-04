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


def plot_deformed(result, scale: float = 1.0, opacity: float = 0.7) -> go.Figure:
    """Mesh deformata 3D colorata con riferimento trasparente.

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
