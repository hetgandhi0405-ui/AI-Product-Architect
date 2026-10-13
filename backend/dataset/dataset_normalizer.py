from typing import Any, Dict, List

import pandas as pd

from backend.dataset.dataset_mapper import map_columns
from backend.dataset.schema import get_required_columns


NULL_VALUES = {
    "",
    "null",
    "none",
    "nan",
    "n/a",
    "na",
    "unknown",
    "not available",
}


def normalize_value(value: Any) -> Any:
    """
    Normalize a single dataset value.

    Empty/null-like values are converted to None.
    Strings are stripped of unnecessary whitespace.
    """
    if pd.isna(value):
        return None

    if isinstance(value, str):
        value = value.strip()

        if value.lower() in NULL_VALUES:
            return None

        return value

    return value


def normalize_column_name_mapping(columns: List[str]) -> Dict[str, str]:
    """
    Build a source-column -> target-column mapping using
    the existing dataset mapper.
    """
    mapping_result = map_columns(columns)

    source_to_target = {}

    for target_column, mapping in mapping_result["mappings"].items():
        source_column = mapping.get("source_column")

        if source_column:
            source_to_target[source_column] = target_column

    return source_to_target


def normalize_record(
    record: Dict[str, Any],
    source_to_target: Dict[str, str],
) -> Dict[str, Any]:
    """
    Convert one source record into the 38-column target schema.

    Missing fields are kept as None.
    No information is fabricated.
    """
    required_columns = get_required_columns()

    normalized_record = {
        column: None
        for column in required_columns
    }

    for source_column, target_column in source_to_target.items():
        if source_column in record:
            normalized_record[target_column] = normalize_value(
                record[source_column]
            )

    return normalized_record


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize an entire DataFrame into the 38-column
    AI Product Architect schema.
    """
    if df is None:
        raise ValueError("Dataset cannot be None.")

    if df.empty:
        raise ValueError("Dataset cannot be empty.")

    source_columns = df.columns.tolist()

    source_to_target = normalize_column_name_mapping(source_columns)

    records = df.to_dict(orient="records")

    normalized_records = [
        normalize_record(record, source_to_target)
        for record in records
    ]

    return pd.DataFrame(
        normalized_records,
        columns=get_required_columns(),
    )


def calculate_missing_value_rate(df: pd.DataFrame) -> float:
    """
    Calculate the percentage of missing values
    across the complete normalized dataset.
    """
    if df is None or df.empty:
        return 0.0

    total_cells = df.shape[0] * df.shape[1]

    if total_cells == 0:
        return 0.0

    missing_cells = int(df.isna().sum().sum())

    return round((missing_cells / total_cells) * 100, 2)


def get_normalization_report(
    source_df: pd.DataFrame,
    normalized_df: pd.DataFrame,
) -> dict:
    """
    Return a summary of the normalization process.
    """
    mapping_result = map_columns(source_df.columns.tolist())

    return {
        "source_rows": len(source_df),
        "source_columns": len(source_df.columns),
        "target_columns": len(normalized_df.columns),
        "target_schema_columns": len(get_required_columns()),
        "mapping_summary": mapping_result["summary"],
        "missing_value_rate": calculate_missing_value_rate(
            normalized_df
        ),
        "normalization_status": (
            "SUCCESS"
            if list(normalized_df.columns) == get_required_columns()
            else "FAILED"
        ),
    }
