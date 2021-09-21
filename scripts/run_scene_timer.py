import argparse
import os
import statistics
import time

import machine_common_sense as mcs

DEFAULT_STEP_COUNT = 20


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'mcs_scene_dir',
        help='MCS JSON scene configuration directory')
    return parser.parse_args()


def run_scene(controller, file_name):
    scene_data, status = mcs.load_scene_json_file(file_name)

    if status is not None:
        print(status)
        return

    scene_file_path = file_name
    scene_file_name = scene_file_path[scene_file_path.rfind('/') + 1:]

    if 'name' not in scene_data.keys():
        scene_data['name'] = scene_file_name[0:scene_file_name.find('.')]

    last_step = DEFAULT_STEP_COUNT
    if (
        'goal' in scene_data.keys(
        ) and 'last_step' in scene_data['goal'].keys()
    ):
        last_step = scene_data['goal']['last_step']

    step_time_list = []

    output = controller.start_scene(scene_data)

    for _ in range(output.step_number + 1, last_step + 1):
        start = time.perf_counter()
        output = controller.step('Pass')
        end = time.perf_counter()
        step_time_list.append(end - start)

    output = controller.end_scene("", "")

    return step_time_list


def main():
    args = parse_args()
    file_list = sorted(
        [
            os.path.join(args.mcs_scene_dir, file_name)
            for file_name in os.listdir(args.mcs_scene_dir)
            if os.path.isfile(os.path.join(args.mcs_scene_dir, file_name)) and
            os.path.splitext(file_name)[1] == '.json'
        ]
    )

    print(
        f'FOUND {len(file_list)} SCENE CONFIGURATION FILES... '
        f'STARTING THE MCS UNITY APP...')
    controller = mcs.create_controller(
        config_file_or_dict={},
        unity_app_file_path=args.mcs_unity_build_file)

    scene_time_list = []
    step_time_list_list = []
    step_time_avg_list = []
    step_time_len_list = []
    step_time_max_list = []
    step_time_min_list = []
    step_time_sum_list = []

    for i in range(len(file_list)):
        print('========================================================='
              '=======================')
        print(f'RUNNING FILE {(i + 1)}: {file_list[i]}')
        start = time.perf_counter()
        step_time_list = run_scene(controller, file_list[i])
        end = time.perf_counter()
        scene_time_list.append(end - start)
        step_time_list_list.append(step_time_list)
        step_time_avg_list.append(statistics.mean(step_time_list))
        step_time_len_list.append(len(step_time_list))
        step_time_max_list.append(max(step_time_list))
        step_time_min_list.append(min(step_time_list))
        step_time_sum_list.append(sum(step_time_list))

    print('===================================================='
          '============================')
    print(f'RAN {len(file_list)} SCENES WITH {sum(step_time_len_list)} '
          f'TOTAL STEPS IN {sum(scene_time_list):0.4f} SECONDS')
    print(
        f'Average single step took {statistics.mean(step_time_avg_list):0.4f} '
        f'seconds')
    print(f'Longest single step took {max(step_time_max_list):0.4f} seconds')
    print(f'Shortest single step took {min(step_time_min_list):0.4f} seconds')
    print(
        f'Average single scene took {statistics.mean(scene_time_list):0.4f} '
        f'seconds')
    print(f'Longest single scene took {max(scene_time_list):0.4f} seconds')
    print(f'Shortest single scene took {min(scene_time_list):0.4f} seconds')


if __name__ == "__main__":
    main()
