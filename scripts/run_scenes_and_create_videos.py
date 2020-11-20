import argparse
import glob
import subprocess

import machine_common_sense as mcs


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'filename_prefix',
        help='Prefix of scene files, with path')
    return parser.parse_args()


def run_scene(file_name):
    scene_data, status = mcs.load_scene_json_file(file_name)

    if status is not None:
        print(status)
        return

    if 'sceneInfo' in scene_data['goal']:
        scene_data['name'] = (
            scene_data['name'] + '_' +
            scene_data['goal']['sceneInfo']['name'].replace(' ', '_')
        )
    else:
        scene_data['name'] = scene_data['name'][
            (scene_data['name'].rfind('/') + 1):
        ]
    last_step = scene_data['goal']['last_step']

    output = controller.start_scene(scene_data)

    for i in range(output.step_number + 1, last_step + 1):
        action = output.action_list[len(output.action_list) - 1]
        output = controller.step(action)

    controller.end_scene("", 1)

    subprocess.call([
        'ffmpeg',
        '-y',
        '-r',
        '20',
        '-i',
        scene_data['name'] + '/frame_image_%d.png',
        scene_data['name'] + '.mp4'
    ])


if __name__ == "__main__":
    args = parse_args()
    controller = mcs.create_controller(
        args.mcs_unity_build_file, debug=True,
        config_file_path='./run_scripts_config.ini'
    )

    filename_list = glob.glob(args.filename_prefix + '*_debug.json')
    if len(filename_list) == 0:
        filename_list = glob.glob(args.filename_prefix + '*.json')

    filename_list.sort()

    for filename in filename_list:
        print('Running ' + filename)
        run_scene(filename)
