import sys

from machine_common_sense.mcs import MCS

if len(sys.argv) < 3:
    print('Usage: python run_mcs_just_rotate.py <mcs_unity_build_file> '
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

    output = controller.start_scene(config_data)

    for i in range(1, 12):
        output = controller.step('RotateLook', rotation=30)
