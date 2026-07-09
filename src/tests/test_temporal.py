import pytest
import numpy as np
from csrf.core.base import ClinicalStateMatrix
from csrf.core.config import CSRFConfig
from csrf.temporal.analyzer import TemporalFidelityAnalyzer

def test_temporal_analyzer_requires_fit():
    analyzer = TemporalFidelityAnalyzer(CSRFConfig())
    with pytest.raises(RuntimeError):
        analyzer.calculate()

def test_temporal_test1_perfect_synchrony():
    """TEST 1: Trayectorias idénticas en tendencia y forma (TF = 1.0)"""
    X = np.array([
        [10, 5], [20, 10], [30, 15],  # P1
        [0,  2], [10,  4], [20,  6]   # P2
    ])
    matrix = ClinicalStateMatrix(X,
                                 patients=["P1", "P1", "P1", "P2", "P2", "P2"],
                                 items=["q1", "q2"],
                                 timestamp=["T1", "T2", "T3", "T1", "T2", "T3"])
    scores = X.sum(axis=1)

    analyzer = TemporalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metric_value == pytest.approx(1.0, abs=1e-2)
    assert result.metadata["tf_trend"] == pytest.approx(1.0, abs=1e-2)

def test_temporal_test2_catastrophic_inversion():
    """TEST 2: Trayectorias con inversión direccional (TF -> 0.0)"""
    X = np.array([[1, 1], [2, 2], [3, 3]])
    matrix = ClinicalStateMatrix(X, patients=["P1", "P1", "P1"], items=["q1", "q2"], timestamp=["T1", "T2", "T3"])
    scores = np.array([30, 20, 10])

    analyzer = TemporalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metric_value < 0.1
    assert result.metadata["tf_trend"] == pytest.approx(0.0, abs=1e-2)

def test_temporal_test3_shape_distortion():
    """TEST 3: Misma dirección, distinta geometría temporal (0.0 < TF < 1.0)"""
    X = np.array([[10, 10], [10, 10], [30, 30]])
    matrix = ClinicalStateMatrix(X, patients=["P1", "P1", "P1"], items=["q1", "q2"], timestamp=["T1", "T2", "T3"])
    scores = np.array([20, 40, 60])

    analyzer = TemporalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert 0.1 < result.metric_value < 0.9
    assert result.metadata["tf_shape"] < 1.0

def test_temporal_test4_attrition_filter():
    """TEST 4: Exclusión controlada de trayectorias cortas (|T| < 3)"""
    X = np.array([
        [1, 1], [2, 2], [3, 3],  # P1: Válido (|T| = 3)
        [1, 1], [2, 2]           # P2: Filtrado por longitud corta (|T| = 2)
    ])
    matrix = ClinicalStateMatrix(X,
                                 patients=["P1", "P1", "P1", "P2", "P2"],
                                 items=["q1", "q2"],
                                 timestamp=["T1", "T2", "T3", "T1", "T2"])
    scores = X.sum(axis=1)

    analyzer = TemporalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metadata["excluded_trajectories"] == 1
    assert result.metadata["analyzed_patients"] == 1

def test_temporal_test5_spurious_dynamics():
    """TEST 5: Clínica constante con Score variable (Penalización Máxima)"""
    X = np.array([[5, 5], [5, 5], [5, 5]])
    matrix = ClinicalStateMatrix(X, patients=["P1", "P1", "P1"], items=["q1", "q2"], timestamp=["T1", "T2", "T3"])
    scores = np.array([10, 20, 15])

    analyzer = TemporalFidelityAnalyzer(CSRFConfig())
    result = analyzer.fit(matrix, scores).calculate()
    assert result.metadata["tf_trend"] == pytest.approx(0.0, abs=1e-2)
