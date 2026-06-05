"""Gmsh-based mesh generation and import helpers."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from volumfeapy.material import Material
from volumfeapy.model import Model

GMSH_TET4 = 4
GMSH_HEX8 = 5
GMSH_WEDGE6 = 6
GMSH_PYRAMID5 = 7
GMSH_TET10 = 11


def _import_gmsh() -> Any:
    try:
        import gmsh  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "Gmsh non e' installato. Installa l'extra opzionale con "
            '`pip install "volumfeapy[mesh]"` oppure `pip install gmsh`.'
        ) from exc
    return gmsh


def _chunks(values: Sequence[int], size: int) -> list[list[int]]:
    return [list(values[i:i + size]) for i in range(0, len(values), size)]


def _add_supported_element(model: Model, eid: int, gmsh_type: int,
                           node_ids: list[int], material: Material) -> bool:
    if gmsh_type == GMSH_TET4:
        model.add_tet4(eid, node_ids, material)
    elif gmsh_type == GMSH_TET10:
        model.add_tet10(eid, node_ids, material)
    elif gmsh_type == GMSH_HEX8:
        model.add_hex8(eid, node_ids, material)
    elif gmsh_type == GMSH_WEDGE6:
        model.add_wedge6(eid, node_ids, material)
    elif gmsh_type == GMSH_PYRAMID5:
        model.add_pyramid5(eid, node_ids, material)
    else:
        return False
    return True


def from_gmsh(material: Material, *, gmsh_module: Any | None = None,
              dim: int = 3) -> Model:
    """Convert the active Gmsh model mesh into a `volumfeapy.Model`.

    Parameters
    ----------
    material:
        Material assigned to every imported volumetric element.
    gmsh_module:
        Existing imported/initialized Gmsh module. If omitted, the function
        imports `gmsh` and reads the current active model.
    dim:
        Mesh dimension to import. The solver currently supports 3D elements.
    """
    gmsh = gmsh_module or _import_gmsh()
    model = Model()

    node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
    tag_to_id: dict[int, int] = {}
    coords = list(node_coords)
    for new_id, tag in enumerate(node_tags, start=1):
        tag_int = int(tag)
        tag_to_id[tag_int] = new_id
        i = 3 * (new_id - 1)
        model.add_node(new_id, float(coords[i]), float(coords[i + 1]),
                       float(coords[i + 2]))

    element_types, element_tags, element_node_tags = gmsh.model.mesh.getElements(dim)
    eid = 1
    skipped: list[int] = []
    for gmsh_type, tags, flat_nodes in zip(
        element_types, element_tags, element_node_tags
    ):
        gmsh_type = int(gmsh_type)
        if len(tags) == 0:
            continue
        nodes_per_element = len(flat_nodes) // len(tags)
        for gmsh_nodes in _chunks([int(n) for n in flat_nodes], nodes_per_element):
            node_ids = [tag_to_id[n] for n in gmsh_nodes]
            if _add_supported_element(model, eid, gmsh_type, node_ids, material):
                eid += 1
            elif gmsh_type not in skipped:
                skipped.append(gmsh_type)

    if not model.elements:
        raise ValueError(
            "La mesh Gmsh non contiene elementi volumetrici supportati "
            f"(tipi saltati: {skipped})."
        )
    return model


def mesh_box_tet(material: Material, lx: float, ly: float, lz: float, *,
                 mesh_size: float, order: int = 1,
                 origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
                 name: str = "box",
                 save_msh: str | Path | None = None) -> Model:
    """Generate a tetrahedral Gmsh mesh for a box and return a FEM model.

    `order=1` generates Tet4 elements; `order=2` generates Tet10 elements.
    The returned node and element IDs are compact and start from 1.
    """
    if order not in {1, 2}:
        raise ValueError("order deve essere 1 (Tet4) oppure 2 (Tet10).")
    if mesh_size <= 0:
        raise ValueError("mesh_size deve essere positivo.")

    gmsh = _import_gmsh()
    already_initialized = bool(getattr(gmsh, "isInitialized", lambda: 0)())
    if not already_initialized:
        gmsh.initialize()

    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add(name)
        x0, y0, z0 = origin
        gmsh.model.occ.addBox(x0, y0, z0, lx, ly, lz)
        gmsh.model.occ.synchronize()
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), mesh_size)
        gmsh.model.mesh.generate(3)
        if order == 2:
            gmsh.model.mesh.setOrder(2)
        if save_msh is not None:
            gmsh.write(str(save_msh))
        return from_gmsh(material, gmsh_module=gmsh, dim=3)
    finally:
        if not already_initialized:
            gmsh.finalize()
