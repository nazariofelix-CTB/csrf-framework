import numpy as np
from typing import Any
from csrf.core.base import DimensionMismatchError

def validate_dimensions(X: np.ndarray, y: Any, axis: int = 0) -> None:
    """Verifica la alineación estructural lanzando un error específico del framework."""
    expected = X.shape[axis]
    actual = len(y) if hasattr(y, '__len__') else y.shape[0]
    if expected != actual:
        raise DimensionMismatchError(f"Inconsistencia dimensional: Esperados {expected}, recibidos {actual}.")

def has_missing_data(X: np.ndarray) -> bool:
    """Retorna True si existen valores faltantes o nulos en la matriz."""
    return bool(np.isnan(X).any() if X.dtype.kind in "biufc" else False)

def validate_no_missing(X: np.ndarray) -> None:
    """Lanza ValueError si la matriz contiene valores nulos y el módulo no los admite."""
    if has_missing_data(X):
        raise ValueError("Operación abortada: La matriz contiene datos ausentes (NaN) no permitidos por este operador.")
