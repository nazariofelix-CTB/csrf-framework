import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

# --- CONTRATOS PRESERVADOS Y EXTENDIDOS DEL ECOSISTEMA ---
class NonUniquePatientIDError(ValueError): pass
class InvalidDomainPartitionError(ValueError): pass
class MissingTimepointError(ValueError): pass
class DimensionMismatchError(ValueError): pass  # <- Excepción propia solicitada

@dataclass
class DomainStructure:
    name: str
    items: List[str]
    weight: float = 1.0

@dataclass
class LongitudinalDataset:
    matrices: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class MissingDataPolicy:
    IGNORE = "ignore"
    ALLOW_ATTRITION = "allow_attrition"
    ERROR = "error"
    STRICT = "strict"

@dataclass
class ClinicalStateMatrix:
    data: np.ndarray
    patients: list
    items: list
    timestamp: Optional[Any] = None

    def __post_init__(self):
        if self.data.ndim != 2:
            raise ValueError("La matriz de datos debe ser bidimensional.")
        if len(self.patients) != self.data.shape[0]:
            raise ValueError("Desalineación en filas (pacientes).")
        if len(self.items) != self.data.shape[1]:
            raise ValueError("Desalineación en columnas (ítems).")

@dataclass
class FidelityResult:
    module_name: str
    metric_value: float
    n_observations: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseFidelityAnalyzer(ABC):
    """Abstracción unificada para los operadores del CSRF."""
    def __init__(self, config: Any):
        self.config = config
        self._is_fitted: bool = False
        self._matrix: Optional[ClinicalStateMatrix] = None
        self._scores: Optional[np.ndarray] = None

    def fit(self, matrix: ClinicalStateMatrix, scores: np.ndarray) -> "BaseFidelityAnalyzer":
        if len(scores) != matrix.data.shape[0]:
            raise DimensionMismatchError(f"Desalineación estructural: {len(scores)} scores frente a {matrix.data.shape[0]} estados.")
        self._matrix = matrix
        self._scores = scores
        self._is_fitted = True
        return self

    def _assert_fitted(self):
        if not self._is_fitted or self._matrix is None or self._scores is None:
            raise RuntimeError(f"Error de ciclo de vida: Ejecute '.fit()' en {self.__class__.__name__}.")

    def calculate(self) -> FidelityResult:
        self._assert_fitted()
        return self._run_analysis()

    @abstractmethod
    def _run_analysis(self) -> FidelityResult:
        pass
