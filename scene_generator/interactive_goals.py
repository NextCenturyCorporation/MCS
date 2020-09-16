import copy
import logging
import math
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AnyStr, Dict, List, Sequence, Tuple

from sympy import Segment, intersection

import exceptions
import geometry
from machine_common_sense.controller_ai2thor import (
    MAX_MOVE_DISTANCE,
    MAX_REACH_DISTANCE,
    PERFORMER_CAMERA_Y
)
import objects
import optimal_path
import tags
from util import (
    finalize_object_definition,
    finalize_object_materials_and_colors,
)


def generate_image_file_name(target: Dict[str, Any]) -> str:
    if 'materials' not in target or not target['materials']:
        return target['type']

    material_name_list = [item[(item.rfind(
        '/') + 1):].lower().replace(' ', '_') for item in target['materials']]
    return target['type'] + ('_' if len(material_name_list) >
                             0 else '') + ('_'.join(material_name_list))


def find_image_for_object(object_def: Dict[str, Any]) -> AnyStr:
    image_file_name = ""

    try:
        image_file_name = 'images/' + \
            generate_image_file_name(object_def) + '.txt'

        with open(image_file_name, 'r') as image_file:
            target_image = image_file.read()

        return target_image
    except BaseException:
        logging.warning(
            'Image object could not be found, make sure you generated ' +
            ' the image: ' + image_file_name)


def find_image_name(target: Dict[str, Any]) -> str:
    return generate_image_file_name(target) + '.png'


def parse_path_section(path_section: Sequence[Sequence[float]],
                       current_heading: float,
                       performer: Tuple[float, float],
                       goal_boundary: List[Dict[str, float]]) -> \
        Tuple[List[Dict[str, Any]], float, Tuple[float, float]]:
    """Compute the actions for one path section, starting with
    current_heading. Returns a tuple: (list of actions, new heading,
    performer position)"""
    actions = []
    dx = path_section[1][0] - performer[0]
    dz = path_section[1][1] - performer[1]
    theta = math.degrees(math.atan2(dz, dx))

    # IF my calculations are correct, this should be right no matter what
    # I'm assuming a positive angle is a clockwise rotation- so this
    # should work
    # I think

    delta_t = (current_heading - theta) % 360
    current_heading = theta
    if delta_t != 0:
        action = {
            'action': 'RotateLook',
            'params': {
                'rotation': round(delta_t, 0),
                'horizon': 0.0
            }
        }
        actions.append(action)

    goal_center = (path_section[1][0], path_section[1][1])
    performer_seg = Segment(performer, goal_center)
    distance = None

    for indx in range(len(goal_boundary)):
        intersect_point = intersection(
            performer_seg,
            Segment(
                (goal_boundary[indx - 1]['x'], goal_boundary[indx - 1]['z']),
                (goal_boundary[indx]['x'], goal_boundary[indx]['z'])
            )
        )
        if intersect_point:
            distance = float(intersect_point[0].distance(performer))
            break

    if distance is None:
        distance = math.sqrt(dx ** 2 + dz ** 2)
    frac, whole = math.modf(distance / MAX_MOVE_DISTANCE)
    actions.extend([{
        "action": "MoveAhead",
        "params": {
            "amount": 1
        }
    }] * int(whole))

    rounded_frac = round(frac, geometry.POSITION_DIGITS)
    if rounded_frac > 0:
        actions.append({
            "action": "MoveAhead",
            "params": {
                "amount": rounded_frac
            }
        })
    # Where am I?
    performer = (performer[0] + distance * math.cos(math.radians(theta)),
                 performer[1] + distance * math.sin(
                     math.radians(theta)))
    return actions, current_heading, performer


def get_navigation_actions(start_location: Dict[str, Any],
                           goal_object: Dict[str, Any],
                           all_objects: List[Dict[str, Any]]) -> \
    Tuple[List[Dict[str, Any]],
          Tuple[float, float],
          float]:
    """Get the action sequence for going from performer start to the
    goal_object. Returns tuple (action_list, performer end position,
    performer end heading).
    """
    performer = (
        start_location['position']['x'],
        start_location['position']['z'])
    if 'locationParent' in goal_object:
        parent = next(
            (obj for obj in all_objects if obj['id'] ==
             goal_object['locationParent']),
            None)
        if parent is None:
            raise PathfindingException(
                f'object {goal_object["id"]} has parent '
                f'{goal_object["locationParent"]} that does not exist')
        goal_object = parent
    goal = (goal_object['shows'][0]['position']['x'],
            goal_object['shows'][0]['position']['z'])
    hole_rects = []

    hole_rects.extend(object['shows'][0]['boundingBox'] for object
                      in all_objects if object['id'] != goal_object['id'] and
                      'locationParent' not in object)
    path = optimal_path.generatepath(performer, goal, hole_rects)
    if path is None:
        raise PathfindingException(
            f'could not find path to target {goal_object["id"]}')
    for object in all_objects:
        if object['id'] == goal_object['id']:
            goal_boundary = object['shows'][0]['boundingBox']
            break
    actions = []
    current_heading = 90 - start_location['rotation']['y']
    for indx in range(len(path) - 1):
        new_actions, current_heading, performer = parse_path_section(
            path[indx:indx + 2], current_heading, performer, goal_boundary)
        actions.extend(new_actions)

    return actions, performer, current_heading


def trim_actions_to_reach(actions: List[Dict[str, Any]],
                          performer: Tuple[float, float],
                          heading: float,
                          goal_obj: Dict[str, Any]) -> \
        Tuple[List[Dict[str, Any]], Tuple[float, float]]:
    """Trim the action list from the end so that the performer doesn't
    take additonal steps toward the goal object once they're within
    MAX_REACH_DISTANCE.
    """
    goal_position = goal_obj['shows'][0]['position']
    total_distance = math.sqrt(
        (performer[0] - goal_position['x']) ** 2 +
        (performer[1] - goal_position['z']) ** 2
    )

    i = len(actions)
    step_dist = 0
    dist_moved = 0
    while total_distance < MAX_REACH_DISTANCE and i > 0:
        i -= 1
        action = actions[i]
        if action['action'] != 'MoveAhead':
            break
        step_dist = action['params']['amount'] * MAX_MOVE_DISTANCE
        total_distance += step_dist
        dist_moved += step_dist

    dist_moved -= step_dist
    new_actions = actions[:i + 1]
    new_x = performer[0] - dist_moved * math.cos(math.radians(heading))
    new_z = performer[1] - dist_moved * math.sin(math.radians(heading))
    return new_actions, (new_x, new_z)


class InteractiveGoal(ABC):
    def __init__(self, name: str, goal_template: Dict[str, Any]):
        self._name = name
        self._goal_template = goal_template

    @abstractmethod
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
        """Choose and return a target definition."""
        pass

    @abstractmethod
    def get_target_count(self) -> int:
        """Return this goal's number of targets."""
        pass

    @abstractmethod
    def update_goal_config(
        self,
        goal_config: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update and return the given goal config for a scene."""
        pass

    @abstractmethod
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        """Return if a target can be positioned at the given location based on
        the previously made targets and the performer's start location."""
        pass

    def choose_definition(self) -> Dict[str, Any]:
        """Choose and return an object definition."""
        # Same chance to pick each list.
        object_definition_list = random.choice(objects.get('ALL_LISTS'))
        # Same chance to pick each object definition from the list.
        object_definition = finalize_object_definition(
            random.choice(object_definition_list))
        return random.choice(
            finalize_object_materials_and_colors(object_definition))

    def choose_location(
        self,
        object_definition: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]]
    ) -> Tuple[Dict[str, Any], List[List[Dict[str, float]]]]:
        """Choose and return a location for the given object and the new
        bounds list."""
        bounds_list_copy = copy.deepcopy(bounds_list)
        object_location = geometry.calc_obj_pos(
            performer_start['position'],
            bounds_list_copy,
            object_definition
        )
        if not object_location:
            raise exceptions.SceneException(
                f'cannot position object (type={object_definition["type"]})')
        return object_location, bounds_list_copy

    def get_goal_template(self) -> Dict[str, Any]:
        """Return this goal's JSON data template."""
        return self._goal_template

    def get_name(self) -> str:
        """Return this goal's name."""
        return self._name


class RetrievalGoal(InteractiveGoal):
    def __init__(self):
        super().__init__(tags.RETRIEVAL, {
            'category': tags.RETRIEVAL,
            'domain_list': [
                tags.DOMAIN_OBJECTS,
                tags.DOMAIN_OBJECTS_SOLIDITY,
                tags.DOMAIN_PLACES,
                tags.DOMAIN_PLACES_LOCALIZATION,
                tags.DOMAIN_PLACES_NAVIGATION
            ],
            'type_list': [
                tags.INTERACTIVE,
                tags.ACTION_FULL,
                tags.RETRIEVAL
            ]
        })

    # Override
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
        definition_list = random.choice(objects.get('PICKUPABLE_LISTS'))
        definition = finalize_object_definition(random.choice(definition_list))
        return random.choice(finalize_object_materials_and_colors(definition))

    # Override
    def get_target_count(self) -> int:
        return 1

    # Override
    def update_goal_config(
        self,
        goal_config: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        image = find_image_for_object(target_list[0])
        image_name = find_image_name(target_list[0])
        goal_config['metadata'] = {
            'target': {
                'id': target_list[0]['id'],
                'info': target_list[0]['info'],
                'match_image': True,
                'image': image,
                'image_name': image_name
            }
        }
        goal_config['description'] = f'Find and pick up the ' \
            f'{target_list[0]["goalString"]}.'
        return goal_config

    # Override
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        return True

    def _find_optimal_path(
        self,
        goal_objects: List[Dict[str, Any]],
        all_objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        actions, performer, heading = get_navigation_actions(
            self._performer_start, goal_objects[0], all_objects)
        actions, performer = trim_actions_to_reach(
            actions, performer, heading, goal_objects[0])

        # Do I have to look down to see the object????
        plane_dist = math.sqrt(
            (goal_objects[0]['shows'][0]['position']['x'] -
                performer[0]) ** 2 +
            (goal_objects[0]['shows'][0]['position']['z'] -
                performer[1]) ** 2
        )
        height_dist = PERFORMER_CAMERA_Y - \
            goal_objects[0]['shows'][0]['position']['y']
        elevation = math.degrees(math.atan2(height_dist, plane_dist))
        if abs(elevation) > 30:
            actions.append({
                'action': 'RotateLook',
                'params': {
                    'rotation': 0,
                    'horizon': round(elevation, 0)
                }
            })
        actions.append({
            'action': 'PickupObject',
            'params': {
                'objectId': goal_objects[0]['id']
            }
        })
        if abs(elevation) > 30:
            actions.append(
                {
                    'action': 'RotateLook',
                    'params': {
                        'rotation': 0,
                        'horizon': -1 * round(elevation, 0)
                    }
                })
        return actions


class TransferralGoal(InteractiveGoal):
    class RelationshipType(Enum):
        NEXT_TO = 'next to'
        ON_TOP_OF = 'on top of'

    def __init__(self):
        super().__init__(tags.TRANSFERRAL, {
            'category': tags.TRANSFERRAL,
            'domain_list': [
                tags.DOMAIN_OBJECTS,
                tags.DOMAIN_OBJECTS_SOLIDITY,
                tags.DOMAIN_PLACES,
                tags.DOMAIN_PLACES_LOCALIZATION,
                tags.DOMAIN_PLACES_NAVIGATION
            ],
            'type_list': [
                tags.INTERACTIVE,
                tags.ACTION_FULL,
                tags.TRANSFERRAL
            ]
        })

    # Override
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
        if target_number == 0:
            definition_list = random.choice(objects.get('PICKUPABLE_LISTS'))

        elif target_number == 1:
            choice_list = []
            for possible_list in objects.get('ALL_LISTS'):
                stack_targets = [
                    definition for definition in possible_list
                    if 'stackTarget' in definition.get('attributes', [])
                ]
                if len(stack_targets) > 0:
                    choice_list.append(stack_targets)

            if len(choice_list) == 0:
                raise exceptions.SceneException(
                    'Cannot find any stack targets in object definitions')

            # Same chance to pick each list.
            definition_list = random.choice(choice_list)

        else:
            raise exceptions.SceneException(
                f'Expected target with number 0 or 1 but got {target_number}')

        # Same chance to pick each object definition from the list.
        definition = finalize_object_definition(random.choice(definition_list))
        return random.choice(finalize_object_materials_and_colors(definition))

    # Override
    def get_target_count(self) -> int:
        return 2

    # Override
    def update_goal_config(
        self,
        goal_config: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        relationship = random.choice(list(self.RelationshipType))
        image_1 = find_image_for_object(target_list[0])
        image_2 = find_image_for_object(target_list[1])
        image_name_1 = find_image_name(target_list[0])
        image_name_2 = find_image_name(target_list[1])
        goal_config['metadata'] = {
            'target_1': {
                'id': target_list[0]['id'],
                'info': target_list[0]['info'],
                'match_image': True,
                'image': image_1,
                'image_name': image_name_1
            },
            'target_2': {
                'id': target_list[1]['id'],
                'info': target_list[1]['info'],
                'match_image': True,
                'image': image_2,
                'image_name': image_name_2
            },
            'relationship': ['target_1', relationship.value, 'target_2']
        }
        goal_config['description'] = f'Find and pick up the ' \
            f'{target_list[0]["goalString"]} and move it ' \
            f'{relationship.value} the {target_list[1]["goalString"]}.'
        return goal_config

    # Override
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        if target_number == 0:
            return True

        elif target_number != 1:
            raise exceptions.SceneException(
                f'Expected target with number 0 or 1 but got {target_number}')

        if len(previously_made_target_list) == 0:
            raise exceptions.SceneException(
                'Expected existing transferral target')

        distance = geometry.position_distance(
            previously_made_target_list[0]['shows'][0]['position'],
            target_location['position']
        )

        # Don't position too close to the existing target.
        return distance >= geometry.MIN_OBJECTS_SEPARATION_DISTANCE

    def _find_optimal_path(
        self,
        goal_objects: List[Dict[str, Any]],
        all_objects: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        actions, performer, heading = get_navigation_actions(
            self._performer_start, goal_objects[0], all_objects
        )
        actions, performer = trim_actions_to_reach(
            actions, performer, heading, goal_objects[0])

        # Do I have to look down to see the object????
        plane_dist = math.sqrt(
            (goal_objects[0]['shows'][0]['position']['x'] - performer[0]) **
            2 +
            (goal_objects[0]['shows'][0]['position']['z'] - performer[1]) ** 2
        )
        height_dist = PERFORMER_CAMERA_Y - \
            goal_objects[0]['shows'][0]['position']['y']
        elevation = math.degrees(math.atan2(height_dist, plane_dist))
        if abs(elevation) > 30:
            actions.append({
                'action': 'RotateLook',
                'params': {
                    'rotation': 0.0,
                    'horizon': round(elevation, geometry.POSITION_DIGITS)
                }
            })
        actions.append({
            'action': 'PickupObject',
            'params': {
                'objectId': goal_objects[0]['id']
            }
        })
        if abs(elevation) > 30:
            actions.append({
                'action': 'RotateLook',
                'params': {
                    'rotation': 0.0,
                    'horizon': -1 * round(elevation, geometry.POSITION_DIGITS)
                }
            })

        ignore_object_ids = [goal_objects[0]['id'], goal_objects[1]['id']]
        if 'locationParent' in goal_objects[0]:
            ignore_object_ids.append(goal_objects[0]['locationParent'])
            parent = next(
                (
                    obj
                    for obj in all_objects
                    if obj['id'] == goal_objects[0]['locationParent']
                )
            )
            target = (
                parent['shows'][0]['position']['x'],
                parent['shows'][0]['position']['z'])
        else:
            target = (
                goal_objects[0]['shows'][0]['position']['x'],
                goal_objects[0]['shows'][0]['position']['z'])
        if 'locationParent' in goal_objects[1]:
            ignore_object_ids.append(goal_objects[1]['locationParent'])
            parent = next(
                (
                    obj
                    for obj in all_objects
                    if obj['id'] == goal_objects[1]['locationParent']
                )
            )
            goal = (parent['shows'][0]['position']['x'],
                    parent['shows'][0]['position']['z'])
        else:
            goal = (
                goal_objects[1]['shows'][0]['position']['x'],
                goal_objects[1]['shows'][0]['position']['z'])

        hole_rects = []
        hole_rects.extend(
            object['shows'][0]['boundingBox']
            for object in all_objects
            if (
                object['id'] not in ignore_object_ids and
                'locationParent' not in object
            )
        )

        logging.debug(
            f'TransferralGoal.f_o_p: target = {target}\tgoal = {goal}\t'
            f'holes = {hole_rects}')
        path = optimal_path.generatepath(target, goal, hole_rects)
        if path is None:
            raise PathfindingException(
                'could not find path from target object to goal')
        logging.debug(f'TransferralGoal.f_o_p: got path = {path}')
        for object in all_objects:
            if object['id'] == goal_objects[1]['id']:
                goal_boundary = object['shows'][0]['boundingBox']
                break
        current_heading = heading
        for indx in range(len(path) - 1):
            new_actions, current_heading, performer = parse_path_section(
                path[indx:indx + 2], current_heading, performer, goal_boundary)
            actions.extend(new_actions)

        actions, performer = trim_actions_to_reach(
            actions, performer, current_heading, goal_objects[1])

        # TODO: maybe look at receptacle part of the parent object (future
        # ticket)
        actions.append({
            'action': 'PutObject',
            'params': {
                'objectId': goal_objects[0]['id'],
                'receptacleObjectId': goal_objects[1]['id']
            }})

        return actions


class TraversalGoal(InteractiveGoal):
    def __init__(self):
        super().__init__(tags.TRAVERSAL, {
            'category': tags.TRAVERSAL,
            'domain_list': [
                tags.DOMAIN_OBJECTS,
                tags.DOMAIN_OBJECTS_SOLIDITY,
                tags.DOMAIN_PLACES,
                tags.DOMAIN_PLACES_LOCALIZATION,
                tags.DOMAIN_PLACES_NAVIGATION
            ],
            'type_list': [
                tags.INTERACTIVE,
                tags.ACTION_FULL,
                tags.TRAVERSAL
            ]
        })

    # Override
    def choose_target_definition(self, target_number: int) -> Dict[str, Any]:
        return self.choose_definition()

    # Override
    def get_target_count(self) -> int:
        return 1

    # Override
    def update_goal_config(
        self,
        goal_config: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        image = find_image_for_object(target_list[0])
        image_name = find_image_name(target_list[0])
        goal_config['metadata'] = {
            'target': {
                'id': target_list[0]['id'],
                'info': target_list[0]['info'],
                'match_image': True,
                'image': image,
                'image_name': image_name
            }
        }
        goal_config['description'] = f'Find the ' \
            f'{target_list[0]["goalString"]} and move near it.'
        return goal_config

    # Override
    def validate_target_location(
        self,
        target_number: int,
        target_location: Dict[str, Any],
        previously_made_target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        distance = geometry.position_distance(
            performer_start['position'],
            target_location['position']
        )
        # Don't position too close to performer's start location.
        return distance >= geometry.MIN_OBJECTS_SEPARATION_DISTANCE

    def _find_optimal_path(
        self,
        goal_objects: List[Dict[str, Any]],
        all_objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return get_navigation_actions(
            self._performer_start, goal_objects[0], all_objects)[0]


class PathfindingException(exceptions.SceneException):
    def __init__(self, message=''):
        super(PathfindingException, self).__init__(message)
