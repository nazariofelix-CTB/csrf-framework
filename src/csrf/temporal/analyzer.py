import numpy as np
from csrf.core.contracts import TemporalStructuralOperator, TemporalStructuralComparator

class TemporalFidelityAnalyzer:
    """
    Orquestador ciego para H3. Implementa la ecuación fundamental:
    TF = 1 - Dist(T(X), T(S))
    """
    def __init__(self, operator: TemporalStructuralOperator, comparator: TemporalStructuralComparator):
        self.operator = operator
        self.comparator = comparator

    def analyze_fidelity(self, X_trajectory: np.ndarray, S_trajectory: np.ndarray) -> float:
        """
        Calcula la retención de la estructura dinámica clínicamente relevante.
        """
        # 1. El operador dinámico procesa las trayectorias y produce las representaciones
        omega_X = self.operator.compute_dynamics(X_trajectory)
        omega_S = self.operator.compute_dynamics(S_trajectory)

        # 2. El comparador calcula la distancia estricta entre ambos mundos dinámicos
        distance = self.comparator.compute_distance(omega_X, omega_S)

        # 3. TF = 1 - Dist(T(X), T(S))
        return max(0.0, min(1.0, 1.0 - distance))
