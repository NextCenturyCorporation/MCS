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
                                       depth_maps=True, object_masks=True)
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    _ = controller.start_scene(config_data)

    for _ in range(36):
        _ = controller.step('RotateRight')

    controller.end_scene("", 1)


if __name__ == "__main__":
    main()
