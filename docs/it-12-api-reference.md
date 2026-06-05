---
layout: default
title: "12 - Riferimento API"
parent: Italiano
nav_order: 12
---

# 12 - Riferimento API

Riferimento completo di tutte le funzioni pubbliche in **volumfeapy**.

Import tipico:

```python
from volumfeapy import Model, Material
from volumfeapy import postprocess
from volumfeapy.plotting import (plot_mesh, plot_deformed, plot_stress, plot_mode)
```

---

## Materiali

### `Material(E, nu=0.3, alpha=0.0, G=None, rho=0.0, name="")`
Materiale elastico isotropo. `G` (modulo di taglio) è derivato come
`E/(2(1+nu))` se non fornito. `alpha` = dilatazione termica; `rho` = densità.

Metodi:
- `D_matrix()` → matrice costitutiva 6×6 (notazione di Voigt)

---

## Modello

### `Model()`
Contenitore del modello FEM. Attributi: `nodes`, `elements`, `nodal_loads`,
`body_forces`, `gravity_loads`, `thermal_loads`, `face_pressures`, `settlements`.

### `add_node(id, x, y, z) -> Node`
Aggiunge un nodo (3 GdL: `ux, uy, uz`).

### Metodi per elementi
- **`add_hex8(id, node_ids, materiale) -> Hex8`** — esaedro a 8 nodi
- **`add_tet4(id, node_ids, materiale) -> Tet4`** — tetraedro a 4 nodi
- **`add_tet10(id, node_ids, materiale) -> Tet10`** — tetraedro a 10 nodi
- **`add_wedge6(id, node_ids, materiale) -> Wedge6`** — cuneo a 6 nodi
- **`add_pyramid5(id, node_ids, materiale) -> Pyramid5`** — piramide a 5 nodi

### Vincoli
- **`fix(nodo, dofs=None)`** — vincola i GdL elencati; `None` = tutti e 3 (fisso).
- **`support(nodo, ux=False, uy=False, uz=False)`** — vincolo selettivo.

### `add_settlement(nodo, dof, valore) -> Settlement`
Cedimento (spostamento imposto): `dof` ∈ `{ux, uy, uz}`.

---

## Carichi

Tutti i metodi `add_*` accettano `case="..."` (caso di carico, default `"default"`).

### `add_nodal_load(nodo, case="default", Fx=0, Fy=0, Fz=0) -> NodalLoad`
Forza concentrata a un nodo (sistema globale).

### `add_body_force(elem, bx=0, by=0, bz=0, case="default") -> BodyForce`
Forza di volume uniforme [N/m³] su un elemento.

### `add_gravity(g=9.81, direction="z", case="default") -> GravityLoad`
Gravità automatica dalla densità del materiale. `direction` ∈ `{x, y, z}`.

### `add_thermal_load(elem, dT, case="default") -> ThermalLoad`
Variazione di temperatura uniforme [°C]. Produce deformazione termica `ε = α·ΔT`.

### `add_face_pressure(elem, face, p, case="default") -> FacePressure`
Pressione su una faccia dell'elemento [Pa].

---

## Soluzione

### `load_cases() -> list[str]`
Lista ordinata dei casi di carico presenti nei carichi.

### `solve(sparse=False, cases=None) -> Result`
Risolve il sistema.
- `sparse`: `True` usa il solver sparso scipy (modelli grandi).
- `cases`: combinazione di carico —
  - `None` = tutti i carichi (coeff 1);
  - stringa = un singolo caso di carico;
  - lista/set = combinazione (coeff 1 ciascuno);
  - **dict `{case: coefficiente}`** = combinazione con coefficienti moltiplicativi.

### `modal(n_modes=10) -> ModalResult`
Analisi modale: risolve `K φ = ω² M φ`. Richiede `rho > 0` nei materiali.

---

## Risultati

### `Result`
Attributi: `U` (spostamenti globali), `R` (reazioni globali),
`element_forces` (forze nodali per elemento).

- **`displacements(nodo) -> ndarray(3)`** — `[ux, uy, uz]` del nodo.
- **`displacement(nodo, dof) -> float`** — singola componente.
- **`reactions(nodo) -> ndarray(3)`** — `[Fx, Fy, Fz]` del nodo.

### `ModalResult`
Attributi: `omega` [rad/s], `freq` [Hz], `period` [s], `phi` (ndof × n_modi).

- **`mode(i) -> ndarray(ndof)`** — vettore i-esima forma modale.
- **`mode_shape(i, nodo) -> ndarray(3)`** — `[ux, uy, uz]` al nodo.

---

## Post-processing (`volumfeapy.postprocess`)

### `element_stresses(result, elem_id) -> dict`
Tensioni al centro dell'elemento. Restituisce `{sxx, syy, szz, txy, tyz, txz, von_mises}`.

### `von_mises(sigma) -> float`
Tensione equivalente di von Mises da vettore tensioni a 6 componenti.

### `principal_stresses(sigma) -> tuple[ndarray, ndarray]`
Tensioni e direzioni principali: `(valori, vettori)`.

### `element_displacements(result, elem_id) -> ndarray`
Vettore spostamenti nodali dell'elemento.

### `all_stresses(result) -> dict`
Tensioni al centro di tutti gli elementi: `{elem_id: {sxx, ..., von_mises}}`.

### `max_von_mises(result) -> tuple[int, float]`
ID elemento e tensione di von Mises massima: `(elem_id, vm_max)`.

---

## Visualizzazione (`volumfeapy.plotting`)

Richiede l'extra `plot` (`plotly`, `kaleido`). Ogni funzione restituisce un
`plotly.graph_objects.Figure`.

- **`plot_mesh(model, show_node_ids=True)`** — mesh 3D con bordi e ID nodi.
- **`plot_deformed(result, scale=1.0)`** — mesh deformata 3D.
- **`plot_stress(result, component="von_mises", subdivisions=5)`** — contorno tensioni 3D con facce esterne suddivise.
- **`plot_mode(modal_result, i=0, scale=1.0)`** — i-esima forma modale.
