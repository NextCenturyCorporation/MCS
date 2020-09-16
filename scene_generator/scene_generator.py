#!/usr/bin/env python3

import argparse
import copy
import json
import logging
import os
import os.path
import random
import sys
import uuid
from typing import Any, Dict, List

import exceptions
import interactive_sequences
import intuitive_physics_sequences
import materials
from pretty_json.pretty_json import PrettyJsonEncoder, PrettyJsonNoIndent


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


SEQUENCE_LIST = (
    interactive_sequences.INTERACTIVE_SCENE_SEQUENCE_LIST +
    intuitive_physics_sequences.INTUITIVE_PHYSICS_SEQUENCE_LIST
)


def strip_debug_info(body: Dict[str, Any]) -> None:
    """Remove info that's only for our internal use (e.g., for debugging)"""
    body.pop('wallColors', None)
    for obj in body['objects']:
        clean_object(obj)
    for goal_key in ('domain_list', 'type_list',
                     'task_list', 'info_list', 'series_id'):
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
    obj.pop('goalString', None)
    obj.pop('dimensions', None)
    obj.pop('offset', None)
    obj.pop('closedDimensions', None)
    obj.pop('closedOffset', None)
    obj.pop('enclosedAreas', None)
    obj.pop('openAreas', None)
    obj.pop('chosenMovement', None)
    obj.pop('isParentOf', None)
    obj.pop('materialsList', None)
    obj.pop('materialCategory', None)
    obj.pop('originalLocation', None)
    obj.pop('novelColor', None)
    obj.pop('novelCombination', None)
    obj.pop('novelShape', None)
    obj.pop('color', None)
    obj.pop('shape', None)
    obj.pop('size', None)
    if 'shows' in obj:
        obj['shows'][0].pop('boundingBox', None)


def generate_body_template(name: str) -> Dict[str, Any]:
    global OUTPUT_TEMPLATE
    body = copy.deepcopy(OUTPUT_TEMPLATE)
    body['name'] = os.path.basename(name)
    ceil_wall_mat_choice = random.choice(materials.CEILING_AND_WALL_MATERIALS)
    body['ceilingMaterial'] = ceil_wall_mat_choice[0]
    body['wallMaterial'] = ceil_wall_mat_choice[0]
    body['wallColors'] = ceil_wall_mat_choice[1]
    body['floorMaterial'] = random.choice(materials.FLOOR_MATERIALS)[0]
    return body


def write_scene(name: str, scene: Dict[str, Any]) -> None:
    # Use PrettyJsonNoIndent on some of the lists and dicts in the
    # output body because the indentation from the normal Python JSON
    # module spaces them out far too much.
    body = copy.deepcopy(scene)

    # Use PrettyJsonNoIndent on some of the lists and dicts in the
    # output body because the indentation from the normal Python JSON
    # module spaces them out far too much.
    wrap_with_json_no_indent(
        body['goal'], [
            'action_list', 'domain_list', 'type_list',
            'task_list', 'info_list'])
    if 'metadata' in body['goal']:
        for target in ['target', 'target_1', 'target_2']:
            if target in body['goal']['metadata']:
                wrap_with_json_no_indent(
                    body['goal']['metadata'][target], [
                        'info', 'image'])

    for object_config in body['objects']:
        wrap_with_json_no_indent(
            object_config, [
                'info', 'materials', 'salientMaterials'])

    with open(name, 'w') as out:
        # PrettyJsonEncoder doesn't work with json.dump so use json.dumps here
        # instead.
        try:
            out.write(json.dumps(body, cls=PrettyJsonEncoder, indent=2))
        except Exception as e:
            logging.error(body, e)


def wrap_with_json_no_indent(
        data: Dict[str, Any], prop_list: List[str]) -> None:
    for prop in prop_list:
        if prop in data:
            data[prop] = PrettyJsonNoIndent(data[prop])


def generate_sequence(
    file_name: str,
    type_name: str,
    training: bool,
    find_path: bool,
    stop_on_error: bool
) -> None:
    body_template = generate_body_template('')
    sequence_id = str(uuid.uuid4())

    sequence_factory = None
    for item in SEQUENCE_LIST:
        if item.name == type_name:
            sequence_factory = item
    if not sequence_factory:
        raise ValueError(f'Failed to find {type_name} sequence factory')

    while True:
        try:
            # Build the sequence and all of its scenes.
            sequence = sequence_factory.build(body_template)
            scenes = sequence.get_scenes()
            if training:
                scenes = [scenes[0]]
            scene_index = 1
            for scene in scenes:
                index_suffix = (
                    '' if len(scenes) == 1 else ('_' + str(scene_index))
                )
                scene_copy = copy.deepcopy(scene)
                scene_name = file_name + index_suffix
                scene_copy['name'] = scene_name
                scene_copy['goal']['sequence_id'] = (
                    sequence.get_name().replace(' ', '_') + '_' +
                    sequence_id + index_suffix
                )
                write_scene(scene_name + '_debug.json', scene_copy)
                strip_debug_info(scene_copy)
                write_scene(scene_name + '.json', scene_copy)
                scene_index += 1
            break
        except (
            RuntimeError,
            ZeroDivisionError,
            TypeError,
            exceptions.SceneException,
            ValueError
        ) as e:
            if stop_on_error:
                raise
            logging.warning(f'Failed to create sequence: {e}')


def generate_scenes(
    prefix: str,
    total: int,
    type_name: str,
    training: bool,
    find_path: bool,
    stop_on_error: bool
) -> None:
    folder_name = os.path.dirname(prefix)
    if folder_name != '':
        os.makedirs(folder_name, exist_ok=True)

    index = 1
    count = 0
    while count < total:
        while True:
            file_name = f'{prefix}_{index:04}'
            file_exists = os.path.exists(
                file_name + ('' if training else '_1') + '.json'
            )
            if not file_exists:
                break
            index += 1
        count += 1
        logging.debug(f'\n\ngenerate sequence {count} / {total}\n')
        generate_sequence(
            file_name,
            type_name,
            training,
            find_path,
            stop_on_error
        )


def main(argv):
    parser = argparse.ArgumentParser(
        description='Generate MCS scene configuration JSON files.')
    parser.add_argument(
        '-p',
        '--prefix',
        required=True,
        help='Output filename prefix')
    parser.add_argument(
        '-t',
        '--type',
        required=True,
        choices=[item.name for item in SEQUENCE_LIST],
        help='Type of sequences to generate')
    parser.add_argument(
        '-c',
        '--count',
        type=int,
        default=1,
        help='Number of sequences to generate [default=1]')
    parser.add_argument(
        '-s',
        '--seed',
        type=int,
        default=None,
        help='Random number seed [default=None]')
    parser.add_argument(
        '--training',
        default=False,
        action='store_true',
        help='Generate training data [default=False]')
    parser.add_argument(
        '--find_path',
        default=False,
        action='store_true',
        help='Run interactive scene goal pathfinding (somewhat slow)')
    parser.add_argument(
        '--stop-on-error',
        default=False,
        action='store_true',
        help='Stop if an error occurs [default=False]')
    parser.add_argument(
        '-l',
        '--loglevel',
        # no public way to find this, apparently :(
        choices=logging._nameToLevel.keys(),
        help='Set log level')

    args = parser.parse_args(argv[1:])
    random.seed(args.seed)

    if args.loglevel:
        logging.getLogger().setLevel(args.loglevel)

    generate_scenes(
        args.prefix,
        args.count,
        args.type,
        args.training,
        args.find_path,
        args.stop_on_error
    )


if __name__ == '__main__':
    main(sys.argv)
