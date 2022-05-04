import argparse
import math

import machine_common_sense as mcs
from machine_common_sense.controller import Controller
from machine_common_sense.logging_config import LoggingConfig

commands = []


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_scene_json_file',
        help='MCS JSON scene configuration file to load')
    parser.add_argument(
        '--mcs_unity_build_file',
        type=str,
        default=None,
        help='Path to MCS unity build file')
    parser.add_argument(
        '--mcs_unity_version',
        type=str,
        default=None,
        help='version of MCS Unity executable.  Default: current')
    parser.add_argument(
        '--config_file_path',
        type=str,
        default=None,
        required=True,
        help='Path to configuration file to read in and set various '
        'properties, such as metadata level and whether or not to '
        'save history files properties.')
    return parser.parse_args()


def run_scene(controller: Controller, scene_data, path):
    max_dist = 0.06
    max_delta_angle = 11

    print("Resetting the current scene...")
    previous_output = controller.start_scene(scene_data)

    for waypoint in path:
        sq_dist, delta_angle = get_deltas(previous_output, waypoint)
        while sq_dist > max_dist * max_dist:
            print(f"DELTA_ANGLE: {delta_angle} dist: {sq_dist}")
            if abs(delta_angle) > max_delta_angle:
                action = 'RotateLeft' if delta_angle > 0 else 'RotateRight'
            else:
                action = 'MoveAhead'
            output = controller.step(action, **{})
            previous_output = output
            sq_dist, delta_angle = get_deltas(previous_output, waypoint)


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
    mcs.init_logging(LoggingConfig.get_dev_logging_config())
    args = parse_args()
    scene_data = mcs.load_scene_json_file(args.mcs_scene_json_file)

    path = scene_data.get('debug').get('path')
    if not path:
        print("Scene did not have 'debug.path' section")
        return

    controller = mcs.create_controller(
        unity_app_file_path=args.mcs_unity_build_file,
        config_file_or_dict=args.config_file_path,
        unity_cache_version=args.mcs_unity_version)

    # controller.get_metadata_level()

    scene_file_path = args.mcs_scene_json_file
    scene_file_name = scene_file_path[scene_file_path.rfind('/') + 1:]

    if 'name' not in scene_data.keys():
        scene_data['name'] = scene_file_name[0:scene_file_name.find('.')]

    if controller is not None:
        run_scene(controller, scene_data, path)


if __name__ == "__main__":
    main()
