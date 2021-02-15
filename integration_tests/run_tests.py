from integration_test_utils import retrieve_test_args
from run_handmade_tests import start_handmade_tests
# from run_prefab_tests import start_prefab_tests


if __name__ == "__main__":
    # TODO MCS-432
    # args = retrieve_test_args('All')
    # start_prefab_tests(
    #     args.mcs_unity_build_file_path,
    #     args.mcs_unity_github_branch_name
    # )
    args = retrieve_test_args('All', handmade_only=True)
    start_handmade_tests(
        args.mcs_unity_build_file_path,
        args.metadata,
        args.test,
        args.dev
    )
