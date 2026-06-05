"""Mesh generation helpers.

The meshing package keeps optional generators isolated from the core solver.
Install `volumfeapy[mesh]` to enable the Gmsh-backed functions.
"""

from .gmsh import from_gmsh, mesh_box_tet

__all__ = ["from_gmsh", "mesh_box_tet"]
