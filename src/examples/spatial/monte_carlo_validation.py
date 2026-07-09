import numpy as np
import pandas as pd
from csrf.spatial.analyzer import SpatialFidelityAnalyzer
from csrf.core.config import CSRFConfig

def run_large_scale_monte_carlo(n_simulations: int = 100000):
    print(f"=== INICIANDO VALIDACIÓN DE MONTE CARLO MASIVA ({n_simulations} PROMs) ===")
    config = CSRFConfig()
    analyzer = SpatialFidelityAnalyzer(config)

    # Contadores de violaciones axiomáticas
    violations = {
        "boundedness": 0,
        "numerical_instability": 0,
        "identity_limit": 0
    }

    # Fijar semilla global para reproducibilidad absoluta del test de estrés
    np.random.seed(12345)

    # Generar bloques aleatorios masivos eficientemente
    for i in range(n_simulations):
        # 1. Parámetros estructurales aleatorios del PROM ficticio
        k_items = np.random.randint(5, 51)
        n_samples = np.random.randint(10, 201)

        # 2. Generar matriz de respuestas aleatoria en el simplex [0, 1]
        raw_data = np.random.rand(n_samples, k_items)
        row_sums = raw_data.sum(axis=1, keepdims=True)
        # Evitar divisiones por cero en casos extremos de ruido
        row_sums[row_sums == 0] = 1.0
        matrix_data = raw_data / row_sums

        # 3. Vector de scores (simulando variabilidad clínica real)
        scores = np.random.rand(n_samples)

        # 4. Inyectar casos límite sintéticos de control cada 1000 iteraciones
        if i % 1000 == 0:
            # Caso ideal: Diversidad cero (matriz homogénea idéntica)
            matrix_data = np.ones((n_samples, k_items)) / k_items

        # Ejecutar el operador
        try:
            # Envoltura simulada de los datos para el analizador
            class MockMatrix:
                def __init__(self, data): self.data = data

            analyzer._matrix = MockMatrix(matrix_data)
            analyzer._scores = scores
            res = analyzer._run_analysis()
            sf = res.metric_value

            # === VERIFICACIÓN DE AXIOMAS ===

            # A1: Acotación estricta SF en [0, 1]
            if sf < -1e-7 or sf > 1.0 + 1e-7:
                violations["boundedness"] += 1

            # A2: Estabilidad numérica (ausencia de NaNs o valores infinitos)
            if np.isnan(sf) or np.isinf(sf):
                violations["numerical_instability"] += 1

            # A3: Identidad del límite (si la distorsión media es 0, SF debe ser 1.0)
            ismd_mean = res.metadata["mean_individual_distortion"]
            if ismd_mean < 1e-9 and abs(sf - 1.0) > 1e-7:
                violations["identity_limit"] += 1

        except Exception:
            violations["numerical_instability"] += 1

        # Reporte de progreso cada 25,000 iteraciones
        if (i + 1) % 25000 == 0:
            print(f" -> Procesadas {i + 1}/{n_simulations} estructuras evaluadas correctamente.")

    print("\n--- RESULTADOS DEL TEST DE ESTRÉS DE MONTE CARLO ---")
    print(f" Violaciones de Acotación [0, 1]: {violations['boundedness']}")
    print(f" Violaciones de Estabilidad Numérica (NaN/Inf): {violations['numerical_instability']}")
    print(f" Violaciones de Identidad en Límite Ideal: {violations['identity_limit']}")

    total_violations = sum(violations.values())
    if total_violations == 0:
        print("\n>>> VERIFICACIÓN EXITOSA: El operador H1 es formalmente robusto ante 100,000 escenarios estocásticos.")
        return True
    else:
        print(f"\n>>> ERROR: Se detectaron {total_violations} fallos axiomáticos en el espacio muestral.")
        return False

if __name__ == "__main__":
    run_large_scale_monte_carlo(n_simulations=100000)
