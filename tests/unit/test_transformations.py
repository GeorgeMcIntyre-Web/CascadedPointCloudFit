"""Unit tests for TransformationUtils."""

import pytest
import numpy as np
from cascaded_fit.core.transformations import TransformationUtils


class TestTransformationUtils:
    """Test TransformationUtils class."""

    def test_float_to_max_decimals_string_default(self):
        """Test float_to_max_decimals_string with default decimals."""
        result = TransformationUtils.float_to_max_decimals_string(1.23456789)
        assert isinstance(result, str)
        # Check it starts with the expected value (floating point precision may vary)
        assert result.startswith('1.2345678')
        assert len(result.split('.')[1]) == 50  # Default is 50 decimals

    def test_float_to_max_decimals_string_custom(self):
        """Test float_to_max_decimals_string with custom decimals."""
        result = TransformationUtils.float_to_max_decimals_string(1.23456789, decimals=5)
        assert result == "1.23457"  # Rounded to 5 decimals

    def test_float_to_max_decimals_string_zero(self):
        """Test float_to_max_decimals_string with zero."""
        result = TransformationUtils.float_to_max_decimals_string(0.0, decimals=5)
        assert result == "0.00000"

    def test_float_to_max_decimals_string_negative(self):
        """Test float_to_max_decimals_string with negative number."""
        result = TransformationUtils.float_to_max_decimals_string(-1.23456789, decimals=3)
        assert result == "-1.235"

    def test_array_to_csv_string_identity(self):
        """Test array_to_csv_string with identity matrix."""
        identity = np.eye(4)
        result = TransformationUtils.array_to_csv_string(identity)
        
        assert isinstance(result, str)
        lines = result.split('\n')
        assert len(lines) == 4  # 4 rows
        
        # Check first line (should be mostly 1.0, 0.0, 0.0, 0.0)
        first_line = lines[0]
        assert '1.00000' in first_line or '1.000000' in first_line

    def test_array_to_csv_string_custom(self):
        """Test array_to_csv_string with custom matrix."""
        matrix = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        result = TransformationUtils.array_to_csv_string(matrix)
        
        lines = result.split('\n')
        assert len(lines) == 2
        
        # Check that values are in the string
        assert '1.0' in lines[0] or '1.00000' in lines[0]
        assert '2.0' in lines[0] or '2.00000' in lines[0]

    def test_array_to_csv_string_no_trailing_newline(self):
        """Test array_to_csv_string doesn't have trailing newline."""
        matrix = np.array([[1.0, 2.0]])
        result = TransformationUtils.array_to_csv_string(matrix)
        
        assert not result.endswith('\n')

