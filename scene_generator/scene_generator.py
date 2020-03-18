#!/usr/bin/env python3
#

import sys
import argparse
import os
import os.path
import json
import copy
import random

OUTPUT_TEMPLATE_JSON = """
{
  "name": "",
  "ceilingMaterial": "Walls/Drywall",
  "floorMaterial": "Fabrics/CarpetWhite 3",
  "wallMaterial": "Walls/DrywallBeige",
  "performerStart": {
    "position": {
      "x": 0,
      "z": 0
    },
    "rotation": {
      "y": 0
    }
  },
  "objects": [],
  "goal": {},
  "answer": {}
}
"""

OUTPUT_TEMPLATE = json.loads(OUTPUT_TEMPLATE_JSON)

# the following mins and maxes are inclusive
MIN_POSITION = -4.8
MAX_POSITION = 4.8
POSITION_DIGITS = 1
MIN_ROTATION = 0
MAX_ROTATION = 359
ROTATION_DIGITS = 0


def random_position():
    return round(random.uniform(MIN_POSITION, MAX_POSITION), POSITION_DIGITS)


def random_rotation():
    rotation = round(random.uniform(MIN_ROTATION, MAX_ROTATION), ROTATION_DIGITS)
    if ROTATION_DIGITS == 0:
        rotation = int(rotation)
    return rotation


def generate_file(name):
    global OUTPUT_TEMPLATE
    body = copy.deepcopy(OUTPUT_TEMPLATE)
    body['name'] = os.path.basename(name)
    position = body['performerStart']['position']
    position['x'] = random_position()
    position['z'] = random_position()
    body['performerStart']['rotation']['y'] = random_rotation()

    with open(name, 'w') as out:
        json.dump(body, out, indent=2)


def generate_one_fileset(prefix, count):
    # skip existing files
    index = 1
    dirname = os.path.dirname(prefix)
    if dirname != '':
        os.makedirs(dirname, exist_ok=True)

    while count > 0:
        file_exists = True
        while file_exists:
            name = f'{prefix}-{index:04}.json'
            file_exists = os.path.exists(name)
            index += 1

        generate_file(name)
        count -= 1


def main(argv):
    parser = argparse.ArgumentParser(description='Create one or more scene descriptions')
    parser.add_argument('--prefix', required=True, help='Prefix for output filenames')
    parser.add_argument('-c', '--count', type=int, default=1, help='How many scenes to generate [default=1]')
    parser.add_argument('--seed', type=int, default=None, help='Random number seed [default=None]')
    
    args = parser.parse_args(argv[1:])

    random.seed(args.seed)
    generate_one_fileset(args.prefix, args.count)
    

if __name__ == '__main__':
    main(sys.argv)
