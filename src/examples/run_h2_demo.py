import numpy as np
from sklearn.linear_model import LinearRegression
from csrf.metrics.bootstrap import BootstrapEngine
from csrf.informational.fidelis import (
    InformationalStructuralOperator,
    InformationalStructuralComparator,
    InformationalFidelityAnalyzer
)

print("=== CSRF: Instantiating Informational Fidelity (H2) Pattern ===")

# 1. Generación de datos sintéticos agnósticos
np.random.seed(42)
n_patients = 120
items_x = np.random.randint(0, 5, size=(n_patients, 8))

# El operador de agregación f(X) puede ser cualquiera. Probamos una transformación no lineal.
representation_s = np.sin(items_x[:, 0]) + np.log1p(items_x[:, 4])

# Criterio clínico externo Y
criterion_y = 2.0 * items_x[:, 0] + 1.5 * items_x[:, 4] + np.random.normal(0, 0.5, size=n_patients)

# 2. Configuración e inyección de dependencias de la arquitectura
bootstrap = BootstrapEngine(n_iterations=200, alpha=0.05)
comparator = InformationalStructuralComparator()

# Definimos el operador inyectando la clase del estimador base (Framework before algorithms)
def target_operator_factory():
    return InformationalStructuralOperator(LinearRegression)

analyzer = InformationalFidelityAnalyzer(
    operator_class=target_operator_factory,
    comparator=comparator,
    bootstrap_engine=bootstrap
)

# 3. Ejecución del análisis relacional
metrics = analyzer.analyze(items_x, representation_s, criterion_y)

# 4. Extracción orientada a la ontología del framework
print(f"R(X,Y) Relational Fidelity (Items):       {metrics['R_X_Y_Fidelity'].value:.4f} {metrics['R_X_Y_Fidelity'].ci}")
print(f"R(S,Y) Relational Fidelity (Aggregate):   {metrics['R_S_Y_Fidelity'].value:.4f} {metrics['R_S_Y_Fidelity'].ci}")
print(f"Information Distortion Index (Loss):      {metrics['Information_Distortion_Index']:.4f}")
print(f"Meets Structural Preservation Standard?:  {metrics['Structural_Preservation_Axiom']}")
