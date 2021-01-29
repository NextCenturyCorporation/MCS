import json

import machine_common_sense as mcs
from integration_test_utils import print_divider, retrieve_test_args


OBJECT_REGISTRY_LIST = [
    'ai2thor_object_registry.json',
    'mcs_object_registry.json',
    'primitive_object_registry.json'
]


def identify_mcs_resources_github_link(branch):
    return f'https://github.com/NextCenturyCorporation/ai2thor/tree/{branch}/unity/Assets/Resources/MCS/'


def start_prefab_tests(mcs_unity_build, branch):
    # TODO MCS-432
    pass


if __name__ == "__main__":
    args = retrieve_test_args('Prefab')
    start_prefab_tests(
        args.mcs_unity_build_file_path,
        args.mcs_unity_github_branch_name
    )
