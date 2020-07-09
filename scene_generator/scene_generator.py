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
import uuid
from enum import Enum, auto
from typing import Dict, Any, List, Tuple

import exceptions
import pairs
import quartets
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
  "wallColors": ["white"],
  "performerStart": {
    "position": {
      "x": 0,
      "y": 0,
      "z": 0
    },
    "rotation": {
      "x": 0,
      "y": 0,
      "z": 0
    }
  },
  "objects": [],
  "goal": {},
  "answer": {}
}
"""

OUTPUT_TEMPLATE = json.loads(OUTPUT_TEMPLATE_JSON)


def strip_debug_info(body: Dict[str, Any]) -> None:
    """Remove info that's only for our internal use (e.g., for debugging)"""
    body.pop('wallColors', None)
    for obj in body['objects']:
        clean_object(obj)
    for goal_key in ('domain_list', 'type_list', 'task_list', 'info_list', 'series_id'):
        body['goal'].pop(goal_key, None)
    if 'metadata' in body['goal']:
        metadata = body['goal']['metadata']
        metadata.pop('objects', None)
        for target_key in ('target', 'target_1', 'target_2'):
            if target_key in metadata:
                metadata[target_key].pop('info', None)


def clean_object(obj: Dict[str, Any]) -> None:
    """Remove properties we do not want TA1s to have access to."""
    obj.pop('info', None)
    obj.pop('info_string', None)
    obj.pop('dimensions', None)
    obj.pop('intphys_option', None)
    obj.pop('materials_list', None)
    obj.pop('materialCategory', None)
    obj.pop('original_location', None)
    obj.pop('novel_color', None)
    obj.pop('novel_combination', None)
    obj.pop('novel_shape', None)
    obj.pop('shape', None)
    obj.pop('similarityScale', None)
    if 'shows' in obj:
        obj['shows'][0].pop('bounding_box', None)


def generate_body_template(name: str) -> Dict[str, Any]:
    global OUTPUT_TEMPLATE
    body = copy.deepcopy(OUTPUT_TEMPLATE)
    body['name'] = os.path.basename(name)
    ceil_wall_mat_choice = random.choice(CEILING_AND_WALL_MATERIALS)
    body['ceilingMaterial'] = ceil_wall_mat_choice[0]
    body['wallMaterial'] = ceil_wall_mat_choice[0]
    body['wallColors'] = ceil_wall_mat_choice[1]
    body['floorMaterial'] = random.choice(FLOOR_MATERIALS)[0]
    return body


def generate_scene(name: str, goal_type: str, find_path: bool) -> Dict[str, Any]:
    body = generate_body_template(name)
    goal_obj = goals.choose_goal(goal_type)
    goal_obj.update_body(body, find_path)
    return body


def write_file(name: str, body: Dict[str, Any]) -> None:
    write_scene(name + '-debug.json', body)
    strip_debug_info(body)
    write_scene(name + '.json', body)


def write_scene(name: str, scene: Dict[str, Any]) -> None:
    # Use PrettyJsonNoIndent on some of the lists and dicts in the
    # output body because the indentation from the normal Python JSON
    # module spaces them out far too much.
    body = copy.deepcopy(scene)

    # Use PrettyJsonNoIndent on some of the lists and dicts in the
    # output body because the indentation from the normal Python JSON
    # module spaces them out far too much.
    wrap_with_json_no_indent(body['goal'], ['action_list', 'domain_list', 'type_list', 'task_list', 'info_list'])
    if 'metadata' in body['goal']:
        for target in ['target', 'target_1', 'target_2']:
            if target in body['goal']['metadata']:
                wrap_with_json_no_indent(body['goal']['metadata'][target], ['info', 'image'])

    for object_config in body['objects']:
        wrap_with_json_no_indent(object_config, ['info', 'materials', 'salientMaterials'])

    with open(name, 'w') as out:
        # PrettyJsonEncoder doesn't work with json.dump so use json.dumps here instead.
        try:
            out.write(json.dumps(body, cls=PrettyJsonEncoder, indent=2))
        except Exception as e:
            logging.error(body, e)


def wrap_with_json_no_indent(data: Dict[str, Any], prop_list: List[str]) -> None:
    for prop in prop_list:
        if prop in data:
            data[prop] = PrettyJsonNoIndent(data[prop])


def generate_name(prefix: str, count: int, scene: int = None) -> str:
    if scene is not None:
        return f'{prefix}-{count:04}-{scene}'
    return f'{prefix}-{count:04}'


def generate_single(prefix: str, count: int, goal_type: str, find_path: bool,
                           stop_on_error: bool) -> None:
    # skip existing files
    index = 1

    while count > 0:
        while True:
            name = generate_name(prefix, index)
            file_exists = os.path.exists(name + '.json')
            if not file_exists:
                break
            index += 1
        try:
            body = generate_scene(name, goal_type, find_path)
            write_file(name, body)
            count -= 1
        except (RuntimeError, ZeroDivisionError, TypeError, exceptions.SceneException, ValueError) as e:
            if stop_on_error:
                raise
            logging.warning(f'failed to create a file: {e}')


def generate_quartet(prefix: str, count: int, quartet_name: str, find_path: bool, stop_on_error: bool) -> None:
    template = generate_body_template('')
    quartet_class = quartets.get_quartet_class(quartet_name)
    quartet = quartet_class(template, find_path)
    quartet_id = str(uuid.uuid4())
    quartet_name = quartet.__class__.__name__.replace('Quartet', '').lower()
    for q in range(1, 5):
        name = generate_name(prefix, count, q)
        logging.debug(f'starting generation of\t{name}')
        while True:
            try:
                scene = quartet.get_scene(q)
                scene['name'] = name
                scene['goal']['series_id'] = 'quartet_' + quartet_name + '_' + quartet_id
                scene_copy = copy.deepcopy(scene)
                write_file(name, scene_copy)
                break
            except (RuntimeError, ZeroDivisionError, TypeError, exceptions.SceneException, ValueError) as e:
                if stop_on_error:
                    raise
                logging.warning(f'failed to create a quartet member: {e}')
        logging.debug(f'end generation of\t{name}')


def generate_quartets(prefix: str, count: int, quartet_name: str, find_path: bool, stop_on_error: bool) -> None:
    index = 1
    while count > 0:
        while True:
            file_exists = os.path.exists(generate_name(prefix, index, 1) + '.json')
            if not file_exists:
                break
            index += 1
        generate_quartet(prefix, index, quartet_name, find_path, stop_on_error)
        count -= 1


def write_scene_of_pair(scene: Dict[str, Any], name: str) -> None:
    scene['name'] = name
    scene_copy = copy.deepcopy(scene)
    write_file(name, scene_copy)


def generate_pair(prefix: str, count: int, find_path: bool, stop_on_error: bool) -> None:
    template = generate_body_template('')
    pair_class = pairs.get_pair_class()
    pair = pair_class(template, find_path)
    pair_id = str(uuid.uuid4())
    pair_name = pair.__class__.__name__.replace('Pair', '').lower()
    logging.debug(f'generating scene pair #{count}')
    while True:
        try:
            scenes = pair.get_scenes()
            scenes[0]['goal']['series_id'] = 'pair_' + pair_name + '_' + pair_id
            scenes[1]['goal']['series_id'] = 'pair_' + pair_name + '_' + pair_id
            write_scene_of_pair(scenes[0], generate_name(prefix, count, 1))
            write_scene_of_pair(scenes[1], generate_name(prefix, count, 2))
            break
        except (RuntimeError, ZeroDivisionError, TypeError, exceptions.SceneException, ValueError) as e:
            if stop_on_error:
                raise
            logging.warning(f'failed to create a pair: {e}')
    logging.debug(f'end generation of scene pair #{count}')


def generate_pairs(prefix: str, count: int, find_path: bool, stop_on_error: bool) -> None:
    index = 1
    while count > 0:
        while True:
            file_exists = os.path.exists(generate_name(prefix, index, 1) + '.json')
            if not file_exists:
                break
            index += 1
        generate_pair(prefix, index, find_path, stop_on_error)
        count -= 1


class FilesetType(Enum):
    SINGLE = auto()
    QUARTET = auto()
    PAIR = auto()


def generate_fileset(prefix: str, count: int, type_name: str, find_path: bool, stop_on_error: bool,
                     fileset_type: FilesetType) -> None:
    dirname = os.path.dirname(prefix)
    if dirname != '':
        os.makedirs(dirname, exist_ok=True)

    if fileset_type == FilesetType.QUARTET:
        generate_quartets(prefix, count, type_name, find_path, stop_on_error)
    elif fileset_type == FilesetType.PAIR:
        generate_pairs(prefix, count, find_path, stop_on_error)
    elif fileset_type == FilesetType.SINGLE:
        generate_single(prefix, count, type_name, find_path, stop_on_error)


def main(argv):
    parser = argparse.ArgumentParser(description='Create one or more scene descriptions')
    parser.add_argument('--prefix', required=True, help='Prefix for output filenames')
    parser.add_argument('-c', '--count', type=int, default=1, help='How many scenes or quartets to generate [default=1]')
    parser.add_argument('--seed', type=int, default=None, help='Random number seed [default=None]')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--goal', default=None, choices=goals.get_goal_types(),
                       help='Generate a goal of the specified type [default is to not generate a goal]. Lowercase '
                       'goals are categories; capitalized goals are specific goals.')
    group.add_argument('--quartet', default=None, choices=quartets.get_quartet_types(),
                       help='Generate a scene quartet for a goal of the specified type [default is to generate individual scenes]. Lowercase '
                       'goals are categories; capitalized goals are specific goals.')
    group.add_argument('--pair', default=False, action='store_true',
                       help='Generate a scene pair for interaction tasks.')
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

    if args.goal is not None:
        type_name = args.goal
        fileset_type = FilesetType.SINGLE
    elif args.quartet is not None:
        type_name = args.quartet
        fileset_type = FilesetType.QUARTET
    elif args.pair:
        type_name = None
        fileset_type = FilesetType.PAIR
    else:
        type_name = None
        fileset_type = FilesetType.SINGLE

    generate_fileset(args.prefix, args.count, type_name, args.find_path, args.stop_on_error, fileset_type)


if __name__ == '__main__':
    main(sys.argv)
