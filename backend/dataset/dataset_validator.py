from typing import List

from backend.dataset.schema import get_required_columns


def validate_dataset_columns(columns: List[str]) -> dict:
    """
    Validate a dataset against the 38-field AI Product Architect schema.
    """
    source_columns = list(columns)
    required_columns = get_required_columns()

    duplicates = [
        column
        for column in set(source_columns)
        if source_columns.count(column) > 1
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in source_columns
    ]

    matched_columns = [
        column
        for column in required_columns
        if column in source_columns
    ]

    coverage = (
        len(matched_columns) / len(required_columns) * 100
        if required_columns
        else 0.0
    )

    return {
        "valid": len(source_columns) > 0 and len(duplicates) == 0,
        "total_source_columns": len(source_columns),
        "total_required_columns": len(required_columns),
        "matched_columns": matched_columns,
        "missing_columns": missing_columns,
        "duplicate_columns": sorted(duplicates),
        "coverage_percent": round(coverage, 2),
    }


def validate_dataset_frame(df) -> dict:
    """
    Validate a loaded pandas DataFrame.
    """
    if df is None:
        return {
            "valid": False,
            "error": "Dataset is None",
        }

    if len(df) == 0:
        return {
            "valid": False,
            "error": "Dataset is empty",
        }

    result = validate_dataset_columns(df.columns.tolist())

    result["rows"] = len(df)
    result["empty_columns"] = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    return result
