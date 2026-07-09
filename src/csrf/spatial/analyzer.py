import numpy as np
from csrf.core.base import BaseFidelityAnalyzer, FidelityResult
from csrf.common.normalization import clip_to_range

class SpatialFidelityAnalyzer(BaseFidelityAnalyzer):
    """
    Operador de Fidelidad Espacial (H1) Corregido.
    Evalúa la preservación de la configuración analizando la desviación
    de los perfiles individuales (filas) respecto a la homogeneidad esperada.
    """

    def _run_analysis(self) -> FidelityResult:
        X = self._matrix.data
        S = self._scores
        N, K = X.shape

        if K <= 1:
            return FidelityResult(module_name="spatial", metric_value=1.0, n_observations=N)

        individual_fidelities = []

        for i in range(N):
            profile = X[i, :]
            score = S[i]

            total_profile = np.sum(profile)
            if total_profile == 0:
                # Si el paciente no tiene síntomas, su configuración es homogénea por definición
                individual_fidelities.append(1.0)
                continue

            # Perfil observado normalizado (probabilidad de distribución del síntoma)
            p_obs = profile / total_profile

            # Perfil ideal homogéneo uniforme (1/K para cada ítem)
            p_ideal = np.ones(K) / K

            # Calculamos la Distorsión Configuracional Individual mediante la distancia Euclídea normalizada
            # El valor máximo teórico de la distancia entre un vector unitario y el centroide es sqrt((K-1)/K)
            max_dist = np.sqrt((K - 1) / K)
            actual_dist = np.linalg.norm(p_obs - p_ideal)

            # Desviación configuracional del paciente (0 = balance perfecto, 1 = dominancia extrema de un ítem)
            individual_distortion = actual_dist / (max_dist + 1e-9)

            # La fidelidad del individuo decrece con su distorsión
            individual_fidelities.append(1.0 - individual_distortion)

        # La fidelidad espacial global es la media de las fidelidades individuales
        sf_value = clip_to_range(np.mean(individual_fidelities))

        return FidelityResult(
            module_name="spatial",
            metric_value=float(sf_value),
            n_observations=N,
            metadata={
                "mean_individual_distortion": float(1.0 - sf_value),
                "min_individual_fidelity": float(np.min(individual_fidelities))
            }
        )
