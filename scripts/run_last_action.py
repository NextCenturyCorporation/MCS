import argparse

import machine_common_sense as mcs


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
    config_data, status = mcs.load_config_json_file(config_file_path)

    if status is not None:
        print(status)
        exit()

    controller = mcs.create_controller(args.mcs_unity_build_file, debug=True,
                                       depth_maps=False, object_masks=False,
                                       history_enabled=False)
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    last_step = 30
    if 'goal' in config_data.keys():
        if 'last_step' in config_data['goal'].keys():
            last_step = config_data['goal']['last_step']

    output = controller.start_scene(config_data)

    for i in range(output.step_number + 1, last_step + 1):
        action = output.action_list[len(output.action_list) - 1]
        output = controller.step(action)

    controller.end_scene("", 1)


if __name__ == "__main__":
    main()
