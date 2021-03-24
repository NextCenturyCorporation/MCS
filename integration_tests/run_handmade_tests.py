import argparse
import glob
import json
import math
import os.path
import time

import machine_common_sense as mcs
from additional_integration_tests import FUNCTION_LIST
from integration_test_utils import METADATA_TIER_LIST, print_divider, \
    add_test_args


INTEGRATION_TESTS_FOLDER = os.path.dirname(os.path.abspath(__file__))
TEST_FOLDER = INTEGRATION_TESTS_FOLDER + '/data/'
SCENE_SUFFIX = '.scene.json'
ACTIONS_SUFFIX = '.actions.txt'
OUTPUTS_SUFFIX = '.outputs.json'
INDENT = '    '


def return_position(expected, actual):
    return ((expected['x'], expected['z']), (actual['x'], actual['z']))


def return_values(expected, actual):
    return (expected, actual)


def create_test_case(name, expected, actual):
    return (name, expected, actual)


def create_step_test_case_list(expected, actual):
    test_case_list = [
        ('action_list', actual.action_list),
        ('head_tilt', round(actual.head_tilt)),
        ('objects_count', len(actual.object_list)),
        ('position_x', actual.position.get('x') if actual.position else None),
        ('position_z', actual.position.get('z') if actual.position else None),
        ('return_status', actual.return_status),
        ('reward', actual.reward),
        ('rotation_y', actual.rotation),
        ('step_number', actual.step_number),
        ('structural_objects_count', len(actual.structural_object_list))
    ]
    return [
        create_test_case([case_name], expected[case_name], actual_data)
        for case_name, actual_data in test_case_list
        if case_name in expected
    ]


def create_object_test_case_list(object_type, expected, actual):
    test_case_list = [
        ('direction_x', actual.direction['x']),
        ('direction_y', actual.direction['y']),
        ('direction_z', actual.direction['z']),
        ('distance', actual.distance_in_world),
        ('held', actual.held),
        ('mass', actual.mass),
        ('material_list', actual.material_list),
        ('position_x', actual.position.get('x') if actual.position else None),
        ('position_y', actual.position.get('y') if actual.position else None),
        ('position_z', actual.position.get('z') if actual.position else None),
        (
            'rotation_x',
            round(actual.rotation.get('x')) if actual.rotation else None
        ),
        (
            'rotation_y',
            round(actual.rotation.get('y')) if actual.rotation else None
        ),
        (
            'rotation_z',
            round(actual.rotation.get('z')) if actual.rotation else None
        ),
        ('shape', actual.shape),
        ('state_list', actual.state_list),
        ('texture_color_list', actual.texture_color_list),
        ('visible', actual.visible)
    ]
    return [create_test_case(
        [object_type, actual.uuid, case_name],
        expected[case_name],
        actual_data
    ) for case_name, actual_data in test_case_list if case_name in expected]


def validate_single_output(expected, actual):
    failed_validation_list = []
    # Create a list of each test case used to validate for the step output.
    test_case_list = create_step_test_case_list(expected, actual)
    # Create a collection of each object with expected output metadata.
    expected_object_dict = {}
    for expected_object in expected.get('objects', []):
        expected_object_dict[expected_object.get('id', '')] = (
            'objects',
            expected_object
        )
    for expected_object in expected.get('structural_objects', []):
        expected_object_dict[expected_object.get('id', '')] = (
            'structural_objects',
            expected_object
        )
    # For each object in the step output metdata...
    for actual_object in (actual.object_list + actual.structural_object_list):
        # If that object has expected metadata to validate...
        if actual_object.uuid not in expected_object_dict:
            continue
        # Add each test case for the object to the list.
        test_case_list.extend(create_object_test_case_list(
            expected_object_dict[actual_object.uuid][0],
            expected_object_dict[actual_object.uuid][1],
            actual_object
        ))
    # Validate each test case.
    for test_case, expected_data, actual_data in test_case_list:
        failed = (expected_data != actual_data)
        if (
            isinstance(expected_data, (int, float)) and
            isinstance(actual_data, (int, float))
        ):
            failed = (not math.isclose(
                expected_data,
                actual_data,
                rel_tol=0.001,
                abs_tol=0.001
            ))
        if failed:
            test_case_string = ' '.join(test_case)
            failed_validation_list.append((
                test_case,
                actual_data,
                expected_data,
                f'{test_case_string}: {actual_data} != {expected_data}'
            ))
    return failed_validation_list


def load_action_list(scene_filename):
    action_filename = scene_filename.replace(SCENE_SUFFIX, ACTIONS_SUFFIX)
    if not os.path.isfile(action_filename):
        return action_filename, None
    action_list = []
    with open(action_filename, encoding='utf-8-sig') as action_file:
        for line in action_file:
            line_data = line.strip().split(',')
            action_data = {
                'action': line_data[0],
                'params': {}
            }
            for key_value in line_data[1:]:
                key_value_data = key_value.split('=')
                action_data['params'][key_value_data[0]] = key_value_data[1]
            action_list.append(action_data)
    return action_filename, action_list


def load_output_list(scene_filename, metadata_tier):
    output_filename = scene_filename.replace(
        SCENE_SUFFIX,
        '.' + metadata_tier + OUTPUTS_SUFFIX
    )
    if not os.path.isfile(output_filename):
        return output_filename, None
    output_list = []
    with open(output_filename, encoding='utf-8-sig') as output_file:
        output_list = json.load(output_file)
    return output_filename, output_list


def run_single_scene(controller, scene_filename, metadata_tier, dev, autofix):
    # Load the test scene's JSON data.
    scene_data, status = mcs.load_scene_json_file(scene_filename)

    if status is not None:
        return False, status

    # Load this test's expected output metadata at each action step.
    output_filename, expected_output_data_list = load_output_list(
        scene_filename,
        metadata_tier
    )
    if expected_output_data_list is None:
        return False, 'No file ' + output_filename
    if len(expected_output_data_list) == 0:
        return False, 'No validation outputs in ' + output_filename

    # Load the actions from the test scene's corresponding actions file.
    action_filename, action_list = load_action_list(scene_filename)
    if action_list is None:
        return False, 'No file ' + action_filename
    if len(action_list) == 0:
        return False, 'No scripted actions in ' + action_filename

    # Initialize the test scene.
    step_metadata = controller.start_scene(scene_data)

    # Need to sleep here to avoid errors while running the tests sequentially.
    time.sleep(1)

    successful = True
    autofix_case_list = []

    # Run the specific actions for the test scene.
    for index, action_data in enumerate(action_list + [None]):
        # Validate the test scene's output metadata at each action step.
        failed_validation_list = validate_single_output(
            expected_output_data_list[index],
            step_metadata
        )
        # If the validation failed, return the failed test case info.
        if len(failed_validation_list) > 0:
            indent = "\n" + INDENT + INDENT
            error_message_list = [item[3] for item in failed_validation_list]
            status = (
                f'Step {index} failed:{indent}'
                f'{indent.join(error_message_list)}'
            )
            successful = False
            if dev or autofix:
                print(status)
                if autofix:
                    autofix_case_list = autofix_case_list + [
                        (index, item[0], item[1], item[2])
                        for item in failed_validation_list
                    ]
            else:
                return False, status
        if action_data:
            step_metadata = controller.step(
                action_data['action'],
                **action_data['params']
            )

    if autofix and len(autofix_case_list):
        for index, test_case, actual, _ in autofix_case_list:
            output_dict = expected_output_data_list[index]
            dict_property = test_case[0]
            if len(test_case) > 1:
                nested_list = output_dict[test_case[0]]
                for nested_dict in nested_list:
                    if nested_dict['id'] == test_case[1]:
                        output_dict = nested_dict
                dict_property = test_case[2]
            output_dict[dict_property] = (
                round(actual, 3) if isinstance(actual, float) else actual
            )
        with open(output_filename, 'w', encoding='utf-8-sig') as output_file:
            json.dump(
                expected_output_data_list,
                output_file,
                indent=4,
                sort_keys=True
            )
            print(f'SAVED {len(autofix_case_list)} FIXES: {output_filename}')

    # Stop the test scene.
    controller.end_scene("", 1)

    # Validation successful!
    return successful, ('' if successful else 'see above')


def start_handmade_tests(
    mcs_unity_build,
    only_metadata_tier,
    only_test_name,
    dev,
    autofix
):
    # Find all of the test scene JSON files.
    scene_filename_list = sorted(glob.glob(TEST_FOLDER + '*' + SCENE_SUFFIX))

    successful_test_list = []
    failed_test_list = []

    # Run each test scene at each metadata tier.
    for metadata_tier, config_filename in METADATA_TIER_LIST:
        if only_metadata_tier and metadata_tier != only_metadata_tier:
            continue
        print_divider()
        print(f'HANDMADE TEST METADATA TIER: {metadata_tier.upper()}')
        # Create one controller to run all of the tests at this metadata tier.
        controller = mcs.create_controller(mcs_unity_build, config_filename)
        # Run each test scene and record if it failed validation.
        for scene_filename in scene_filename_list:
            if (
                only_test_name and not
                os.path.basename(scene_filename).startswith(only_test_name)
            ):
                continue
            print(f'RUNNING SCENE: {os.path.basename(scene_filename)}')
            successful, status = run_single_scene(
                controller,
                scene_filename,
                metadata_tier,
                dev,
                autofix
            )
            test_name = (
                os.path.basename(scene_filename).replace(SCENE_SUFFIX, '')
            )
            if successful:
                successful_test_list.append((test_name, metadata_tier))
            else:
                failed_test_list.append((test_name, metadata_tier, status))
        # Run each additional test at this metadata tier.
        for runner_function in ([] if only_test_name else FUNCTION_LIST):
            print(f'RUNNING TESTS: {runner_function.__name__}')
            successful, status = runner_function(controller, metadata_tier)
            test_name = runner_function.__name__
            if successful:
                successful_test_list.append((test_name, metadata_tier))
            else:
                failed_test_list.append((test_name, metadata_tier, status))
        controller.stop_simulation()

    successful_test_list.sort(key=lambda x: x[0])
    failed_test_list.sort(key=lambda x: x[0])

    print_divider()
    print('SUCCESSFUL INTEGRATION TESTS:')
    if len(successful_test_list) == 0:
        print(f'{INDENT}NONE')
    for scene_prefix, metadata_tier in successful_test_list:
        print(f'{INDENT}{scene_prefix} ({metadata_tier})')
    print('FAILED INTEGRATION TESTS:')
    if len(failed_test_list) == 0:
        print(f'{INDENT}NONE')
    for scene_prefix, metadata_tier, status in failed_test_list:
        print(f'{INDENT}{scene_prefix} ({metadata_tier}): {status}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Handmade Integration Tests"
    )
    parser = add_test_args(parser, handmade_only=True)
    args = parser.parse_args()
    start_handmade_tests(
        args.mcs_unity_build_file_path,
        args.metadata,
        args.test,
        args.dev,
        args.autofix
    )
