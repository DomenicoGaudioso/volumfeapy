---
layout: default
title: "04 - Element Types"
parent: English
nav_order: 4
---

# 04 - Element Types

volumfeapy provides five 3D solid element types, all with 3 DOFs per node
(`ux, uy, uz`).

## Hex8 — Hexahedron (8 nodes)

**Trilinear** hexahedral element (brick).

### Key features

- **8 nodes**, 24 DOFs total
- **Trilinear shape functions**: standard Q1 interpolation
- **2×2×2 Gauss integration** (8 points)
- Suitable for structured meshes

### Node ordering

```
    8 --- 7       top face (zeta=+1): 5,6,7,8
   /|    /|       bottom face (zeta=-1): 1,2,3,4
  5 --- 6 |
  | 4 --| 3
  |/    |/
  1 --- 2
```

```python
m.add_hex8(id, [1, 2, 3, 4, 5, 6, 7, 8], mat)
```

## Tet4 — Tetrahedron (4 nodes)

**Linear** tetrahedral element with constant strain.

### Key features

- **4 nodes**, 12 DOFs total
- **Linear shape functions**: constant strain/stress within element
- **Exact integration** with 1 Gauss point
- Suitable for unstructured meshes (automatic meshing)

### Limitations

- Stiff behavior (requires fine mesh for accuracy)
- Constant strain: stress jumps at element boundaries

```python
m.add_tet4(id, [1, 2, 3, 4], mat)
```

## Tet10 — Tetrahedron (10 nodes)

**Quadratic** tetrahedral element with linear strain variation.

### Key features

- **10 nodes** (4 vertices + 6 midside nodes), 30 DOFs total
- **Quadratic shape functions**: linear strain/stress variation
- **4-point Gauss integration** (order 2)
- Much more accurate than Tet4 with same mesh

### Node ordering

Nodes 1-4: vertices; nodes 5-10: midside nodes on edges:
(1-2), (2-3), (3-1), (1-4), (2-4), (3-4).

```python
m.add_tet10(id, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], mat)
```

## Wedge6 — Wedge/Prism (6 nodes)

**Triangular base × linear extrusion** element.

### Key features

- **6 nodes**, 18 DOFs total
- **Linear in triangle × linear in extrusion**
- **3×2 Gauss integration** (3 triangle points × 2 in zeta)
- Useful for transition zones between hex and tet meshes

### Node ordering

```
  6 --- 5       top (zeta=+1): 4,5,6
  |  /  |       bottom (zeta=-1): 1,2,3
  | /   |
  4 --- 3
   \   /
    \ /
     2
     |
     1
```

```python
m.add_wedge6(id, [1, 2, 3, 4, 5, 6], mat)
```

## Pyramid5 — Pyramid (5 nodes)

**Quadrilateral base + apex** element.

### Key features

- **5 nodes**, 15 DOFs total
- **Bilinear base × linear to apex**
- **2×2×2 Gauss integration**
- Useful for transition from hex to tet meshes

### Node ordering

```
      5           apex (zeta=+1): 5
     /|\          base (zeta=-1): 1,2,3,4
    / | \
   4--|--3
   |  |  |
   1--|--2
```

```python
m.add_pyramid5(id, [1, 2, 3, 4, 5], mat)
```

## Comparison

| Element | Nodes | DOFs | Integration | Order | Best for |
|---------|-------|------|-------------|-------|----------|
| Hex8 | 8 | 24 | 2×2×2 | Linear | Structured meshes |
| Tet4 | 4 | 12 | 1 pt | Linear | Auto-meshing (coarse) |
| Tet10 | 10 | 30 | 4 pt | Quadratic | Auto-meshing (accurate) |
| Wedge6 | 6 | 18 | 3×2 | Linear | Transition zones |
| Pyramid5 | 5 | 15 | 2×2×2 | Linear | Hex-tet transition |

## Recommendation

- **Structured geometry**: use Hex8 for best accuracy per DOF
- **Complex geometry**: use Tet10 (avoid Tet4 unless mesh is very fine)
- **Mixed meshes**: use Wedge6 and Pyramid5 for transitions
