"""Transformation utilities."""

import numpy as np


class TransformationUtils:
    """Utilities for transformation matrices."""

    @staticmethod
    def float_to_max_decimals_string(value: float, decimals: int = 50) -> str:
        """
        Convert float to string with maximum decimals.

        Args:
            value: Float value
            decimals: Number of decimal places

        Returns:
            Formatted string
        """
        return f"{value:.{decimals}f}"

    @staticmethod
    def array_to_csv_string(array: np.ndarray) -> str:
        """
        Convert numpy array to CSV string.

        Args:
            array: Numpy array (typically 4x4 transformation matrix)

        Returns:
            CSV-formatted string
        """
        csv_string = ""
        for row in array:
            row_string = ",".join(
                TransformationUtils.float_to_max_decimals_string(value)
                for value in row
            )
            csv_string += row_string + "\n"

        # Remove final newline
        csv_string = csv_string.rstrip("\n")
        return csv_string
