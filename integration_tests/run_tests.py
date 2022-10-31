import argparse

from integration_test_utils import add_test_args
from run_handmade_tests import start_handmade_tests

# from run_prefab_tests import start_prefab_tests


if __name__ == "__main__":
    # TODO MCS-432
    # args = retrieve_test_args('All')
    # start_prefab_tests(
    #     args.mcs_unity_build_file_path,
    #     args.mcs_unity_github_branch_name
    # )
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
