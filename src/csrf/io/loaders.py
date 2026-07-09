from typing import List, Optional
import pandas as pd
from csrf.core.base import ClinicalStateMatrix, TimestampType

def validate_schema(df: pd.DataFrame, expected_columns: List[str]) -> bool:
    """
    Verifica de forma estricta que todas las columnas esperadas del PROM
    y los metadatos existan dentro del DataFrame cargado.
    """
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Violación de esquema: Faltan las siguientes columnas críticas: {missing_cols}")
    return True

def load_dataframe(
    df: pd.DataFrame,
    patient_col: str,
    item_cols: List[str],
    timestamp_val: TimestampType = "Baseline"
) -> ClinicalStateMatrix:
    """
    Transforma un DataFrame transaccional de Pandas en una estructura fuertemente
    tipada 'ClinicalStateMatrix', aislando la matriz numérica de los metadatos.
    """
    # 1. Validar esquema básico de las columnas solicitadas
    validate_schema(df, [patient_col] + item_cols)

    # 2. Extraer la matriz pura de respuestas al instrumento (PROM)
    data_matrix = df[item_cols].to_numpy(dtype=float)

    # 3. Extraer metadatos relacionales
    patients = df[patient_col].astype(str).tolist()

    # 4. Construir la estructura de datos core (delegando validaciones internas al constructor)
    return ClinicalStateMatrix(
        data=data_matrix,
        patient_ids=patients,
        item_ids=item_cols,
        timestamp=timestamp_val
    )

def load_csv(
    filepath: str,
    patient_col: str,
    item_cols: List[str],
    timestamp_val: TimestampType = "Baseline",
    **kwargs
) -> ClinicalStateMatrix:
    """
    Lector de conveniencia periférico que envuelve la funcionalidad de load_dataframe
    tras la lectura de un archivo plano desde almacenamiento secundario (disco).
    """
    df = pd.read_csv(filepath, **kwargs)
    return load_dataframe(
        df=df,
        patient_col=patient_col,
        item_cols=item_cols,
        timestamp_val=timestamp_val
    )
