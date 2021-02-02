import argparse
import cmd
import os
import machine_common_sense as mcs

commandList = []

os.environ['MCS_CONFIG_FILE_PATH'] = "../mcs_config.yaml"
print(os.environ['MCS_CONFIG_FILE_PATH'])

def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'mcs_config_json_file',
        help='MCS JSON scene configuration file to load')
    parser.add_argument(
        'mcs_command_list_file',
        help='MCS text file with commands to run')
    parser.add_argument(
        '--debug',
        default=False,
        action='store_true',
        help='Generate MCS debug files [default=False]')
    parser.add_argument(
        '--depth_maps',
        default=False,
        action='store_true',
        help='Render and return depth masks of each scene ' +
        '(will slightly decrease performance) [default=False]')
    parser.add_argument(
        '--object_masks',
        default=False,
        action='store_true',
        help='Render and return object (instance segmentation) masks of ' +
        'each scene (will significantly decrease performance) [default=False]')
    parser.add_argument(
        '--history_enabled',
        default=True,
        help='Whether to save all the history files and generated image ' +
        'history to local disk or not. [default=True]')
    return parser.parse_args()


def load_command_file(command_text_file):
    commands = []
    command_file = open(command_text_file, 'r')
    for line in command_file:
        commands.append(line.strip())
    command_file.close()

    return commands


def run_commands(controller, config_data, command_data):
    _ = controller.start_scene(config_data)

    for command in command_data:
        _ = controller.step(command)
    
    controller.end_scene("", 1)


def main():
    args = parse_args()
    config_data, status = mcs.load_config_json_file(args.mcs_config_json_file)
    command_data = load_command_file(args.mcs_command_list_file)

    if status is not None:
        print(status)
        exit()

    controller = mcs.create_controller(args.mcs_unity_build_file,
                                       debug=args.debug,
                                       depth_maps=args.depth_maps,
                                       object_masks=args.object_masks,
                                       history_enabled=args.history_enabled)

    config_file_path = args.mcs_config_json_file
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    if controller is not None:
        run_commands(controller, config_data, command_data)


if __name__ == "__main__":
    main()

