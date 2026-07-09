import pytest
import numpy as np
from csrf.core.base import ClinicalStateMatrix
from csrf.core.config import CSRFConfig  # <--- CORREGIDO: Importado desde su módulo correcto
from csrf.spatial.analyzer import SpatialFidelityAnalyzer
from csrf.metrics.distance import hamming_distance, jaccard_distance

# =====================================================================
# 1. TESTS DE PROPIEDADES ALGEBRAICAS (MÉTRICAS DE BAJO NIVEL)
# =====================================================================

@pytest.fixture
def dummy_prom_data():
    """Genera una matriz sintética aleatoria de respuestas binarias (N=10, k=5)."""
    np.random.seed(42)
    return np.random.randint(0, 2, size=(10, 5))

def test_hamming_distance_diagonal_zero(dummy_prom_data):
    """Propiedad de Identidad: La distancia de un paciente consigo mismo debe ser 0."""
    D = hamming_distance(dummy_prom_data)
    assert np.allclose(np.diag(D), 0.0)

def test_hamming_distance_symmetry(dummy_prom_data):
    """Propiedad de Simetría: d(i, j) debe ser igual a d(j, i)."""
    D = hamming_distance(dummy_prom_data)
    assert np.allclose(D, D.T)

def test_jaccard_distance_diagonal_zero(dummy_prom_data):
    """Propiedad de Identidad (Jaccard): La auto-distancia debe ser 0."""
    D = jaccard_distance(dummy_prom_data)
    assert np.allclose(np.diag(D), 0.0)

def test_jaccard_distance_symmetry(dummy_prom_data):
    """Propiedad de Simetría (Jaccard): La matriz debe ser perfectamente simétrica."""
    D = jaccard_distance(dummy_prom_data)
    assert np.allclose(D, D.T)


# =====================================================================
# 2. TESTS DE ROBUSTEZ Y CONTROL DE FLUJO DEL ANALIZADOR
# =====================================================================

def test_fit_dimension_mismatch():
    """Verifica que salte un ValueError si el vector de scores no se alinea con las filas de X."""
    data = np.array([[1, 0], [0, 1], [1, 1]])  # N = 3
    matrix = ClinicalStateMatrix(data, ["P1", "P2", "P3"], ["q1", "q2"], "Baseline")
    scores = np.array([10, 20])  # Error: Longitud 2 en lugar de 3

    config = CSRFConfig()
    analyzer = SpatialFidelityAnalyzer(config)

    with pytest.raises(ValueError, match="Desalineación analítica"):
        analyzer.fit(matrix, scores)

def test_calculate_without_fit():
    """Garantiza que no se pueda explotar el pipeline llamando a calculate() en frío."""
    config = CSRFConfig()
    analyzer = SpatialFidelityAnalyzer(config)

    # CORREGIDO: Usamos un raw string r"..." para evitar el SyntaxWarning en Python 3.12
    with pytest.raises(RuntimeError, match=r"El analizador debe ejecutar el método '\.fit\(\)'"):
        analyzer.calculate()


# =====================================================================
# 3. ESCENARIOS CLÍNICOS DEL SPRINT 2 (CONSERVADOS INTEGRALMENTE)
# =====================================================================

def test_perfect_spatial_fidelity():
    data = np.array([[1, 0, 1], [1, 0, 1], [0, 1, 0], [0, 1, 0]])
    matrix = ClinicalStateMatrix(data, ["P1", "P2", "P3", "P4"], ["q1", "q2", "q3"], "Baseline")
    scores = np.array([1, 1, 2, 2])
    analyzer = SpatialFidelityAnalyzer(CSRFConfig(distance_metric="hamming"))
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metric_value == pytest.approx(1.0)

def test_maximum_heterogeneity_low_fidelity():
    data = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1]])
    matrix = ClinicalStateMatrix(data, ["P1", "P2", "P3", "P4"], ["q1", "q2", "q3", "q4"], "Baseline")
    scores = np.array([1, 1, 1, 1])
    analyzer = SpatialFidelityAnalyzer(CSRFConfig(distance_metric="hamming"))
    result = analyzer.fit(matrix, scores).calculate()
    assert 0.0 < result.metric_value < 0.7

def test_mixed_fidelity_scenario():
    data = np.array([[1, 0, 0], [1, 0, 0], [0, 1, 1], [1, 1, 0]])
    matrix = ClinicalStateMatrix(data, ["P1", "P2", "P3", "P4"], ["q1", "q2", "q3"], "Baseline")
    scores = np.array([10, 10, 20, 20])
    analyzer = SpatialFidelityAnalyzer(CSRFConfig(distance_metric="hamming"))
    result = analyzer.fit(matrix, scores).calculate()
    assert 0.0 < result.metric_value < 1.0

def test_single_patient_stratum():
    data = np.array([[1, 1, 1], [0, 0, 0]])
    matrix = ClinicalStateMatrix(data, ["P1", "P2"], ["q1", "q2", "q3"], "Baseline")
    scores = np.array([100, 200])
    analyzer = SpatialFidelityAnalyzer(CSRFConfig(distance_metric="hamming"))
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metric_value == pytest.approx(1.0)
