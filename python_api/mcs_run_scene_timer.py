import os
import statistics
import sys
import time

from machine_common_sense.mcs import MCS

def run_scene(file_name):
    config_data, status = MCS.load_config_json_file(file_name)

    if status is not None:
        print(status)
        return

    config_file_path = file_name
    config_file_name = config_file_path[config_file_path.rfind('/')+1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    last_step = 20
    if 'goal' in config_data.keys():
        if 'last_step' in config_data['goal'].keys():
            last_step = config_data['goal']['last_step']

    step_time_list = []

    output = controller.start_scene(config_data)

    for i in range(output.step_number + 1, last_step + 1):
        start = time.perf_counter()
        output = controller.step('Pass')
        end = time.perf_counter()
        step_time_list.append(end - start)

    return step_time_list

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python mcs_run_scene_timer.py <mcs_unity_build_file> <scene_configuration_directory>')
        sys.exit()

    file_list = [os.path.join(sys.argv[2], file_name) for file_name in os.listdir(sys.argv[2]) if \
            os.path.isfile(os.path.join(sys.argv[2], file_name)) and os.path.splitext(file_name)[1] == '.json']

    print(f'FOUND {len(file_list)} SCENE CONFIGURATION FILES... STARTING MCS PYTHON CONTROLLER AND UNITY APP...')
    controller = MCS.create_controller(sys.argv[1], debug='terminal')

    scene_time_list = []
    step_time_list_list = []
    step_time_avg_list = []
    step_time_len_list = []
    step_time_max_list = []
    step_time_min_list = []
    step_time_sum_list = []

    for i in range(0, len(file_list)):
        print('========================================')
        print('RUNNING ' + file_list[i])
        start = time.perf_counter()
        step_time_list = run_scene(file_list[i])
        end = time.perf_counter()
        scene_time_list.append(end - start)
        step_time_list_list.append(step_time_list)
        step_time_avg_list.append(statistics.mean(step_time_list))
        step_time_len_list.append(len(step_time_list))
        step_time_max_list.append(max(step_time_list))
        step_time_min_list.append(min(step_time_list))
        step_time_sum_list.append(sum(step_time_list))

    print('========================================')
    print(f'RAN {len(file_list)} SCENES WITH {sum(step_time_len_list)} TOTAL STEPS IN {sum(scene_time_list):0.4f} SECONDS')
    print(f'Average single step took {statistics.mean(step_time_avg_list):0.4f} seconds')
    print(f'Longest single step took {max(step_time_max_list):0.4f} seconds')
    print(f'Shortest single step took {min(step_time_min_list):0.4f} seconds')
    print(f'Average single scene took {statistics.mean(scene_time_list):0.4f} seconds')
    print(f'Longest single scene took {max(scene_time_list):0.4f} seconds')
    print(f'Shortest single scene took {min(scene_time_list):0.4f} seconds')

