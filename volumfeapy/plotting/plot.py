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


def plot_deformed(result, scale: float = 1.0) -> go.Figure:
    """Mesh deformata 3D."""
    model = result.model
    fig = go.Figure()

    for el in model.elements.values():
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        u = result.U[ed]
        deformed = coords + scale * u.reshape(-1, 3)
        edges = _get_edges(el)
        for i, j in edges:
            fig.add_trace(go.Scatter3d(
                x=[deformed[i, 0], deformed[j, 0]],
                y=[deformed[i, 1], deformed[j, 1]],
                z=[deformed[i, 2], deformed[j, 2]],
                mode="lines", line=dict(color="crimson", width=4),
                showlegend=False,
            ))

    for el in model.elements.values():
        coords = el._coords()
        edges = _get_edges(el)
        for i, j in edges:
            fig.add_trace(go.Scatter3d(
                x=[coords[i, 0], coords[j, 0]],
                y=[coords[i, 1], coords[j, 1]],
                z=[coords[i, 2], coords[j, 2]],
                mode="lines", line=dict(color="lightgray", width=2, dash="dot"),
                showlegend=False,
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


def plot_mode(modal_result, i: int = 0, scale: float = 1.0) -> go.Figure:
    """Disegna la i-esima forma modale."""
    model = modal_result.model
    phi_i = modal_result.phi[:, i]

    fig = go.Figure()
    for el in model.elements.values():
        coords = el._coords()
        ed = el.global_dofs(model.dof_map)
        u = phi_i[ed]
        deformed = coords + scale * u.reshape(-1, 3)
        edges = _get_edges(el)
        for i_e, j_e in edges:
            fig.add_trace(go.Scatter3d(
                x=[deformed[i_e, 0], deformed[j_e, 0]],
                y=[deformed[i_e, 1], deformed[j_e, 1]],
                z=[deformed[i_e, 2], deformed[j_e, 2]],
                mode="lines", line=dict(color="#8e44ad", width=4),
                showlegend=False,
            ))

    f = modal_result.freq[i]
    fig.update_layout(
        title=f"Modo {i + 1} — f = {f:.3f} Hz" if f > 0 else f"Modo {i + 1}",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z",
                   aspectmode="data"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
