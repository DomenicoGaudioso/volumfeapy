---
layout: default
title: "03 - Modello Strutturale"
parent: Italiano
nav_order: 3
---

# 03 - Modello Strutturale

## Nodi

Ogni nodo ha 3 gradi di libertà (GdL): `[ux, uy, uz]`.

```python
m.add_node(id, x, y, z)   # id = identificativo intero, coordinate in metri
```

Esempio:
```python
m.add_node(1, 0, 0, 0)    # origine
m.add_node(2, 5, 0, 0)    # 5 m lungo X
m.add_node(3, 5, 3, 0)    # 5 m in X, 3 m in Y
m.add_node(4, 0, 0, 4)    # 4 m in Z (verticale)
```

## Materiali

```python
mat = Material(E=210e9, nu=0.3, alpha=1.2e-5)   # acciaio
mat = Material(E=30e9, nu=0.2, alpha=1.0e-5)       # calcestruzzo
```

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `E` | Modulo di Young [Pa] | richiesto |
| `nu` | Coefficiente di Poisson | 0.3 |
| `alpha` | Coefficiente di dilatazione termica [1/°C] | 0.0 |
| `G` | Modulo di taglio [Pa] | calcolato da E e nu |
| `rho` | Densità [kg/m³] | 0.0 |

### Matrice costitutiva

Il materiale fornisce la matrice costitutiva D 6×6 (notazione di Voigt):

```python
D = mat.D_matrix()
# [σxx, σyy, σzz, τxy, τyz, τxz] = D @ [εxx, εyy, εzz, γxy, γyz, γxz]
```

## Elementi

### Aggiungere elementi

```python
# Esaedro (8 nodi)
m.add_hex8(id, [n1, n2, n3, n4, n5, n6, n7, n8], materiale)

# Tetraedro (4 nodi)
m.add_tet4(id, [n1, n2, n3, n4], materiale)

# Tetraedro (10 nodi, quadratico)
m.add_tet10(id, [n1, ..., n10], materiale)

# Cuneo (6 nodi)
m.add_wedge6(id, [n1, n2, n3, n4, n5, n6], materiale)

# Piramide (5 nodi)
m.add_pyramid5(id, [n1, n2, n3, n4, n5], materiale)
```

Vedi [Tipi di Elemento](it-04-element-types.md) per l'ordinamento dei nodi e i dettagli.

## Vincoli

```python
m.fix(nodo)                              # fisso: tutti e 3 i GdL vincolati
m.support(nodo, ux=True, uy=True)        # personalizzato: solo GdL specificati
```

| Metodo | GdL Vincolati | Uso tipico |
|--------|---------------|------------|
| `fix(n)` | ux, uy, uz | Appoggio fisso |
| `support(n,...)` | personalizzato | Carrello, simmetria, ecc. |

Esempi:
```python
# Appoggio fisso
m.fix(1)

# Piano di simmetria (ux=0)
m.support(2, ux=True)

# Carrello (uy=0, uz=0)
m.support(3, uy=True, uz=True)
```

## Soluzione

```python
res = m.solve()                   # solver denso (default)
res = m.solve(sparse=True)        # solver sparso (modelli grandi)
res = m.solve(cases=["G", "Q"])    # casi di carico specifici
```

Vedi [Soluzione](it-07-solution.md) per i dettagli.
