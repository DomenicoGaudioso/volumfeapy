"""volumfeapy - Solutore FEM per elementi volumetrici 3D.

Libreria didattica/ingegneristica per l'analisi statica e modale di
solidi 3D con elementi finiti.

Elementi disponibili:
  * Hex8 - esaedro (brick) a 8 nodi, trilineare
  * Tet4 - tetraedro a 4 nodi, lineare
  * Tet10 - tetraedro a 10 nodi, quadratico
  * Wedge6 - cuneo (prisma) a 6 nodi
  * Pyramid5 - piramide a 5 nodi

Funzionalita':
  * carichi nodali
  * forze di volume (body forces)
  * carico gravitazionale automatico
  * carichi termici
  * pressione su facce
  * cedimenti nodali
  * analisi modale
  * post-processing (tensioni, von Mises, tensioni principali)
  * visualizzazione Plotly

Esempio minimo:

    from volumfeapy import Model, Material

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
    m.add_hex8(1, [1,2,3,4,5,6,7,8], mat)
    for nid in range(1, 5):
        m.fix(nid)
    m.add_nodal_load(6, Fz=-10000)
    res = m.solve()
    print(res.displacements(6))
"""

from .material import Material
from .node import Node
from .element import Hex8, Tet4, Tet10, Wedge6, Pyramid5
from .loads import (
    NodalLoad, BodyForce, GravityLoad, ThermalLoad,
    FacePressure, Settlement,
)
from .model import Model, Result, ModalResult
from . import postprocess

__all__ = [
    "Material",
    "Node",
    "Hex8",
    "Tet4",
    "Tet10",
    "Wedge6",
    "Pyramid5",
    "NodalLoad",
    "BodyForce",
    "GravityLoad",
    "ThermalLoad",
    "FacePressure",
    "Settlement",
    "Model",
    "Result",
    "ModalResult",
    "postprocess",
]

__version__ = "0.1.0"
