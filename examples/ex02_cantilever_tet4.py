"""Esempio: mensola 3D con Tet4 (cantilever beam)."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from volumfeapy import Model, Material
from volumfeapy import postprocess

L = 2.0
b = 0.1
h = 0.2
nx, ny, nz = 8, 1, 2

m = Model()
nid = 1
for k in range(nz + 1):
    for j in range(ny + 1):
        for i in range(nx + 1):
            m.add_node(nid, i * L / nx, j * b / ny, k * h / nz)
            nid += 1

mat = Material(E=210e9, nu=0.3)

eid = 1
for k in range(nz):
    for j in range(ny):
        for i in range(nx):
            n = (nx + 1) * (ny + 1)
            n1 = k * n + j * (nx + 1) + i + 1
            n2 = n1 + 1
            n3 = n1 + (nx + 1) + 1
            n4 = n1 + (nx + 1)
            n5 = n1 + n
            n6 = n2 + n
            n7 = n3 + n
            n8 = n4 + n

            m.add_tet4(eid, [n1, n2, n4, n5], mat)
            eid += 1
            m.add_tet4(eid, [n2, n3, n4, n7], mat)
            eid += 1
            m.add_tet4(eid, [n2, n5, n6, n7], mat)
            eid += 1
            m.add_tet4(eid, [n2, n4, n5, n7], mat)
            eid += 1
            m.add_tet4(eid, [n4, n5, n7, n8], mat)
            eid += 1

for nid_k in range(nz + 1):
    for nid_j in range(ny + 1):
        nid = nid_k * (nx + 1) * (ny + 1) + nid_j * (nx + 1) + 1
        m.fix(nid)

P = 1000.0
for j in range(ny + 1):
    for k in range(nz + 1):
        nid = k * (nx + 1) * (ny + 1) + j * (nx + 1) + nx + 1
        m.add_nodal_load(nid, Fz=-P / ((ny + 1) * (nz + 1)))

res = m.solve()

tip_nid = nz * (nx + 1) * (ny + 1) + (ny + 1) * (nx + 1) // 2 + nx + 1
u_tip = res.displacement(tip_nid, "uz")

I = b * h**3 / 12.0
u_exact = P * L**3 / (3 * mat.E * I)

print(f"Mensola 3D con Tet4 ({nx}x{ny}x{nz} blocchi, {eid - 1} tetraedri)")
print(f"P = {P:.0f} N, L = {L} m, b = {b} m, h = {h} m")
print(f"uz punta FEM    = {u_tip:.6e} m")
print(f"uz punta esatto = {u_exact:.6e} m")
print(f"Errore = {abs(u_tip - u_exact) / u_exact * 100:.2f}%")

eid_max, vm_max = postprocess.max_von_mises(res)
print(f"\nMax von Mises = {vm_max:.3e} Pa (elemento {eid_max})")
