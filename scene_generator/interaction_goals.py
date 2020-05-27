import copy
import logging
from abc import ABC
from enum import Enum
import random

import math
from typing import Dict, Any, AnyStr, List, Tuple, Sequence

from sympy import Segment, intersection

from machine_common_sense.mcs_controller_ai2thor import MAX_MOVE_DISTANCE, PERFORMER_CAMERA_Y

import geometry
import objects
from geometry import POSITION_DIGITS
from goal import GoalException, Goal
from optimal_path import generatepath
from util import finalize_object_definition, instantiate_object


def set_enclosed_info(goal: Dict[str, Any], *targets: Dict[str, Any]) -> None:
    """If any target is in an enclosed area, add 'target_enclosed' to the
    'type_list' of the goal. If any target isn't in an enclosed area,
    add 'target_not_enclosed'.
    """
    type_list = goal['type_list']
    for target in targets:
        enclosed_string = 'target_not_enclosed' if target.get('locationParent', None) is None else 'target_enclosed'
        if enclosed_string not in type_list:
            type_list.append(enclosed_string)


def generate_image_file_name(target: Dict[str, Any]) -> str:
    if 'materials' not in target:
        return target['type']

    material_name_list = [item[(item.rfind('/') + 1):].lower().replace(' ', '_') for item in target['materials']]
    return target['type'] + ('_' if len(material_name_list) > 0 else '') + ('_'.join(material_name_list))


def find_image_for_object(object_def: Dict[str, Any]) -> AnyStr:
    image_file_name = ""

    try:
        image_file_name = 'images/' + generate_image_file_name(object_def) + '.txt'

        with open(image_file_name, 'r') as image_file:
            target_image = image_file.read()
            
        return target_image
    except: 
        logging.warning('Image object could not be found, make sure you generated the image: ' + image_file_name)


def find_image_name(target: Dict[str, Any]) -> str:
    return generate_image_file_name(target) + '.png'


def parse_path_section(path_section: List[Sequence[float]],
                       current_heading: float,
                       performer: Tuple[float, float],
                       goal_boundary: List[Dict[str, float]]) -> \
                       Tuple[List[Dict[str, Any]], float, Tuple[float, float]]:
    """Compute the actions for one path section, starting with
    current_heading. Returns a tuple: (list of actions, new heading, performer position)"""
    actions = []
    dx = path_section[1][0]-performer[0]
    dz = path_section[1][1]-performer[1]
    theta = math.degrees(math.atan2(dz, dx))

        #IF my calculations are correct, this should be right no matter what
        # I'm assuming a positive angle is a clockwise rotation- so this should work
        #I think

    delta_t = (current_heading-theta) % 360
    current_heading = theta
    if delta_t != 0:
        action = {
            'action': 'RotateLook',
            'params': {
                'rotation': round(delta_t,0),
                'horizon': 0.0
            }
        }
        actions.append(action)

    goal_center = (path_section[1][0],path_section[1][1])
    performer_seg = Segment(performer, goal_center)
    distance = None

    for indx in range(len(goal_boundary)):
        intersect_point = intersection(performer_seg, Segment((goal_boundary[indx-1]['x'],goal_boundary[indx-1]['z']),
                                                              (goal_boundary[indx]['x'],goal_boundary[indx]['z'] )))
        if intersect_point:
            distance = float(intersect_point[0].distance(performer))
            break

    if distance is None:
        distance = math.sqrt( dx ** 2 + dz ** 2 )
    frac, whole = math.modf(distance / MAX_MOVE_DISTANCE)
    actions.extend([{
        "action": "MoveAhead",
        "params": {}
    }] * int(whole))

    rounded_frac = round(frac, POSITION_DIGITS)
    if rounded_frac == 1.0:
        actions.append({
            "action": "MoveAhead",
            "params": {}
        })
    elif rounded_frac > 0:
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
                           Tuple[List[Dict[str, Any]], Tuple[float, float]]:
    """Get the action sequence for going from performer start to the
    goal_object. Returns tuple (action_list, performer end position)."""
    performer = (start_location['position']['x'], start_location['position']['z'])
    if 'locationParent' in goal_object:
        parent = next((obj for obj in all_objects if obj['id'] == goal_object['locationParent']), None)
        if parent is None:
            raise GoalException(f'object {goal_object["id"]} has parent {goal_object["locationParent"]} that does not exist')
        goal_object = parent
    goal = (goal_object['shows'][0]['position']['x'], goal_object['shows'][0]['position']['z'])
    hole_rects = []

    hole_rects.extend(object['shows'][0]['bounding_box'] for object
                      in all_objects if object['id'] != goal_object['id']
                      and 'locationParent' not in object)
    path = generatepath(performer, goal, hole_rects)
    if path is None:
        raise GoalException(f'could not find path to target {goal_object["id"]}')
    for object in all_objects:
        if object['id'] == goal_object['id']:
            goal_boundary = object['shows'][0]['bounding_box']
            break
    actions = []
    current_heading = start_location['rotation']['y']
    for indx in range(len(path)-1):
        new_actions, current_heading, performer = parse_path_section(path[indx:indx+2], current_heading, performer, goal_boundary)
        actions.extend(new_actions)

    return actions, performer


def move_to_container(target: Dict[str, Any], all_objects: List[Dict[str, Any]],
                      bounding_rects: List[List[Dict[str, float]]], performer_position: Dict[str, float]) -> bool:
    """Try to find a random container that target will fit in. If found, set the target's locationParent, and add
    container to all_objects (and bounding_rects). Return True iff the target was put in a container."""
    shuffled_containers = objects.get_enclosed_containers().copy()
    random.shuffle(shuffled_containers)
    for container_def in shuffled_containers:
        container_def = finalize_object_definition(container_def)
        area_index = geometry.can_contain(container_def, target)
        if area_index is not None:
            # try to place the container before we accept it
            container_location = geometry.calc_obj_pos(performer_position, bounding_rects, container_def)
            if container_location is not None:
                found_container = instantiate_object(container_def, container_location)
                found_area = container_def['enclosed_areas'][area_index]
                all_objects.append(found_container)
                target['locationParent'] = found_container['id']
                target['shows'][0]['position'] = found_area['position'].copy()
                if 'rotation' not in target['shows'][0]:
                    target['shows'][0]['rotation'] = geometry.ORIGIN.copy()
                return True
    return False


class InteractionGoal(Goal, ABC):
    TARGET_CONTAINED_CHANCE = 0.25
    """Chance that the target will be in a container"""
    OBJECT_CONTAINED_CHANCE = 0.5
    """Chance that, if the target is in a container, a non-target pickupable object in the scene will be, too."""

    def __init__(self):
        super(InteractionGoal, self).__init__()
        self._bounding_rects = []

    def _set_performer_start(self) -> None:
        self._performer_start = self.compute_performer_start()

    def _set_target_def(self) -> None:
        """Chooses a pickupable object since most interaction goals require that."""
        pickupable_defs = random.choice(objects.OBJECTS_PICKUPABLE_LISTS)
        self._target_def = finalize_object_definition(random.choice(pickupable_defs))

    def _set_target_location(self) -> None:
        performer_position = self._performer_start['position']
        self._target_location = geometry.calc_obj_pos(performer_position, self._bounding_rects, self._target_def)
        if self._target_location is None:
            raise GoalException(f'could not place target object (type={self._target_def["type"]})')

    def _set_goal_objects(self) -> None:
        """Set all objects required for the goal other than the target, if any. May update _bounding_rects."""
        self._goal_objects = []

    def add_objects(self, all_objects: List[Dict[str, Any]], bounding_rects: List[List[Dict[str, float]]],
                    performer_position: Dict[str, float]) -> None:
        """Maybe add a container and put the target inside it. If so, maybe put other objects in other objects, too."""
        if random.random() <= self.TARGET_CONTAINED_CHANCE:
            if move_to_container(self._target, all_objects, bounding_rects, performer_position):
                # maybe do it with other objects, too
                super(InteractionGoal, self).add_objects(all_objects, bounding_rects, performer_position)
                for obj in all_objects:
                    if obj != self._target and obj.get('pickupable', False) \
                            and random.random() <= self.OBJECT_CONTAINED_CHANCE:
                        move_to_container(obj, all_objects, bounding_rects, performer_position)

    def compute_objects(self, wall_material_name: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[List[Dict[str, float]]]]:
        self._set_performer_start()
        self._set_target_def()
        self._set_target_location()
        self._target = instantiate_object(self._target_def, self._target_location)
        self._set_goal_objects()
        
        all_objects = [self._target] + self._goal_objects
        all_goal_objects = all_objects.copy()
        self.add_objects(all_objects, self._bounding_rects, self._performer_start['position'])

        return all_goal_objects, all_objects, self._bounding_rects


class RetrievalGoal(InteractionGoal):
    """Going to a specified object and picking it up."""

    TEMPLATE = {
        'category': 'retrieval',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interaction', 'action_full', 'retrieve'],
        'task_list': ['navigate', 'localize', 'retrieve'],
    }

    def __init__(self):
        super(RetrievalGoal, self).__init__()

    def get_config(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 1:
            raise ValueError('need at least 1 object for this goal')

        target = goal_objects[0]
        self._target = target
        self._targets.append(target)
        target_image_obj = find_image_for_object(target)
        image_name = find_image_name(target)

        goal = copy.deepcopy(self.TEMPLATE)
        set_enclosed_info(goal, target)
        goal['metadata'] = {
            'target': {
                'id': target['id'],
                'info': target['info'],
                'match_image': True,
                'image': target_image_obj,
                'image_name': image_name
            }
        }
        goal['description'] = f'Find and pick up the {target["info"][-1]}.'
        self._update_goal_info_list(goal, all_objects)
        return goal

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        actions, performer = get_navigation_actions(self._performer_start, goal_objects[0], all_objects)

        # Do I have to look down to see the object????
        plane_dist = math.sqrt((goal_objects[0]['shows'][0]['position']['x'] - performer[0]) ** 2 +
                               (goal_objects[0]['shows'][0]['position']['z'] - performer[1]) ** 2)
        height_dist = PERFORMER_CAMERA_Y - goal_objects[0]['shows'][0]['position']['y']
        print(f'plane_dist={plane_dist}\theight_dist={height_dist}')              
        elevation = math.degrees(math.atan2(height_dist, plane_dist))
        if abs(elevation) > 30:
            actions.append({
                'action': 'RotateLook',
                'params': {
                    'rotation': 0,
                    'horizon': round(elevation,0)
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
                    'horizon': -1*round(elevation, 0)
                    }
                })
        return actions
        

class TransferralGoal(InteractionGoal):
    """Moving a specified object to another specified object."""

    class RelationshipType(Enum):
        NEXT_TO = 'next to'
        ON_TOP_OF = 'on top of'

    TEMPLATE = {
        'category': 'transferral',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interaction', 'identification', 'objects', 'places'],
        'task_list': ['navigation', 'identification', 'transportation']
    }

    def __init__(self):
        super(TransferralGoal, self).__init__()

    def _set_goal_objects(self) -> None:
        targets = objects.get_all_object_defs()
        random.shuffle(targets)
        target2_def = next((tgt for tgt in targets if 'stackTarget' in tgt.get('attributes', [])), None)
        if target2_def is None:
            raise ValueError(f'No stack targets found for transferral goal')
        target2_location = geometry.calc_obj_pos(self._performer_start['position'], self._bounding_rects, target2_def)
        target2 = instantiate_object(target2_def, target2_location)
        self._goal_objects = [target2]

    def get_config(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 2:
            raise ValueError(f'need at least 2 objects for this goal, was given {len(goal_objects)}')
        target1, target2 = goal_objects[0:2]
        if not target1.get('pickupable', False):
            raise ValueError(f'first object must be "pickupable": {target1}')
        if not target2.get('stackTarget', False):
            raise ValueError(f'second object must be "stackable": {target2}')
        relationship = random.choice(list(self.RelationshipType))

        self._targets.append([target1, target2])
        target1_image_obj = find_image_for_object(target1)
        target2_image_obj = find_image_for_object(target2)

        image_name1 = find_image_name(target1)
        image_name2 = find_image_name(target2)

        goal: Dict[str, Any] = copy.deepcopy(self.TEMPLATE)
        set_enclosed_info(goal, target1, target2)
        goal['metadata'] = {
            'target_1': {
                'id': target1['id'],
                'info': target1['info'],
                'match_image': True,
                'image': target1_image_obj,
                'image_name': image_name1
            },
            'target_2': {
                'id': target2['id'],
                'info': target2['info'],
                'match_image': True,
                'image': target2_image_obj,
                'image_name': image_name2
            },
            'relationship': ['target_1', relationship.value, 'target_2']
        }
        goal['description'] = f'Find and pick up the {target1["info"][-1]} and move it {relationship.value} ' \
            f'the {target2["info"][-1]}.'
        self._update_goal_info_list(goal, all_objects)
        return goal

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        actions, performer = get_navigation_actions(self._performer_start, goal_objects[0], all_objects)
        # Do I have to look down to see the object????
        plane_dist = math.sqrt((goal_objects[0]['shows'][0]['position']['x'] - performer[0]) ** 2 +
                               (goal_objects[0]['shows'][0]['position']['z'] - performer[1]) ** 2)
        height_dist = PERFORMER_CAMERA_Y-goal_objects[0]['shows'][0]['position']['y']
        elevation = math.degrees(math.atan2(height_dist, plane_dist))
        if abs(elevation) > 30:
            actions.append(
                 {
                'action': 'RotateLook',
                'params': {
                    'rotation': 0.0,
                    'horizon': round(elevation, POSITION_DIGITS)
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
                    'rotation': 0.0,
                    'horizon': -1*round(elevation, POSITION_DIGITS)
                    }
                })
        hole_rects = []
        hole_rects.extend(object['shows'][0]['bounding_box'] for object
                          in all_objects if (object['id'] != goal_objects[0]['id']
                                             and object['id'] != goal_objects[1]['id']
                                             and 'locationParent' not in object))
        if 'locationParent' in goal_objects[0]:
            parent = next((obj for obj in all_objects if obj['id'] == goal_objects[0]['locationParent']))
            target = (parent['shows'][0]['position']['x'], parent['shows'][0]['position']['z'])
        else:
            target = (goal_objects[0]['shows'][0]['position']['x'], goal_objects[0]['shows'][0]['position']['z'])
        goal = (goal_objects[1]['shows'][0]['position']['x'], goal_objects[1]['shows'][0]['position']['z'])
        logging.debug(f'TransferralGoal.f_o_p: target = {target}\tgoal = {goal}\tholes = {hole_rects}')
        path = generatepath(target, goal, hole_rects)
        if path is None:
            raise GoalException('could not find path from target object to goal')
        logging.debug(f'TransferralGoal.f_o_p: got path = {path}')
        for object in all_objects:
            if object['id'] == goal_objects[0]['id']:
                goal_boundary = object['shows'][0]['bounding_box']
                break
        current_heading = self._performer_start['rotation']['y']
        performer = (self._performer_start['position']['x'], self._performer_start['position']['z'])
        for indx in range(len(path)-1):
            actions, current_heading, performer = parse_path_section(path[indx:indx+2], current_heading, performer, goal_boundary)
            actions.extend(actions)

        # TODO: maybe look at receptacle part of the parent object (future ticket)
        actions.append({
            'action': 'PutObject',
            'params': {
                'objectId': goal_objects[0]['id'],
                'receptacleObjectId': goal_objects[1]['id']
                }})
  
        return actions


class TraversalGoal(Goal):
    """Locating and navigating to a specified object."""

    TEMPLATE = {
        'category': 'traversal',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interaction', 'action_full', 'traversal'],
        'task_list': ['navigate', 'localize', 'traversal'],
    }

    def __init__(self):
        super(TraversalGoal, self).__init__()

    def compute_objects(self, wall_material_name: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[List[Dict[str, float]]]]:
        # add objects we need for the goal
        target_def = self.choose_object_def()
        performer_start = self.compute_performer_start()
        performer_position = performer_start['position']
        bounding_rects = []
        target_location = geometry.calc_obj_pos(performer_position, bounding_rects, target_def)
        if target_location is None:
            raise GoalException('could not place target object')

        target = instantiate_object(target_def, target_location)
        self._targets.append(target)
        all_objects = [target]
        self.add_objects(all_objects, bounding_rects, performer_position)

        return [target], all_objects, bounding_rects

    def get_config(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 1:
            raise ValueError('need at least 1 object for this goal')

        target = goal_objects[0]

        target_image_obj = find_image_for_object(target)
        image_name = find_image_name(target)

        goal: Dict[str, Any] = copy.deepcopy(self.TEMPLATE)
        set_enclosed_info(goal, target)
        goal['metadata'] = {
            'target': {
                'id': target['id'],
                'info': target['info'],
                'match_image': True,
                'image': target_image_obj,
                'image_name': image_name
            }
        }
        goal['description'] = f'Find the {target["info"][-1]} and move near it.'
        self._update_goal_info_list(goal, all_objects)
        return goal

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        # TODO: (maybe) look at actual object if it's inside a parent (future ticket)
        return get_navigation_actions(self._performer_start, goal_objects[0], all_objects)[0]
