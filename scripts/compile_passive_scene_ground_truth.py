#!/usr/bin/env python3

import argparse
import glob
import json


def main(args):
    filename_list = sorted(glob.glob(args.folder + '*_debug.json'))
    data = {}
    for filename in filename_list:
        scene_data = None
        with open(filename, encoding='utf-8-sig') as json_file:
            scene_data = json.load(json_file)
        if not scene_data:
            print(f'Cannot load JSON file as an MCS scene: {filename}')
            continue
        data[scene_data['name']] = scene_data['goal']['answer']['choice']
    with open(args.output, 'w') as output_file:
        for name, answer in data.items():
            output_file.write(f'{name},{answer}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Compile passive scene ground truth data into a CSV file',
    )
    parser.add_argument('folder', help='Passive scene folder prefix')
    parser.add_argument('output', help='Output file (please end with .csv)')
    args = parser.parse_args()
    main(args)
