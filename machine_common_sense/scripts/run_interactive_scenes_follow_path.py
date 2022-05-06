import math

from runner_script import MultipleFileRunnerScript

waypoint_index = 0
scene_name = ""
MAX_DISTANCE = 0.06
MAX_DELTA_ANGLE = 11


def action_callback(scene_data, step_metadata, runner_script):

    global waypoint_index
    global scene_name
    if scene_data['name'] != scene_name:
        scene_name = scene_data['name']
        waypoint_index = 0

    path = scene_data.get('debug', {}).get('path')
    if not path:
        print("Scene did not have 'debug.path' section")
        return None, None

    if not step_metadata.position:
        print("No position provided.  Oracle metadata is required for this"
              " script.")
        return None, None
    if len(step_metadata.action_list) == 1:
        return step_metadata.action_list[0]
    waypoint = path[waypoint_index]
    sq_dist, delta_angle = get_deltas(step_metadata, waypoint)
    while sq_dist < MAX_DISTANCE**2:
        waypoint_index += 1
        if waypoint_index >= len(path):
            return None, None
        waypoint = path[waypoint_index]
        sq_dist, delta_angle = get_deltas(step_metadata, waypoint)

    action = get_waypoint_action(delta_angle)
    return action, {}


def get_waypoint_action(delta_angle):
    if abs(delta_angle) > MAX_DELTA_ANGLE:
        return 'RotateLeft' if delta_angle > 0 else 'RotateRight'
    else:
        return 'MoveAhead'


def get_deltas(previous_output, waypoint):
    pos = previous_output.position
    rot = previous_output.rotation
    delta_x = waypoint['x'] - pos['x']
    delta_z = waypoint['z'] - pos['z']
    square_distance = delta_x * delta_x + delta_z * delta_z
    target_angle = math.degrees(math.atan2(delta_x, delta_z))
    delta_angle = (rot - target_angle + 720) % 360
    delta_angle = delta_angle if delta_angle <= 180 else delta_angle - 360
    return square_distance, delta_angle


def main():
    MultipleFileRunnerScript(
        'Interactive Scenes - Follow Path',
        action_callback)


if __name__ == "__main__":
    main()
