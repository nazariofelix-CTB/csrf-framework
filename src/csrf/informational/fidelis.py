import numpy as np
from typing import Dict, Any, Type
from csrf.core.contracts import StructuralOperator, StructuralComparator, FidelityResult
from csrf.metrics.bootstrap import BootstrapEngine

class InformationalStructuralOperator(StructuralOperator):
    """
    Instanciación de StructuralOperator para H2.
    Construye la representación relacional R(Data, Y) mapeando la proyección predictiva.
    """
    def __init__(self, core_estimator_class: Type):
        self.estimator = core_estimator_class()

    def fit_operator(self, data: np.ndarray, criterion: np.ndarray) -> None:
        # Asegura la dimensionalidad correcta para datos unidimensionales o multidimensionales
        x_input = data.reshape(-1, 1) if data.ndim == 1 else data
        self.estimator.fit(x_input, criterion)

    def compute_relational_representation(self, data: np.ndarray) -> np.ndarray:
        x_input = data.reshape(-1, 1) if data.ndim == 1 else data
        return self.estimator.predict(x_input)

class InformationalStructuralComparator(StructuralComparator):
    """
    Instanciación de StructuralComparator para H2.
    Calcula la distorsión basándose en el coeficiente de determinación del espacio relacional.
    """
    def compare(self, r_data: np.ndarray, r_criterion: np.ndarray) -> float:
        ss_res = np.sum((r_criterion - r_data) ** 2)
        ss_tot = np.sum((r_criterion - np.mean(r_criterion)) ** 2)
        return float(1 - (ss_res / ss_tot)) if ss_tot != 0 else 0.0

class InformationalFidelityAnalyzer:
    """
    Orquestador del módulo H2. Coordina el flujo bajo el patrón:
    StructuralOperator -> StructuralComparator -> FidelityResult.
    """
    def __init__(self, operator_class: Type, comparator: StructuralComparator, bootstrap_engine: BootstrapEngine):
        self.operator_class = operator_class
        self.comparator = comparator
        self.bootstrap = bootstrap_engine

    def analyze(
        self,
        items_x: np.ndarray,
        representation_s: np.ndarray,
        criterion_y: np.ndarray
    ) -> Dict[str, Any]:

        # Funciones auxiliares locales para pasar de forma limpia al motor de Bootstrap independiente
        def eval_x(x_slice, y_slice):
            op = self.operator_class()
            op.fit_operator(x_slice, y_slice)
            r_x = op.compute_relational_representation(x_slice)
            return self.comparator.compare(r_x, y_slice)

        def eval_s(s_slice, y_slice):
            op = self.operator_class()
            op.fit_operator(s_slice, y_slice)
            r_s = op.compute_relational_representation(s_slice)
            return self.comparator.compare(r_s, y_slice)

        # Invocación de la infraestructura común de Bootstrap
        x_val, x_ci, x_dist = self.bootstrap.compute_uncertainty(items_x, criterion_y, eval_x)
        s_val, s_ci, s_dist = self.bootstrap.compute_uncertainty(representation_s, criterion_y, eval_s)

        # Resultados empaquetados bajo la ontología del framework
        fidelity_x = FidelityResult(x_val, x_ci, x_dist)
        fidelity_s = FidelityResult(s_val, s_ci, s_dist)

        net_distortion = float(fidelity_x.value - fidelity_s.value)

        return {
            "R_X_Y_Fidelity": fidelity_x,
            "R_S_Y_Fidelity": fidelity_s,
            "Information_Distortion_Index": net_distortion,
            "Structural_Preservation_Axiom": bool(net_distortion <= 0.05)
        }
