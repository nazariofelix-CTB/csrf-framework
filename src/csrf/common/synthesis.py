import numpy as np
from typing import Sequence, Optional

def geometric_synthesis(metrics: Sequence[float], weights: Optional[Sequence[float]] = None) -> float:
    """
    Operador de Síntesis Axiomática Psi (Ψ).
    Calcula la media geométrica ponderada de forma segura para los operadores elementales.
    Si cualquier operador elemental satura en 0 (distorsión máxima), la fidelidad global es 0.
    """
    arr = np.asarray(metrics, dtype=float)
    if arr.size == 0:
        return 0.0
    if np.any(arr < 0.0):
        raise ValueError("Los operadores de fidelidad elemental deben estar normalizados en [0, 1].")

    if weights is None:
        return float(np.exp(np.mean(np.log(np.maximum(arr, 1e-12)))))

    w = np.asarray(weights, dtype=float)
    if w.shape != arr.shape:
        raise ValueError("El vector de pesos debe tener la misma dimensión que las métricas.")

    return float(np.exp(np.sum(w * np.log(np.maximum(arr, 1e-12))) / np.sum(w)))
