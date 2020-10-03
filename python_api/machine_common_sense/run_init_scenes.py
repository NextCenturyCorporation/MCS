import glob
import sys
from machine_common_sense.mcs import MCS

if len(sys.argv) < 4:
    print('Usage: python run_init_scenes.py <mcs_unity_build_file> '
          '<json_input_folder> <image_output_folder>')
    sys.exit()

if __name__ == "__main__":
    output_folder = sys.argv[3] + '/'

    json_file_list = glob.glob(sys.argv[2] + '/*.json')

    controller = MCS.create_controller(sys.argv[1], debug=False,
                                       depth_masks=True, object_masks=True)

    for json_file_name in json_file_list:
        config_data, status = MCS.load_config_json_file(json_file_name)

        if status is not None:
            print('Error with JSON config file ' + json_file_name)
            print(status)
            continue

        if 'name' not in config_data.keys():
            config_data['name'] = json_file_name[json_file_name.rfind(
                '/') + 1:json_file_name.rfind('.')]

        output = controller.start_scene(config_data)

        print(
            'Saving initialization output (scene image and metadata) of ' +
            'JSON config file ' + config_data['name'])

        with open(output_folder + config_data['name'] +
                  '.json', 'w') as output_json_file:
            output_json_file.write(str(output))

        output.image_list[0].save(
            fp=output_folder +
            config_data['name'] +
            '.png')
