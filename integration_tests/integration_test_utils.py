import argparse
import pathlib

METADATA_TIER_LIST = ['level1', 'level2', 'oracle']

config_dir = pathlib.Path(__file__).parent
DEFAULT_TEST_CONFIGS = {
    'level1': str(config_dir / 'config_level1.ini'),
    'level2': str(config_dir / 'config_level2.ini'),
    'oracle': str(config_dir / 'config_oracle.ini')
}


def print_divider():
    print('========================================')


def add_test_args(parser: argparse.ArgumentParser,
                  handmade_only=False) -> argparse.ArgumentParser:
    parser.add_argument(
        '--metadata',
        default=None,
        choices=[metadata_tier for metadata_tier in METADATA_TIER_LIST],
        help='Metadata tier to run (by default, test each metadata tier)'
    )
    parser.add_argument(
        '--test',
        default=None,
        help='Specific test filename prefix to run (by default, all files)'
    )
    parser.add_argument(
        '--ignore',
        default=None,
        help='Comma-separated list of each test filename prefix to ignore'
    )
    parser.add_argument(
        '--dev',
        default=False,
        action='store_true',
        help='Run in dev mode (useful for adding new test scenes)'
    )
    parser.add_argument(
        '--autofix',
        default=False,
        action='store_true',
        help='Automatically fix test failures (only use with care!)'
    )
    parser.add_argument(
        '--mcs_unity_build_file_path',
        type=str,
        default=None,
        help='Path to MCS unity build file'
    )
    parser.add_argument(
        '--mcs_unity_version',
        type=str,
        default=None,
        help=(
            'Version of the MCS Unity build and addressables to download '
            '(like "development"). Default: current'
        )
    )
    return parser
