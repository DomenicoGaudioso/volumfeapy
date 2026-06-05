---
layout: default
title: "09 - Grafici Plotly"
parent: Italiano
nav_order: 9
---

# 09 - Grafici Plotly

volumfeapy fornisce 4 funzioni di visualizzazione interattiva basate su Plotly.

## Installazione

```bash
pip install volumfeapy[plot]
```

## Funzioni disponibili

### plot_mesh(m, show_node_ids=True)

Visualizzazione 3D della mesh con ID dei nodi e bordi degli elementi:

```python
from volumfeapy.plotting import plot_mesh
fig = plot_mesh(m)
fig.show()
```

Disegna i bordi degli elementi secondo il tipo:
- Hex8: 12 bordi
- Tet4: 6 bordi
- Wedge6: 9 bordi
- Pyramid5: 8 bordi

### plot_deformed(result, scale=1.0)

Mesh deformata 3D sovrapposta alla geometria non deformata:

```python
from volumfeapy.plotting import plot_deformed
plot_deformed(res, scale=100).show()
```

Il modello indeformato e' disegnato come riferimento trasparente; la mesh
deformata e' colorata in base alla norma reale dello spostamento `|u|`.

### plot_stress(result, component="von_mises", title=None)

Mappa a colori 3D delle tensioni sulle facce esterne visibili della mesh:

```python
from volumfeapy.plotting import plot_stress

# Tensione di von Mises
plot_stress(res, "von_mises").show()

# Tensioni normali
plot_stress(res, "sxx").show()
plot_stress(res, "syy").show()
plot_stress(res, "szz").show()

# Tensioni tangenziali
plot_stress(res, "txy").show()
```

Componenti disponibili: `sxx`, `syy`, `szz`, `txy`, `tyz`, `txz`, `von_mises`.

Le tensioni sono recuperate ai nodi dell'elemento dove la formulazione lo
consente, mediate sui nodi condivisi della mesh e interpolate sulle facce
esterne. In questo modo si ottiene un contour FEM continuo sulla pelle reale
della mesh, non marker isolati.

### plot_mode(modal_result, i=0, scale=1.0)

Visualizzazione 3D della forma modale:

```python
from volumfeapy.plotting import plot_mode

# Primo modo
plot_mode(mr, i=0, scale=100).show()

# Ciclo sui modi
for i in range(min(6, len(mr.freq))):
    plot_mode(mr, i=i, scale=100).show()
```

## Salvataggio figure

```python
fig = plot_stress(res, "von_mises")
fig.write_html("tensione_von_mises.html", include_plotlyjs="cdn")
fig.write_image("tensione_von_mises.png", width=1200, height=800)  # richiede kaleido
```

## Esempio completo

```python
from volumfeapy import Model, Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress

# Creare modello
m = Model()
# ... aggiungere nodi, elementi, carichi ...
res = m.solve()

# Visualizzare
plot_mesh(m).show()
plot_deformed(res, scale=100).show()
plot_stress(res, "von_mises").show()
plot_stress(res, "szz").show()
```

## Mappe di colore

Tutti i grafici delle tensioni usano la scala di colori `RdYlBu`:
- **Rosso**: alti valori positivi
- **Blu**: valori bassi/negativi
- **Giallo/bianco**: vicino allo zero

La barra dei colori mostra l'intervallo di valori con le unità.
