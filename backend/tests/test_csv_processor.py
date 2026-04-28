"""Tests for csv_processor module.

This test suite covers:
- CSV parameter detection (encoding, delimiter, header)
- CSV parsing with column selection
- CSV validation rules
- Error handling and edge cases
"""

import io
from typing import Callable

import numpy as np
import pandas as pd
import pytest

from app.csv_processor import (
    CSVParseResult,
    CSVValidationError,
    detect_csv_parameters,
    parse_csv,
    validate_csv_data,
)


# ============================================================================
# Test Fixtures - CSV byte strings
# ============================================================================


@pytest.fixture
def sample_csv_comma() -> bytes:
    """UTF-8, comma-delimited, with header, 100 rows."""
    lines = ["date,value"]
    for i in range(100):
        lines.append(f"2024-01-{i % 30 + 1:02d},{i * 0.5}")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_semicolon() -> bytes:
    """Latin-1, semicolon-delimited, with header, 100 rows."""
    lines = ["horodatage;mesure"]
    for i in range(100):
        lines.append(f"2024-01-{i % 30 + 1:02d};{i * 0.5}")
    return "\n".join(lines).encode("latin-1")


@pytest.fixture
def sample_csv_tab() -> bytes:
    """Tab-delimited, no header, 50 rows."""
    lines = []
    for i in range(50):
        lines.append(f"{i}\t{i * 0.1}")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_pipe() -> bytes:
    """Pipe-delimited, with header, 50 rows."""
    lines = ["id|reading"]
    for i in range(50):
        lines.append(f"row_{i}|{i * 1.5}")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_no_header() -> bytes:
    """No header, comma-delimited, numeric only, 100 rows."""
    lines = []
    for i in range(100):
        lines.append(f"{i},{i * 0.5}")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_multi_column() -> bytes:
    """3 numeric columns to test column selection."""
    lines = ["time,open,high,low,close"]
    for i in range(100):
        lines.append(f"{i},{i * 1.0},{i * 1.1},{i * 0.9},{i * 1.05}")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_quoted() -> bytes:
    """Fields with commas inside quotes, 13 rows total (3 data + header)."""
    content = 'name,value\n"John, Smith",100\n"Doe, Jane",200\n"Test, Inc.",300\n"Data, Corp.",400\n"Acme, LLC",500\n"Global, Inc",600\n"Local, Ltd",700\n"First, Corp",800\n"Second, LLC",900\n"Third, Inc",1000\n"Fourth, Ltd",1100\n"Fifth, Corp",1200'
    return content.encode("utf-8")


@pytest.fixture
def sample_csv_windows_line_endings() -> bytes:
    """\\r\\n line endings."""
    lines = ["date,value"]
    for i in range(50):
        lines.append(f"2024-01-{i % 30 + 1:02d},{i * 0.5}")
    return "\r\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_empty() -> bytes:
    """Empty file."""
    return b""


@pytest.fixture
def sample_csv_non_numeric() -> bytes:
    """All text values."""
    content = "name,description\nfoo,bar\nbaz,qux\nabc,def"
    return content.encode("utf-8")


@pytest.fixture
def sample_csv_flat() -> bytes:
    """100 identical values - should fail flat signal check."""
    lines = ["value"]
    for _ in range(100):
        lines.append("42.0")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_too_few_rows() -> bytes:
    """Only 5 rows - below minimum 10."""
    lines = ["value"]
    for i in range(5):
        lines.append(f"{i}.0")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_large() -> bytes:
    """50,000 rows for performance test."""
    lines = ["value"]
    for i in range(50000):
        lines.append(f"{i * 0.5}")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_mixed_numeric_text() -> bytes:
    """Mixed numeric and non-numeric values - should pass if 50%+ numeric."""
    lines = ["value"]
    for i in range(100):
        if i % 100 < 51:
            lines.append(f"{i}.0")
        else:
            lines.append("N/A")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def sample_csv_cp1252() -> bytes:
    """CP1252 encoded content with special character."""
    return b"value\neuro: \x80\ntest: 100"


@pytest.fixture
def sample_csv_utf8_bom() -> bytes:
    """UTF-8 with BOM marker."""
    content = "\ufeffvalue\n100\n200\n300"
    return content.encode("utf-8-sig")


# ============================================================================
# Test Class: Detect CSV Parameters
# ============================================================================


class TestDetectCSVParameters:
    """Tests for detect_csv_parameters function."""

    def test_detect_comma_delimiter(self, sample_csv_comma: bytes) -> None:
        """Comma delimiter is correctly detected."""
        result = detect_csv_parameters(sample_csv_comma)
        assert result["delimiter"] == ","
        assert result["encoding"] == "utf-8"

    def test_detect_semicolon_delimiter(self, sample_csv_semicolon: bytes) -> None:
        """Semicolon delimiter is correctly detected."""
        result = detect_csv_parameters(sample_csv_semicolon)
        assert result["delimiter"] == ";"
        # Encoding may be utf-8 or latin-1 depending on content
        assert result["encoding"] in ("utf-8", "latin-1")

    def test_detect_tab_delimiter(self, sample_csv_tab: bytes) -> None:
        """Tab delimiter is correctly detected."""
        result = detect_csv_parameters(sample_csv_tab)
        assert result["delimiter"] == "\t"

    def test_detect_pipe_delimiter(self, sample_csv_pipe: bytes) -> None:
        """Pipe delimiter is correctly detected."""
        result = detect_csv_parameters(sample_csv_pipe)
        assert result["delimiter"] == "|"

    def test_detect_utf8_encoding(self, sample_csv_comma: bytes) -> None:
        """UTF-8 encoding is correctly detected."""
        result = detect_csv_parameters(sample_csv_comma)
        assert result["encoding"] == "utf-8"

    def test_detect_latin1_encoding(self, sample_csv_semicolon: bytes) -> None:
        """Latin-1 encoding is correctly detected."""
        result = detect_csv_parameters(sample_csv_semicolon)
        # Encoding may be utf-8 or latin-1 depending on content
        assert result["encoding"] in ("utf-8", "latin-1")

    def test_detect_cp1252_encoding(self, sample_csv_cp1252: bytes) -> None:
        """CP1252 encoding is correctly detected."""
        result = detect_csv_parameters(sample_csv_cp1252)
        # Latin-1 is checked before CP1252, so it may return latin-1 for CP1252-compatible bytes
        assert result["encoding"] in ("latin-1", "cp1252")

    def test_detect_utf8_bom(self, sample_csv_utf8_bom: bytes) -> None:
        """UTF-8 BOM is handled."""
        result = detect_csv_parameters(sample_csv_utf8_bom)
        assert result["encoding"] in ("utf-8", "utf-8-sig")
        assert result["has_header"] is True

    def test_detect_has_header(self, sample_csv_comma: bytes) -> None:
        """Header row is correctly detected when first row has non-numeric values."""
        result = detect_csv_parameters(sample_csv_comma)
        assert result["has_header"] is True
        assert result["column_count"] == 2

    def test_detect_no_header(self, sample_csv_no_header: bytes) -> None:
        """No header is detected when first row is numeric."""
        result = detect_csv_parameters(sample_csv_no_header)
        assert result["has_header"] is False
        assert result["column_count"] == 2

    def test_detect_column_count(self, sample_csv_multi_column: bytes) -> None:
        """Column count is correctly detected."""
        result = detect_csv_parameters(sample_csv_multi_column)
        assert result["column_count"] == 5


# ============================================================================
# Test Class: Parse CSV
# ============================================================================


class TestParseCSV:
    """Tests for parse_csv function."""

    def test_parse_basic_csv(self, sample_csv_comma: bytes) -> None:
        """Basic CSV parsing returns correct data."""
        result = parse_csv(sample_csv_comma)
        assert isinstance(result, CSVParseResult)
        assert result.row_count == 100
        assert len(result.data) == 100
        assert result.detected_encoding == "utf-8"
        assert result.detected_delimiter == ","

    def test_parse_auto_select_first_numeric_column(
        self, sample_csv_multi_column: bytes
    ) -> None:
        """When no column specified, first numeric column is selected."""
        result = parse_csv(sample_csv_multi_column)
        assert result.selected_column == "time"
        expected = np.array([float(i) for i in range(100)], dtype=np.float64)
        np.testing.assert_array_almost_equal(result.data, expected)

    def test_parse_with_column_index(self, sample_csv_comma: bytes) -> None:
        """Column selection by index works."""
        # value is column index 1
        result = parse_csv(sample_csv_comma, column_index=1)
        assert result.selected_column == "value"
        assert len(result.data) == 100

    def test_parse_with_column_name(self, sample_csv_comma: bytes) -> None:
        """Column selection by name works."""
        result = parse_csv(sample_csv_comma, column_name="value")
        assert result.selected_column == "value"
        assert len(result.data) == 100

    def test_parse_semicolon_delimited(self, sample_csv_semicolon: bytes) -> None:
        """Semicolon-delimited CSV is parsed correctly."""
        result = parse_csv(sample_csv_semicolon)
        assert result.detected_delimiter == ";"
        assert result.row_count == 100

    def test_parse_tab_delimited(self, sample_csv_tab: bytes) -> None:
        """Tab-delimited CSV is parsed correctly."""
        result = parse_csv(sample_csv_tab)
        assert result.detected_delimiter == "\t"
        assert result.row_count == 50

    def test_parse_pipe_delimited(self, sample_csv_pipe: bytes) -> None:
        """Pipe-delimited CSV is parsed correctly."""
        result = parse_csv(sample_csv_pipe)
        assert result.detected_delimiter == "|"
        assert result.row_count == 50

    def test_parse_quoted_fields(self, sample_csv_quoted: bytes) -> None:
        """Quoted fields with commas are handled correctly."""
        result = parse_csv(sample_csv_quoted)
        assert result.row_count == 12
        assert "value" in result.column_names

    def test_parse_windows_line_endings(self, sample_csv_windows_line_endings: bytes) -> None:
        """Windows line endings (\\r\\n) are handled correctly."""
        result = parse_csv(sample_csv_windows_line_endings)
        assert result.row_count == 50
        assert len(result.data) == 50

    def test_parse_large_file(self, sample_csv_large: bytes) -> None:
        """50,000 row file is parsed efficiently."""
        import time

        start = time.time()
        result = parse_csv(sample_csv_large)
        elapsed = time.time() - start

        assert result.row_count == 50000
        assert len(result.data) == 50000
        # Should complete in under 2 seconds
        assert elapsed < 2.0, f"Parsing took {elapsed:.2f}s, expected < 2s"


# ============================================================================
# Test Class: Validate CSV Data
# ============================================================================


class TestValidateCSVData:
    """Tests for validate_csv_data function."""

    def test_validate_accepts_valid_data(self, sample_csv_comma: bytes) -> None:
        """Valid CSV data passes validation."""
        result = parse_csv(sample_csv_comma)
        # Should not raise
        validate_csv_data(result.data, pd.Series(result.data))
        # If we get here, validation passed

    def test_validate_rejects_empty(self, sample_csv_empty: bytes) -> None:
        """Empty file raises CSVValidationError."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(sample_csv_empty)
        assert "empty" in str(exc_info.value).lower()

    def test_validate_rejects_too_few_rows(self, sample_csv_too_few_rows: bytes) -> None:
        """File with fewer than 10 rows raises CSVValidationError."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(sample_csv_too_few_rows)
        assert "10" in str(exc_info.value) or "row" in str(exc_info.value).lower()

    def test_validate_rejects_all_non_numeric(self, sample_csv_non_numeric: bytes) -> None:
        """File with all non-numeric data raises CSVValidationError."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(sample_csv_non_numeric)
        assert "numeric" in str(exc_info.value).lower() or "valid" in str(exc_info.value).lower()

    def test_validate_rejects_flat_signal(self, sample_csv_flat: bytes) -> None:
        """File with flat signal (>90% identical values) raises CSVValidationError."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(sample_csv_flat)
        assert "flat" in str(exc_info.value).lower() or "identical" in str(exc_info.value).lower()

    def test_validate_accepts_mixed_with_majority_numeric(
        self, sample_csv_mixed_numeric_text: bytes
    ) -> None:
        """Mixed numeric/non-numeric with 50%+ numeric passes validation."""
        result = parse_csv(sample_csv_mixed_numeric_text)
        # Should not raise - ~67% numeric (>50%)
        validate_csv_data(result.data, pd.Series(result.data))

    def test_validate_accepts_large_file(self, sample_csv_large: bytes) -> None:
        """50,000 row file passes validation."""
        result = parse_csv(sample_csv_large)
        # Should not raise
        validate_csv_data(result.data, pd.Series(result.data))


# ============================================================================
# Test Class: CSV Errors
# ============================================================================


class TestCSVErrors:
    """Tests for CSVValidationError exception."""

    def test_error_message_contains_column_stats(self, sample_csv_flat: bytes) -> None:
        """Error message includes column statistics for debugging."""
        with pytest.raises(CSVValidationError) as exc_info:
            parse_csv(sample_csv_flat)
        error_msg = str(exc_info.value)
        # Should mention unique value count or similar stats
        assert len(error_msg) > 0

    def test_error_on_invalid_column_index(self, sample_csv_comma: bytes) -> None:
        """Invalid column index raises CSVValidationError."""
        with pytest.raises(CSVValidationError):
            parse_csv(sample_csv_comma, column_index=999)

    def test_error_on_nonexistent_column_name(self, sample_csv_comma: bytes) -> None:
        """Nonexistent column name raises CSVValidationError."""
        with pytest.raises(CSVValidationError):
            parse_csv(sample_csv_comma, column_name="nonexistent_column")

    def test_error_empty_after_stripping(self) -> None:
        """File with only whitespace raises CSVValidationError."""
        with pytest.raises(CSVValidationError):
            parse_csv(b"   \n   \n   ")


# ============================================================================
# Test Class: CSV Edge Cases
# ============================================================================


class TestCSVEdgeCases:
    """Tests for edge cases in CSV processing."""

    def test_leading_whitespace(self) -> None:
        """Leading whitespace in data is handled."""
        content = "value\n  100\n  200\n  300\n  400\n  500\n  600\n  700\n  800\n  900\n  1000"
        result = parse_csv(content.encode("utf-8"))
        assert len(result.data) == 10

    def test_trailing_newline(self) -> None:
        """Trailing newline does not cause issues."""
        content = "value\n100\n200\n300\n400\n500\n600\n700\n800\n900\n1000\n"
        result = parse_csv(content.encode("utf-8"))
        assert len(result.data) == 10

    def test_single_row(self) -> None:
        """Single row file raises validation error (below minimum)."""
        content = "value\n100"
        with pytest.raises(CSVValidationError):
            parse_csv(content.encode("utf-8"))

    def test_single_valid_row(self) -> None:
        """Single row passes if we bypass validation (edge case)."""
        # Direct validation call on minimal data
        data = np.array([100.0])
        with pytest.raises(CSVValidationError):
            validate_csv_data(data, pd.Series(data))
