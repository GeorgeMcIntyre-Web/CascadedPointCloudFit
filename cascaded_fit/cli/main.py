"""
Command-line interface for cascaded point cloud registration.

This module provides a modern CLI for running point cloud registration
with comprehensive options, logging, and output formatting.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from cascaded_fit.utils.logger import Logger
from cascaded_fit.utils.config import Config
from cascaded_fit.utils.exceptions import CascadedFitError
from cascaded_fit.fitters.cascaded_fitter import CascadedFitter
from cascaded_fit.io.readers import PointCloudReader
from cascaded_fit.core.transformations import TransformationUtils

# Initialize logger
logger = Logger.get(__name__)


class CLI:
    """
    Command-line interface for point cloud registration.

    Provides options for:
    - ICP and FGR registration
    - Visualization of results
    - Custom configuration files
    - JSON or text output
    - Verbose logging
    """

    def __init__(self):
        """Initialize CLI with argument parser."""
        self.parser = self._create_parser()
        self.config = Config()

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create argument parser with all CLI options.

        Returns:
            Configured ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description='Cascaded point cloud registration using ICP and FGR',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic registration
  python -m cascaded_fit.cli.main source.ply target.ply

  # With visualization
  python -m cascaded_fit.cli.main source.ply target.ply --visualize

  # Custom configuration
  python -m cascaded_fit.cli.main source.ply target.ply --config custom.yaml

  # JSON output to file
  python -m cascaded_fit.cli.main source.ply target.ply --output result.json --format json

  # Verbose logging
  python -m cascaded_fit.cli.main source.ply target.ply --verbose
            """
        )

        # Required arguments
        parser.add_argument(
            'source_file',
            type=str,
            help='Path to source point cloud file (CSV or PLY)'
        )

        parser.add_argument(
            'target_file',
            type=str,
            help='Path to target point cloud file (CSV or PLY)'
        )

        # Optional arguments
        parser.add_argument(
            '--visualize',
            action='store_true',
            help='Visualize registration results using Open3D'
        )

        parser.add_argument(
            '--config',
            type=str,
            default=None,
            help='Path to custom configuration YAML file'
        )

        parser.add_argument(
            '--output',
            '-o',
            type=str,
            default=None,
            help='Path to save output results'
        )

        parser.add_argument(
            '--format',
            choices=['text', 'json', 'csv'],
            default='text',
            help='Output format (default: text)'
        )

        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='Enable verbose logging (DEBUG level)'
        )

        parser.add_argument(
            '--log-file',
            type=str,
            default=None,
            help='Path to log file (default: cascaded_fit.log)'
        )

        # Registration parameters (override config)
        reg_group = parser.add_argument_group('registration parameters')

        reg_group.add_argument(
            '--rmse-threshold',
            type=float,
            default=None,
            help='RMSE threshold for success (default: from config)'
        )

        reg_group.add_argument(
            '--max-iterations',
            type=int,
            default=None,
            help='Maximum ICP iterations (default: from config)'
        )

        # ICP parameters
        icp_group = parser.add_argument_group('ICP parameters')

        icp_group.add_argument(
            '--icp-max-correspondence-distance',
            type=float,
            default=None,
            help='ICP max correspondence distance (default: from config)'
        )

        icp_group.add_argument(
            '--icp-relative-fitness',
            type=float,
            default=None,
            help='ICP relative fitness (default: from config)'
        )

        icp_group.add_argument(
            '--icp-relative-rmse',
            type=float,
            default=None,
            help='ICP relative RMSE (default: from config)'
        )

        # FGR parameters
        fgr_group = parser.add_argument_group('FGR parameters')

        fgr_group.add_argument(
            '--fgr-voxel-size',
            type=float,
            default=None,
            help='FGR voxel size (default: from config)'
        )

        fgr_group.add_argument(
            '--fgr-distance-threshold',
            type=float,
            default=None,
            help='FGR distance threshold (default: from config)'
        )

        return parser

    def setup_logging(self, args: argparse.Namespace) -> None:
        """
        Setup logging based on CLI arguments.

        Args:
            args: Parsed command-line arguments
        """
        log_level = 'DEBUG' if args.verbose else 'INFO'
        log_file = args.log_file or 'cascaded_fit.log'

        Logger.setup(
            log_file=log_file,
            level=log_level,
            log_to_console=True
        )

        logger.info("=" * 60)
        logger.info("Cascaded Point Cloud Registration CLI")
        logger.info("=" * 60)

    def validate_inputs(self, args: argparse.Namespace) -> None:
        """
        Validate input files exist.

        Args:
            args: Parsed command-line arguments

        Raises:
            FileNotFoundError: If input files don't exist
        """
        source_path = Path(args.source_file)
        target_path = Path(args.target_file)

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {args.source_file}")

        if not target_path.exists():
            raise FileNotFoundError(f"Target file not found: {args.target_file}")

        logger.info(f"Source file: {source_path.absolute()}")
        logger.info(f"Target file: {target_path.absolute()}")

    def load_config(self, args: argparse.Namespace) -> None:
        """
        Load configuration from file or use defaults.

        Args:
            args: Parsed command-line arguments
        """
        if args.config:
            logger.info(f"Loading custom configuration: {args.config}")
            self.config.load(args.config)
        else:
            logger.info("Using default configuration")
            self.config.load()

    def create_fitter(self, args: argparse.Namespace) -> CascadedFitter:
        """
        Create CascadedFitter with configuration.

        Args:
            args: Parsed command-line arguments

        Returns:
            Configured CascadedFitter instance
        """
        # Override config with CLI arguments if provided
        fitter_kwargs = {}

        if args.rmse_threshold is not None:
            fitter_kwargs['rmse_threshold'] = args.rmse_threshold

        if args.max_iterations is not None:
            fitter_kwargs['max_iterations'] = args.max_iterations

        if args.icp_max_correspondence_distance is not None:
            fitter_kwargs['icp_max_correspondence_distance'] = \
                args.icp_max_correspondence_distance

        if args.icp_relative_fitness is not None:
            fitter_kwargs['icp_relative_fitness'] = args.icp_relative_fitness

        if args.icp_relative_rmse is not None:
            fitter_kwargs['icp_relative_rmse'] = args.icp_relative_rmse

        if args.fgr_voxel_size is not None:
            fitter_kwargs['fgr_voxel_size'] = args.fgr_voxel_size

        if args.fgr_distance_threshold is not None:
            fitter_kwargs['fgr_distance_threshold'] = args.fgr_distance_threshold

        fitter_kwargs['visualize'] = args.visualize

        logger.info(f"Creating fitter with parameters: {fitter_kwargs}")

        return CascadedFitter(**fitter_kwargs)

    def format_output(
        self,
        result: dict,
        format_type: str
    ) -> str:
        """
        Format registration result for output.

        Args:
            result: Registration result dictionary
            format_type: Output format ('text', 'json', 'csv')

        Returns:
            Formatted output string
        """
        if format_type == 'json':
            return json.dumps(result, indent=2)

        elif format_type == 'csv':
            # CSV format for transformation matrix
            transform = result.get('transformation')
            if transform:
                return TransformationUtils.array_to_csv_string(transform)
            return ""

        else:  # text
            lines = []
            lines.append("\n" + "=" * 60)
            lines.append("REGISTRATION RESULTS")
            lines.append("=" * 60)

            lines.append(f"\nMethod: {result.get('method', 'Unknown')}")
            lines.append(f"Success: {'Yes' if result.get('is_success') else 'No'}")
            lines.append(f"RMSE: {result.get('inlier_rmse', 0):.6f}")
            lines.append(f"Max Error: {result.get('max_error', 0):.6f}")

            if result.get('transformation') is not None:
                lines.append("\nTransformation Matrix:")
                transform = result['transformation']
                for row in transform:
                    lines.append("  " + " ".join(f"{x:12.8f}" for x in row))

            lines.append("=" * 60 + "\n")

            return "\n".join(lines)

    def save_output(self, output: str, output_path: str) -> None:
        """
        Save output to file.

        Args:
            output: Formatted output string
            output_path: Path to save output
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(output)

        logger.info(f"Results saved to: {output_file.absolute()}")

    def run(self, args: Optional[argparse.Namespace] = None) -> int:
        """
        Run the CLI application.

        Args:
            args: Optional parsed arguments (for testing)

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Parse arguments
            if args is None:
                args = self.parser.parse_args()

            # Setup logging
            self.setup_logging(args)

            # Validate inputs
            self.validate_inputs(args)

            # Load configuration
            self.load_config(args)

            # Create fitter
            fitter = self.create_fitter(args)

            # Run registration
            logger.info("Starting registration...")
            result = fitter.run(args.source_file, args.target_file)

            # Format output
            output = self.format_output(result, args.format)

            # Print to console
            print(output)

            # Save to file if requested
            if args.output:
                self.save_output(output, args.output)

            # Return success/failure based on result
            if result.get('is_success'):
                logger.info("Registration completed successfully")
                return 0
            else:
                logger.warning("Registration did not meet success criteria")
                return 1

        except FileNotFoundError as e:
            logger.error(f"File error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 2

        except CascadedFitError as e:
            logger.error(f"Registration error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 3

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 4


def main():
    """Entry point for CLI."""
    cli = CLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
