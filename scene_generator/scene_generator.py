#!/usr/bin/env python3
#

import sys
import argparse
import os
import os.path
import json

DEFAULT_JSON = """
{
  "name": "file_name_prefix_uuid",
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


def generate_file(name):
    global DEFAULT_JSON
    body = json.loads(DEFAULT_JSON)
    body['name'] = os.path.basename(name)
    with open(name, 'w') as out:
        json.dump(body, out, indent=2)


def generate_one_fileset(prefix):
    # skip existing files
    file_exists = True
    index = 1
    while file_exists:
        name = f'{prefix}-{index:04}.json'
        file_exists = os.path.exists(name)
        index += 1

    dirname = os.path.dirname(name)
    if dirname != '':
        os.makedirs(dirname, exist_ok=True)

    generate_file(name)


def main(argv):
    parser = argparse.ArgumentParser(description='Create one or more scene descriptions')
    parser.add_argument('--prefix', help='Prefix for output filenames')
    
    args = parser.parse_args(argv[1:])
    
    generate_one_fileset(args.prefix)
    

if __name__ == '__main__':
    main(sys.argv)