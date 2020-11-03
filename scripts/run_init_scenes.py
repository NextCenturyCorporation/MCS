import glob
import argparse

import machine_common_sense as mcs


def parse_args():
    parser = argparse.ArgumentParser(description='Run MCS')
    parser.add_argument(
        'mcs_unity_build_file',
        help='Path to MCS unity build file')
    parser.add_argument(
        'json_input_folder',
        help='MCS JSON scene input folder')
    parser.add_argument(
        'image_output_folder',
        help='MCS image output folder')
    return parser.parse_args()


def main():
    args = parse_args()

    output_folder = args.image_output_folder + '/'
    json_file_list = glob.glob(args.json_input_folder + '/*.json')

    controller = mcs.create_controller(
        args.mcs_unity_build_file,
        debug=False,
        depth_maps=True,
        object_masks=True)

    for json_file_name in json_file_list:
        config_data, status = mcs.load_config_json_file(json_file_name)

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

    controller.end_scene("", 1)


if __name__ == "__main__":
    main()
