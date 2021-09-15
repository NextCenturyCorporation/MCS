import argparse

import machine_common_sense as mcs

commandList = []


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
    return parser.parse_args()


def load_command_file(command_text_file):
    with open(command_text_file, 'r') as command_file:
        commands = [line.strip() for line in command_file]
    return commands


def run_commands(controller, config_data, command_data):
    _ = controller.start_scene(config_data)

    for command in command_data:
        _ = controller.step(command)

    controller.end_scene("", 1)


def main():
    args = parse_args()
    config_data, status = mcs.load_scene_json_file(args.mcs_config_json_file)
    command_data = load_command_file(args.mcs_command_list_file)

    if status is not None:
        print(status)
        exit()

    controller = mcs.create_controller(
        unity_app_file_path=args.mcs_unity_build_file,
        config_file_or_dict='./run_scripts_config_with_history.ini'
    )

    config_file_path = args.mcs_config_json_file
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    if controller is not None:
        run_commands(controller, config_data, command_data)


if __name__ == "__main__":
    main()
