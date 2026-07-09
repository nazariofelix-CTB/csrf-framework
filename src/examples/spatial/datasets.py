import numpy as np
from csrf.core.base import ClinicalStateMatrix

def generate_stochastic_spatial_universe(n_samples: int, k_items: int, delta: float, experiment_type: str, seed: int) -> tuple[ClinicalStateMatrix, np.ndarray, float]:
    """
    Genera una población con variabilidad real inter-paciente (estratos verdaderos),
    pero donde el perfil interno se degrada sistemáticamente según delta.
    """
    np.random.seed(seed)

    # Generamos scores verdaderos heterogéneos para los pacientes (población real)
    true_patient_scores = np.random.uniform(15.0, 45.0, size=n_samples)
    X = np.zeros((n_samples, k_items))

    for i in range(n_samples):
        base_score = true_patient_scores[i]

        if experiment_type == "A":
            # Experimento A: Heterogeneidad generalizada exponencial
            weights = np.ones(k_items) + (np.exp(np.linspace(0, 2.5, k_items)) - 1) * delta
            weights /= np.sum(weights)
            X[i, :] = base_score * weights * k_items
            X[i, :] += np.random.normal(0, 1.0 * delta, size=k_items)

        elif experiment_type == "B":
            # Experimento B: Dominancia severa de un ítem caníbal
            weights = np.ones(k_items)
            weights[0] = 1.0 + (k_items - 1) * delta
            weights[1:] = 1.0 - delta if delta < 1.0 else 0.001
            weights /= np.sum(weights)
            X[i, :] = base_score * weights * k_items
            X[i, :] += np.random.normal(0, 0.5 * delta, size=k_items)

    X = np.clip(X, 0.0, 100.0)
    scores = np.mean(X, axis=1)

    # Métrica de Diversidad Observada Real: desviación estándar promedio de los perfiles internos
    observed_diversity = float(np.mean(np.std(X, axis=1)))

    items = [f"D1_q{j}" for j in range(k_items)]
    patients = [f"P{i}" for i in range(n_samples)]

    return ClinicalStateMatrix(X, patients=patients, items=items), scores, observed_diversity
