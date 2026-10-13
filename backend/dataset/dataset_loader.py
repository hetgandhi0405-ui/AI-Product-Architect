from pathlib import Path
import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet"}


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a dataset from CSV, JSON, JSONL, or Parquet format.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported dataset format: {path.suffix}. "
            f"Supported formats: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    extension = path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(path)

    if extension == ".json":
        return pd.read_json(path)

    if extension == ".jsonl":
        return pd.read_json(path, lines=True)

    if extension == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(f"Unsupported dataset format: {extension}")


def inspect_dataset(df: pd.DataFrame) -> dict:
    """
    Return basic dataset intelligence for schema mapping.
    """
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "missing_values": df.isna().sum().to_dict(),
        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
    }
