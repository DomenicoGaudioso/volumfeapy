"""Convergenza Hex8: cubo in trazione uniassiale."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from volumfeapy import Model, Material
from volumfeapy import postprocess

L = 1.0
F = 1e6
E = 210e9
nu = 0.3
A = 1.0
u_exact = F * L / (E * A)

print("Convergenza Hex8 - trazione uniassiale")
print(f"F = {F:.0f} N, L = {L} m, E = {E:.0f} Pa")
print(f"uz esatto = {u_exact:.6e}")
print(f"{'Mesh':>8s}  {'uz FEM':>12s}  {'errore %':>10s}")

for n_el in [1, 2, 4, 6, 8]:
    m = Model()
    nid = 1
    for k in range(n_el + 1):
        for j in range(n_el + 1):
            for i in range(n_el + 1):
                m.add_node(nid, i * L / n_el, j * L / n_el, k * L / n_el)
                nid += 1

    mat = Material(E=E, nu=nu)
    eid = 1
    n = n_el + 1
    for k in range(n_el):
        for j in range(n_el):
            for i in range(n_el):
                n1 = k * n * n + j * n + i + 1
                n2 = n1 + 1
                n3 = n1 + n + 1
                n4 = n1 + n
                n5 = n1 + n * n
                n6 = n2 + n * n
                n7 = n3 + n * n
                n8 = n4 + n * n
                m.add_hex8(eid, [n1, n2, n3, n4, n5, n6, n7, n8], mat)
                eid += 1

    for j in range(n):
        for i in range(n):
            nid = j * n + i + 1
            m.fix(nid)

    top_nodes = []
    for j in range(n):
        for i in range(n):
            nid = n_el * n * n + j * n + i + 1
            top_nodes.append(nid)

    f_per_node = F / len(top_nodes)
    for nid in top_nodes:
        m.add_nodal_load(nid, Fz=f_per_node)

    res = m.solve()
    u_max = max(res.displacement(nid, "uz") for nid in top_nodes)
    err = abs(u_max - u_exact) / u_exact * 100
    print(f"{n_el:4d}x{n_el}x{n_el}  {u_max:12.6e}  {err:10.4f}")
