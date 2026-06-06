"""Test per elementi volumetrici."""

import numpy as np
import pytest

from volumfeapy import Model, Material


def _single_hex8():
    """Singolo elemento Hex8 unitario."""
    m = Model()
    m.add_node(1, 0, 0, 0)
    m.add_node(2, 1, 0, 0)
    m.add_node(3, 1, 1, 0)
    m.add_node(4, 0, 1, 0)
    m.add_node(5, 0, 0, 1)
    m.add_node(6, 1, 0, 1)
    m.add_node(7, 1, 1, 1)
    m.add_node(8, 0, 1, 1)
    mat = Material(E=210e9, nu=0.3)
    m.add_hex8(1, [1, 2, 3, 4, 5, 6, 7, 8], mat)
    return m


def _single_tet4():
    """Singolo elemento Tet4."""
    m = Model()
    m.add_node(1, 0, 0, 0)
    m.add_node(2, 1, 0, 0)
    m.add_node(3, 0, 1, 0)
    m.add_node(4, 0, 0, 1)
    mat = Material(E=210e9, nu=0.3)
    m.add_tet4(1, [1, 2, 3, 4], mat)
    return m


def test_hex8_stiffness_symmetry():
    m = _single_hex8()
    K = m.assemble_stiffness()
    assert np.allclose(K, K.T, atol=1e-10)


def test_hex8_stiffness_positive_diagonal():
    m = _single_hex8()
    K = m.assemble_stiffness()
    assert np.all(np.diag(K) >= -1e-15)


def test_hex8_volume():
    m = _single_hex8()
    el = m.elements[1]
    assert abs(el.volume() - 1.0) < 1e-10


def test_hex8_uniaxial_tension():
    """Hex8 in trazione uniassiale: sigma_zz = F/A, u_z = F*L/(E*A)."""
    m = _single_hex8()
    F = 1e6
    A = 1.0
    L = 1.0
    E = 210e9

    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    for nid in [5, 6, 7, 8]:
        m.add_nodal_load(nid, Fz=F / 4.0)

    res = m.solve()
    u_z = res.displacement(5, "uz")
    u_exact = F * L / (E * A)
    rel_error = abs(u_z - u_exact) / u_exact
    assert rel_error < 0.15, f"Errore {rel_error:.4f}"


def test_tet4_stiffness_symmetry():
    m = _single_tet4()
    K = m.assemble_stiffness()
    assert np.allclose(K, K.T, atol=1e-10)


def test_tet4_volume():
    m = _single_tet4()
    el = m.elements[1]
    assert abs(el.volume() - 1.0 / 6.0) < 1e-10


def test_tet4_stresses_constant():
    """Le tensioni nel Tet4 devono essere costanti."""
    m = _single_tet4()
    for nid in [1, 2, 3]:
        m.fix(nid)
    m.add_nodal_load(4, Fz=-1000.0)
    res = m.solve()

    from volumfeapy import postprocess
    s = postprocess.element_stresses(res, 1)
    assert s["von_mises"] >= 0


def test_tet10_solve_single_element():
    m = Model()
    coords = [
        (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (0.5, 0, 0), (0.5, 0.5, 0), (0, 0.5, 0),
        (0, 0, 0.5), (0.5, 0, 0.5), (0, 0.5, 0.5),
    ]
    for i, (x, y, z) in enumerate(coords, start=1):
        m.add_node(i, x, y, z)
    mat = Material(E=210e9, nu=0.3)
    m.add_tet10(1, list(range(1, 11)), mat)

    for nid in [1, 2, 3, 5, 6, 7]:
        m.fix(nid)
    m.add_nodal_load(4, Fz=-1000.0)
    m.add_nodal_load(8, Fz=-500.0)
    m.add_nodal_load(9, Fz=-500.0)
    m.add_nodal_load(10, Fz=-500.0)

    res = m.solve()
    assert np.isfinite(res.U).all()
    assert res.displacement(4, "uz") < 0


def test_settlement():
    m = _single_hex8()
    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    m.add_settlement(5, "uz", -0.001)
    res = m.solve()
    u5 = res.displacement(5, "uz")
    assert abs(u5 - (-0.001)) < 1e-10


def test_gravity_load():
    m = _single_hex8()
    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    m.elements[1].material.rho = 7850.0
    m.add_gravity(g=9.81, direction="z")
    res = m.solve()
    assert res.U is not None


def test_modal_analysis():
    m = _single_hex8()
    m.elements[1].material.rho = 7850.0
    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    modal = m.modal(n_modes=3)
    assert len(modal.freq) == 3
    assert all(f >= 0 for f in modal.freq)


def test_von_mises():
    from volumfeapy.postprocess import von_mises
    sigma = np.array([100, 0, 0, 0, 0, 0], dtype=float)
    vm = von_mises(sigma)
    assert abs(vm - 100.0) < 1e-10


def test_principal_stresses():
    from volumfeapy.postprocess import principal_stresses
    sigma = np.array([100, 50, 0, 0, 0, 0], dtype=float)
    vals, vecs = principal_stresses(sigma)
    assert abs(vals[0] - 100.0) < 1e-10
    assert abs(vals[1] - 50.0) < 1e-10
    assert abs(vals[2] - 0.0) < 1e-10


def test_plot_stress_subdivides_boundary_faces():
    m = _single_hex8()
    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    for nid in [5, 6, 7, 8]:
        m.add_nodal_load(nid, Fz=250.0)

    res = m.solve()

    from volumfeapy.plotting import plot_stress
    fig = plot_stress(res, "szz", subdivisions=2)

    mesh = fig.data[0]
    assert mesh.type == "mesh3d"
    assert len(mesh.x) > 8
    assert len(mesh.i) > 12
    assert len(mesh.customdata) == len(mesh.x)


def test_plot_stress_adds_isolines_and_opaque_default():
    m = _single_hex8()
    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    for nid in [5, 6, 7, 8]:
        m.add_nodal_load(nid, Fz=250.0)

    res = m.solve()

    from volumfeapy.plotting import plot_stress
    fig = plot_stress(res, "von_mises", subdivisions=2, n_isolines=4)

    assert fig.data[0].opacity == 1.0
    assert any(trace.type == "scatter3d" for trace in fig.data[1:])


def test_plot_supports_and_reactions():
    m = _single_hex8()
    for nid in [1, 2, 3, 4]:
        m.fix(nid)
    for nid in [5, 6, 7, 8]:
        m.add_nodal_load(nid, Fz=-250.0)

    res = m.solve()

    from volumfeapy.plotting import plot_reactions, plot_supports
    supports = plot_supports(m)
    reactions = plot_reactions(res)

    assert any(trace.name == "Vincoli" for trace in supports.data)
    assert any(trace.name == "Reazioni" for trace in reactions.data)


def test_wedge6_volume():
    m = Model()
    m.add_node(1, 0, 0, 0)
    m.add_node(2, 1, 0, 0)
    m.add_node(3, 0, 1, 0)
    m.add_node(4, 0, 0, 1)
    m.add_node(5, 1, 0, 1)
    m.add_node(6, 0, 1, 1)
    mat = Material(E=210e9, nu=0.3)
    m.add_wedge6(1, [1, 2, 3, 4, 5, 6], mat)
    el = m.elements[1]
    assert el.volume() > 0


def test_pyramid5_volume():
    m = Model()
    m.add_node(1, 0, 0, 0)
    m.add_node(2, 1, 0, 0)
    m.add_node(3, 1, 1, 0)
    m.add_node(4, 0, 1, 0)
    m.add_node(5, 0.5, 0.5, 1)
    mat = Material(E=210e9, nu=0.3)
    m.add_pyramid5(1, [1, 2, 3, 4, 5], mat)
    el = m.elements[1]
    assert el.volume() > 0


def test_chimney_case_builds_supported_loaded_solid():
    from casestudies.cs12_chimney import build_chimney_solid

    m, meta = build_chimney_solid(ntheta=8, nz=6)
    base_nodes = [nid for nid, node in m.nodes.items() if abs(node.z) < 1e-12]

    assert len(m.elements) < 8 * 6
    assert base_nodes
    assert m.nodal_loads
    assert all(len(set(m.dof_map[nid]).intersection(m._prescribed)) == 3
               for nid in base_nodes)
    assert meta["outer_faces"]


def test_mixed_case_is_single_positive_volume_object():
    from casestudies.cs11_mixed_elements import build_mixed_model

    mat = Material(E=30e9, nu=0.22)
    m, eid_by_name = build_mixed_model(mat)

    assert set(eid_by_name) == {"Hex8", "Wedge6", "Pyramid5", "Tet4", "Tet10"}
    assert all(m.elements[eid].volume() > 0.0 for eid in eid_by_name.values())
    assert len(m.nodes) < 30


def test_box_girder_solid_builds_thin_walled_volume():
    from casestudies.cs13_box_girder import build_box_girder_solid

    m, meta = build_box_girder_solid(nx=4, n_width=1, n_height=1)
    xs = [node.x for node in m.nodes.values()]
    ys = [node.y for node in m.nodes.values()]
    zs = [node.z for node in m.nodes.values()]

    assert len(m.elements) == 16
    assert min(xs) == 0.0
    assert max(xs) == meta["L"]
    assert min(ys) < 0.0 < max(ys)
    assert min(zs) < 0.0 < max(zs)
    assert meta["fixed_nodes"]
    assert meta["tip_nodes"]
