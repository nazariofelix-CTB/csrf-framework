import numpy as np
from typing import Callable, Tuple

class BootstrapEngine:
    """
    Infraestructura estadística reutilizable del CSRF.
    Proporciona estimaciones de incertidumbre mediante remuestreo no paramétrico
    a nivel de fila (paciente) de forma agnóstica al módulo de fidelidad.
    """
    def __init__(self, n_iterations: int = 1000, alpha: float = 0.05, seed: int = 42):
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.seed = seed

    def compute_uncertainty(
        self,
        data_matrix: np.ndarray,
        criterion: np.ndarray,
        eval_func: Callable[[np.ndarray, np.ndarray], float]
    ) -> Tuple[float, Tuple[float, float], np.ndarray]:

        np.random.seed(self.seed)
        n_samples = data_matrix.shape[0]
        boot_metrics = []

        # Métrica base original
        baseline_metric = eval_func(data_matrix, criterion)

        for _ in range(self.n_iterations):
            boot_idx = np.random.choice(n_samples, size=n_samples, replace=True)
            try:
                score = eval_func(data_matrix[boot_idx], criterion[boot_idx])
                boot_metrics.append(score)
            except Exception:
                continue

        boot_metrics = np.array(boot_metrics)
        lower_bound = float(np.percentile(boot_metrics, (self.alpha / 2) * 100))
        upper_bound = float(np.percentile(boot_metrics, (1 - self.alpha / 2) * 100))

        return baseline_metric, (lower_bound, upper_bound), boot_metrics
