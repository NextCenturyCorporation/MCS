import argparse
import glob
import json


def main(debug_scene_folder: str, output_file_name: str):
    json_file_list = glob.glob(f"{debug_scene_folder}*_debug.json")
    json_file_list = sorted(json_file_list)
    print(f'Found {len(json_file_list)} debug files in {debug_scene_folder}')
    all_ground_truth = {}
    for json_file_name in json_file_list:
        with open(json_file_name) as json_file:
            data = json.load(json_file)
            scene_name = data['name']
            ground_truth = data['goal']['answer']['choice']
            all_ground_truth[scene_name] = ground_truth
    print(f'Saving {len(all_ground_truth.keys())} rows to {output_file_name}')
    with open(output_file_name, 'w') as output_file:
        output_file.write('scene_name,ground_truth\n')
        for scene_name, ground_truth in all_ground_truth.items():
            output_file.write(f'{scene_name},{ground_truth}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=('Extract Ground Truth'))
    parser.add_argument(
        'debug_scene_folder',
        type=str,
        help='Folder containing the MCS scene JSON debug files'
    )
    parser.add_argument(
        'output_file_name',
        type=str,
        help='Name of the output CSV file'
    )
    args = parser.parse_args()
    main(args.debug_scene_folder, args.output_file_name)
