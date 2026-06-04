---
layout: default
title: "08 - Post-Processing"
parent: Italiano
nav_order: 8
---

# 08 - Post-Processing

Dopo la soluzione (`res = m.solve()`), è possibile calcolare tensioni, deformazioni
e spostamenti in qualsiasi punto all'interno di ogni elemento.

## Risultati nodali

```python
res.displacements(nodo)           # array [ux, uy, uz]
res.displacement(nodo, "uz")      # singolo GdL (float)
res.reactions(nodo)               # array [Fx, Fy, Fz]
```

## Tensioni nell'elemento

```python
from volumfeapy import postprocess

s = postprocess.element_stresses(res, elem_id)
# Restituisce dict: sxx, syy, szz, txy, tyz, txz, von_mises
```

Componenti (notazione di Voigt):
- `sxx`, `syy`, `szz`: tensioni normali
- `txy`, `tyz`, `txz`: tensioni tangenziali
- `von_mises`: tensione equivalente di von Mises

Le tensioni sono calcolate al centro dell'elemento (origine delle coordinate naturali).

## Tensione di von Mises

```python
vm = postprocess.von_mises(sigma)
```

La tensione equivalente di von Mises è:

```
σ_VM = √(0.5 · ((σxx−σyy)² + (σyy−σzz)² + (σzz−σxx)² + 6·(τxy² + τyz² + τxz²)))
```

Usata per criteri di snervamento di materiali duttili (Tresca/von Mises).

## Tensioni principali

```python
vals, vecs = postprocess.principal_stresses(sigma)
```

Restituisce:
- `vals`: tensioni principali `[σ1, σ2, σ3]` (ordinate in modo decrescente)
- `vecs`: direzioni principali (matrice 3×3, colonne = autovettori)

Le tensioni principali sono gli autovalori del tensore delle tensioni:

```
[σxx  τxy  τxz]
[τxy  σyy  τyz]
[τxz  τyz  σzz]
```

## Tensioni di tutti gli elementi

```python
all_s = postprocess.all_stresses(res)
# Restituisce dict: {elem_id: {sxx, syy, szz, txy, tyz, txz, von_mises}}
```

## Von Mises massimo

```python
eid, vm_max = postprocess.max_von_mises(res)
print(f"Max von Mises = {vm_max:.3e} Pa all'elemento {eid}")
```

## Spostamenti dell'elemento

```python
u_elem = postprocess.element_displacements(res, elem_id)
# Restituisce il vettore degli spostamenti nodali (n_dof,)
```

## Esempio completo

```python
res = m.solve()

# Spostamento massimo
u_max = max(np.linalg.norm(res.displacements(nid)) for nid in m.nodes)
print(f"u_max = {u_max:.4e} m")

# Tensioni al centro dell'elemento
s = postprocess.element_stresses(res, 1)
print(f"σxx = {s['sxx']:.3e} Pa")
print(f"σyy = {s['syy']:.3e} Pa")
print(f"σzz = {s['szz']:.3e} Pa")
print(f"von Mises = {s['von_mises']:.3e} Pa")

# Tensioni principali
vals, vecs = postprocess.principal_stresses(
    np.array([s['sxx'], s['syy'], s['szz'], s['txy'], s['tyz'], s['txz']]))
print(f"σ1 = {vals[0]:.3e} Pa")
print(f"σ2 = {vals[1]:.3e} Pa")
print(f"σ3 = {vals[2]:.3e} Pa")

# Von Mises massimo nel modello
eid, vm_max = postprocess.max_von_mises(res)
print(f"Max σ_VM = {vm_max:.3e} Pa all'elemento {eid}")
```

## Esempi di visualizzazione

Le seguenti immagini mostrano risultati tipici di post-processing per solidi 3D.

### Mensola (mesh Tet4)

![Mesh mensola](images/mesh_cantilever_tet4.png)
*Mesh tetraedrica di una mensola.*

![Mensola deformata](images/deformed_cantilever_tet4.png)
*Forma deformata di una mensola sotto carico in punta (scala 100×).*

![Von Mises mensola](images/stress_von_mises_cantilever.png)
*Tensione di von Mises [Pa] in una mensola. Massimo all'incastro.*

### Componenti di tensione

La funzione `plot_stress` può visualizzare qualsiasi componente di tensione:

```python
from volumfeapy.plotting import plot_stress

# Tensioni normali
plot_stress(res, "sxx").show()
plot_stress(res, "syy").show()
plot_stress(res, "szz").show()

# Tensioni tangenziali
plot_stress(res, "txy").show()
plot_stress(res, "tyz").show()
plot_stress(res, "txz").show()

# Von Mises
plot_stress(res, "von_mises").show()
```
