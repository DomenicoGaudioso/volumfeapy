---
layout: default
title: "05 - Carichi"
parent: Italiano
nav_order: 5
---

# 05 - Carichi

volumfeapy supporta tutti i principali tipi di carico per l'analisi statica di
solidi 3D.

## Carichi nodali

Forze applicate direttamente ai nodi (sistema globale):

```python
m.add_nodal_load(nodo, Fx=1000, Fy=-5000, Fz=0, case="G")
```

Tutti i parametri sono opzionali tranne il nodo. Le componenti sono in coordinate globali.

## Forze di volume

Forze di volume uniformi (es. inerzia, elettromagnetiche):

```python
# Forza di volume su un elemento
m.add_body_force(elem, bx=0, by=0, bz=-9810)    # es. peso fluido

# Applicare a tutti gli elementi
for eid in m.elements:
    m.add_body_force(eid, bz=-9810)
```

Le forze di volume sono convertite in forze nodali equivalenti tramite integrazione numerica:

```
f_i = ∫ N_i · b dV
```

## Carichi gravitazionali

Gravità automatica dalla densità del materiale:

```python
# Gravità in direzione -Z (default)
m.add_gravity(g=9.81, direction="z")

# Gravità in direzione -Y
m.add_gravity(g=9.81, direction="y")
```

La forza di volume è calcolata come `b = -ρ · g` nella direzione specificata.
Richiede `rho > 0` nella definizione del materiale.

## Carichi termici

Variazione di temperatura uniforme:

```python
m.add_thermal_load(elem, dT=50.0)    # aumento di 50°C
```

La deformazione termica è:

```
ε_th = α · ΔT · [1, 1, 1, 0, 0, 0]
```

Questo produce tensioni termiche quando la deformazione è vincolata.

## Pressioni su facce

Pressione su facce degli elementi:

```python
m.add_face_pressure(elem, face=0, p=-1e6)    # 1 MPa sulla faccia 0
```

## Cedimenti

Spostamenti imposti ai nodi:

```python
m.add_settlement(nodo, "uz", -0.005)    # 5 mm verso il basso
m.add_settlement(nodo, "ux", 0.001)     # 1 mm in X
```

Il GdL può essere: `ux`, `uy`, `uz`.

## Assegnazione ai Casi di Carico

Ogni carico può avere un `case`:

```python
m.add_nodal_load(2, Fz=-10000, case="G")          # permanente
m.add_body_force(1, bz=-9810, case="G")            # permanente
m.add_nodal_load(5, Fx=30000, case="Q")             # variabile
m.add_thermal_load(3, dT=30.0, case="T")             # termico

m.load_cases()                    # → ['G', 'Q', 'T']
res = m.solve(cases=["G", "Q"])    # combinazione
res = m.solve(cases="G")           # singolo caso
res = m.solve()                     # tutti i carichi
```

## Combinazioni con coefficienti

```python
res = m.solve(cases={"G": 1.35, "Q": 1.5})        # combinazione SLU
res = m.solve(cases={"G": 1.0, "Q": 0.3})          # combinazione SLE
```

Tutti i risultati (spostamenti, reazioni, tensioni) rispettano i coefficienti.

## Esempi illustrati

**Mensola sotto peso proprio:**

```python
m = Model()
# ... creare mesh ...
mat = Material(E=210e9, nu=0.3, rho=7850.0)
# ... aggiungere elementi ...
m.add_gravity(g=9.81, direction="z")
for nid in nodi_fissi:
    m.fix(nid)
res = m.solve()
```

Vedi [Esempi d'Uso](it-14-usage-examples.md) per script completi.
