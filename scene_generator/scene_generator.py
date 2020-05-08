#!/usr/bin/env python3
#
import logging
import sys
import argparse
import os
import os.path
import json
import copy
import random
from typing import Dict, Any, List

from materials import *
from pretty_json.pretty_json import PrettyJsonEncoder, PrettyJsonNoIndent
import goals

# no public way to find this, apparently :(
LOG_LEVELS = logging._nameToLevel.keys()

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


def strip_debug_info(body):
    """Remove info that's only for our internal use (e.g., for debugging)"""
    for obj in body['objects']:
        clean_object(obj)
    for goal_key in ('domain_list', 'type_list', 'task_list', 'info_list'):
        body['goal'].pop(goal_key, None)
    if 'metadata' in body['goal']:
        metadata = body['goal']['metadata']
        for target_key in ('target', 'target_1', 'target_2'):
            if target_key in metadata:
                metadata[target_key].pop('info', None)


def clean_object(obj):
    """Remove properties we do not want TA1s to have access to."""
    obj.pop('info', None)
    obj.pop('dimensions', None)
    obj.pop('intphys_option', None)
    if 'shows' in obj:
        obj['shows'][0].pop('bounding_box', None)


def generate_scene(name, goal_type, find_path):
    global OUTPUT_TEMPLATE
    body = copy.deepcopy(OUTPUT_TEMPLATE)
    body['name'] = os.path.basename(name)
    ceil_wall_mat_choice = random.choice(CEILING_AND_WALL_MATERIALS)
    body['ceilingMaterial'] = ceil_wall_mat_choice[0]
    body['wallMaterial'] = ceil_wall_mat_choice[0]
    body['floorMaterial'] = random.choice(FLOOR_MATERIALS)[0]

    goal_obj = goals.choose_goal(goal_type)
    goal_obj.update_body(body, find_path)
    return body


def generate_file(name, goal_type, find_path):
    """Create a new scenery file and a debug file. name must end with '.json'."""
    body = generate_scene(name, goal_type, find_path)
    
    debug_name = name[:-5] + '-debug.json'
    write_scene(debug_name, body)
    strip_debug_info(body)
    write_scene(name, body)
    

def write_scene(name, scene):
    # Use PrettyJsonNoIndent on some of the lists and dicts in the output body because the indentation from the normal
    # Python JSON module spaces them out far too much.
    body = copy.deepcopy(scene)

    # Use PrettyJsonNoIndent on some of the lists and dicts in the output body because the indentation from the normal
    # Python JSON module spaces them out far too much.
    wrap_with_json_no_indent(body['goal'], ['action_list', 'domain_list', 'type_list', 'task_list', 'info_list'])
    if 'metadata' in body['goal']:
        for target in ['target', 'target_1', 'target_2']:
            if target in body['goal']['metadata']:
                wrap_with_json_no_indent(body['goal']['metadata'][target], ['info', 'image'])

    for object_config in body['objects']:
        wrap_with_json_no_indent(object_config, ['info', 'materials', 'salientMaterials'])

    with open(name, 'w') as out:
        # PrettyJsonEncoder doesn't work with json.dump so use json.dumps here instead.
        out.write(json.dumps(body, cls=PrettyJsonEncoder, indent=2))


def wrap_with_json_no_indent(data: Dict[str, Any], prop_list: List[str]):
    for prop in prop_list:
        if prop in data:
            data[prop] = PrettyJsonNoIndent(data[prop])


def generate_fileset(prefix: str, count: int, goal_type: str, find_path: bool, stop_on_error: bool) -> None:
    # skip existing files
    index = 1
    dirname = os.path.dirname(prefix)
    if dirname != '':
        os.makedirs(dirname, exist_ok=True)

    while count > 0:
        while True:
            name = f'{prefix}-{index:04}.json'
            file_exists = os.path.exists(name)
            if not file_exists:
                break
            index += 1
        try:
            generate_file(name, goal_type, find_path)
            count -= 1
        except (RuntimeError, ZeroDivisionError, TypeError, goals.GoalException, ValueError) as e:
            if stop_on_error:
                raise
            logging.warning(f'failed to create a file: {e}')


def main(argv):
    parser = argparse.ArgumentParser(description='Create one or more scene descriptions')
    parser.add_argument('--prefix', required=True, help='Prefix for output filenames')
    parser.add_argument('-c', '--count', type=int, default=1, help='How many scenes to generate [default=1]')
    parser.add_argument('--seed', type=int, default=None, help='Random number seed [default=None]')
    parser.add_argument('--goal', default=None, choices=goals.get_goal_types(),
                        help='Generate a goal of the specified type [default is to not generate a goal]. Lowercase '
                             'goals are categories; capitalized goals are specific goals.')
    parser.add_argument('--find_path', default=False, action='store_true',
                        help='Whether to run the pathfinding for interaction goals')
    parser.add_argument('--stop-on-error', default=False, action='store_true',
                        help='Stop immediately if there is an error generating a file [default is print a warning but '
                             'do not stop]')
    parser.add_argument('--loglevel', choices=LOG_LEVELS, help='set logging level')

    args = parser.parse_args(argv[1:])
    random.seed(args.seed)

    if args.loglevel:
        logging.getLogger().setLevel(args.loglevel)

    generate_fileset(args.prefix, args.count, args.goal, args.find_path, args.stop_on_error)


if __name__ == '__main__':
    main(sys.argv)
