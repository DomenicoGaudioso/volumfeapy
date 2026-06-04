---
layout: default
title: "16 - Shape Functions"
parent: English
nav_order: 16
---

# 16 - Shape Functions

Shape functions are the mathematical foundation of the finite element method. They interpolate the displacement field within an element from the nodal values.

## Hex8 Element (Hexahedron 8-node)

The Hex8 element uses **trilinear shape functions** defined in natural coordinates (ξ, η, ζ) ∈ [-1, 1]³.

### Shape Function Definitions

For a hexahedral element with nodes numbered according to the convention:

```
Nᵢ(ξ,η,ζ) = ⅛(1 + ξᵢ·ξ)(1 + ηᵢ·η)(1 + ζᵢ·ζ)
```

where (ξᵢ, ηᵢ, ζᵢ) are the natural coordinates of node i:

| Node | ξᵢ | ηᵢ | ζᵢ |
|------|----|----|----|
| 1 | -1 | -1 | -1 |
| 2 | +1 | -1 | -1 |
| 3 | +1 | +1 | -1 |
| 4 | -1 | +1 | -1 |
| 5 | -1 | -1 | +1 |
| 6 | +1 | -1 | +1 |
| 7 | +1 | +1 | +1 |
| 8 | -1 | +1 | +1 |

### Properties

1. **Partition of unity**: Σ Nᵢ = 1 everywhere
2. **Kronecker delta**: Nᵢ(ξⱼ, ηⱼ, ζⱼ) = δᵢⱼ
3. **Linear along edges**: varies linearly along each element edge
4. **Trilinear inside**: product of linear functions in ξ, η, and ζ

### Visualization

![Shape functions Hex8](images/shape_functions_hex8.png)
*The eight trilinear shape functions evaluated at ζ=0 (mid-plane).*

### Displacement Interpolation

The displacement at any point (ξ, η, ζ) is:

```
u(ξ,η,ζ) = Σᵢ Nᵢ·uᵢ
v(ξ,η,ζ) = Σᵢ Nᵢ·vᵢ
w(ξ,η,ζ) = Σᵢ Nᵢ·wᵢ
```

## Tet4 Element (Tetrahedron 4-node)

The Tet4 element uses **linear shape functions** defined in barycentric (volume) coordinates (L₁, L₂, L₃, L₄) where L₁ + L₂ + L₃ + L₄ = 1.

### Shape Function Definitions

```
N₁ = L₁
N₂ = L₂
N₃ = L₃
N₄ = L₄
```

### Properties

1. **Partition of unity**: L₁ + L₂ + L₃ + L₄ = 1
2. **Kronecker delta**: Nᵢ at node j = δᵢⱼ
3. **Linear variation**: displacement varies linearly within the element
4. **Constant strain**: strain and stress are constant within the element

### Visualization

![Shape functions Tet4](images/shape_functions_tet4.png)
*The four linear shape functions for a tetrahedral element. Each function equals 1 at its node and 0 at the opposite face.*

### Barycentric Coordinates

Barycentric coordinates (L₁, L₂, L₃, L₄) represent the volume ratios:

```
Lᵢ = Vᵢ / V
```

where Vᵢ is the volume of the sub-tetrahedron opposite to node i, and V is the total element volume.

### Coordinate Transformation

From barycentric to Cartesian coordinates:

```
x = L₁·x₁ + L₂·x₂ + L₃·x₃ + L₄·x₄
y = L₁·y₁ + L₂·y₂ + L₃·y₃ + L₄·y₄
z = L₁·z₁ + L₂·z₂ + L₃·z₃ + L₄·z₄
```

## Tet10 Element (Tetrahedron 10-node)

The Tet10 element uses **quadratic shape functions** with 4 vertex nodes and 6 midside nodes.

### Shape Function Definitions

For vertex nodes (i = 1, 2, 3, 4):

```
Nᵢ = Lᵢ(2Lᵢ - 1)
```

For midside nodes (i = 5, 6, ..., 10) between vertices j and k:

```
Nᵢ = 4·Lⱼ·Lₖ
```

### Properties

1. **Quadratic variation**: displacement varies quadratically within the element
2. **Linear strain**: strain and stress vary linearly within the element
3. **Higher accuracy**: much more accurate than Tet4 for the same mesh

## Integration Schemes

### Hex8 Integration

Uses **Gauss quadrature** in natural coordinates:

```
∫∫∫ f(ξ,η,ζ) dξ dη dζ ≈ Σᵢ Σⱼ Σₖ wᵢ·wⱼ·wₖ·f(ξᵢ, ηⱼ, ζₖ)
```

| Scheme | Points | Accuracy | Use |
|--------|--------|----------|-----|
| 1×1×1 | 1 | Linear | Reduced integration |
| 2×2×2 | 8 | Cubic | Full integration (default) |
| 3×3×3 | 27 | Quintic | Higher order |

### Tet4 Integration

Uses **1-point Gauss rule** (exact for linear functions):

```
∫∫∫ f(L₁,L₂,L₃,L₄) dV ≈ V · f(¼, ¼, ¼, ¼)
```

where V is the element volume.

### Tet10 Integration

Uses **4-point Gauss rule** (exact for quadratic functions):

| Point | L₁ | L₂ | L₃ | L₄ | Weight |
|-------|----|----|----|----|--------|
| 1 | α | β | β | β | V/4 |
| 2 | β | α | β | β | V/4 |
| 3 | β | β | α | β | V/4 |
| 4 | β | β | β | α | V/4 |

where α = (5-√5)/20 ≈ 0.1382 and β = (5+3√5)/20 ≈ 0.5854.

## Jacobian Matrix

The Jacobian matrix J relates derivatives in natural and physical coordinates:

### For Hex8:

```
J = [∂x/∂ξ  ∂y/∂ξ  ∂z/∂ξ]
    [∂x/∂η  ∂y/∂η  ∂z/∂η]
    [∂x/∂ζ  ∂y/∂ζ  ∂z/∂ζ]
```

### For Tet4/Tet10:

The Jacobian is constant for Tet4 and relates barycentric to Cartesian derivatives.

The determinant |J| must be positive everywhere for a valid element.

## Implementation

In volumfeapy, shape functions are implemented in the element classes:

```python
class Hex8:
    def _shape_functions(self, xi, eta, zeta):
        """Trilinear shape functions N1..N8."""
        return 0.125 * np.array([
            (1 - xi) * (1 - eta) * (1 - zeta),
            (1 + xi) * (1 - eta) * (1 - zeta),
            (1 + xi) * (1 + eta) * (1 - zeta),
            (1 - xi) * (1 + eta) * (1 - zeta),
            (1 - xi) * (1 - eta) * (1 + zeta),
            (1 + xi) * (1 - eta) * (1 + zeta),
            (1 + xi) * (1 + eta) * (1 + zeta),
            (1 - xi) * (1 + eta) * (1 + zeta),
        ])
```

The B-matrix (strain-displacement) is computed using the shape function derivatives and the Jacobian inverse.

## References

- Zienkiewicz, O.C., Taylor, R.L. (2000). *The Finite Element Method*, Vol. 1. Butterworth-Heinemann.
- Hughes, T.J.R. (1987). *The Finite Element Method*. Prentice-Hall.
- Bathe, K.J. (1996). *Finite Element Procedures*. Prentice-Hall.
