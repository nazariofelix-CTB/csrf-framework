import pytest
import numpy as np
from csrf.core.base import ClinicalStateMatrix
from csrf.core.config import CSRFConfig

try:
    from csrf.informational import InformationalFidelityAnalyzer
except ImportError:
    InformationalFidelityAnalyzer = None

@pytest.fixture
def base_environment():
    """Genera estructuras básicas alineadas para tests de flujo."""
    data = np.array([[1, 0], [0, 1], [1, 1]])
    matrix = ClinicalStateMatrix(data, ["P1", "P2", "P3"], ["q1", "q2"], "T1")
    scores = np.array([1, 1, 2])
    target = np.array([10.5, 11.0, 20.2])
    return matrix, scores, target

# =====================================================================
# 1. TESTS DE CONTROL DE FLUJO Y ROBUSTEZ CLÍNICA
# =====================================================================

def test_informational_analyzer_requires_fit():
    if InformationalFidelityAnalyzer is None:
        pytest.skip("Fase RED: Analizador no implementado todavía.")
    analyzer = InformationalFidelityAnalyzer(CSRFConfig())
    with pytest.raises(RuntimeError, match=r"El analizador debe ejecutar el método '\.fit\(\)'"):
        analyzer.calculate()

def test_informational_fit_dimension_mismatch(base_environment):
    if InformationalFidelityAnalyzer is None:
        pytest.skip("Fase RED: Analizador no implementado todavía.")
    matrix, scores, target = base_environment
    broken_target = np.array([10.5, 12.0])
    analyzer = InformationalFidelityAnalyzer(CSRFConfig())
    with pytest.raises(ValueError, match="Desalineación analítica"):
        analyzer.fit(matrix, scores, broken_target)

def test_informational_target_contains_nan(base_environment):
    if InformationalFidelityAnalyzer is None:
        pytest.skip("Fase RED: Analizador no implementado todavía.")
    matrix, scores, target = base_environment
    target_with_nan = np.array([10.5, np.nan, 20.2])
    analyzer = InformationalFidelityAnalyzer(CSRFConfig())
    with pytest.raises(ValueError, match="El vector target contiene valores faltantes"):
        analyzer.fit(matrix, scores, target_with_nan)

# =====================================================================
# 2. ESCENARIOS MATEMÁTICOS Y COMPRESIÓN CLÍNICA (H2)
# =====================================================================

def test_perfect_compression_fidelity():
    """TEST 1: Perfect Compression (IF = 1.0)."""
    if InformationalFidelityAnalyzer is None:
        pytest.fail("Fase RED: InformationalFidelityAnalyzer no existe.")

    X = np.array([[1, 0, 0], [1, 0, 0], [1, 1, 0], [1, 1, 0], [1, 1, 1], [1, 1, 1]])
    matrix = ClinicalStateMatrix(X, [f"P{i}" for i in range(1, 7)], ["q1", "q2", "q3"], "T1")
    scores = np.array([1, 1, 2, 2, 3, 3])
    target = np.array([10.0, 10.0, 20.0, 20.0, 30.0, 30.0])

    analyzer = InformationalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores, target).calculate()

    assert result.metric_value == pytest.approx(1.0, abs=1e-2)
    assert result.metadata["if_r2"] == pytest.approx(1.0)
    assert result.metadata["if_rmse"] == pytest.approx(1.0)

def test_catastrophic_information_loss():
    """TEST 2: Pérdida Catastrófica de Información (IF -> 0.0) por cancelación."""
    if InformationalFidelityAnalyzer is None:
        pytest.skip("Fase RED: Analizador no implementado todavía.")

    X = np.array([[1, 1, 0, 0], [0, 0, 1, 1], [1, 1, 0, 0], [0, 0, 1, 1]])
    matrix = ClinicalStateMatrix(X, ["P1", "P2", "P3", "P4"], ["q1", "q2", "q3", "q4"], "T1")
    scores = np.array([2, 2, 2, 2])
    target = np.array([50.0, 5.0, 50.0, 5.0])

    analyzer = InformationalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores, target).calculate()

    assert result.metric_value < 0.2
    assert result.metadata["if_r2"] == pytest.approx(0.0, abs=1e-4)

def test_mixed_informational_scenario():
    """TEST 3: Caso Mixto / Realista (0.0 < IF < 1.0)."""
    if InformationalFidelityAnalyzer is None:
        pytest.skip("Fase RED: Analizador no implementado todavía.")

    np.random.seed(42)
    X = np.random.randint(0, 2, size=(30, 5))
    matrix = ClinicalStateMatrix(X, [f"P{i}" for i in range(1, 31)], [f"q{i}" for i in range(1, 6)], "T1")
    scores = X.sum(axis=1)
    target = 2.5 * scores + 5.0 * X[:, 0] + np.random.normal(0, 0.5, size=30)

    analyzer = InformationalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores, target).calculate()

    assert 0.0 < result.metric_value < 1.0

def test_irrelevant_predictor_fidelity():
    """
    TEST 5: Predictor Irrelevante (IF ≈ 1.0)
    Si Y es puro ruido aleatorio, ningún modelo tiene poder predictivo real.
    La agregación no destruye información que no existía.
    """
    if InformationalFidelityAnalyzer is None:
        pytest.skip("Fase RED: Analizador no implementado todavía.")

    np.random.seed(123)
    X = np.random.randint(0, 2, size=(40, 4))
    matrix = ClinicalStateMatrix(X, [f"P{i}" for i in range(1, 41)], ["q1", "q2", "q3", "q4"], "T1")
    scores = X.sum(axis=1)
    # Y es ruido blanco desacoplado de los datos
    target = np.random.normal(100, 15, size=40)

    analyzer = InformationalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores, target).calculate()

    # Ambos modelos rinden igual de mal. La fidelidad informacional relativa debe aproximarse a 1.0
    assert result.metric_value == pytest.approx(1.0, abs=1e-1)
