---
layout: default
title: "11 - Conventions"
parent: English
nav_order: 11
---

# 11 - Conventions

## Nodal degrees of freedom

Each node has 3 DOFs in order: `[ux, uy, uz]`

- `ux`: translation along global X-axis
- `uy`: translation along global Y-axis
- `uz`: translation along global Z-axis

## Stress notation (Voigt)

Stresses are stored in Voigt notation as a 6-component vector:

```
[σxx, σyy, σzz, τxy, τyz, τxz]
```

- `σxx`, `σyy`, `σzz`: normal stresses
- `τxy`, `τyz`, `τxz`: shear stresses

## Strain notation

Strains follow the same Voigt convention:

```
[εxx, εyy, εzz, γxy, γyz, γxz]
```

where `γ = 2·ε` for shear components (engineering shear strain).

## Constitutive matrix

The material matrix D relates stresses to strains:

```
σ = D · ε
```

For isotropic materials:

```
D = E/((1+ν)(1-2ν)) · [1-ν  ν    ν    0      0      0   ]
                       [ν    1-ν  ν    0      0      0   ]
                       [ν    ν    1-ν  0      0      0   ]
                       [0    0    0    (1-2ν)/2  0   0   ]
                       [0    0    0    0      (1-2ν)/2 0 ]
                       [0    0    0    0      0      (1-2ν)/2]
```

## Element node ordering

See [Element Types](en-04-element-types.md) for detailed node ordering diagrams.

## Sign convention

- **Normal stresses**: positive = tension
- **Shear stresses**: positive when acting in the positive direction of the corresponding axis on a face with outward normal in the positive direction

## Units

The system is **unit-agnostic**: the user chooses units as long as they are consistent.

| Quantity | SI Unit |
|----------|---------|
| Length | m |
| Force | N |
| Stress | Pa (N/m²) |
| Temperature | °C |
| Density | kg/m³ |
| Gravity | m/s² |

## Natural coordinates

Element integration uses natural coordinates:

| Element | Coordinates | Range |
|---------|-------------|-------|
| Hex8 | (ξ, η, ζ) | [-1, 1]³ |
| Tet4/Tet10 | (L1, L2, L3, L4) | barycentric, Σ=1 |
| Wedge6 | (L1, L2, L3, ζ) | triangle × [-1, 1] |
| Pyramid5 | (ξ, η, ζ) | [-1, 1]² × [-1, 1] |
