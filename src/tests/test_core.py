import pytest
import numpy as np
from csrf.core.base import (
    ClinicalStateMatrix,
    DomainStructure,
    LongitudinalDataset,
    FidelityResult,
    MissingDataPolicy,
    NonUniquePatientIDError,
    InvalidDomainPartitionError,
    MissingTimepointError
)

# =====================================================================
# 1. TESTS PARA CLINICALSTATEMATRIX
# =====================================================================

def test_clinical_state_matrix_valid_instantiation():
    """Verifica que una matriz correcta con tipos válidos se instancia sin problemas."""
    data = np.array([[1, 2], [3, 4]])
    patients = ["P01", "P02"]
    items = ["q1", "q2"]

    # Probar con string como timestamp
    matrix_str = ClinicalStateMatrix(data, patients, items, "Baseline")
    assert matrix_str.timestamp == "Baseline"

    # Probar con int como timestamp (flexibilidad del sprint)
    matrix_int = ClinicalStateMatrix(data, patients, items, 1)
    assert matrix_int.timestamp == 1

def test_clinical_state_matrix_dimension_mismatch():
    """Verifica que desalinear filas o columnas con la matriz de datos lanza ValueError."""
    data = np.array([[1, 2], [3, 4]])

    # Error en filas (pacientes)
    with pytest.raises(ValueError, match="Desalineación de filas"):
        ClinicalStateMatrix(data, ["P01"], ["q1", "q2"], "Baseline")

    # Error en columnas (ítems)
    with pytest.raises(ValueError, match="Desalineación de columnas"):
        ClinicalStateMatrix(data, ["P01", "P02"], ["q1"], "Baseline")

def test_clinical_state_matrix_duplicate_patients():
    """Fuerza IDs duplicados en el mismo checkpoint y verifica que salte la restricción de unicidad."""
    data = np.array([[1, 2], [3, 4]])
    with pytest.raises(NonUniquePatientIDError):
        ClinicalStateMatrix(data, ["P01", "P01"], ["q1", "q2"], "Baseline")


# =====================================================================
# 2. TESTS PARA DOMAINSTRUCTURE
# =====================================================================

def test_domain_structure_overlap():
    """Verifica que un ítem asignado a múltiples dominios lanza InvalidDomainPartitionError."""
    # El ítem 'q2' está duplicado en Pain y Fatigue
    bad_mapping = {
        "Pain": ["q1", "q2"],
        "Fatigue": ["q2", "q3"]
    }
    with pytest.raises(InvalidDomainPartitionError):
        DomainStructure(bad_mapping)


# =====================================================================
# 3. TESTS PARA FIDELITYRESULT (GUARDIÁN DEL ESPACIO MATEMÁTICO [0,1])
# =====================================================================

def test_fidelity_result_bounds():
    """Garantiza que valores fuera de [0, 1] en métricas o intervalos rompan inmediatamente."""
    # Métrica > 1.0
    with pytest.raises(ValueError, match="Violación de axioma matemático"):
        FidelityResult(module_name="spatial", metric_value=1.05, n_observations=100)

    # Métrica < 0.0
    with pytest.raises(ValueError, match="Violación de axioma matemático"):
        FidelityResult(module_name="spatial", metric_value=-0.01, n_observations=100)

    # Intervalo de confianza invertido (low > high)
    with pytest.raises(ValueError, match="Intervalo de confianza inconsistente"):
        FidelityResult(module_name="temporal", metric_value=0.5, n_observations=100, confidence_interval=(0.8, 0.2))


# =====================================================================
# 4. TESTS PARA LONGITUDINALDATASET (POLÍTICAS DE DATOS FALTANTES)
# =====================================================================

@pytest.fixture
def sample_longitudinal_data():
    """Fixture que genera una cohorte longitudinal sintética donde un paciente deserta en t2."""
    data_t1 = np.array([[1, 2], [3, 4]])
    matrix_t1 = ClinicalStateMatrix(data_t1, ["P01", "P02"], ["q1", "q2"], "Baseline")

    # En t2, el paciente P02 deserta (pérdida de seguimiento)
    data_t2 = np.array([[1, 3]])
    matrix_t2 = ClinicalStateMatrix(data_t2, ["P01"], ["q1", "q2"], "Month_3")

    dummy_agg = lambda x: np.sum(x, axis=1)

    dataset = LongitudinalDataset(
        states={"Baseline": matrix_t1, "Month_3": matrix_t2},
        aggregation_function=dummy_agg
    )
    return dataset

def test_longitudinal_strict_policy_raises_error(sample_longitudinal_data):
    """Bajo la política STRICT, la deserción detectada debe lanzar MissingTimepointError."""
    with pytest.raises(MissingTimepointError):
        sample_longitudinal_data.validate_integrity(MissingDataPolicy.STRICT)

def test_longitudinal_allow_attrition_policy_passes(sample_longitudinal_data):
    """Bajo ALLOW_ATTRITION, la validación inter-temporal debe pasar limpiamente."""
    # No debe levantar ninguna excepción, permitiendo el análisis de cohortes reales
    sample_longitudinal_data.validate_integrity(MissingDataPolicy.ALLOW_ATTRITION)
