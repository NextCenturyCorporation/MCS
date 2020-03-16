import sys
from machine_common_sense.mcs import MCS

if len(sys.argv) < 2:
    print('Usage: python run_mcs_intphys_samples.py <mcs_unity_build_file>')
    sys.exit()

def run_scene(file_name):
    config_data, status = MCS.load_config_json_file(file_name)

    if status is not None:
        print(status)
        return

    config_file_path = file_name
    config_file_name = config_file_path[config_file_path.rfind('/')+1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    last_step = 30
    if 'goal' in config_data.keys():
        if 'last_step' in config_data['goal'].keys():
            last_step = config_data['goal']['last_step']

    output = controller.start_scene(config_data)

    for i in range(1, last_step + 1):
        output = controller.step('Pass')

if __name__ == "__main__":
    controller = MCS.create_controller(sys.argv[1], debug=True)

    run_scene('./scenes/intphys_gravity_plausible_sample_1.json')
    run_scene('./scenes/intphys_gravity_implausible_sample_1.json')
    run_scene('./scenes/intphys_object_permanence_plausible_sample_1.json')
    run_scene('./scenes/intphys_object_permanence_implausible_sample_1.json')
    run_scene('./scenes/intphys_shape_constancy_plausible_sample_1.json')
    run_scene('./scenes/intphys_shape_constancy_implausible_sample_1.json')
    run_scene('./scenes/intphys_spatial_temporal_continuity_plausible_sample_1.json')
    run_scene('./scenes/intphys_spatial_temporal_continuity_implausible_sample_1.json')

