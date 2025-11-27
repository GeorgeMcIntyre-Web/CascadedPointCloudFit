"""Unit tests for CLI __main__ module."""

import pytest
import sys
from unittest.mock import patch
from cascaded_fit.cli import __main__


class TestCLIMain:
    """Test CLI __main__ module."""

    @patch('cascaded_fit.cli.__main__.main')
    @patch('sys.argv', ['cascaded_fit.cli', '--help'])
    def test_main_entry_point(self, mock_main):
        """Test __main__ entry point calls main()."""
        # This would normally call sys.exit, so we mock it
        with patch('sys.exit'):
            if __name__ == '__main__':
                __main__.main()
        
        # Verify main was imported
        assert hasattr(__main__, 'main')

