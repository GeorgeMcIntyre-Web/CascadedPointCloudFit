"""Integration tests for CLI interface."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from cascaded_fit.cli.main import CLI, main
from cascaded_fit.utils.exceptions import CascadedFitError


class TestCLI:
    """Test CLI class."""

    def test_cli_initialization(self):
        """Test CLI initializes correctly."""
        cli = CLI()
        assert cli.parser is not None
        assert cli.config is not None

    def test_parse_arguments_basic(self):
        """Test basic argument parsing."""
        cli = CLI()
        
        # Test with minimal arguments
        args = cli.parser.parse_args(['source.ply', 'target.ply'])
        assert args.source_file == 'source.ply'
        assert args.target_file == 'target.ply'
        assert args.visualize is False
        assert args.verbose is False

    def test_parse_arguments_with_options(self):
        """Test argument parsing with options."""
        cli = CLI()
        
        args = cli.parser.parse_args([
            'source.ply',
            'target.ply',
            '--visualize',
            '--verbose',
            '--output', 'result.json',
            '--format', 'json'
        ])
        
        assert args.visualize is True
        assert args.verbose is True
        assert args.output == 'result.json'
        assert args.format == 'json'

    def test_parse_arguments_with_config(self):
        """Test argument parsing with config file."""
        cli = CLI()
        
        args = cli.parser.parse_args([
            'source.ply',
            'target.ply',
            '--config', 'custom.yaml'
        ])
        
        assert args.config == 'custom.yaml'

    def test_parse_arguments_rmse_threshold(self):
        """Test RMSE threshold argument."""
        cli = CLI()
        
        args = cli.parser.parse_args([
            'source.ply',
            'target.ply',
            '--rmse-threshold', '0.001'
        ])
        
        # Argument parser converts string to float
        assert args.rmse_threshold == 0.001

    @patch('cascaded_fit.cli.main.CascadedFitter')
    @patch('cascaded_fit.cli.main.PointCloudReader')
    def test_run_success(self, mock_reader, mock_fitter_class):
        """Test successful CLI run."""
        # Setup mocks
        mock_fitter = MagicMock()
        mock_fitter.run.return_value = {
            'transformation': [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            'inlier_rmse': 0.001,
            'max_error': 0.003,
            'is_success': True,
            'method': 'ICP'
        }
        mock_fitter_class.return_value = mock_fitter
        
        cli = CLI()
        args = cli.parser.parse_args(['source.ply', 'target.ply'])
        
        # Should not raise exception
        try:
            cli.run(args)
        except SystemExit:
            pass  # CLI may call sys.exit

    @patch('cascaded_fit.cli.main.CascadedFitter')
    @patch('cascaded_fit.cli.main.Path')
    def test_run_file_not_found(self, mock_path, mock_fitter_class):
        """Test CLI run with non-existent file."""
        # Mock Path.exists to return False
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        cli = CLI()
        args = cli.parser.parse_args(['nonexistent.ply', 'target.ply'])
        
        # CLI returns error code 2 for file errors (doesn't raise)
        result = cli.run(args)
        assert result == 2

    @patch('cascaded_fit.cli.main.CascadedFitter')
    @patch('cascaded_fit.cli.main.Path')
    def test_run_registration_error(self, mock_path, mock_fitter_class):
        """Test CLI run with registration error."""
        from cascaded_fit.utils.exceptions import RegistrationError
        
        # Mock Path.exists to return True (files exist)
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_fitter = MagicMock()
        mock_fitter.run.side_effect = RegistrationError("Registration failed")
        mock_fitter_class.return_value = mock_fitter
        
        cli = CLI()
        args = cli.parser.parse_args(['source.ply', 'target.ply'])
        
        # CLI returns error code 3 for registration errors (doesn't raise)
        result = cli.run(args)
        assert result == 3


class TestCLIMainFunction:
    """Test main function entry point."""

    @patch('cascaded_fit.cli.main.CLI')
    @patch('sys.argv', ['cascaded_fit.cli', 'source.ply', 'target.ply'])
    def test_main_function(self, mock_cli_class):
        """Test main function calls CLI."""
        mock_cli = MagicMock()
        mock_cli_class.return_value = mock_cli
        
        try:
            main()
        except SystemExit:
            pass  # CLI may call sys.exit
        
        # Verify CLI was instantiated and run was called
        mock_cli_class.assert_called_once()

    @patch('sys.argv', ['cascaded_fit.cli', '--help'])
    def test_main_help(self):
        """Test main function with --help."""
        with pytest.raises(SystemExit):
            main()


class TestCLIOutputFormats:
    """Test CLI output format handling."""

    @patch('cascaded_fit.cli.main.CascadedFitter')
    def test_output_format_text(self, mock_fitter_class):
        """Test text output format."""
        mock_fitter = MagicMock()
        mock_fitter.run.return_value = {
            'transformation': [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            'inlier_rmse': 0.001,
            'max_error': 0.003,
            'is_success': True,
            'method': 'ICP'
        }
        mock_fitter_class.return_value = mock_fitter
        
        cli = CLI()
        args = cli.parser.parse_args([
            'source.ply',
            'target.ply',
            '--format', 'text'
        ])
        
        # Should handle text format
        try:
            cli.run(args)
        except SystemExit:
            pass

    @patch('cascaded_fit.cli.main.CascadedFitter')
    @patch('builtins.open', create=True)
    def test_output_format_json(self, mock_open, mock_fitter_class):
        """Test JSON output format."""
        mock_fitter = MagicMock()
        mock_fitter.run.return_value = {
            'transformation': [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            'inlier_rmse': 0.001,
            'max_error': 0.003,
            'is_success': True,
            'method': 'ICP'
        }
        mock_fitter_class.return_value = mock_fitter
        
        cli = CLI()
        args = cli.parser.parse_args([
            'source.ply',
            'target.ply',
            '--format', 'json',
            '--output', 'result.json'
        ])
        
        # Should write JSON file
        try:
            cli.run(args)
        except SystemExit:
            pass

