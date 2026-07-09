import numpy as np
from csrf.common.constants import EPSILON, FIDELITY_MIN, FIDELITY_MAX

def clip_to_range(value: float) -> float:
    """Garantiza de forma segura la saturación en el espacio de fidelidad [0, 1]."""
    if not np.isfinite(value):
        return FIDELITY_MIN
    return float(np.clip(value, FIDELITY_MIN, FIDELITY_MAX))

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide dos escalares de forma segura, protegiendo contra indeterminaciones e infinitos."""
    if not np.isfinite(denominator) or abs(denominator) < EPSILON:
        return default

    result = numerator / denominator

    if not np.isfinite(result):
        return default

    return float(result)
