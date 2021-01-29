import argparse


METADATA_TIER_LIST = [
    ('level1', './config_level1.ini'),
    ('level2', './config_level2.ini'),
    ('oracle', './config_oracle.ini')
]


def print_divider():
    print('========================================')


def retrieve_test_args(name, handmade_only=False):
    parser = argparse.ArgumentParser(
        description=(f'Run {name} Integration Tests')
    )
    parser.add_argument(
        'mcs_unity_build_file_path',
        help='Path to MCS unity build file'
    )
    if not handmade_only:
        parser.add_argument(
            'mcs_unity_github_branch_name',
            help='Name of branch/tag on MCS AI2-THOR Unity GitHub repository'
        )
    parser.add_argument(
        '--metadata',
        default=None,
        choices=[metadata_tier[0] for metadata_tier in METADATA_TIER_LIST],
        help='Metadata tier to run (by default, test each metadata tier)'
    )
    parser.add_argument(
        '--test',
        default=None,
        help='Specific test filename prefix to run (by default, all files)'
    )
    return parser.parse_args()
