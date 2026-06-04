"""Mensola 3D con Tet4: convergenza."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from volumfeapy import Model, Material
from volumfeapy import postprocess

L = 2.0
b = 0.1
h = 0.2
P = 1000.0
E = 210e9
nu = 0.3
I = b * h**3 / 12.0
u_exact = P * L**3 / (3 * E * I)

print(f"Mensola 3D con Tet4")
print(f"P = {P:.0f} N, L = {L} m, b = {b} m, h = {h} m")
print(f"uz esatto = {u_exact:.6e}")
print(f"{'Mesh':>12s}  {'Tet4':>6s}  {'uz FEM':>12s}  {'errore %':>10s}")

for nx in [4, 8, 12, 16]:
    ny = max(1, nx // 4)
    nz = max(1, nx // 4)

    m = Model()
    nid = 1
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                m.add_node(nid, i * L / nx, j * b / ny, k * h / nz)
                nid += 1

    mat = Material(E=E, nu=nu)
    eid = 1
    n = (nx + 1) * (ny + 1)
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n1 = k * n + j * (nx + 1) + i + 1
                n2 = n1 + 1
                n3 = n1 + (nx + 1) + 1
                n4 = n1 + (nx + 1)
                n5 = n1 + n
                n6 = n2 + n
                n7 = n3 + n
                n8 = n4 + n

                m.add_tet4(eid, [n1, n2, n4, n5], mat); eid += 1
                m.add_tet4(eid, [n2, n3, n4, n7], mat); eid += 1
                m.add_tet4(eid, [n2, n5, n6, n7], mat); eid += 1
                m.add_tet4(eid, [n2, n4, n5, n7], mat); eid += 1
                m.add_tet4(eid, [n4, n5, n7, n8], mat); eid += 1

    for nid_k in range(nz + 1):
        for nid_j in range(ny + 1):
            nid = nid_k * (nx + 1) * (ny + 1) + nid_j * (nx + 1) + 1
            m.fix(nid)

    for j in range(ny + 1):
        for k in range(nz + 1):
            nid = k * (nx + 1) * (ny + 1) + j * (nx + 1) + nx + 1
            m.add_nodal_load(nid, Fz=-P / ((ny + 1) * (nz + 1)))

    res = m.solve()
    tip_nid = nz * (nx + 1) * (ny + 1) + (ny + 1) * (nx + 1) // 2 + nx + 1
    u_tip = abs(res.displacement(tip_nid, "uz"))
    err = abs(u_tip - u_exact) / u_exact * 100
    print(f"{nx:4d}x{ny:2d}x{nz:2d}  {eid - 1:6d}  {u_tip:12.6e}  {err:10.2f}")
