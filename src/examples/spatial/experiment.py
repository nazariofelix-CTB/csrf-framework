import numpy as np
import pandas as pd
from csrf.spatial.analyzer import SpatialFidelityAnalyzer
from csrf.core.config import CSRFConfig
from examples.spatial.datasets import generate_stochastic_spatial_universe

def run_spatial_stress_test() -> tuple[pd.DataFrame, pd.DataFrame]:
    deltas = np.linspace(0.0, 1.0, 15)
    k_ranges = [5, 10, 20, 40]
    n_iterations = 50

    raw_records = []
    summary_records = []
    config = CSRFConfig()

    for k in k_ranges:
        for d in deltas:
            sf_a_list, ismd_a_list = [], []
            sf_b_list, ismd_b_list = [], []

            for iter_idx in range(n_iterations):
                seed = 1000 * iter_idx + int(d * 100)

                # Experimento A
                matrix_a, scores_a, _ = generate_stochastic_spatial_universe(
                    n_samples=40, k_items=k, delta=d, experiment_type="A", seed=seed
                )
                res_a = SpatialFidelityAnalyzer(config).fit(matrix_a, scores_a).calculate()
                # El objeto matemático real extraído de la metadata del operador
                actual_ismd_a = res_a.metadata["mean_individual_distortion"]
                sf_a_list.append(res_a.metric_value)
                ismd_a_list.append(actual_ismd_a)
                raw_records.append({"k_items": k, "delta": d, "experiment": "A", "obs_ismd": actual_ismd_a, "sf": res_a.metric_value})

                # Experimento B
                matrix_b, scores_b, _ = generate_stochastic_spatial_universe(
                    n_samples=40, k_items=k, delta=d, experiment_type="B", seed=seed
                )
                res_b = SpatialFidelityAnalyzer(config).fit(matrix_b, scores_b).calculate()
                actual_ismd_b = res_b.metadata["mean_individual_distortion"]
                sf_b_list.append(res_b.metric_value)
                ismd_b_list.append(actual_ismd_b)
                raw_records.append({"k_items": k, "delta": d, "experiment": "B", "obs_ismd": actual_ismd_b, "sf": res_b.metric_value})

            summary_records.append({
                "k_items": k, "delta": d, "experiment": "A",
                "obs_ismd": np.mean(ismd_a_list),
                "sf_mean": np.mean(sf_a_list),
                "sf_ci_lower": np.percentile(sf_a_list, 2.5),
                "sf_ci_upper": np.percentile(sf_a_list, 97.5)
            })
            summary_records.append({
                "k_items": k, "delta": d, "experiment": "B",
                "obs_ismd": np.mean(ismd_b_list),
                "sf_mean": np.mean(sf_b_list),
                "sf_ci_lower": np.percentile(sf_b_list, 2.5),
                "sf_ci_upper": np.percentile(sf_b_list, 97.5)
            })

    return pd.DataFrame(summary_records), pd.DataFrame(raw_records)
