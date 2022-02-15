import glob
import os.path

import numpy as np

import machine_common_sense as mcs

INTEGRATION_TESTS_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEPTH_AND_SEGMENTATION_SCENE = (
    INTEGRATION_TESTS_FOLDER + '/depth_and_segmentation.scene.json'
)
HABITUATION_TRIAL_COUNTS_SCENE = (
    INTEGRATION_TESTS_FOLDER + '/habituation_trial_counts.scene.json'
)
NUMPY_ARRAY_DATA_SCENE = (
    INTEGRATION_TESTS_FOLDER + '/numpy_array_data.scene.json'
)
RESTRICTED_ACTION_LIST_SCENE = (
    INTEGRATION_TESTS_FOLDER + '/restricted_action_list.scene.json'
)
SAMPLE_SCENES_FOLDER = (
    INTEGRATION_TESTS_FOLDER + '../machine_common_sense/scenes/'
)


def run_depth_and_segmentation_test(controller, metadata_tier):
    # Load the test scene's JSON data.
    scene_data = mcs.load_scene_json_file(DEPTH_AND_SEGMENTATION_SCENE)

    # Initialize the test scene.
    step_metadata_0 = controller.start_scene(scene_data)

    # Verify the depth map and object mask lists from step 0.
    if len(step_metadata_0.depth_map_list) != 1:
        return (
            False,
            f'Step 0 {metadata_tier} failed: depth_map_list with length '
            f'{len(step_metadata_0.depth_map_list)} should be length 1'
        )
    if metadata_tier == 'level2' or metadata_tier == 'oracle':
        if len(step_metadata_0.object_mask_list) != 1:
            return (
                False,
                f'Step 0 {metadata_tier} failed: object_mask_list with length '
                f'{len(step_metadata_0.object_mask_list)} should be length 1'
            )

    # Run an action step.
    step_metadata_1 = controller.step('Pass')

    # Verify the depth map list and object mask list from step 1.
    if len(step_metadata_1.depth_map_list) != 1:
        return (
            False,
            f'Step 1 {metadata_tier} failed: depth_map_list with length '
            f'{len(step_metadata_1.depth_map_list)} should be length 1'
        )
    if metadata_tier == 'level2' or metadata_tier == 'oracle':
        if len(step_metadata_1.object_mask_list) != 1:
            return (
                False,
                f'Step 1 {metadata_tier} failed: object_mask_list with length '
                f'{len(step_metadata_1.object_mask_list)} should be length 1'
            )
    # Verify the consistent segment_color of each object across both steps.
    if metadata_tier == 'oracle':
        if (
            step_metadata_0.object_list[0].uuid !=
            step_metadata_1.object_list[0].uuid
        ):
            return (
                False,
                f'Step 1 {metadata_tier} failed: object_list[0].uuid '
                f'{step_metadata_0.object_list[0].uuid} != '
                f'{step_metadata_1.object_list[0].uuid}'
            )
        if (
            step_metadata_0.object_list[1].uuid !=
            step_metadata_1.object_list[1].uuid
        ):
            return (
                False,
                f'Step 1 {metadata_tier} failed: object_list[1].uuid '
                f'{step_metadata_0.object_list[1].uuid} != '
                f'{step_metadata_1.object_list[1].uuid}'
            )
        if (
            step_metadata_0.object_list[0].segment_color !=
            step_metadata_1.object_list[0].segment_color
        ):
            return (
                False,
                f'Step 1 {metadata_tier} failed: object_list[0].segment_color '
                f'{step_metadata_0.object_list[0].segment_color} != '
                f'{step_metadata_1.object_list[0].segment_color}'
            )
        if (
            step_metadata_0.object_list[1].segment_color !=
            step_metadata_1.object_list[1].segment_color
        ):
            return (
                False,
                f'Step 1 {metadata_tier} failed: object_list[1].segment_color '
                f'{step_metadata_0.object_list[1].segment_color} != '
                f'{step_metadata_1.object_list[1].segment_color}'
            )

    # Stop the test scene.
    controller.end_scene()

    # Validation successful!
    return True, ''


def run_habituation_trial_counts_test(controller, metadata_tier):
    # Load the test scene's JSON data.
    scene_data = mcs.load_scene_json_file(
        HABITUATION_TRIAL_COUNTS_SCENE
    )

    # Initialize the test scene.
    step_metadata = controller.start_scene(scene_data)
    if step_metadata.habituation_trial != 1:
        return (
            False,
            f'Step {step_metadata.step_number} failed: habituation_trial '
            f'{step_metadata.habituation_trial} != 1'
        )

    # Try a couple of pass actions.
    for i in range(0, 2):
        step_metadata = controller.step('Pass')
        if step_metadata.habituation_trial != 1:
            return (
                False,
                f'Step {step_metadata.step_number} failed: habituation_trial '
                f'{step_metadata.habituation_trial} != 1'
            )

    # End habituation trial 1.
    step_metadata = controller.step('EndHabituation')
    if step_metadata.habituation_trial != 2:
        return (
            False,
            f'Step {step_metadata.step_number} failed: habituation_trial '
            f'{step_metadata.habituation_trial} != 2'
        )

    # Try a lot of pass actions.
    for i in range(0, 10):
        step_metadata = controller.step('Pass')
        if step_metadata.habituation_trial != 2:
            return (
                False,
                f'Step {step_metadata.step_number} failed: habituation_trial '
                f'{step_metadata.habituation_trial} != 2'
            )

    # End habituation trial 2.
    step_metadata = controller.step('EndHabituation')
    if step_metadata.habituation_trial != 3:
        return (
            False,
            f'Step {step_metadata.step_number} failed: habituation_trial '
            f'{step_metadata.habituation_trial} != 3'
        )

    # End habituation trial 3.
    step_metadata = controller.step('EndHabituation')
    if step_metadata.habituation_trial is not None:
        return (
            False,
            f'Step {step_metadata.step_number} failed: habituation_trial '
            f'{step_metadata.habituation_trial} is not None'
        )

    # Try a couple of pass actions.
    for i in range(0, 2):
        step_metadata = controller.step('Pass')
        if step_metadata.habituation_trial is not None:
            return (
                False,
                f'Step {step_metadata.step_number} failed: habituation_trial '
                f'{step_metadata.habituation_trial} is not None'
            )

    # Stop the test scene.
    controller.end_scene()

    # Validation successful!
    return True, ''


def run_numpy_array_data_test(controller, metadata_tier):
    # Load the test scene's JSON data.
    scene_data = mcs.load_scene_json_file(NUMPY_ARRAY_DATA_SCENE)

    # Convert the objects array to a numpy array
    scene_data['objects'] = np.array(scene_data.get("objects", []))

    # Initialize the test scene.
    step_metadata = controller.start_scene(scene_data)

    if step_metadata:
        # Try a pass action.
        step_metadata = controller.step('Pass')

    # Stop the test scene.
    controller.end_scene()

    if not step_metadata:
        return False, 'Failed to load scene with numpy array data'

    # Validation successful!
    return True, ''


def run_position_by_step_test(controller, metadata_tier):
    # TODO MCS-570
    return True, ''


def run_public_sample_scenes_test(controller, metadata_tier):
    scene_filename_list = sorted(glob.glob(SAMPLE_SCENES_FOLDER + '*.json'))
    failed_test_list = []

    for scene_filename in scene_filename_list:
        # Load the sample scene's JSON data.
        scene_data = mcs.load_scene_json_file(scene_filename)

        # Initialize the test scene.
        step_metadata = controller.start_scene(scene_data)

        if step_metadata:
            # Try a pass action.
            step_metadata = controller.step('Pass')

        if not step_metadata:
            failed_test_list.append(os.path.basename(scene_filename))

        # Stop the test scene.
        controller.end_scene()

    return (
        len(failed_test_list) == 0,
        f'Failed to load scenes {",".join(failed_test_list)}'
    )


def run_restricted_action_list_test(controller, metadata_tier):
    # Load the test scene's JSON data.
    scene_data = mcs.load_scene_json_file(RESTRICTED_ACTION_LIST_SCENE)

    # Initialize the test scene.
    step_metadata = controller.start_scene(scene_data)
    if step_metadata.goal.last_step != 4:
        return (
            False,
            f'Step 0 failed: last_step {step_metadata.goal.last_step} != 4'
        )
    if step_metadata.action_list != [('Pass', {})]:
        return (
            False,
            f'Step 0 failed: action_list {step_metadata.action_list} != '
            f'[("Pass", {{}})]'
        )

    # Try an illegal action.
    step_metadata = controller.step('MoveAhead')
    if step_metadata:
        return (
            False,
            f'Step 1 failed: step_metadata from illegal action with '
            f'return_status {step_metadata.return_status} != None'
        )

    # Step 1.
    step_metadata = controller.step('Pass')
    if step_metadata.step_number != 1:
        return (
            False,
            f'Step 1 failed: step_number {step_metadata.step_number} != 1'
        )
    if step_metadata.return_status != 'SUCCESSFUL':
        return (
            False,
            f'Step 1 failed: return_status {step_metadata.return_status} != '
            f'SUCCESSFUL'
        )
    if step_metadata.action_list != [('MoveAhead', {}), ('MoveBack', {})]:
        return (
            False,
            f'Step 1 failed: action_list {step_metadata.action_list} != '
            f'[("MoveAhead", {{}}), ("MoveBack", {{}})]'
        )

    # Step 2.
    step_metadata = controller.step('MoveAhead')
    if step_metadata.step_number != 2:
        return (
            False,
            f'Step 2 failed: step_number {step_metadata.step_number} != 2'
        )
    if step_metadata.return_status != 'SUCCESSFUL':
        return (
            False,
            f'Step 2 failed: return_status {step_metadata.return_status} != '
            f'SUCCESSFUL'
        )
    if step_metadata.action_list != [('MoveAhead', {}), ('MoveBack', {})]:
        return (
            False,
            f'Step 2 failed: action_list {step_metadata.action_list} != '
            f'[("MoveAhead", {{}}), ("MoveBack", {{}})]'
        )

    # Step 3.
    step_metadata = controller.step('MoveBack')
    if step_metadata.step_number != 3:
        return (
            False,
            f'Step 3 failed: step_number {step_metadata.step_number} != 3'
        )
    if step_metadata.return_status != 'SUCCESSFUL':
        return (
            False,
            f'Step 3 failed: return_status {step_metadata.return_status} != '
            f'SUCCESSFUL'
        )
    if (
        step_metadata.action_list !=
        [('PickupObject', {'objectId': 'testBall2'})]
    ):
        return (
            False,
            f'Step 3 failed: action_list {step_metadata.action_list} != '
            f'[("PickupObject", {{"objectId": "testBall2"}})]'
        )

    # Try a legal action with an illegal parameter.
    step_metadata = controller.step('PickupObject', objectId='testBall1')
    if step_metadata:
        return (
            False,
            f'Step 4 failed: step_metadata from illegal action with '
            f'return_status {step_metadata.return_status} != None'
        )

    # Step 4.
    step_metadata = controller.step('PickupObject', objectId='testBall2')
    if step_metadata.step_number != 4:
        return (
            False,
            f'Step 4 failed: step_number {step_metadata.step_number} != 4'
        )
    if step_metadata.return_status != 'SUCCESSFUL':
        return (
            False,
            f'Step 4 failed: return_status {step_metadata.return_status} != '
            f'SUCCESSFUL'
        )
    if step_metadata.action_list != []:
        return (
            False,
            f'Step 4 failed: action_list {step_metadata.action_list} != []'
        )

    # Try an action after the last step of the scene.
    step_metadata = controller.step('Pass')
    if step_metadata:
        return (
            False,
            f'Step 5 failed: step_metadata from illegal action with '
            f'return_status {step_metadata.return_status} != None'
        )

    # Stop the test scene.
    controller.end_scene()

    # Validation successful!
    return True, ''


FUNCTION_LIST = [
    run_depth_and_segmentation_test,
    run_habituation_trial_counts_test,
    run_numpy_array_data_test,
    run_position_by_step_test,
    run_public_sample_scenes_test,
    run_restricted_action_list_test
]
