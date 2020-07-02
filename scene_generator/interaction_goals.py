import copy
import logging
import math
import random
from abc import ABC
from enum import Enum
from typing import Dict, Any, AnyStr, List, Tuple, Sequence

from sympy import Segment, intersection

import containers
import geometry
import objects
import util
from geometry import POSITION_DIGITS
from goal import GoalException, Goal
from machine_common_sense.mcs_controller_ai2thor import MAX_MOVE_DISTANCE, MAX_REACH_DISTANCE, PERFORMER_CAMERA_Y
from optimal_path import generatepath
from util import finalize_object_definition, instantiate_object


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


def parse_path_section(path_section: Sequence[Sequence[float]],
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

    # IF my calculations are correct, this should be right no matter what
    # I'm assuming a positive angle is a clockwise rotation- so this should work
    # I think

    delta_t = (current_heading-theta) % 360
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
        "params": {
            "amount": 1
        }
    }] * int(whole))

    rounded_frac = round(frac, POSITION_DIGITS)
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
    current_heading = 90 - start_location['rotation']['y']
    for indx in range(len(path)-1):
        new_actions, current_heading, performer = parse_path_section(path[indx:indx+2], current_heading, performer, goal_boundary)
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
    total_distance = math.sqrt((performer[0] - goal_position['x'])**2 + (performer[1] - goal_position['z'])**2)

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
    new_actions = actions[:i+1]
    new_x = performer[0] - dist_moved * math.cos(math.radians(heading))
    new_z = performer[1] - dist_moved * math.sin(math.radians(heading))
    return new_actions, (new_x, new_z)


def move_to_container(target: Dict[str, Any], bounding_rectangles: List[List[Dict[str, float]]],
                      performer_position: Dict[str, float]) -> Dict[str, Any]:
    """Try to find a random container that target will fit in. If found, set the target's locationParent, and add
    container to bounding_rectangles. Return the container, or None if the target was not put into a container."""
    shuffled_containers = objects.get_enclosed_containers().copy()
    random.shuffle(shuffled_containers)
    for container_definition in shuffled_containers:
        container_definition = finalize_object_definition(container_definition)
        containment = containers.how_can_contain(container_definition, target)
        if containment is not None:
            # try to place the container before we accept it
            container_location = geometry.calc_obj_pos(performer_position, bounding_rectangles, container_definition)
            if container_location is not None:
                container = instantiate_object(container_definition, container_location)
                area, angles = containment
                containers.put_object_in_container(target, container, container_definition, area, angles[0])
                return container
    return None


class InteractionGoal(Goal, ABC):
    LAST_STEP = 600
    MAX_DISTRACTORS = 10
    OBJECT_RECEPTACLE_CHANCE = 0.5

    def __init__(self, choose_target_definition):
        super(InteractionGoal, self).__init__()
        self._bounding_rects = []

    def _choose_distractor_definition(self) -> Dict[str, Any]:
        """Choose and return an object definition for a distractor object."""
        target_shape_list = [target['info'][-1] for target in self._targets]
        while True:
            distractor_definition = self._choose_object_definition()
            distractor_shape = distractor_definition['info'][-1]
            if distractor_shape not in target_shape_list:
                break
        return distraction_definition

    def _choose_object_definition(self) -> Dict[str, Any]:
        """Choose and return an object definition."""
        object_definition_list = random.choices(
            [objects.OBJECTS_PICKUPABLE, objects.OBJECTS_MOVEABLE, objects.OBJECTS_IMMOBILE],
            [50, 25, 25]
        )[0]
        return finalize_object_definition(random.choice(object_definition_list))

    def _choose_target_definition(self, index: int) -> Dict[str, Any]:
        """Choose and return an object definition for a target object at the given index."""
        if index == 0:
            object_definition_list = random.choice(objects.OBJECTS_PICKUPABLE_LISTS)
            return finalize_object_definition(random.choice(object_definition_list))
        return self._choose_object_definition()

    def _generate_targets(self) -> List[Dict[str, Any]]:
        """Returns a list of one or more target objects required for the goal. Will update _bounding_rects."""
        target_definition = self._choose_target_definition(0)
        target_location = geometry.calc_obj_pos(self._performer_start['position'], self._bounding_rects, \
                target_definition)
        if target_location is None:
            raise GoalException(f'could not place target object (type={target_definition["type"]})')
        target = instantiate_object(target_definition, target_location)
        return [target]

    def _generate_distractors(self) -> List[Dict[str, Any]]:
        """Returns a list of zero or more random distractors. Will update _bounding_rects."""
        distractor_count = random.randint(0, MAX_DISTRACTORS)
        distractor_list = []
        while len(distractor_list) < distractor_count:
            distractor_definition = self._choose_distractor_definition()
            distractor_location = geometry.calc_obj_pos(self._performer_start['position'], self._bounding_rects, \
                    distractor_definition)
            if distractor_location is not None:
                distractor = util.instantiate_object(distractor_definition, distractor_location)
                distractor_list.append(distractor)
                if random.random() <= OBJECT_RECEPTACLE_CHANCE and distractor.get('pickupable', False)
                    container = move_to_container(distractor, self._bounding_rects, self._performer_start['position'])
                    if container:
                        distractor_list.append(container)

    def compute_objects(self, room_wall_material_name: str) -> \
            Tuple[Dict[str, List[Dict[str, Any]]], List[List[Dict[str, float]]]]:

        target_list = self._generate_targets()
        distractor_list = self._generate_distractors()
        for target in target_list:
            if random.random() <= OBJECT_RECEPTACLE_CHANCE and target.get('pickupable', False):
                container = move_to_container(target, self._bounding_rects, self._performer_start['position'])
                if container:
                    distractor_list.append(container)

        return {
            'target': target_list,
            'distractor': distractor_list
        }, self._bounding_rects


class RetrievalGoal(InteractionGoal):
    """Going to a specified object and picking it up."""

    TEMPLATE = {
        'category': 'retrieval',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interactive', 'action_full', 'retrieval'],
        'task_list': ['navigate', 'localize', 'identify', 'retrieve'],
        'last_step': InteractionGoal.LAST_STEP
    }

    def __init__(self):
        super(RetrievalGoal, self).__init__()

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 1:
            raise ValueError('need at least 1 object for this goal')

        target = goal_objects[0]
        target_image_obj = find_image_for_object(target)
        image_name = find_image_name(target)

        goal: Dict[str, Any] = copy.deepcopy(self.TEMPLATE)
        goal['metadata'] = {
            'target': {
                'id': target['id'],
                'info': target['info'],
                'match_image': True,
                'image': target_image_obj,
                'image_name': image_name
            }
        }
        goal['description'] = f'Find and pick up the {target["info_string"]}.'
        return goal

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        actions, performer, heading = get_navigation_actions(self._performer_start, goal_objects[0], all_objects)
        actions, performer = trim_actions_to_reach(actions, performer, heading, goal_objects[0])

        # Do I have to look down to see the object????
        plane_dist = math.sqrt((goal_objects[0]['shows'][0]['position']['x'] - performer[0]) ** 2 +
                               (goal_objects[0]['shows'][0]['position']['z'] - performer[1]) ** 2)
        height_dist = PERFORMER_CAMERA_Y - goal_objects[0]['shows'][0]['position']['y']
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
        'type_list': ['interactive', 'action_full', 'transferral'],
        'task_list': ['navigate', 'localize', 'identify', 'retrieve', 'transfer'],
        'last_step': InteractionGoal.LAST_STEP
    }

    def __init__(self):
        super(TransferralGoal, self).__init__()

    def _generate_targets(self) -> List[Dict[str, Any]]:
        target_list = super(InteractionGoal, self)._generate_targets()
        target1 = target_list[0]
        object_definition_list = objects.get_all_object_defs()
        random.shuffle(object_definition_list)
        target2_defintion = next((definition for definition in object_definition_list \
                if 'stackTarget' in definition.get('attributes', [])), None)
        if target2_defintion is None:
            raise ValueError(f'No stack target definitions found for transferral goal')
        # ensure the targets aren't too close together
        while True:
            bounding_rectangles = self._bounding_rects.copy()
            target2_location = geometry.calc_obj_pos(self._performer_start['position'],
                                                     bounding_rectangles, target2_defintion)
            distance = geometry.position_distance(target1['shows'][0]['position'],
                                                  target2_location['position'])
            if distance >= geometry.MINIMUM_TARGET_SEPARATION:
                break
        self._bounding_rects = bounding_rectangles
        target2 = instantiate_object(target2_defintion, target2_location)
        return target_list + [target2]

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 2:
            raise ValueError(f'need at least 2 objects for this goal, was given {len(goal_objects)}')
        target1, target2 = goal_objects[0:2]
        if not target1.get('pickupable', False):
            raise ValueError(f'first object must be "pickupable": {target1}')
        if not target2.get('stackTarget', False):
            raise ValueError(f'second object must be "stackTarget": {target2}')
        relationship = random.choice(list(self.RelationshipType))

        target1_image_obj = find_image_for_object(target1)
        target2_image_obj = find_image_for_object(target2)

        image_name1 = find_image_name(target1)
        image_name2 = find_image_name(target2)

        goal: Dict[str, Any] = copy.deepcopy(self.TEMPLATE)
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
        goal['description'] = f'Find and pick up the {target1["info_string"]} and move it {relationship.value} ' \
            f'the {target2["info_string"]}.'
        return goal

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        actions, performer, heading = get_navigation_actions(self._performer_start,
                                                             goal_objects[0],
                                                             all_objects)
        actions, performer = trim_actions_to_reach(actions, performer, heading, goal_objects[0])

        # Do I have to look down to see the object????
        plane_dist = math.sqrt((goal_objects[0]['shows'][0]['position']['x'] - performer[0]) ** 2 +
                               (goal_objects[0]['shows'][0]['position']['z'] - performer[1]) ** 2)
        height_dist = PERFORMER_CAMERA_Y-goal_objects[0]['shows'][0]['position']['y']
        elevation = math.degrees(math.atan2(height_dist, plane_dist))
        if abs(elevation) > 30:
            actions.append({
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
            actions.append({
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
            if object['id'] == goal_objects[1]['id']:
                goal_boundary = object['shows'][0]['bounding_box']
                break
        current_heading = heading
        for indx in range(len(path)-1):
            new_actions, current_heading, performer = parse_path_section(path[indx:indx+2], current_heading, performer, goal_boundary)
            actions.extend(new_actions)

        actions, performer = trim_actions_to_reach(actions, performer, current_heading, goal_objects[1])

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
        'type_list': ['interactive', 'action_full', 'traversal'],
        'task_list': ['navigate', 'localize', 'identify'],
        'last_step': InteractionGoal.LAST_STEP
    }

    def __init__(self):
        super(TraversalGoal, self).__init__()

    def _generate_targets(self) -> List[Dict[str, Any]]:
        target_definition = self._choose_object_definition()
        while True:
            bounding_rectangles = self._bounding_rects.copy()
            target_location = geometry.calc_obj_pos(self._performer_start['position'], bounding_rectangles, \
                    target_definition)
            if target_location is None:
                raise GoalException(f'could not place target object (type={target_definition["type"]})')
            distance = geometry.position_distance(performer_start['position'],
                                                  target_location['position'])
            if distance >= geometry.MINIMUM_START_DIST_FROM_TARGET:
                break
        self._bounding_rects = bounding_rectangles
        target = instantiate_object(target_definition, target_location)
        return [target]

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 1:
            raise ValueError('need at least 1 object for this goal')

        target = goal_objects[0]
        target_image_obj = find_image_for_object(target)
        image_name = find_image_name(target)

        goal: Dict[str, Any] = copy.deepcopy(self.TEMPLATE)
        goal['metadata'] = {
            'target': {
                'id': target['id'],
                'info': target['info'],
                'match_image': True,
                'image': target_image_obj,
                'image_name': image_name
            }
        }
        goal['description'] = f'Find the {target["info_string"]} and move near it.'
        return goal

    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        # TODO: (maybe) look at actual object if it's inside a parent (future ticket)
        return get_navigation_actions(self._performer_start, goal_objects[0], all_objects)[0]

