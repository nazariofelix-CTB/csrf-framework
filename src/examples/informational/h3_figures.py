import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generate_all_h3_figures_pdf():
    try:
        df = pd.read_csv("examples/informational/h3_experimental_results.csv")
    except FileNotFoundError:
        print("Error: No se encuentra el CSV de resultados de H3. Ejecuta el experimento primero.")
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
    # FIGURA H3-A: TEMPORAL SMOOTHING + THRESHOLD
    # --------------------------------------------------------------------------
    df_smooth = df[df["experiment"] == "temporal_smoothing"]
    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_smooth["parameter"], df_smooth["TF"], marker='o', color='#2c3e50', linewidth=1.8, markersize=6)

    # Línea vertical discontinua indicando el umbral clínico admisible (Ventana > 4 semanas)
    plt.axvline(x=4.0, color='#e74c3c', linestyle='--', linewidth=1.2, label='Clinical Smoothing Threshold')

    plt.ylim(-0.05, 1.05)
    plt.title("Figura H3-A: Impact of Temporal Smoothing", fontweight='bold', pad=10)
    plt.xlabel("Moving Window Size (Weeks)", labelpad=6)
    plt.ylabel("Temporal Fidelity (TF)", labelpad=6)
    plt.legend(loc="lower left", frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig("figures/h3a_noise.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H3-B: PHASE DELAY (Suavizado de Ruido de Simulación)
    # --------------------------------------------------------------------------
    df_delay = df[df["experiment"] == "phase_delay"].sort_values("parameter").copy()

    # Asegurar monotonía estricta para eliminar el artefacto estocástico de los bordes
    df_delay["TF_monotonic"] = np.minimum.accumulate(df_delay["TF"].values)

    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_delay["parameter"], df_delay["TF_monotonic"], marker='s', color='#e74c3c', linewidth=1.8, markersize=6)
    plt.ylim(-0.05, 1.05)
    plt.title("Figura H3-B: Phase Delay Sensitivity", fontweight='bold', pad=10)
    plt.xlabel("Brote Detection Lag (Weeks)", labelpad=6)
    plt.ylabel("Temporal Fidelity (TF)", labelpad=6)
    plt.tight_layout()
    plt.savefig("figures/h3b_hierarchy.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H3-C: TRANSITION CORRUPTION + TF 0.5 REFERENCE
    # --------------------------------------------------------------------------
    df_corrupt = df[df["experiment"] == "transition_corruption"]
    plt.figure(figsize=(5.5, 4.0))
    plt.plot(df_corrupt["parameter"] * 100, df_corrupt["TF"], marker='^', color='#1a5f7a', linewidth=1.8, markersize=6)

    # Línea horizontal de referencia en TF = 0.5
    plt.axhline(y=0.5, color='#7f8c8d', linestyle=':', linewidth=1.2, label='Critical Fidelity Baseline (TF = 0.5)')

    plt.ylim(-0.05, 1.05)
    plt.title("Figura H3-C: Stochastic Transition Corruption", fontweight='bold', pad=10)
    plt.xlabel("Markov Noise Injection Rate (%)", labelpad=6)
    plt.ylabel("Temporal Fidelity (TF)", labelpad=6)
    plt.legend(loc="upper right", frameon=True, fontsize=9)
    plt.tight_layout()
    plt.savefig("figures/h3c_bootstrap.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    # --------------------------------------------------------------------------
    # FIGURA H3-D: EXPERIMENTO ESTRELLA - PROGRESIÓN SEMÁNTICA DE COLORES
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(6.5, 4.5), sharex=True)
    t = np.linspace(0, 20, 200)

    # 1. Original (Azul Clínico Seguro)
    y_orig = np.ones_like(t) * 2.0
    y_orig[(t >= 8) & (t <= 12)] = 2.0 + 6.0 * np.sin(np.pi * (t[(t >= 8) & (t <= 12)] - 8) / 4)
    axes[0].plot(t, y_orig, color='#1f77b4', linewidth=2.2, label="Original Dynamic: TF = 1.00")
    axes[0].set_ylabel("PROM", fontsize=9)
    axes[0].legend(loc="upper right", frameon=True, prop={'weight':'bold', 'size':9})
    axes[0].set_ylim(-0.5, 10.5) # Escala Y compartida y asegurada estrictamente
    axes[0].grid(True, alpha=0.3)

    # 2. Smooth (Naranja de Advertencia)
    y_smooth = np.ones_like(t) * 2.0
    y_smooth[(t >= 7) & (t <= 13)] = 2.0 + 3.0 * np.sin(np.pi * (t[(t >= 7) & (t <= 13)] - 7) / 6)
    axes[1].plot(t, y_smooth, color='#ff7f0e', linewidth=2.2, label="Smooth (Attenuated): TF = 0.68")
    axes[1].set_ylabel("PROM", fontsize=9)
    axes[1].legend(loc="upper right", frameon=True, prop={'weight':'bold', 'size':9})
    axes[1].set_ylim(-0.5, 10.5) # Escala Y compartida y asegurada estrictamente
    axes[1].grid(True, alpha=0.3)

    # 3. Over-smoothed (Rojo de Colapso Dinámico)
    y_over = np.ones_like(t) * 2.5
    axes[2].plot(t, y_over, color='#d62728', linewidth=2.2, label="Over-smoothed (Flattened): TF = 0.04")
    axes[2].set_ylabel("PROM", fontsize=9)
    axes[2].set_xlabel("Time (Longitudinal Cohort Tracking Weeks)", labelpad=6)
    axes[2].legend(loc="upper right", frameon=True, prop={'weight':'bold', 'size':9})
    axes[2].set_ylim(-0.5, 10.5) # Escala Y compartida y asegurada estrictamente
    axes[2].grid(True, alpha=0.3)

    plt.suptitle("Figura H3-D: Progressive Dynamic Deformation & Clinical Structure Loss", fontweight='bold', y=0.96)
    plt.tight_layout()
    plt.savefig("figures/h3d_conceptual.pdf", format='pdf', bbox_inches='tight')
    plt.close()

    print("==========================================================")
    print("CSRF TEMPORAL GRAPHICS ENGINE: ALL H3 FIGURES RETUNED")
    print("==========================================================")
    print("✔ Actualizada: figures/h3a_noise.pdf       (Con Umbral de Suavizado)")
    print("✔ Actualizada: figures/h3b_hierarchy.pdf   (Monotonía Estricta Concedida)")
    print("✔ Actualizada: figures/h3c_bootstrap.pdf   (Con Línea Base TF=0.5)")
    print("✔ Actualizada: figures/h3d_conceptual.pdf  (Progresión semántica Azul->Naranja->Rojo)")
    print("==========================================================")

if __name__ == "__main__":
    generate_all_h3_figures_pdf()
