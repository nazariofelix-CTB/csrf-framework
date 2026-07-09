import numpy as np

def hamming_distance(X: np.ndarray) -> np.ndarray:
    """
    Calcula la matriz de distancia Hamming por pares utilizando broadcasting.

    Parámetros:
        X (np.ndarray): Matriz bidimensional de dimensiones (N x k) con las
                        respuestas del PROM de los pacientes.

    Retorna:
        np.ndarray: Matriz simétrica de dimensiones (N x N) donde la celda (i, j)
                    representa la proporción de ítems discrepantes entre el
                    paciente i y el paciente j.
    """
    if X.ndim != 2:
        raise ValueError("La matriz de entrada debe ser estrictamente bidimensional (N x k).")

    # Broadcasting: (N x 1 x k) comparado contra (1 x N x k) da una matriz (N x N x k)
    # Evaluamos la desigualdad y promediamos a lo largo del eje de los ítems (axis=2)
    return (X[:, None, :] != X[None, :, :]).mean(axis=2)


def jaccard_distance(X: np.ndarray) -> np.ndarray:
    """
    Calcula la matriz de distancia Jaccard por pares para atributos binarios/booleanos.

    Parámetros:
        X (np.ndarray): Matriz bidimensional de dimensiones (N x k).

    Retorna:
        np.ndarray: Matriz simétrica de dimensiones (N x N) con la distancia Jaccard.
    """
    if X.ndim != 2:
        raise ValueError("La matriz de entrada debe ser estrictamente bidimensional (N x k).")

    # Convertir a booleano para operaciones lógicas eficientes
    X_bool = X.astype(bool)

    # Calcular intersección (AND) y unión (OR) por pares mediante broadcasting
    intersection = (X_bool[:, None, :] & X_bool[None, :, :]).sum(axis=2)
    union = (X_bool[:, None, :] | X_bool[None, :, :]).sum(axis=2)

    # Manejar indeterminaciones (0/0) si dos filas están completamente vacías de activaciones
    # La distancia entre dos vectores completamente vacíos se define como 0.0
    with np.errstate(divide='ignore', invalid='ignore'):
        distance = 1.0 - (intersection / union)
        distance = np.nan_to_num(distance, nan=0.0)

    return distance
