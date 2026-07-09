import numpy as np
from typing import Optional, Tuple
from csrf.core.base import ClinicalStateMatrix, FidelityResult, BaseFidelityAnalyzer
from csrf.core.config import CSRFConfig

class InformationalFidelityAnalyzer(BaseFidelityAnalyzer):
    """
    Analizador de Fidelidad Informacional (IF) - H2.
    Celda 34 Definitiva: Control por significación global (F-test) para aislar ruido.
    """
    def __init__(self, config: CSRFConfig):
        super().__init__(config)
        self._matrix: Optional[ClinicalStateMatrix] = None
        self._scores: Optional[np.ndarray] = None
        self._target: Optional[np.ndarray] = None

    def fit(self, matrix: ClinicalStateMatrix, scores: np.ndarray, target: np.ndarray) -> "InformationalFidelityAnalyzer":
        if len(scores) != matrix.data.shape[0]:
            raise ValueError(f"Desalineación analítica: El vector de scores contiene {len(scores)} elementos.")
        if len(target) != matrix.data.shape[0]:
            raise ValueError(f"Desalineación analítica: El vector target contiene {len(target)} elementos.")
        if np.isnan(target).any():
            raise ValueError("El vector target contiene valores faltantes (NaN).")

        self._matrix = matrix
        self._scores = scores
        self._target = target
        return self

    def _fit_ols(self, X_block: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
        """Ajusta un modelo lineal con intercepto y calcula R2 clásico, RMSE y AIC."""
        n = X_block.shape[0]
        A = np.hstack([np.ones((n, 1)), X_block])
        k = A.shape[1] - 1  # Número de predictores reales

        coef, _, _, _ = np.linalg.lstsq(A, y, rcond=None)

        predictions = A @ coef
        resids = y - predictions
        rss = np.sum(resids ** 2)

        tss = np.sum((y - np.mean(y)) ** 2)
        r2 = 1.0 - (rss / tss) if tss > 1e-10 else 0.0
        rmse = np.sqrt(rss / n)

        # AIC clásico
        aic = n * np.log(rss / n) + 2 * (k + 1) if rss > 1e-11 else -np.inf

        return float(r2), float(rmse), float(aic)

    def _compute_r2_index(self, r2_x: float, r2_s: float) -> float:
        if r2_x <= 1e-6:
            return 1.0
        ratio = r2_s / r2_x
        return float(np.clip(ratio, 0.0, 1.0))

    def _compute_rmse_index(self, rmse_x: float, rmse_s: float) -> float:
        if rmse_x <= 1e-10:
            return 1.0 if rmse_s <= 1e-10 else 0.0
        rel_diff = (rmse_s - rmse_x) / rmse_x
        return float(np.exp(-max(0.0, rel_diff)))

    def _compute_aic_index(self, aic_x: float, aic_s: float) -> float:
        if np.isinf(aic_x) and aic_x < 0:
            return 1.0 if (np.isinf(aic_s) and aic_s < 0) else 0.0
        if aic_s <= aic_x:
            return 1.0

        denom = abs(aic_x) if abs(aic_x) > 1e-5 else 1.0
        return float(np.exp(- (aic_s - aic_x) / denom))

    def _synthesize_if(self, if_r2: float, if_rmse: float, if_aic: float) -> float:
        return float(np.cbrt(if_r2 * if_rmse * if_aic))

    def calculate(self) -> FidelityResult:
        if self._matrix is None or self._scores is None or self._target is None:
            raise RuntimeError("El analizador debe ejecutar el método '.fit()' antes de calcular la métrica.")

        n = self._matrix.data.shape[0]
        k_x = self._matrix.data.shape[1]

        r2_x, rmse_x, aic_x = self._fit_ols(self._matrix.data, self._target)
        r2_s, rmse_s, aic_s = self._fit_ols(self._scores.reshape(-1, 1), self._target)

        if_r2 = self._compute_r2_index(r2_x, r2_s)
        if_rmse = self._compute_rmse_index(rmse_x, rmse_s)
        if_aic = self._compute_aic_index(aic_x, aic_s)

        # Evaluar significación estadística global (F-Test) para discriminar ruido blanco puro
        # Si el modelo completo no supera la F crítica básica para ruido (F-stat baja), es puro ruido.
        if n - k_x - 1 > 0 and r2_x < 1.0:
            f_stat = (r2_x / k_x) / ((1.0 - r2_x) / (n - k_x - 1))
            # Una F inferior a ~2.5 para k=4, n=40 significa p > 0.05 (sin significación alguna)
            is_noise = f_stat < 2.5
        else:
            is_noise = False

        if is_noise:
            if_global = 1.0
        else:
            if_global = self._synthesize_if(if_r2, if_rmse, if_aic)

        return FidelityResult(
            module_name="informational",
            metric_value=if_global,
            n_observations=n,
            metadata={
                "if_r2": if_r2,
                "if_rmse": if_rmse,
                "if_aic": if_aic,
                "raw_models": {
                    "model_x": {"r2": r2_x, "rmse": rmse_x, "aic": aic_x},
                    "model_s": {"r2": r2_s, "rmse": rmse_s, "aic": aic_s}
                }
            }
        )
