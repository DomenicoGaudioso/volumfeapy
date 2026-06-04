"""
Genera immagini per la documentazione volumfeapy.
"""
import sys
from pathlib import Path

# Aggiungi il path per importare volumfeapy
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go

from volumfeapy import Model, Material
from volumfeapy.plotting import plot_mesh, plot_deformed, plot_stress, plot_mode


def create_cube_hex8(n_elements=4):
    """Crea un cubo con elementi Hex8."""
    L = 1.0
    m = Model()
    
    # Nodi
    nid = 1
    for k in range(n_elements + 1):
        for j in range(n_elements + 1):
            for i in range(n_elements + 1):
                m.add_node(nid, i * L / n_elements, j * L / n_elements, k * L / n_elements)
                nid += 1
    
    # Materiale
    mat = Material(E=210e9, nu=0.3)
    
    # Elementi
    eid = 1
    for k in range(n_elements):
        for j in range(n_elements):
            for i in range(n_elements):
                n1 = k * (n_elements + 1)**2 + j * (n_elements + 1) + i + 1
                n2 = n1 + 1
                n3 = n1 + (n_elements + 1) + 1
                n4 = n1 + (n_elements + 1)
                n5 = n1 + (n_elements + 1)**2
                n6 = n2 + (n_elements + 1)**2
                n7 = n3 + (n_elements + 1)**2
                n8 = n4 + (n_elements + 1)**2
                m.add_hex8(eid, [n1, n2, n3, n4, n5, n6, n7, n8], mat)
                eid += 1
    
    return m


def create_cantilever_tet4(n_elements=4):
    """Crea una mensola con elementi Tet4."""
    L = 2.0
    b = 0.2
    h = 0.4
    m = Model()
    
    # Nodi
    nid = 1
    for k in range(n_elements + 1):
        for j in range(n_elements + 1):
            for i in range(2 * n_elements + 1):
                m.add_node(nid, i * L / (2 * n_elements), j * b / n_elements, k * h / n_elements)
                nid += 1
    
    # Materiale
    mat = Material(E=210e9, nu=0.3)
    
    # Elementi (ogni cubo diviso in 5 tetraedri)
    eid = 1
    for k in range(n_elements):
        for j in range(n_elements):
            for i in range(2 * n_elements):
                n1 = k * (n_elements + 1) * (2 * n_elements + 1) + j * (2 * n_elements + 1) + i + 1
                n2 = n1 + 1
                n3 = n1 + (2 * n_elements + 1) + 1
                n4 = n1 + (2 * n_elements + 1)
                n5 = n1 + (n_elements + 1) * (2 * n_elements + 1)
                n6 = n2 + (n_elements + 1) * (2 * n_elements + 1)
                n7 = n3 + (n_elements + 1) * (2 * n_elements + 1)
                n8 = n4 + (n_elements + 1) * (2 * n_elements + 1)
                
                # 5 tetraedri per cubo
                m.add_tet4(eid, [n1, n2, n4, n5], mat); eid += 1
                m.add_tet4(eid, [n2, n3, n4, n7], mat); eid += 1
                m.add_tet4(eid, [n2, n5, n6, n7], mat); eid += 1
                m.add_tet4(eid, [n4, n5, n7, n8], mat); eid += 1
                m.add_tet4(eid, [n2, n4, n5, n7], mat); eid += 1
    
    return m


def generate_mesh_image(m, filename, title="Mesh"):
    """Genera immagine della mesh."""
    fig = plot_mesh(m, show_node_ids=False)
    fig.update_layout(title=title, width=800, height=600)
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_deformed_image(res, filename, scale=100, title="Deformata"):
    """Genera immagine della deformata."""
    fig = plot_deformed(res, scale=scale)
    fig.update_layout(title=title, width=800, height=600)
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_stress_image(res, filename, component="von_mises", title=None):
    """Genera immagine delle tensioni."""
    if title is None:
        title = f"Tensioni: {component}"
    fig = plot_stress(res, component=component)
    fig.update_layout(title=title, width=800, height=600)
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_mode_image(mr, mode_idx, filename, scale=100):
    """Genera immagine di una forma modale."""
    fig = plot_mode(mr, i=mode_idx, scale=scale)
    fig.update_layout(width=800, height=600)
    fig.write_image(filename, scale=2)
    print(f"Generata: {filename}")


def generate_shape_functions_hex8_image(filename):
    """Genera immagine delle funzioni di forma Hex8."""
    fig = plt.figure(figsize=(15, 10))
    
    # Funzioni di forma trilineari
    def N(i, xi, eta, zeta):
        xi_i = [-1, 1, 1, -1, -1, 1, 1, -1][i]
        eta_i = [-1, -1, 1, 1, -1, -1, 1, 1][i]
        zeta_i = [-1, -1, -1, -1, 1, 1, 1, 1][i]
        return 0.125 * (1 + xi_i * xi) * (1 + eta_i * eta) * (1 + zeta_i * zeta)
    
    # Crea griglia
    xi = np.linspace(-1, 1, 20)
    eta = np.linspace(-1, 1, 20)
    zeta = np.linspace(-1, 1, 20)
    
    # Visualizza 8 funzioni di forma (una per nodo)
    for idx in range(8):
        ax = fig.add_subplot(2, 4, idx + 1, projection='3d')
        
        # Valuta la funzione di forma su un piano (zeta=0)
        XI, ETA = np.meshgrid(xi, eta)
        Z = N(idx, XI, ETA, 0)
        
        # Superficie
        surf = ax.plot_surface(XI, ETA, Z, cmap='viridis', alpha=0.8)
        
        ax.set_xlabel('ξ')
        ax.set_ylabel('η')
        ax.set_zlabel(f'N{idx+1}')
        ax.set_title(f'N{idx+1}(ξ,η,ζ=0)')
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(0, 1)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Generata: {filename}")


def generate_shape_functions_tet4_image(filename):
    """Genera immagine delle funzioni di forma Tet4."""
    fig = plt.figure(figsize=(12, 10))
    
    # Coordinate baricentriche per Tet4
    # N1 = L1, N2 = L2, N3 = L3, N4 = L4 dove L1+L2+L3+L4=1
    
    # Visualizza le 4 funzioni di forma
    titles = ['N₁ = L₁', 'N₂ = L₂', 'N₃ = L₃', 'N₄ = L₄']
    
    # Coordinate dei nodi del tetraedro di riferimento
    nodes = np.array([
        [0, 0, 0],      # Nodo 1
        [1, 0, 0],      # Nodo 2
        [0, 1, 0],      # Nodo 3
        [0, 0, 1],      # Nodo 4
    ])
    
    for idx in range(4):
        ax = fig.add_subplot(2, 2, idx + 1, projection='3d')
        
        # Disegna il tetraedro
        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        for i, j in edges:
            ax.plot([nodes[i, 0], nodes[j, 0]],
                   [nodes[i, 1], nodes[j, 1]],
                   [nodes[i, 2], nodes[j, 2]], 'k-', linewidth=1)
        
        # Evidenzia il nodo corrente
        ax.scatter(nodes[idx, 0], nodes[idx, 1], nodes[idx, 2],
                  s=200, c='red', marker='o')
        
        # Aggiungi punti interni con colore proporzionale a Ni
        n_pts = 50
        L1 = np.random.rand(n_pts)
        L2 = np.random.rand(n_pts) * (1 - L1)
        L3 = np.random.rand(n_pts) * (1 - L1 - L2)
        L4 = 1 - L1 - L2 - L3
        
        # Coordinate cartesiane
        x = L2 * nodes[1, 0] + L3 * nodes[2, 0] + L4 * nodes[3, 0]
        y = L2 * nodes[1, 1] + L3 * nodes[2, 1] + L4 * nodes[3, 1]
        z = L2 * nodes[1, 2] + L3 * nodes[2, 2] + L4 * nodes[3, 2]
        
        # Valore della funzione di forma
        L_vals = [L1, L2, L3, L4]
        Ni = L_vals[idx]
        
        scatter = ax.scatter(x, y, z, c=Ni, cmap='viridis', s=30, alpha=0.6)
        plt.colorbar(scatter, ax=ax, label=f'N{idx+1}')
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        ax.set_title(titles[idx])
    
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Generata: {filename}")


def main():
    """Genera tutte le immagini per la documentazione."""
    output_dir = Path(__file__).parent.parent / "docs" / "images"
    output_dir.mkdir(exist_ok=True)
    
    print("Generazione immagini per documentazione volumfeapy...")
    print("=" * 60)
    
    # 1. Cubo con Hex8
    print("\n1. Cubo con elementi Hex8")
    m_cube = create_cube_hex8(n_elements=4)
    generate_mesh_image(m_cube, output_dir / "mesh_cube_hex8.png",
                       "Mesh cubo con elementi Hex8 (4×4×4)")
    
    # Applica vincoli e carichi
    for nid in m_cube.nodes:
        node = m_cube.nodes[nid]
        if node.z == 0:
            m_cube.fix(nid)
    
    # Carico sulla faccia superiore
    for nid in m_cube.nodes:
        node = m_cube.nodes[nid]
        if node.z == 1.0:
            m_cube.add_nodal_load(nid, Fz=-1e6)
    
    # Risolvi
    res_cube = m_cube.solve()
    
    # 2. Deformata cubo
    generate_deformed_image(res_cube, output_dir / "deformed_cube_hex8.png",
                           scale=100, title="Deformata cubo Hex8 (scala 100×)")
    
    # 3. Tensioni von Mises
    generate_stress_image(res_cube, output_dir / "stress_von_mises_cube.png",
                         component="von_mises", title="Tensione di von Mises [Pa]")
    
    # 4. Tensioni szz
    generate_stress_image(res_cube, output_dir / "stress_szz_cube.png",
                         component="szz", title="Tensione normale σzz [Pa]")
    
    # 5. Mensola con Tet4
    print("\n2. Mensola con elementi Tet4")
    m_cant = create_cantilever_tet4(n_elements=3)
    generate_mesh_image(m_cant, output_dir / "mesh_cantilever_tet4.png",
                       "Mesh mensola con elementi Tet4")
    
    # Applica vincoli e carichi
    for nid in m_cant.nodes:
        node = m_cant.nodes[nid]
        if node.x == 0:
            m_cant.fix(nid)
    
    # Carico sulla faccia libera
    for nid in m_cant.nodes:
        node = m_cant.nodes[nid]
        if abs(node.x - 2.0) < 1e-6:
            m_cant.add_nodal_load(nid, Fz=-1e4)
    
    # Risolvi
    res_cant = m_cant.solve()
    
    # 6. Deformata mensola
    generate_deformed_image(res_cant, output_dir / "deformed_cantilever_tet4.png",
                           scale=100, title="Deformata mensola Tet4 (scala 100×)")
    
    # 7. Tensioni von Mises mensola
    generate_stress_image(res_cant, output_dir / "stress_von_mises_cantilever.png",
                         component="von_mises", title="Tensione di von Mises [Pa]")
    
    # 8. Analisi modale
    print("\n3. Analisi modale")
    m_modal = create_cube_hex8(n_elements=3)
    # Aggiungi densità per analisi modale
    for el in m_modal.elements.values():
        el.material.rho = 7850.0
    
    # Vincoli
    for nid in m_modal.nodes:
        node = m_modal.nodes[nid]
        if node.z == 0:
            m_modal.fix(nid)
    
    mr = m_modal.modal(n_modes=6)
    
    for i in range(min(4, len(mr.freq))):
        generate_mode_image(mr, i, output_dir / f"mode_{i+1}.png", scale=100)
    
    # 9. Funzioni di forma
    print("\n4. Funzioni di forma")
    generate_shape_functions_hex8_image(output_dir / "shape_functions_hex8.png")
    generate_shape_functions_tet4_image(output_dir / "shape_functions_tet4.png")
    
    print("\n" + "=" * 60)
    print(f"Generazione completata! Immagini salvate in: {output_dir}")
    print(f"Totale immagini: {len(list(output_dir.glob('*.png')))}")


if __name__ == "__main__":
    main()
