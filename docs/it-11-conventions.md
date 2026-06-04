---
layout: default
title: "11 - Convenzioni"
parent: Italiano
nav_order: 11
---

# 11 - Convenzioni

## Gradi di libertà nodali

Ogni nodo ha 3 GdL in ordine: `[ux, uy, uz]`

- `ux`: traslazione lungo l'asse X globale
- `uy`: traslazione lungo l'asse Y globale
- `uz`: traslazione lungo l'asse Z globale

## Notazione delle tensioni (Voigt)

Le tensioni sono memorizzate in notazione di Voigt come vettore a 6 componenti:

```
[σxx, σyy, σzz, τxy, τyz, τxz]
```

- `σxx`, `σyy`, `σzz`: tensioni normali
- `τxy`, `τyz`, `τxz`: tensioni tangenziali

## Notazione delle deformazioni

Le deformazioni seguono la stessa convenzione di Voigt:

```
[εxx, εyy, εzz, γxy, γyz, γxz]
```

dove `γ = 2·ε` per le componenti tangenziali (deformazione di taglio ingegneristica).

## Matrice costitutiva

La matrice del materiale D lega tensioni e deformazioni:

```
σ = D · ε
```

Per materiali isotropi:

```
D = E/((1+ν)(1-2ν)) · [1-ν  ν    ν    0      0      0   ]
                       [ν    1-ν  ν    0      0      0   ]
                       [ν    ν    1-ν  0      0      0   ]
                       [0    0    0    (1-2ν)/2  0   0   ]
                       [0    0    0    0      (1-2ν)/2 0 ]
                       [0    0    0    0      0      (1-2ν)/2]
```

## Ordinamento nodi degli elementi

Vedi [Tipi di Elemento](it-04-element-types.md) per i diagrammi dettagliati
dell'ordinamento dei nodi.

## Convenzione dei segni

- **Tensioni normali**: positivo = trazione
- **Tensioni tangenziali**: positive quando agiscono nella direzione positiva dell'asse corrispondente su una faccia con normale esterna nella direzione positiva

## Unità di misura

Il sistema è **agnostico rispetto alle unità**: l'utente sceglie le unità purché
siano coerenti.

| Grandezza | Unità SI |
|-----------|----------|
| Lunghezza | m |
| Forza | N |
| Tensione | Pa (N/m²) |
| Temperatura | °C |
| Densità | kg/m³ |
| Gravità | m/s² |

## Coordinate naturali

L'integrazione degli elementi usa coordinate naturali:

| Elemento | Coordinate | Intervallo |
|----------|------------|------------|
| Hex8 | (ξ, η, ζ) | [-1, 1]³ |
| Tet4/Tet10 | (L1, L2, L3, L4) | baricentriche, Σ=1 |
| Wedge6 | (L1, L2, L3, ζ) | triangolo × [-1, 1] |
| Pyramid5 | (ξ, η, ζ) | [-1, 1]² × [-1, 1] |
