"""CSV processing module for time series data.

Provides robust CSV parsing with automatic parameter detection,
manual column selection, and validation.
"""

import io
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

ENCODINGS_TO_TRY = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
DELIMITERS_TO_TRY = [",", ";", "\t", "|"]


class CSVValidationError(Exception):
    """Raised when CSV validation fails."""

    pass


@dataclass
class CSVParseResult:
    """Result of parsing a CSV file."""

    data: np.ndarray
    column_names: List[str]
    selected_column: str
    row_count: int
    detected_encoding: str
    detected_delimiter: str
    has_header: bool


def detect_csv_parameters(file_content: bytes) -> dict:
    """Detect CSV parameters from file content.

    Args:
        file_content: Raw bytes of the CSV file.

    Returns:
        Dictionary with keys: encoding, delimiter, has_header, column_count
    """
    for encoding in ENCODINGS_TO_TRY:
        try:
            content = file_content.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        content = file_content.decode("utf-8", errors="replace")

    best_delimiter = ","
    best_score = 0
    best_column_count = 0

    for delimiter in DELIMITERS_TO_TRY:
        try:
            lines = content.split("\n")[:5]
            column_counts = []
            for line in lines:
                if line.strip():
                    count = len(line.split(delimiter))
                    column_counts.append(count)
            if column_counts:
                consistency = len(set(column_counts))
                column_count = column_counts[0]
                score = consistency * 100 + column_count
                if score > best_score:
                    best_score = score
                    best_delimiter = delimiter
                    best_column_count = column_count
        except Exception:
            continue

    first_row = content.split("\n")[0] if content.strip() else ""
    has_header = False
    if first_row:
        header_parts = first_row.split(best_delimiter)
        for part in header_parts:
            try:
                float(part.strip())
            except ValueError:
                has_header = True
                break

        logger.info(
            "Detected CSV parameters: encoding=%s, delimiter=%r, has_header=%s",
            encoding,
            best_delimiter,
            has_header,
        )

    return {
        "encoding": encoding,
        "delimiter": best_delimiter,
        "has_header": has_header,
        "column_count": best_column_count,
    }


def _try_parse_with_params(
    content: str, delimiter: str, has_header: bool
) -> Optional[pd.DataFrame]:
    """Try to parse content with given parameters."""
    try:
        df = pd.read_csv(
            content if isinstance(content, str) else content.decode("utf-8"),
            delimiter=delimiter,
            header=0 if has_header else None,
            encoding="utf-8",
        )
        return df
    except Exception:
        return None


def parse_csv(
    file_content: bytes,
    column_index: Optional[int] = None,
    column_name: Optional[str] = None,
) -> CSVParseResult:
    """Parse a CSV file and extract time series data.

    Args:
        file_content: Raw bytes of the CSV file.
        column_index: Optional 0-based column index to select.
        column_name: Optional column name to select.

    Returns:
        CSVParseResult with extracted data and metadata.

    Raises:
        CSVValidationError: If CSV is empty, invalid, or fails validation.
    """
    if not file_content or not file_content.strip():
        raise CSVValidationError("CSV file is empty")

    params = detect_csv_parameters(file_content)
    encoding = params["encoding"]
    delimiter = params["delimiter"]
    has_header = params["has_header"]

    content = file_content.decode(encoding)

    if not content.strip():
        raise CSVValidationError("CSV file is empty after stripping whitespace")

    try:
        df = pd.read_csv(
            io.StringIO(content),
            delimiter=delimiter,
            header=0 if has_header else None,
        )
    except Exception as e:
        raise CSVValidationError(f"Failed to parse CSV: {e}")

    column_names = list(df.columns)

    if df.empty:
        raise CSVValidationError("CSV file has no data rows")

    row_count = len(df)

    if column_index is not None:
        if column_index < 0 or column_index >= len(df.columns):
            raise CSVValidationError(f"Invalid column index: {column_index}")
        selected_col = df.columns[column_index]
        selected_column = str(selected_col)
        col_values = df.iloc[:, column_index]
    elif column_name is not None:
        if column_name not in df.columns:
            raise CSVValidationError(f"Column not found: {column_name}")
        selected_column = column_name
        col_values = df[column_name]
    else:
        numeric_cols = []
        for i, col in enumerate(df.columns):
            try:
                pd.to_numeric(df[col], errors="raise")
                numeric_cols.append((i, col))
            except (ValueError, TypeError):
                continue

        if not numeric_cols:
            raise CSVValidationError("No numeric columns found in CSV")

        selected_idx, selected_col = numeric_cols[0]
        selected_column = str(selected_col)
        col_values = df.iloc[:, selected_idx]

    col_values = col_values.replace(r"^\s*$", np.nan, regex=True)
    numeric_values = pd.to_numeric(col_values, errors="coerce")
    valid_mask = ~numeric_values.isna()
    numeric_ratio = valid_mask.sum() / len(numeric_values) if len(numeric_values) > 0 else 0

    if numeric_ratio < 0.5:
        raise CSVValidationError(
            f"Less than 50% numeric values in selected column (found {numeric_ratio*100:.1f}%)"
        )

    data = numeric_values.dropna().values.astype(np.float64)

    validate_csv_data(data, col_values)

    return CSVParseResult(
        data=data,
        column_names=column_names,
        selected_column=selected_column,
        row_count=row_count,
        detected_encoding=encoding,
        detected_delimiter=delimiter,
        has_header=has_header,
    )


def validate_csv_data(data: np.ndarray, column_values: pd.Series) -> None:
    """Validate parsed CSV data.

    Args:
        data: The numpy array of time series values.
        column_values: The original pandas Series for statistics.

    Raises:
        CSVValidationError: If validation fails.
    """
    if len(data) < 10:
        raise CSVValidationError(
            f"Insufficient data rows: {len(data)} (minimum 10 required)"
        )

    total_values = len(column_values)
    numeric_values = pd.to_numeric(column_values, errors="coerce")
    valid_numeric = numeric_values.dropna()
    numeric_ratio = len(valid_numeric) / total_values if total_values > 0 else 0

    if numeric_ratio < 0.5:
        raise CSVValidationError(
            f"Less than 50% numeric values in column (found {numeric_ratio*100:.1f}%)"
        )

    unique_values = np.unique(data)
    if len(unique_values) == 1:
        raise CSVValidationError(
            f"Flat signal detected: all {len(data)} values are identical ({unique_values[0]})"
        )

    most_common_count = np.sum(data == unique_values[0])
    flat_ratio = most_common_count / len(data) if len(data) > 0 else 0
    if flat_ratio > 0.9:
        raise CSVValidationError(
            f"Flat signal detected: {flat_ratio*100:.1f}% of values are identical"
        )
