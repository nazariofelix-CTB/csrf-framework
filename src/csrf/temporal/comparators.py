from csrf.core.contracts import TemporalStructuralComparator, TemporalRepresentation
import numpy as np

class BaseTemporalDistanceComparator(TemporalStructuralComparator):
    """
    Base para comparadores geométricos e informacionales sobre representaciones indexadas.
    """
    def __init__(self, gamma: float = 1.0):
        self.gamma = gamma

    def compute_distance(self, omega_X: TemporalRepresentation, omega_S: TemporalRepresentation) -> float:
        # Forzar que la salida se ajuste estrictamente a la métrica abstracta del framework [0, 1]
        dist = self._calculate_raw_distance(omega_X.representation, omega_S.representation)
        return max(0.0, min(1.0, 1.0 - np.exp(-self.gamma * dist)))

    def _calculate_raw_distance(self, rep_a: np.ndarray, rep_b: np.ndarray) -> float:
        raise NotImplementedError
