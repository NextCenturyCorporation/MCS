from runner_script import MultipleFileRunnerScript

import machine_common_sense as mcs

experience_with_room_action_list = [
    # Spin around, and then rotate to face the first container/corner.
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    # Move ahead to the first container/corner.
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    # Look down into the container, and then back up.
    'LookDown', 'LookDown', 'LookDown', 'LookDown', 'LookDown',
    'LookUp', 'LookUp', 'LookUp', 'LookUp', 'LookUp',
    # Rotate to face the second container/corner.
    'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight',
    'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight',
    'RotateRight', 'RotateRight',
    # Move ahead to the second container/corner (along a short wall).
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    # Rotate to face the second container/corner.
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft',
    # Look down into the container, and then back up.
    'LookDown', 'LookDown', 'LookDown', 'LookDown', 'LookDown',
    'LookUp', 'LookUp', 'LookUp', 'LookUp', 'LookUp',
    # Rotate to face the third container/corner.
    'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight',
    'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight',
    'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight',
    # Move ahead to the third container/corner (along a long wall).
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead',
    # Rotate to face the third container/corner.
    'RotateLeft', 'RotateLeft', 'RotateLeft',
    # Look down into the container, and then back up.
    'LookDown', 'LookDown', 'LookDown', 'LookDown', 'LookDown',
    'LookUp', 'LookUp', 'LookUp', 'LookUp', 'LookUp',
    # Rotate to face the fourth container/corner.
    'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight',
    'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight', 'RotateRight',
    'RotateRight', 'RotateRight',
    # Move ahead to the fourth container/corner (along a long wall).
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    # Rotate to face the fourth container/corner.
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft',
    # Look down into the container, and then back up.
    'LookDown', 'LookDown', 'LookDown', 'LookDown', 'LookDown',
    'LookUp', 'LookUp', 'LookUp', 'LookUp', 'LookUp',
    # Pass until the first kidnap event, and then pass during the drop event.
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass',
    'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass', 'Pass'
    'Pass',
    # Spin around after the final kidnap event.
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft', 'RotateLeft',
    'RotateLeft'
]

move_to_target_action_list = [
    # Move ahead to the target container/corner.
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead', 'MoveAhead',
    # Look down to the container.
    'LookDown', 'LookDown', 'LookDown'
]

scene_state = {}


def action_callback(scene_data, step_metadata, runner_script):
    global scene_state

    if step_metadata.step_number == 0:
        scene_state = {
            'action_list': [],
            'move_back_count': 0,
            'open': False,
            'pickup': False,
            'target_id': None
        }
        kidnap_rotation = int(
            scene_data['goal']['sceneInfo']['kidnapRotation']
        )
        rotate_right_count = int((360 - kidnap_rotation) / 10)
        target_corner = scene_data['debug']['chosenCorner']
        if target_corner == 'back_left':
            rotate_right_count -= 15
        elif target_corner == 'back_right':
            rotate_right_count += 15
        elif target_corner == 'front_left':
            rotate_right_count -= 3
        elif target_corner == 'front_right':
            rotate_right_count += 3
        else:
            raise ValueError(f'The chosenCorner is not valid: {target_corner}')
        rotate_right_count %= 36
        if rotate_right_count > 18:
            rotate_right_count -= 36
        scene_state['target_id'] = (
            scene_data['goal']['metadata']['target']['id']
        )
        scene_state['action_list'].extend(
            experience_with_room_action_list.copy() + ([
                f"Rotate{'Left' if rotate_right_count < 0 else 'Right'}"
            ] * rotate_right_count) + move_to_target_action_list.copy()
        )

    if len(step_metadata.action_list) == 1:
        return step_metadata.action_list[0]

    if len(scene_state['action_list']) > step_metadata.step_number:
        return mcs.Action.input_to_action_and_params(
            scene_state['action_list'][step_metadata.step_number]
        )

    if not scene_state['open']:
        scene_state['open'] = True
        return 'OpenObject', {
            'objectImageCoordsX': 300,
            'objectImageCoordsY': 200
        }

    if scene_state['open'] and step_metadata.return_status == 'OBSTRUCTED':
        scene_state['open'] = False
        scene_state['move_back_count'] += 1
        return 'MoveBack', {}

    if not scene_state['pickup']:
        scene_state['pickup'] = True
        return 'PickupObject', {'objectId': scene_state['target_id']}

    if scene_state['pickup'] and step_metadata.return_status != 'SUCCESSFUL':
        scene_state['pickup'] = False
        if scene_state['move_back_count'] > 0:
            scene_state['move_back_count'] -= 1
            return 'MoveAhead', {}

    return None, None


def main():
    MultipleFileRunnerScript('Reorientation Scenes', action_callback)


if __name__ == "__main__":
    main()
