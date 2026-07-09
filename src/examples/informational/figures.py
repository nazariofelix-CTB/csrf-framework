import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_all_h2_figures_pdf():
    # Cargar resultados corregidos del experimento libre de sesgos
    try:
        df = pd.read_csv("examples/informational/h2_experimental_results.csv")
    except FileNotFoundError:
        print("Error: No se encuentra el CSV de resultados. Ejecuta primero `experiment.py`.")
        return

    # Forzar un estilo limpio y académico apto para publicación
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'figure.titlesize': 12,
        'pdf.fonttype': 42,  # Evita problemas de fuentes incrustadas en el envío a la revista
        'ps.fonttype': 42
    })

    # --------------------------------------------------------------------------
    # FIGURA H2-B: JERARQUÍA DE AGREGACIÓN REAL (MONÓTONA Y CORREGIDA)
    # --------------------------------------------------------------------------
    df_aggr = df[df["experiment"] == "aggregation_hierarchy"]

    plt.figure(figsize=(6.5, 4.5))
    plt.plot(df_aggr["parameter"], df_aggr["IF"], marker='o', color='#1a5f7a', linewidth=2.0, markersize=7)
    plt.ylim(-0.05, 1.05)
    plt.title("Figura H2-B: Aggregation Hierarchy vs. Informational Fidelity", fontweight='bold', pad=12)
    plt.xlabel("Aggregation Strategy (Severe Loss Spectrum)", labelpad=8)
    plt.ylabel("Informational Fidelity (IF)", labelpad=8)
    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    plt.savefig("examples/informational/fig_h2_b_aggregation_hierarchy.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H2-A: INYECCIÓN DE RUIDO (CONTINUA)
    # --------------------------------------------------------------------------
    df_noise = df[df["experiment"] == "noise_injection"]

    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_noise["noise"], df_noise["IF"], marker='s', color='#2c3e50', linewidth=1.8, markersize=6)
    plt.ylim(-0.05, 1.05)
    plt.title("Figura H2-A: Noise Injection Impact on Stability", fontweight='bold', pad=10)
    plt.xlabel("Noise Level (σ in Criterion Variable)", labelpad=6)
    plt.ylabel("Informational Fidelity (IF)", labelpad=6)
    plt.tight_layout()
    plt.savefig("examples/informational/fig_h2_a_noise_injection.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H2-C: ROBUSTEZ MUESTRAL (ETIQUETAS REFINADAS E INFERENCIA B=1000)
    # --------------------------------------------------------------------------
    df_ss = df[df["experiment"] == "sample_size"]

    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_ss["N"], df_ss["IF"], marker='^', color='#e74c3c', linewidth=1.8, markersize=6, label="Estimated IF")
    plt.fill_between(df_ss["N"], df_ss["ci_lower"], df_ss["ci_upper"], color='#e74c3c', alpha=0.12,
                     label="95% bootstrap CI\n(B = 1000)")
    plt.xscale('log')
    plt.xticks(df_ss["N"], labels=[str(n) for n in df_ss["N"]])
    plt.ylim(-0.05, 1.05)
    plt.title("Figura H2-C: Sample Size Robustness & Bootstrap Convergence", fontweight='bold', pad=10)
    plt.xlabel("Sample Size (N, Log Scale)", labelpad=6)
    plt.ylabel("Estimated Informational Fidelity (IF)", labelpad=6)
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    plt.savefig("examples/informational/fig_h2_c_sample_size_robustness.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H2-D: ESPECTRO CONCEPTUAL DE COMPRESIÓN ESTRUCTURAL
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 5.5)

    concepts = [
        {"name": "Original PROM Matrix", "width": 8.0, "color": "#1a5f7a", "if": "1.0"},
        {"name": "Principal Component", "width": 6.5, "color": "#248ea9", "if": "≈ 0.95"},
        {"name": "Arithmetic Mean", "width": 5.0, "color": "#28c7fa", "if": "≥ 0.90"},
        {"name": "Median Operator", "width": 3.5, "color": "#a3f7bf", "if": "≥ 0.75"},
        {"name": "Binary Threshold", "width": 1.8, "color": "#f67280", "if": "≥ 0.50"},
        {"name": "Random Noise", "width": 0.5, "color": "#c0c0c0", "if": "≈ 0.0"}
    ]

    for idx, c in enumerate(reversed(concepts)):
        y_pos = idx
        # Dibujar bloques vectoriales limpios
        rect = patches.Rectangle((1.2, y_pos - 0.22), c["width"], 0.44, facecolor=c["color"], edgecolor='#333333', linewidth=0.8, alpha=0.9)
        ax.add_patch(rect)
        # Nombres alineados a la derecha del inicio del bloque
        ax.text(1.0, y_pos, c["name"], ha='right', va='center', fontsize=9.5, fontweight='bold')
        # Valores de fidelidad conceptual a la derecha del bloque
        ax.text(1.4 + c["width"], y_pos, f"IF {c['if']}", ha='left', va='center', fontsize=9, fontstyle='italic', color='#222222')

    ax.axis('off')
    plt.title("Figura H2-D: Conceptual Spectrum of Progressive Structural Compression", fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig("examples/informational/fig_h2_d_conceptual_compression.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    print("==========================================================")
    print("CSRF VECTORIAL ENGINE: ALL FIGURES GENERATED AS PDF")
    print("==========================================================")
    print("✔ Guardada: examples/informational/fig_h2_b_aggregation_hierarchy.pdf (PRINCIPAL)")
    print("✔ Guardada: examples/informational/fig_h2_a_noise_injection.pdf")
    print("✔ Guardada: examples/informational/fig_h2_c_sample_size_robustness.pdf")
    print("✔ Guardada: examples/informational/fig_h2_d_conceptual_compression.pdf (CONCEPTUAL)")
    print("==========================================================")

if __name__ == "__main__":
    generate_all_h2_figures_pdf()
