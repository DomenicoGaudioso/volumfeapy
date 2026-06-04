"""Validazione: cubo Hex8 in trazione uniassiale."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from volumfeapy import Model, Material
from volumfeapy import postprocess

L = 1.0
F = 1e6
E = 210e9
nu = 0.3
A = 1.0

print("Validazione Hex8 - trazione uniassiale")
print(f"u_esatto = {F * L / (E * A):.6e}")
print(f"sigma_esatto = {F / A:.6e}")

m = Model()
m.add_node(1, 0, 0, 0)
m.add_node(2, L, 0, 0)
m.add_node(3, L, L, 0)
m.add_node(4, 0, L, 0)
m.add_node(5, 0, 0, L)
m.add_node(6, L, 0, L)
m.add_node(7, L, L, L)
m.add_node(8, 0, L, L)

mat = Material(E=E, nu=nu)
m.add_hex8(1, [1, 2, 3, 4, 5, 6, 7, 8], mat)

for nid in [1, 2, 3, 4]:
    m.fix(nid)

for nid in [5, 6, 7, 8]:
    m.add_nodal_load(nid, Fz=F / 4.0)

res = m.solve()

print(f"\nSpostamenti nodi superiori:")
for nid in [5, 6, 7, 8]:
    u = res.displacements(nid)
    print(f"  Nodo {nid}: uz = {u[2]:.6e}")

s = postprocess.element_stresses(res, 1)
print(f"\nTensioni al centro:")
print(f"  szz = {s['szz']:.6e}  (esatto: {F / A:.6e})")
print(f"  von Mises = {s['von_mises']:.6e}")

vals, vecs = postprocess.principal_stresses(
    np.array([s['sxx'], s['syy'], s['szz'], s['txy'], s['tyz'], s['txz']]))
print(f"\nTensioni principali: {vals}")
