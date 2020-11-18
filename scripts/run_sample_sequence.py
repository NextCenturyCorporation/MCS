import argparse
import glob

import machine_common_sense as mcs


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'filename_prefix',
        help='Prefix of scene files')
    return parser.parse_args()


def run_scene(file_name):
    config_data, status = mcs.load_config_json_file(file_name)

    if status is not None:
        print(status)
        return

    if 'sceneInfo' in config_data['goal']:
        config_data['name'] = (
            config_data['goal']['sceneInfo']['name'].replace(' ', '_')
        )
    else:
        config_data['name'] = config_data['name'][
            (config_data['name'].rfind('/') + 1):
        ]
    last_step = config_data['goal']['last_step']

    output = controller.start_scene(config_data)

    for i in range(output.step_number + 1, last_step + 1):
        action = output.action_list[len(output.action_list) - 1]
        output = controller.step(action)

    controller.end_scene("", 1)


if __name__ == "__main__":
    args = parse_args()
    controller = mcs.create_controller(
        args.mcs_unity_build_file,
        debug=True,
        config_file_path='./run_scripts_config.ini'
    )

    filename_list = glob.glob(args.filename_prefix + '*_debug.json')
    if len(filename_list) == 0:
        filename_list = glob.glob(args.filename_prefix + '*.json')

    filename_list.sort()

    for filename in filename_list:
        print('Running ' + filename)
        run_scene(filename)
