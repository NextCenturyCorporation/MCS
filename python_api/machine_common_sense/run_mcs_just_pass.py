import sys
from machine_common_sense.mcs import MCS

if len(sys.argv) < 3:
    print('Usage: python run_mcs_just_pass.py <mcs_unity_build_file> '
          '<mcs_config_json_file>')
    sys.exit()

if __name__ == "__main__":
    config_data, status = MCS.load_config_json_file(sys.argv[2])

    if status is not None:
        print(status)
        exit()

    controller = MCS.create_controller(sys.argv[1], debug=True)

    config_file_path = sys.argv[2]
    config_file_name = config_file_path[config_file_path.rfind('/') + 1:]

    if 'name' not in config_data.keys():
        config_data['name'] = config_file_name[0:config_file_name.find('.')]

    last_step = 60
    if 'goal' in config_data.keys():
        if 'last_step' in config_data['goal'].keys():
            last_step = config_data['goal']['last_step']

    output = controller.start_scene(config_data)

    for i in range(1, last_step + 1):
        output = controller.step('Pass')
