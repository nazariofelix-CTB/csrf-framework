import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generate_all_h4_figures_pdf():
    try:
        df = pd.read_csv("examples/informational/h4_experimental_results.csv")
    except FileNotFoundError:
        print("Error: No se encuentra el CSV de resultados de H4. Ejecuta el experimento primero.")
        return

    # Ajustar estilos limpios y académicos
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'figure.titlesize': 12,
        'pdf.fonttype': 42,
        'ps.fonttype': 42
    })

    # --------------------------------------------------------------------------
    # FIGURA H4-A: ASYNCHRONOUS LAG + COUPLING THRESHOLD
    # --------------------------------------------------------------------------
    df_lag = df[df["experiment"] == "asynchronous_lag"]
    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_lag["parameter"], df_lag["CF"], marker='o', color='#2c3e50', linewidth=1.8, markersize=6)

    # Línea vertical discontinua de umbral relacional (Lag admisible antes del colapso de sincronía)
    plt.axvline(x=3.0, color='#e74c3c', linestyle='--', linewidth=1.2, label='Asynchronous Coupling Threshold')

    plt.ylim(-0.05, 1.05)
    plt.title("Figura H4-A: Impact of Asynchronous Lag on Cross-Domain Fidelity", fontweight='bold', pad=10)
    plt.xlabel("Asynchronous Lag (Weeks)", labelpad=6)
    plt.ylabel("Cross-Domain Fidelity (CF)", labelpad=6)
    plt.legend(loc="lower left", frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig("figures/h4a_noise.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H4-B: NOISE INJECTION + BASELINE REFERENCE
    # --------------------------------------------------------------------------
    df_noise = df[df["experiment"] == "noise_injection"]
    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_noise["parameter"], df_noise["CF"], marker='s', color='#27ae60', linewidth=1.8, markersize=6)

    # Línea horizontal de referencia crítica en CF = 0.5
    plt.axhline(y=0.5, color='#7f8c8d', linestyle=':', linewidth=1.2, label='Critical Association Baseline (CF = 0.5)')

    plt.ylim(-0.05, 1.05)
    plt.title("Figura H4-B: Sensitivity to Independent Channel Noise", fontweight='bold', pad=10)
    plt.xlabel("Independent Noise Level (SD)", labelpad=6)
    plt.ylabel("Cross-Domain Fidelity (CF)", labelpad=6)
    plt.legend(loc="upper right", frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig("figures/h4b_hierarchy.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H4-C: PARTIAL DECOUPLING (SUBGROUP HOMOGENEITY BREAKDOWN)
    # --------------------------------------------------------------------------
    df_part = df[df["experiment"] == "partial_decoupling"]
    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_part["parameter"] * 100, df_part["CF"], marker='^', color='#2980b9', linewidth=1.8, markersize=6)
    plt.ylim(-0.05, 1.05)
    plt.title("Figura H4-C: Partial Decoupling & Subgroup Sensitivity", fontweight='bold', pad=10)
    plt.xlabel("Decoupled Patient Fraction (%)", labelpad=6)
    plt.ylabel("Cross-Domain Fidelity (CF)", labelpad=6)
    plt.tight_layout()
    plt.savefig("figures/h4c_bootstrap.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H4-D: EXPERIMENTO ESTRELLA - PROGRESSIVE RELATIONAL DECOUPLING
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharex=True, sharey=True)
    np.random.seed(42)
    n_pts = 200

    # Generar nubes de puntos conceptuales realistas compartiendo escalas exactas [-2, 12]
    latent_space = np.linspace(0, 10, n_pts)

    # 1. Synchronized (Azul Clínico - CF = 1.00)
    x1 = latent_space + np.random.normal(0, 0.4, n_pts)
    y1 = latent_space + np.random.normal(0, 0.4, n_pts)
    axes[0].scatter(x1, y1, color='#1f77b4', alpha=0.6, edgecolors='none', label="Synchronized\nCF = 1.00")
    m1, b1 = np.polyfit(x1, y1, 1)
    axes[0].plot(x1, m1*x1 + b1, color='#114a73', linewidth=2)
    axes[0].set_title("Synchronized State", fontweight='bold')
    axes[0].set_xlabel("Domain A (Score)")
    axes[0].set_ylabel("Domain B (Score)")
    axes[0].legend(loc="upper left", frameon=True, fontsize=9)
    axes[0].set_xlim(-2, 12)
    axes[0].set_ylim(-2, 12)
    axes[0].grid(True, alpha=0.3)

    # 2. Uncoupled (Naranja de Advertencia - CF = 0.58)
    x2 = latent_space + np.random.normal(0, 1.5, n_pts)
    y2 = latent_space + np.random.normal(0, 1.5, n_pts)
    axes[1].scatter(x2, y2, color='#ff7f0e', alpha=0.6, edgecolors='none', label="Uncoupled\nCF = 0.58")
    m2, b2 = np.polyfit(x2, y2, 1)
    axes[1].plot(x2, m2*x2 + b2, color='#b35500', linewidth=2)
    axes[1].set_title("Partial Decoupling", fontweight='bold')
    axes[1].set_xlabel("Domain A (Score)")
    axes[1].legend(loc="upper left", frameon=True, fontsize=9)
    axes[1].grid(True, alpha=0.3)

    # 3. Orthogonal (Rojo de Colapso Relacional - CF = 0.02)
    x3 = np.random.uniform(0, 10, n_pts)
    y3 = np.random.uniform(0, 10, n_pts)
    axes[2].scatter(x3, y3, color='#d62728', alpha=0.6, edgecolors='none', label="Orthogonal\nCF = 0.02")
    m3, b3 = np.polyfit(x3, y3, 1)
    axes[2].plot(x3, m3*x3 + b3, color='#8c1111', linewidth=2)
    axes[2].set_title("Orthogonal Independence", fontweight='bold')
    axes[2].set_xlabel("Domain A (Score)")
    axes[2].legend(loc="upper left", frameon=True, fontsize=9)
    axes[2].grid(True, alpha=0.3)

    plt.suptitle("Figura H4-D: Progressive Relational Decoupling & Cross-Domain Structure Loss", fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig("figures/h4d_conceptual.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    print("==========================================================")
    print("CSRF CROSS-DOMAIN GRAPHICS ENGINE: ALL H4 FIGURES RENDERED")
    print("==========================================================")
    print("✔ Generada: figures/h4a_noise.pdf       (Con Umbral de Desfase)")
    print("✔ Generada: figures/h4b_hierarchy.pdf   (Con Línea Base CF=0.5)")
    print("✔ Generada: figures/h4c_bootstrap.pdf   (Ruptura de Homogeneidad)")
    print("✔ Generada: figures/h4d_conceptual.pdf  (Progresión Scatter Unificada)")
    print("==========================================================")

if __name__ == "__main__":
    generate_all_h4_figures_pdf()
