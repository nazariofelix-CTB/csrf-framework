import numpy as np
from csrf.core.contracts import TemporalStructuralOperator, TemporalStructuralComparator, TemporalRepresentation
from csrf.temporal.comparators import BaseTemporalDistanceComparator

class MarkovTransitionOperator(TemporalStructuralOperator):
    """
    Implementación Canónica v1.0: Mapea trayectorias a matrices de transición de Markov.
    """
    def __init__(self, n_states: int = 3, min_val: float = 0.0, max_val: float = 10.0):
        self.n_states = n_states
        # Definir bins fijos para mapear valores continuos de PROMs a estados clínicos (ej. Remisión, Estable, Recaída)
        self.bins = np.linspace(min_val, max_val, n_states + 1)

    def _discretize_trajectory(self, trajectory: np.ndarray) -> np.ndarray:
        # Si la trayectoria es multidimensional, se colapsa de forma estable para la matriz latente
        if len(trajectory.shape) > 1 and trajectory.shape[1] > 1:
            mean_track = np.mean(trajectory, axis=1)
        else:
            mean_track = trajectory.flatten()
        return np.digitize(mean_track, self.bins) - 1

    def compute_dynamics(self, trajectory: np.ndarray) -> TemporalRepresentation:
        states = self._discretize_trajectory(trajectory)
        P = np.zeros((self.n_states, self.n_states))

        # Contar transiciones directas t -> t+1
        for t in range(len(states) - 1):
            i, j = states[t], states[t+1]
            if 0 <= i < self.n_states and 0 <= j < self.n_states:
                P[i, j] += 1

        # Normalizar filas para obtener probabilidades estocásticas reales
        for i in range(self.n_states):
            row_sum = P[i, :].sum()
            if row_sum > 0:
                P[i, :] /= row_sum
            else:
                P[i, :] = 1.0 / self.n_states # Distribución uniforme si no hay datos

        return TemporalRepresentation(representation=P, metadata={"type": "Markov_Transition_Matrix", "states": self.n_states})

class FrobeniusTemporalComparator(BaseTemporalDistanceComparator):
    """
    Mide la distorsión geométrica global usando la norma de Frobenius.
    """
    def _calculate_raw_distance(self, rep_a: np.ndarray, rep_b: np.ndarray) -> float:
        return float(np.linalg.norm(rep_a - rep_b, ord='fro'))

class KLTemporalComparator(BaseTemporalDistanceComparator):
    """
    Mide la distorsión informacional usando la Divergencia de Kullback-Leibler promedio entre perfiles.
    """
    def _calculate_raw_distance(self, rep_a: np.ndarray, rep_b: np.ndarray) -> float:
        eps = 1e-9 # Evitar divisiones por cero o log(0)
        p = rep_a + eps
        q = rep_b + eps
        # Normalizar de nuevo tras sumar eps
        p /= p.sum(axis=1, keepdims=True)
        q /= q.sum(axis=1, keepdims=True)
        kl_div = np.sum(p * np.log(p / q), axis=1)
        return float(np.mean(kl_div))
