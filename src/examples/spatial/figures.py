import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_spatial_figures(summary_df: pd.DataFrame, raw_points_df: pd.DataFrame, output_dir: str):
    """
    Genera las figuras axiomáticas oficiales para el manuscrito de JCE.
    Eje X: Observed Mean ISMD (Métrica nativa del operador).
    Eje Y: Spatial Fidelity (SF).
    """
    os.makedirs(output_dir, exist_ok=True)
    sns.set_theme(style="ticks", context="paper")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "axes.edgecolor": "#222222",
        "grid.color": "#eef0f2",
        "pdf.fonttype": 42
    })

    # Rango teórico común para superponer la curva axiomática SF = exp(-ISMD)
    ismd_theoretical = np.linspace(0, 1.5, 200)
    sf_theoretical = np.exp(-ismd_theoretical)

    # ==========================================
    # 1. FIGURA PRINCIPAL (MANUSCRITO: k = 20)
    # ==========================================
    fig_main, axes_m = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    sum_main = summary_df[summary_df["k_items"] == 20]
    raw_main = raw_points_df[raw_points_df["k_items"] == 20]

    # Panel A: General Configurational Heterogeneity
    ax_ma = axes_m[0]
    df_ma = raw_main[raw_main["experiment"] == "A"]
    ax_ma.scatter(df_ma["obs_ismd"], df_ma["sf"], color="#1f77b4", alpha=0.2, s=12, label="Simulations (k=20)")

    sum_ma = sum_main[sum_main["experiment"] == "A"].sort_values("obs_ismd")
    ax_ma.plot(sum_ma["obs_ismd"], sum_ma["sf_mean"], color="#1f77b4", linewidth=3, label="Observed Fit")
    ax_ma.plot(ismd_theoretical[ismd_theoretical <= sum_ma["obs_ismd"].max()],
               sf_theoretical[ismd_theoretical <= sum_ma["obs_ismd"].max()],
               color="black", linestyle="--", linewidth=1.5, label="Theoretical $\exp(-\overline{ISMD})$")

    ax_ma.set_title("General Configurational Heterogeneity", fontsize=11, fontweight="bold", pad=12)
    ax_ma.set_xlabel("Observed Mean $ISMD$", fontsize=10)
    ax_ma.set_ylabel("Spatial Fidelity ($SF$)", fontsize=10)
    ax_ma.set_ylim(-0.05, 1.05)
    ax_ma.grid(True, linestyle=":", alpha=0.5)
    ax_ma.legend(frameon=True, loc="lower left")

    # Panel B: Single-Item Structural Dominance
    ax_mb = axes_m[1]
    df_mb = raw_main[raw_main["experiment"] == "B"]
    ax_mb.scatter(df_mb["obs_ismd"], df_mb["sf"], color="#2ca02c", alpha=0.2, s=12)

    sum_mb = sum_main[sum_main["experiment"] == "B"].sort_values("obs_ismd")
    ax_mb.plot(sum_mb["obs_ismd"], sum_mb["sf_mean"], color="#2ca02c", linewidth=3)
    ax_mb.plot(ismd_theoretical[ismd_theoretical <= sum_mb["obs_ismd"].max()],
               sf_theoretical[ismd_theoretical <= sum_mb["obs_ismd"].max()],
               color="black", linestyle="--", linewidth=1.5)

    # Localizar el punto crítico de colapso estructural (donde la derivada se acelera o SF cae por debajo de 0.8)
    critical_points = sum_mb[sum_mb["sf_mean"] < 0.85]
    if not critical_points.empty:
        critical_ismd = critical_points["obs_ismd"].values[0]
        ax_mb.axvline(x=critical_ismd, color="#d62728", linestyle=":", linewidth=2)
        ax_mb.text(critical_ismd + 0.02, 0.4, "Structural Collapse\nThreshold",
                   color="#d62728", fontweight="bold", fontsize=9, rotation=0, va="center")

    ax_mb.set_title("Single-Item Structural Dominance", fontsize=11, fontweight="bold", pad=12)
    ax_mb.set_xlabel("Observed Mean $ISMD$", fontsize=10)
    ax_mb.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "figure_h1_main.pdf"), format="pdf", dpi=300)
    plt.savefig(os.path.join(output_dir, "figure_h1_main.png"), format="png", dpi=150)
    plt.close()

    # ==========================================
    # 2. FIGURA SUPLEMENTARIA (ROBUSTNESS ANALYSIS)
    # ==========================================
    fig_sup, axes_s = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)
    k_unique = sorted(summary_df["k_items"].unique())
    palette = sns.color_palette("muted", n_colors=len(k_unique))

    # Panel A Sup: Heterogeneidad
    ax_sa = axes_s[0]
    for idx, k in enumerate(k_unique):
        df_k = raw_points_df[(raw_points_df["k_items"] == k) & (raw_points_df["experiment"] == "A")]
        ax_sa.scatter(df_k["obs_ismd"], df_k["sf"], color=palette[idx], alpha=0.1, s=6, edgecolor='none')
        sum_k = summary_df[(summary_df["k_items"] == k) & (summary_df["experiment"] == "A")].sort_values("obs_ismd")
        ax_sa.plot(sum_k["obs_ismd"], sum_k["sf_mean"], color=palette[idx], linewidth=2, label=f"k = {k} items")

    ax_sa.plot(ismd_theoretical, sf_theoretical, color="black", linestyle="--", linewidth=1.2, label="Theoretical Limit")
    ax_sa.set_title("PROM Length Robustness: Heterogeneity", fontsize=11, fontweight="bold", pad=12)
    ax_sa.set_xlabel("Observed Mean $ISMD$", fontsize=10)
    ax_sa.set_ylabel("Spatial Fidelity ($SF$)", fontsize=10)
    ax_sa.grid(True, linestyle=":", alpha=0.5)
    ax_sa.legend(frameon=True, loc="lower left")

    # Panel B Sup: Dominancia
    ax_sb = axes_s[1]
    for idx, k in enumerate(k_unique):
        df_k = raw_points_df[(raw_points_df["k_items"] == k) & (raw_points_df["experiment"] == "B")]
        ax_sb.scatter(df_k["obs_ismd"], df_k["sf"], color=palette[idx], alpha=0.1, s=6, edgecolor='none')
        sum_k = summary_df[(summary_df["k_items"] == k) & (summary_df["experiment"] == "B")].sort_values("obs_ismd")
        ax_sb.plot(sum_k["obs_ismd"], sum_k["sf_mean"], color=palette[idx], linewidth=2)

    ax_sb.plot(ismd_theoretical, sf_theoretical, color="black", linestyle="--", linewidth=1.2)
    ax_sb.set_title("PROM Length Robustness: Dominance", fontsize=11, fontweight="bold", pad=12)
    ax_sb.set_xlabel("Observed Mean $ISMD$", fontsize=10)
    ax_sb.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "figure_h1_supplementary.pdf"), format="pdf", dpi=300)
    plt.savefig(os.path.join(output_dir, "figure_h1_supplementary.png"), format="png", dpi=150)
    plt.close()
