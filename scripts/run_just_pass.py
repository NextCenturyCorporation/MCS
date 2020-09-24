import argparse

from machine_common_sense.mcs import MCS


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'mcs_config_json_file',
        help='MCS JSON scene configuration file to load')
    return parser.parse_args()


def main():
    args = parse_args()
    config_file_path = args.mcs_config_json_file
    config_data, status = MCS.load_config_json_file(config_file_path)

    if status is not None:
        print(status)
        exit()

    controller = MCS.create_controller(args.mcs_unity_build_file, debug=True)
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    last_step = 60
    if 'goal' in config_data.keys():
        if 'last_step' in config_data['goal'].keys():
            last_step = config_data['goal']['last_step']

    _ = controller.start_scene(config_data)

    for i in range(1, last_step + 1):
        _ = controller.step('Pass')


if __name__ == "__main__":
    main()