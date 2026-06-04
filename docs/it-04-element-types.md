---
layout: default
title: "04 - Tipi di Elemento"
parent: Italiano
nav_order: 4
---

# 04 - Tipi di Elemento

volumfeapy fornisce cinque tipi di elementi solidi 3D, tutti con 3 GdL per nodo
(`ux, uy, uz`).

## Hex8 — Esaedro (8 nodi)

Elemento esaedrico **trilineare** (brick).

### Caratteristiche principali

- **8 nodi**, 24 GdL totali
- **Funzioni di forma trilineari**: interpolazione Q1 standard
- **Integrazione 2×2×2 Gauss** (8 punti)
- Adatto per mesh strutturate

### Ordinamento nodi

```
    8 --- 7       faccia superiore (zeta=+1): 5,6,7,8
   /|    /|       faccia inferiore (zeta=-1): 1,2,3,4
  5 --- 6 |
  | 4 --| 3
  |/    |/
  1 --- 2
```

```python
m.add_hex8(id, [1, 2, 3, 4, 5, 6, 7, 8], mat)
```

## Tet4 — Tetraedro (4 nodi)

Elemento tetraedrico **lineare** con deformazione costante.

### Caratteristiche principali

- **4 nodi**, 12 GdL totali
- **Funzioni di forma lineari**: deformazione/tensione costante nell'elemento
- **Integrazione esatta** con 1 punto di Gauss
- Adatto per mesh non strutturate (meshing automatico)

### Limitazioni

- Comportamento rigido (richiede mesh fine per accuratezza)
- Deformazione costante: salti di tensione ai bordi degli elementi

```python
m.add_tet4(id, [1, 2, 3, 4], mat)
```

## Tet10 — Tetraedro (10 nodi)

Elemento tetraedrico **quadratico** con variazione lineare della deformazione.

### Caratteristiche principali

- **10 nodi** (4 vertici + 6 nodi medi), 30 GdL totali
- **Funzioni di forma quadratiche**: variazione lineare di deformazione/tensione
- **Integrazione 4 punti Gauss** (ordine 2)
- Molto più accurato del Tet4 con la stessa mesh

### Ordinamento nodi

Nodi 1-4: vertici; nodi 5-10: nodi medi sugli spigoli:
(1-2), (2-3), (3-1), (1-4), (2-4), (3-4).

```python
m.add_tet10(id, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], mat)
```

## Wedge6 — Cuneo/Prisma (6 nodi)

Elemento **base triangolare × estrusione lineare**.

### Caratteristiche principali

- **6 nodi**, 18 GdL totali
- **Lineare nel triangolo × lineare in estrusione**
- **Integrazione 3×2 Gauss** (3 punti triangolo × 2 in zeta)
- Utile per zone di transizione tra mesh hex e tet

```python
m.add_wedge6(id, [1, 2, 3, 4, 5, 6], mat)
```

## Pyramid5 — Piramide (5 nodi)

Elemento **base quadrilatera + apice**.

### Caratteristiche principali

- **5 nodi**, 15 GdL totali
- **Bilineare sulla base × lineare verso l'apice**
- **Integrazione 2×2×2 Gauss**
- Utile per transizione da mesh hex a tet

```python
m.add_pyramid5(id, [1, 2, 3, 4, 5], mat)
```

## Confronto

| Elemento | Nodi | GdL | Integrazione | Ordine | Ideale per |
|----------|------|-----|--------------|--------|------------|
| Hex8 | 8 | 24 | 2×2×2 | Lineare | Mesh strutturate |
| Tet4 | 4 | 12 | 1 pt | Lineare | Auto-meshing (grezzo) |
| Tet10 | 10 | 30 | 4 pt | Quadratico | Auto-meshing (accurato) |
| Wedge6 | 6 | 18 | 3×2 | Lineare | Zone di transizione |
| Pyramid5 | 5 | 15 | 2×2×2 | Lineare | Transizione hex-tet |

## Raccomandazione

- **Geometria strutturata**: usare Hex8 per la migliore accuratezza per GdL
- **Geometria complessa**: usare Tet10 (evitare Tet4 a meno che la mesh sia molto fine)
- **Mesh miste**: usare Wedge6 e Pyramid5 per le transizioni
