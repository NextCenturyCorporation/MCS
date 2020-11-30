import argparse

import machine_common_sense as mcs


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'mcs_scene_json_file',
        help='MCS JSON scene configuration file to load')
    return parser.parse_args()


def main():
    args = parse_args()
    scene_file_path = args.mcs_scene_json_file
    scene_data, status = mcs.load_scene_json_file(scene_file_path)

    if status is not None:
        print(status)
        exit()

    controller = mcs.create_controller(
        args.mcs_unity_build_file,
        config_file_path='./run_scripts_config_no_metadata.ini'
    )
    scene_file_name = scene_file_path[scene_file_path.rfind('/') + 1:]

    if 'name' not in scene_data.keys():
        scene_data['name'] = scene_file_name[0:scene_file_name.find('.')]

    last_step = 30
    if 'goal' in scene_data.keys():
        if 'last_step' in scene_data['goal'].keys():
            last_step = scene_data['goal']['last_step']

    output = controller.start_scene(scene_data)

    for i in range(output.step_number + 1, last_step + 1):
        action = output.action_list[len(output.action_list) - 1]
        output = controller.step(action)

    controller.end_scene("", 1)


if __name__ == "__main__":
    main()
