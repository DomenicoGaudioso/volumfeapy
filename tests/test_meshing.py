"""Tests for optional meshing helpers."""

import numpy as np
import pytest

from volumfeapy import Material
from volumfeapy.meshing import from_gmsh, mesh_box_tet


def test_from_gmsh_imports_tet4_from_fake_module():
    class FakeMesh:
        @staticmethod
        def getNodes():
            return (
                np.array([10, 20, 30, 40]),
                np.array([
                    0.0, 0.0, 0.0,
                    1.0, 0.0, 0.0,
                    0.0, 1.0, 0.0,
                    0.0, 0.0, 1.0,
                ]),
                [],
            )

        @staticmethod
        def getElements(dim):
            assert dim == 3
            return (
                np.array([4]),
                [np.array([1])],
                [np.array([10, 20, 30, 40])],
            )

    class FakeModel:
        mesh = FakeMesh()

    class FakeGmsh:
        model = FakeModel()

    mat = Material(E=30e9, nu=0.2)
    m = from_gmsh(mat, gmsh_module=FakeGmsh())

    assert len(m.nodes) == 4
    assert len(m.elements) == 1
    assert list(m.elements[1].node_ids) == [1, 2, 3, 4]


def test_mesh_box_tet_requires_gmsh_when_used():
    gmsh = pytest.importorskip("gmsh")
    mat = Material(E=30e9, nu=0.2)

    m = mesh_box_tet(mat, 1.0, 0.5, 0.25, mesh_size=0.6, order=1)

    assert len(m.nodes) >= 4
    assert len(m.elements) >= 1
    assert all(el.__class__.__name__ == "Tet4" for el in m.elements.values())
    assert not bool(getattr(gmsh, "isInitialized", lambda: 0)())


def test_mesh_box_tet_order2_generates_tet10():
    pytest.importorskip("gmsh")
    mat = Material(E=30e9, nu=0.2)

    m = mesh_box_tet(mat, 1.0, 0.5, 0.25, mesh_size=0.7, order=2)

    assert len(m.elements) >= 1
    assert all(el.__class__.__name__ == "Tet10" for el in m.elements.values())
