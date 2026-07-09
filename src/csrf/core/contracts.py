from abc import ABC, abstractmethod
import numpy as np

class TemporalRepresentation:
    """
    Contenedor agnóstico para transportar estructuras dinámicas del sistema.
    Permite encapsular desde matrices de transición de Markov hasta parámetros de HMM.
    """
    def __init__(self, representation: np.ndarray, metadata: dict = None):
        self.representation = representation
        self.metadata = metadata or {}

class TemporalStructuralOperator(ABC):
    """
    Contrato abstracto para operadores encargados de mapear series
    temporales clínicas a representaciones dinámicas (T: X -> TemporalRepresentation).
    """
    @abstractmethod
    def compute_dynamics(self, trajectory: np.ndarray) -> TemporalRepresentation:
        pass

class TemporalStructuralComparator(ABC):
    """
    Contrato para la evaluación polimórfica de distorsión temporal
    basada en las representaciones dinámicas generadas.
    """
    @abstractmethod
    def compute_distance(self, omega_X: TemporalRepresentation, omega_S: TemporalRepresentation) -> float:
        """
        Calcula Dist(T(X), T(S)) garantizando un retorno acotado en [0, 1].
        """
        pass
