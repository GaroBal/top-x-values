from pathlib import Path

import dask.dataframe as dd

from app.exceptions import DataProcessingError, DataValidationError


def validate_and_extract_value(raw_data: str) -> int:
    """
    Validates and extracts numeric value from raw data string.

    Args:
        raw_data: String in format "id_value"

    Returns:
        Extracted integer value
    """
    if not isinstance(raw_data, str):
        raise DataValidationError(f"Expected string data, got {type(raw_data)}")

    parts = raw_data.split("_")

    try:
        return int(parts[1])
    except ValueError:
        raise DataValidationError(
            f"Invalid value format in '{raw_data}': expected integer"
        )


def read_dataframe(data_path: Path, partition_size: str) -> dd.DataFrame:
    """
    Helper method to read parquet file.

    Returns:
        Dask DataFrame
    """
    try:
        return dd.read_parquet(data_path, engine="pyarrow", blocksize=partition_size)
    except Exception as e:
        raise DataProcessingError(f"Failed to read parquet file: {str(e)}")
