---
layout: default
title: "13 - Test e Validazione"
parent: Italiano
nav_order: 13
---

# 13 - Test e Validazione

## Esecuzione test

```bash
pip install -e ".[dev]"
python -m pytest tests -v
```

## Copertura test

La suite di test include:

| Test | Descrizione |
|------|-------------|
| `test_hex8_stiffness_symmetry` | Simmetria matrice K Hex8 |
| `test_hex8_stiffness_positive_diagonal` | Diagonale K Hex8 non negativa |
| `test_hex8_volume` | Calcolo volume unitario Hex8 |
| `test_hex8_uniaxial_tension` | Trazione uniassiale Hex8 vs analitico |
| `test_tet4_stiffness_symmetry` | Simmetria matrice K Tet4 |
| `test_tet4_volume` | Calcolo volume Tet4 |
| `test_tet4_stresses_constant` | Campo di tensione costante Tet4 |
| `test_settlement` | Spostamento imposto |
| `test_gravity_load` | Applicazione carico gravitazionale |
| `test_modal_analysis` | Analisi modale (frequenze positive) |
| `test_von_mises` | Calcolo tensione di von Mises |
| `test_principal_stresses` | Calcolo tensioni principali |
| `test_wedge6_volume` | Calcolo volume Wedge6 |
| `test_pyramid5_volume` | Calcolo volume Pyramid5 |

## Validazione analitica

### Trazione uniassiale (Hex8)

Per un cubo unitario in trazione uniassiale F:

```
σ_zz = F / A
u_z = F · L / (E · A)
```

L'elemento Hex8 riproduce questo esattamente per una mesh a singolo elemento.

### Mensola (Tet4)

Per una mensola (L × b × h) con carico in punta P:

```
u_punta = P · L³ / (3 · E · I)
```

dove `I = b·h³/12`. Gli elementi Tet4 richiedono una mesh fine per accuratezza
(limitazione della deformazione costante).

## Script di validazione

```bash
python validation/validate_hex8_tension.py
```

Questo script esegue un test di trazione uniassiale su un singolo elemento Hex8
e stampa spostamenti e tensioni confrontati con la soluzione analitica.

## Limitazioni note

1. **Elemento Tet4**: deformazione/tensione costante all'interno di ogni elemento.
   Richiede mesh molto fine per risultati accurati. Usare Tet10 per migliore accuratezza.

2. **Elemento Hex8**: interpolazione trilineare. Può mostrare locking volumetrico
   per materiali quasi incomprimibili (ν → 0.5).

3. **Elemento Pyramid5**: usa derivazione numerica per le derivate delle funzioni
   di forma. L'accuratezza può essere ridotta vicino all'apice.

4. **Elemento Wedge6**: interpolazione lineare. Limitazioni simili al Tet4.

5. **Distorsione mesh**: elementi altamente distorti riducono l'accuratezza.
   Mantenere rapporto d'aspetto < 5 e Jacobiano > 0 ovunque.

## Confronto con la letteratura

Le formulazioni degli elementi seguono i libri di testo standard FEM:

- Zienkiewicz, O.C., Taylor, R.L. (2000). *The Finite Element Method*, Vol. 1.
  Butterworth-Heinemann.
- Hughes, T.J.R. (1987). *The Finite Element Method*. Prentice-Hall.
- Bathe, K.J. (1996). *Finite Element Procedures*. Prentice-Hall.
