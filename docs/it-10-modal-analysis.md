---
layout: default
title: "10 - Analisi Modale"
parent: Italiano
nav_order: 10
---

# 10 - Analisi Modale

## Frequenze naturali e forme modali

```python
mr = m.modal(n_modes=6)

for i in range(len(mr.freq)):
    print(f"Modo {i+1}: f = {mr.freq[i]:.3f} Hz, T = {mr.period[i]:.3f} s")
```

`modal()` risolve il problema agli autovalori `K φ = ω² M φ` sui GdL liberi.

## Matrice di massa

La matrice di massa è **concentrata** (diagonale) e calcolata dalla densità
degli elementi:

```python
M = m.assemble_mass()    # vettore di massa diagonale (ndof,)
```

Massa per nodo:

```
m_nodo = ρ · V_elemento / n_nodi
```

dove `V_elemento` è il volume dell'elemento e `n_nodi` è il numero di nodi.

## Oggetto Result

```python
mr = m.modal(n_modes=10)

mr.omega          # pulsazioni [rad/s]
mr.freq           # frequenze naturali [Hz]
mr.period         # periodi [s]
mr.phi            # forme modali (ndof × n_modi)

# Singolo modo
mr.mode(i)                    # vettore forma modale (ndof,)
mr.mode_shape(i, nodo)        # [ux, uy, uz] al nodo
```

## Visualizzazione

```python
from volumfeapy.plotting import plot_mode

# Primo modo
plot_mode(mr, i=0, scale=100).show()

# Ciclo sui modi
for i in range(min(6, len(mr.freq))):
    plot_mode(mr, i=i, scale=100).show()
```

## Confronto analitico

Per una mensola (L × b × h), la prima frequenza di flessione è:

```
f_1 = (1.875² / (2π·L²)) · √(E·I / (ρ·A))
```

dove `I = b·h³/12` e `A = b·h`.

### Esempio: mensola in acciaio

```python
import numpy as np

L = 2.0
b = 0.1
h = 0.2
E = 210e9
rho = 7850.0

I = b * h**3 / 12
A = b * h

f_1 = (1.875**2 / (2 * np.pi * L**2)) * np.sqrt(E * I / (rho * A))
print(f"f_1 analitica = {f_1:.3f} Hz")

# Confronto con FEM
mr = m.modal(n_modes=1)
print(f"f_1 FEM        = {mr.freq[0]:.3f} Hz")
```

## Requisiti

- Il materiale deve avere `rho > 0` (densità)
- Vincoli sufficienti a prevenire modi di corpo rigido
- I GdL liberi senza massa sono eliminati per condensazione statica

Se `rho = 0`, `modal()` genera:
```
ValueError: Massa nulla: impostare rho nel materiale.
```
