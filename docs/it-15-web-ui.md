---
layout: default
title: "15 - Interfaccia Web"
parent: Italiano
nav_order: 15
---

# 15 - Interfaccia Web (Streamlit)

volumfeapy include un'applicazione web Streamlit per l'analisi interattiva di
solidi 3D.

## Installazione

```bash
pip install volumfeapy streamlit plotly
```

## Avvio

```bash
streamlit run app.py
```

L'app si apre nel browser predefinito a `http://localhost:8501`.

## Layout dell'interfaccia

L'interfaccia web ha tre tab:

### Modello

Definire il modello 3D attraverso tabelle modificabili:

- **Nodi**: ID nodo, coordinate X, Y, Z
- **Materiali**: nome materiale, E, nu, alpha, rho
- **Elementi**: ID elemento, tipo (hex8/tet4/tet10/wedge6/pyramid5), nodi (separati da virgola), materiale
- **Vincoli**: ID nodo, Ux, Uy, Uz (checkbox booleane)
- **Carichi nodali**: ID nodo, Fx, Fy, Fz, Caso

Cliccare **Applica modifiche** per ricostruire il modello.

### Analisi

Scegliere il tipo di analisi:

- **Statica**: risolvere il problema statico
- **Modale**: calcolare frequenze naturali e forme modali

Opzioni:
- Solver sparso (per modelli grandi)
- Numero di modi (per analisi modale)

### Risultati

Visualizzare i risultati:

- **Deformata**: mesh deformata 3D con fattore di scala
- **Mappe tensioni**: von Mises, sxx, syy, szz
- **Spostamenti nodali**: tabella di [ux, uy, uz] per nodo
- **Tabella tensioni**: von Mises e componenti di tensione per elemento
- **Forme modali**: visualizzazione 3D di ogni modo
- **Tabella frequenze**: frequenze naturali e periodi

## Flusso di lavoro esempio

1. **Definire nodi**: creare 8 nodi per un cubo unitario
2. **Aggiungere materiale**: E=210e9, nu=0.3
3. **Aggiungere elemento**: tipo=hex8, nodi=1,2,3,4,5,6,7,8
4. **Applicare vincoli**: fissare faccia inferiore (Ux=Uy=Uz=1 sui nodi 1-4)
5. **Applicare carico**: Fz=-10000 sui nodi superiori
6. **Eseguire analisi statica**
7. **Visualizzare risultati**: forma deformata, tensione di von Mises

## Screenshot

L'interfaccia web fornisce:
- Visualizzazione 3D interattiva (rotazione, zoom, pan)
- Tabelle modificabili con aggiunta/rimozione righe
- Anteprima del modello in tempo reale
- Selettore tipo elemento (dropdown)

## Limitazioni

- Nessuna generazione mesh (input manuale nodi/elementi)
- Nessun import Excel (pianificato)
- Nessun export HDF5 (pianificato)
- Limitato alle funzionalità disponibili nell'API Python

## Accesso programmatico

L'interfaccia web usa la stessa API Python della libreria:

```python
from volumfeapy import Model, Material

# L'interfaccia web costruisce questo modello dalle tabelle
m = Model()
# ... aggiungere nodi, elementi, carichi ...
res = m.solve()
```
