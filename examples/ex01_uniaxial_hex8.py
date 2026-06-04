"""Esempio: cubo unitario in trazione uniassiale con Hex8."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from volumfeapy import Model, Material
from volumfeapy import postprocess

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

for nid in [1, 2, 3, 4]:
    m.fix(nid)

F = 1e6
for nid in [5, 6, 7, 8]:
    m.add_nodal_load(nid, Fz=F / 4.0)

res = m.solve()

print("Cubo unitario in trazione uniassiale (Hex8)")
print(f"F = {F:.0f} N, A = 1 m^2, L = 1 m, E = {mat.E:.0f} Pa")
print()
for nid in range(1, 9):
    u = res.displacements(nid)
    print(f"  Nodo {nid}: ux={u[0]:.6e}, uy={u[1]:.6e}, uz={u[2]:.6e}")

s = postprocess.element_stresses(res, 1)
print(f"\nTensioni al centro:")
print(f"  sxx = {s['sxx']:.3e}")
print(f"  syy = {s['syy']:.3e}")
print(f"  szz = {s['szz']:.3e}")
print(f"  von Mises = {s['von_mises']:.3e}")

u_exact = F * 1.0 / (mat.E * 1.0)
u_fem = res.displacement(5, "uz")
print(f"\nuz esatto = {u_exact:.6e}")
print(f"uz FEM    = {u_fem:.6e}")
print(f"Errore    = {abs(u_fem - u_exact) / u_exact * 100:.4f}%")
