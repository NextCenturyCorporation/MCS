#!/usr/bin/env python3
#

import sys
import argparse
import os
import os.path
import json
import copy
import random

from materials import *
import goals

OUTPUT_TEMPLATE_JSON = """
{
  "name": "",
  "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
  "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
  "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
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
MIN_SCENE_POSITION = -4.95
MAX_SCENE_POSITION = 4.95
MAX_TRIES = 20


def load_object_file(object_file_name):
    with open(object_file_name) as object_file:
        objects = json.load(object_file)
    return objects


def generate_file(name, object_defs, goal_type):
    global OUTPUT_TEMPLATE
    body = copy.deepcopy(OUTPUT_TEMPLATE)
    body['name'] = os.path.basename(name)
    body['ceilingMaterial'] = random.choice(CEILING_AND_WALL_MATERIALS)
    body['wallMaterial'] = random.choice(CEILING_AND_WALL_MATERIALS)
    body['floorMaterial'] = random.choice(FLOOR_MATERIALS)

    goal_obj = goals.choose_goal(goal_type)
    goal_obj.update_body(object_defs, body)

    with open(name, 'w') as out:
        json.dump(body, out, indent=2)


def generate_one_fileset(prefix, count, object_defs, goal_type):
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

        generate_file(name, object_defs, goal_type)
        count -= 1


def main(argv):
    parser = argparse.ArgumentParser(description='Create one or more scene descriptions')
    parser.add_argument('--prefix', required=True, help='Prefix for output filenames')
    parser.add_argument('-c', '--count', type=int, default=1, help='How many scenes to generate [default=1]')
    parser.add_argument('--seed', type=int, default=None, help='Random number seed [default=None]')
    parser.add_argument('--objects', required=True, metavar='OBJECTS_FILE',
                        help='File containing a list of objects to choose from')
    parser.add_argument('--goal', default=None, choices=goals.get_goal_types(),
                        help='Generate a goal of the specified type [default is to not generate a goal]')

    args = parser.parse_args(argv[1:])
    random.seed(args.seed)
    objects = load_object_file(args.objects)
    generate_one_fileset(args.prefix, args.count, objects, args.goal)


if __name__ == '__main__':
    main(sys.argv)
