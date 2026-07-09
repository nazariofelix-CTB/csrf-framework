import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from csrf.core.base import ClinicalStateMatrix
from csrf.core.config import CSRFConfig
from csrf.spatial.analyzer import SpatialFidelityAnalyzer

# El mismo estrato estricto sugerido en tu prueba del algodón
X_diag = np.array([
    [20.0, 20.0, 20.0, 20.0],  # Paciente A: Perfil perfectamente plano (Fidelidad = 1.0)
    [20.0, 20.0, 20.0, 20.0],  # Paciente B: Perfil perfectamente plano (Fidelidad = 1.0)
    [80.0,  0.0,  0.0,  0.0],  # Paciente C: Dominancia salvaje (Distorsión máxima -> Fidelidad = 0.0)
    [ 0.0, 80.0,  0.0,  0.0],  # Paciente D: Dominancia salvaje (Distorsión máxima -> Fidelidad = 0.0)
])

scores_diag = np.array([20.0, 20.0, 20.0, 20.0])

matrix_diag = ClinicalStateMatrix(data=X_diag, patients=['A','B','C','D'], items=['i1','i2','i3','i4'])
res = SpatialFidelityAnalyzer(CSRFConfig()).fit(matrix_diag, scores_diag).calculate()

print("\n=== VERDICTO DE LA PRUEBA DEL ALGODÓN ===")
print(f"-> NEW Diagnostic SF Result: {res.metric_value:.4f}")
print(f"-> Metadata: {res.metadata}\n")
