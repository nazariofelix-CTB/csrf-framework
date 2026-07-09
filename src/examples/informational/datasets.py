import numpy as np

def generate_base_clinical_data(n_patients: int = 150, n_items: int = 6, seed: int = 42):
    """
    Genera un modelo de factor latente clínico. Un único rasgo latente (z)
    conduce tanto a las respuestas de los ítems como al criterio clínico final (Y).
    """
    np.random.seed(seed)

    # Rasgo latente del paciente (ej. severidad del dolor crónico)
    z = np.random.normal(0, 1, size=n_patients)

    # Los ítems cargan fuertemente en el factor latente con algo de ruido único
    X = np.zeros((n_patients, n_items))
    for i in range(n_items):
        X[:, i] = 2.0 + 1.2 * z + np.random.normal(0, 0.4, size=n_patients)

    # El criterio clínico real Y responde directamente al factor latente real
    Y = 5.0 * z + np.random.normal(0, 0.2, size=n_patients)
    return X, Y

def apply_aggregation_strategy(X: np.ndarray, strategy: str):
    if strategy == "Original (Upper Bound)":
        return X
    elif strategy == "Principal Component":
        from sklearn.decomposition import PCA
        # Extrae la primera componente (que ahora se alineará con el factor latente)
        return PCA(n_components=1).fit_transform(X)
    elif strategy == "Mean":
        return np.mean(X, axis=1).reshape(-1, 1)
    elif strategy == "Median":
        return np.median(X, axis=1).reshape(-1, 1)
    elif strategy == "Binary (Thresh)":
        return (np.mean(X, axis=1) > 2.0).astype(float).reshape(-1, 1)
    elif strategy == "Random (Lower Bound)":
        return np.random.normal(0, 1, size=(X.shape[0], 1))
    else:
        raise ValueError(f"Estrategia desconocida: {strategy}")
