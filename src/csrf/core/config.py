from dataclasses import dataclass
from csrf.core.base import MissingDataPolicy

@dataclass(frozen=True)
class CSRFConfig:
    """
    Encapsula todos los hiperparámetros, métricas por defecto y semillas
    de aleatoriedad del framework para garantizar la reproducibilidad por diseño.
    """
    distance_metric: str = "hamming"
    bootstrap_iterations: int = 1000
    random_seed: int = 42
    cv_folds: int = 5
    missing_data_policy: MissingDataPolicy = MissingDataPolicy.STRICT
    output_directory: str = "./csrf_output"
