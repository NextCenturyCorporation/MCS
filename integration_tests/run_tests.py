import argparse

from integration_test_utils import add_test_args
from run_handmade_tests import start_handmade_tests

"""
This script is effectively the same as running run_handmade_tests directly,
but kept here to avoid breaking our CI/CD workflow.
"""


if __name__ == "__main__":
    # Intentionally don't run the "prefab tests", because it seems excessive.
    parser = argparse.ArgumentParser(
        description="Run All Integration Tests"
    )
    parser = add_test_args(parser, handmade_only=True)
    args = parser.parse_args()
    start_handmade_tests(
        args.mcs_unity_build_file_path,
        args.metadata,
        args.test,
        args.dev,
        args.autofix,
        args.ignore,
        unity_version=args.mcs_unity_version
    )
