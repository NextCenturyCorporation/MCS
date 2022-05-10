import argparse

import machine_common_sense as mcs
from machine_common_sense.controller import Controller
from machine_common_sense.logging_config import LoggingConfig
from machine_common_sense.scripts.run_interactive_scenes_follow_path import \
    PathFollower

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


path_follower = PathFollower()


def run_scene(controller: Controller, scene_data, path):

    print("Resetting the current scene...")
    output = controller.start_scene(scene_data)

    action = 'start'
    while action is not None:
        action, params = path_follower.action_callback(
            scene_data, output, None)
        controller.step(action, **params)

    controller.end_scene()


def main():
    mcs.init_logging(LoggingConfig.get_dev_logging_config())
    args = parse_args()
    scene_data = mcs.load_scene_json_file(args.mcs_scene_json_file)

    path = scene_data.get('debug', {}).get('path')
    if not path:
        print("Scene did not have 'debug.path' section")
        return

    controller = mcs.create_controller(
        unity_app_file_path=args.mcs_unity_build_file,
        config_file_or_dict=args.config_file_path,
        unity_cache_version=args.mcs_unity_version)

    path_follower.init_callback(controller)

    scene_file_path = args.mcs_scene_json_file
    scene_file_name = scene_file_path[scene_file_path.rfind('/') + 1:]

    if 'name' not in scene_data.keys():
        scene_data['name'] = scene_file_name[0:scene_file_name.find('.')]

    if controller is not None:
        run_scene(controller, scene_data, path)


if __name__ == "__main__":
    main()
