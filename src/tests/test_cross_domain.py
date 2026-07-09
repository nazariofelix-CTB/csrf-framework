import pytest
import numpy as np
from csrf.core.base import ClinicalStateMatrix
from csrf.core.config import CSRFConfig
from csrf.cross_domain.analyzer import CrossDomainFidelityAnalyzer

def test_cross_domain_analyzer_requires_fit():
    analyzer = CrossDomainFidelityAnalyzer(CSRFConfig())
    with pytest.raises(RuntimeError):
        analyzer.calculate()

def test_cross_domain_test1_perfect_coupling():
    """TEST 1: Preservación perfecta de la red de acoplamiento (CDF = 1.0)"""
    # Dos dominios (q1, q2 frente a q3, q4) con acoplamiento síncrono perfecto
    X = np.array([
        [10, 10, 5, 5],
        [20, 20, 10, 10],
        [30, 30, 15, 15]
    ])
    matrix = ClinicalStateMatrix(
        X,
        patients=["P1", "P1", "P1"],
        items=["D1_q1", "D1_q2", "D2_q3", "D2_q4"],
        timestamp=["T1", "T2", "T3"]
    )
    # Scores que preservan exactamente la proporcionalidad inter-dominio
    scores = np.array([15, 30, 45])

    analyzer = CrossDomainFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metric_value == pytest.approx(1.0, abs=1e-2)
    assert result.metadata["cdf_static"] == pytest.approx(1.0, abs=1e-2)

def test_cross_domain_test2_coupling_collapse():
    """TEST 2: Colapso de acoplamiento. Los dominios interactúan en X pero se vuelven ortogonales en S."""
    X = np.array([
        [10, 5],
        [20, 10],
        [30, 15]
    ])
    matrix = ClinicalStateMatrix(X, patients=["P1", "P1", "P1"], items=["D1_q1", "D2_q2"], timestamp=["T1", "T2", "T3"])
    # Un vector de scores plano o disociado que destruye la varianza cruzada
    scores = np.array([10, 10, 10])

    analyzer = CrossDomainFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metric_value < 0.2
    assert result.metadata["cdf_static"] == pytest.approx(0.0, abs=1e-2)

def test_cross_domain_test3_directional_reversal():
    """TEST 3: Directional Coupling Reversal. La dinámica relacional se invierte en el espacio resumido."""
    X = np.array([
        [10, 5],
        [20, 10],
        [30, 15]
    ])
    matrix = ClinicalStateMatrix(X, patients=["P1", "P1", "P1"], items=["D1_q1", "D2_q2"], timestamp=["T1", "T2", "T3"])
    # Scores que invierten la trayectoria del acoplamiento (direccionalidad opuesta)
    scores = np.array([45, 30, 15])

    analyzer = CrossDomainFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metadata["cdf_static"] < 0.1

def test_cross_domain_test4_lag_distortion():
    """TEST 4: Desalineación temporal de efectos cruzados (Lag Distortion)."""
    # D1 precede a D2 en los datos crudos
    X = np.array([
        [10, 0],
        [20, 10],
        [30, 20]
    ])
    matrix = ClinicalStateMatrix(X, patients=["P1", "P1", "P1"], items=["D1_q1", "D2_q2"], timestamp=["T1", "T2", "T3"])
    scores = np.array([10, 15, 12])  # Suavizado espurio que diluye el desfase temporal

    analyzer = CrossDomainFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metadata["cdf_lag"] < 0.5

def test_cross_domain_test5_independence_invariance():
    """TEST 5: Domain Independence Invariance (Análogo a Information Neutrality)."""
    # Dominios ortogonales sin estructura de acoplamiento alguna en X
    X = np.array([
        [1, 0],
        [0, 1],
        [1, 0]
    ])
    matrix = ClinicalStateMatrix(X, patients=["P1", "P2", "P3"], items=["D1_q1", "D2_q2"])
    scores = np.array([1, 1, 1])

    analyzer = CrossDomainFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    # Si no había acoplamiento que preservar, la fidelidad relacional se mantiene intacta en la neutralidad
    assert result.metric_value == pytest.approx(1.0, abs=1e-2)
