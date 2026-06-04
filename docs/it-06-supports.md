---
layout: default
title: "06 - Vincoli"
parent: Italiano
nav_order: 6
---

# 06 - Vincoli e Condizioni al Contorno

## Tipi di vincolo

### Fisso

Tutti e 3 i GdL vincolati: `ux = 0`, `uy = 0`, `uz = 0`.

```python
m.fix(nodo)
```

Uso tipico: appoggi fissi, bordi incastrati.

### Vincolo personalizzato

Vincolo selettivo dei GdL:

```python
m.support(nodo, ux=True, uy=True, uz=False)
```

## Condizioni al contorno comuni

| Condizione | Codice | Significato fisico |
|------------|--------|-------------------|
| Fisso | `m.fix(n)` | ux=0, uy=0, uz=0 |
| Simmetria (x=cost) | `m.support(n, ux=True)` | ux=0 |
| Simmetria (y=cost) | `m.support(n, uy=True)` | uy=0 |
| Simmetria (z=cost) | `m.support(n, uz=True)` | uz=0 |
| Carrello (piano XY) | `m.support(n, uz=True)` | uz=0, ux/uy liberi |
| Libero | (niente) | Nessun vincolo |

## Condizioni di simmetria

Per un solido con simmetria rispetto al piano X-Y (a z=0):

```python
for nid in nodi_simmetria:
    m.support(nid, uz=True)
```

Per simmetria rispetto al piano X-Z (a y=0):

```python
for nid in nodi_simmetria:
    m.support(nid, uy=True)
```

Per simmetria rispetto al piano Y-Z (a x=0):

```python
for nid in nodi_simmetria:
    m.support(nid, ux=True)
```

## Cedimenti

Spostamenti imposti (valori prescritti non nulli):

```python
m.add_settlement(nodo, "uz", -0.005)    # 5 mm verso il basso
m.add_settlement(nodo, "ux", 0.001)     # 1 mm in direzione X
```

I cedimenti vengono applicati durante la fase di soluzione e influenzano il
vettore dei carichi.

## Requisiti di stabilità

Il modello deve avere vincoli sufficienti a prevenire moti rigidi:

- **Minimo**: almeno 3 nodi non allineati con tutti e 3 i GdL vincolati, o equivalente
- **Raccomandato**: condizioni al contorno appropriate su tutte le superfici vincolate

Se la matrice di rigidezza è singolare, `solve()` genera un `ValueError`.
