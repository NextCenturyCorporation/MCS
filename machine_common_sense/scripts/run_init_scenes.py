import argparse
import glob

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
        unity_app_file_path=args.mcs_unity_build_file,
        config_file_or_dict='./config_oracle_debug.ini')

    for json_file_name in json_file_list:
        scene_data, status = mcs.load_scene_json_file(json_file_name)

        if status is not None:
            print('Error with JSON scene config file ' + json_file_name)
            print(status)
            continue

        if 'name' not in scene_data.keys():
            scene_data['name'] = json_file_name[json_file_name.rfind(
                '/') + 1:json_file_name.rfind('.')]

        output = controller.start_scene(scene_data)

        print(
            'Saving initialization output (scene image and metadata) of ' +
            'JSON scene config file ' + scene_data['name'])

        with open(output_folder + scene_data['name'] +
                  '.json', 'w') as output_json_file:
            output_json_file.write(str(output))

        output.image_list[0].save(
            fp=output_folder +
            scene_data['name'] +
            '.png')

    controller.end_scene("", 1)


if __name__ == "__main__":
    main()
