import copy
import logging
import math
import random
from abc import ABC
from enum import Enum
from typing import Dict, Any, AnyStr, List, Tuple, Sequence

from sympy import Segment, intersection

import containers
import exceptions
import geometry
import objects
import util
from geometry import POSITION_DIGITS
from goal import GoalException, Goal, generate_wall
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


def move_to_container(target: Dict[str, Any], bounds_list: List[List[Dict[str, float]]],
                      performer_position: Dict[str, float]) -> Dict[str, Any]:
    """Try to find a random container that target will fit in. If found, set the target's locationParent, and add
    container to bounds_list. Return the container, or None if the target was not put into a container."""
    shuffled_containers = objects.get_enclosed_containers().copy()
    random.shuffle(shuffled_containers)
    for container_definition in shuffled_containers:
        container_definition = finalize_object_definition(container_definition)
        containment = containers.how_can_contain(container_definition, target)
        if containment is not None:
            # try to place the container before we accept it
            container_location = geometry.calc_obj_pos(performer_position, bounds_list, container_definition)
            if container_location is not None:
                container = instantiate_object(container_definition, container_location)
                area, angles = containment
                containers.put_object_in_container(target, container, container_definition, area, angles[0])
                return container
    return None


class ObjectRule():
    """Defines rules for how a specific object can be made and positioned as part of a specific goal."""

    def __init__(self, position_in_receptacle = False, position_on_receptacle = False):
        self.position_in_receptacle = position_in_receptacle
        self.position_on_receptacle = position_on_receptacle

    def choose_definition(self) -> Dict[str, Any]:
        """Choose and return an object definition."""
        # Same chance to pick each list.
        object_definition_list = random.choice(
            [objects.OBJECTS_PICKUPABLE, objects.OBJECTS_MOVEABLE, objects.OBJECTS_IMMOBILE]
        )
        # Same chance to pick each object definition from the list.
        return finalize_object_definition(random.choice(object_definition_list))

    def choose_location(self, object_definition: Dict[str, Any], performer_start: Dict[str, Dict[str, float]], \
            bounds_list: List[List[Dict[str, float]]]) -> Tuple[Dict[str, Any], List[List[Dict[str, float]]]]:
        """Choose and return the location for the given object definition. Will modify bounds_list."""
        object_location = geometry.calc_obj_pos(performer_start['position'], bounds_list, object_definition)
        if not object_location:
            raise GoalException(f'cannot position object (type={object_definition["type"]})')
        return object_location, bounds_list

    def validate_location(self, object_location: Dict[str, Any], target_list: List[Dict[str, Any]], \
            performer_start: Dict[str, Dict[str, float]]) -> bool:
        """Returns if the given object location is valid."""
        return True


class PickupableObjectRule(ObjectRule):
    def __init__(self, position_in_receptacle = False, position_on_receptacle = False):
        super(PickupableObjectRule, self).__init__(position_in_receptacle, position_on_receptacle)

    def choose_definition(self) -> Dict[str, Any]:
        object_definition_list = random.choice(objects.OBJECTS_PICKUPABLE_LISTS)
        return finalize_object_definition(random.choice(object_definition_list))


class TransferToObjectRule(ObjectRule):
    def __init__(self, position_in_receptacle = False, position_on_receptacle = False):
        super(TransferToObjectRule, self).__init__(position_in_receptacle, position_on_receptacle)

    def choose_definition(self) -> Dict[str, Any]:
        stack_targets_pickupable = [definition for definition in objects.OBJECTS_PICKUPABLE \
                if 'stackTarget' in definition.get('attributes', [])]
        stack_targets_moveable = [definition for definition in objects.OBJECTS_MOVEABLE \
                if 'stackTarget' in definition.get('attributes', [])]
        stack_targets_immobile = [definition for definition in objects.OBJECTS_IMMOBILE \
                if 'stackTarget' in definition.get('attributes', [])]

        choice_list = []
        if len(stack_targets_pickupable) > 0:
            choice_list.append(stack_targets_pickupable)
        if len(stack_targets_moveable) > 0:
            choice_list.append(stack_targets_moveable)
        if len(stack_targets_immobile) > 0:
            choice_list.append(stack_targets_immobile)

        if len(choice_list) == 0:
            raise exceptions.SceneException('cannot find any stack target definition')

        # Same chance to pick each list.
        object_definition_list = random.choice(choice_list)
        # Same chance to pick each object definition from the list.
        return finalize_object_definition(random.choice(object_definition_list))

    def validate_location(self, object_location: Dict[str, Any], target_list: List[Dict[str, Any]], \
            performer_start: Dict[str, Dict[str, float]]) -> bool:

        if len(target_list) == 0:
            raise exceptions.SceneException('cannot find existing target to transfer')

        target_1_position = target_list[0]['shows'][0]['position']

        distance = geometry.position_distance(target_1_position, object_location['position'])

        # Cannot be positioned too close to the existing target object.
        return distance >= geometry.MINIMUM_TARGET_SEPARATION


class FarOffObjectRule(ObjectRule):
    def __init__(self, position_in_receptacle = False, position_on_receptacle = False):
        super(FarOffObjectRule, self).__init__(position_in_receptacle, position_on_receptacle)

    def validate_location(self, object_location: Dict[str, Any], target_list: List[Dict[str, Any]], \
            performer_start: Dict[str, Dict[str, float]]) -> bool:

        distance = geometry.position_distance(performer_start['position'], object_location['position'])

        # Cannot be positioned too close to the performer.
        return distance >= geometry.MINIMUM_START_DIST_FROM_TARGET


class DistractorObjectRule(ObjectRule):
    def __init__(self, target_list: List[Dict[str, Any]], position_in_receptacle = False, \
            position_on_receptacle = False):
        super(DistractorObjectRule, self).__init__(position_in_receptacle, position_on_receptacle)
        self._target_list = target_list

    def choose_definition(self) -> Dict[str, Any]:
        target_shape_list = [target['info'][-1] for target in self._target_list]
        for _ in range(util.MAX_TRIES):
            distractor_definition = super(DistractorObjectRule, self).choose_definition()
            distractor_shape = distractor_definition['info'][-1]
            # Cannot have the same shape as a target object, so we don't unintentionally generate a confusor.
            if distractor_shape not in target_shape_list:
                break
            distractor_definition = None
        return distractor_definition


class ConfusorObjectRule(ObjectRule):
    def __init__(self, target_definition: Dict[str, Any]):
        super(ConfusorObjectRule, self).__init__()
        self._target_definition = target_definition

    def choose_definition(self) -> Dict[str, Any]:
        if not self._target_definition:
            raise exceptions.SceneException('cannot create a confusor with no target definition')
        confusor_definition = util.get_similar_definition(self._target_definition, objects.get_all_object_defs())
        if not confusor_definition:
            raise exceptions.SceneException(f'cannot find a confusor to create with target={self._target_definition}')
        return util.finalize_object_definition(confusor_definition)


class ObstructorObjectRule(ObjectRule):
    def __init__(self, target_definition: Dict[str, Any], performer_start: Dict[str, Dict[str, float]], \
            obstruct_vision: bool = False):
        super(ObstructorObjectRule, self).__init__()
        self._target_definition = target_definition
        self._obstruct_vision = obstruct_vision

    def choose_definition(self) -> Dict[str, Any]:
        if not self._target_definition:
            raise exceptions.SceneException('cannot create an obstructor with no target definition')
        obstructor_definition_list = geometry.get_wider_and_taller_defs(self._target_definition) if \
                self._obstruct_vision else [] # TODO MCS-262
        if not obstructor_definition_list:
            raise exceptions.SceneException(f'cannot find an obstructor to create with target={self._target_definition}')
        obstructor_definition, obstructor_angle = random.choice(obstructor_definition_list)
        obstructor_definition = util.finalize_object_definition(obstructor_definition)
        if not 'rotation' in obstructor_definition:
            obstructor_definition['rotation'] = {
                'x': 0,
                'y': 0,
                'z': 0
            }
        # Note that this rotation must be also modified with the final performer start Y.
        obstructor_definition['rotation']['y'] += obstructor_angle
        return obstructor_definition


class InteractionGoal(Goal, ABC):
    LAST_STEP = 600
    # MAX_DISTRACTORS doesn't count the receptacles randomly generated to containerize other objects.
    MAX_DISTRACTORS = 10
    OBJECT_RECEPTACLE_CHANCE = 0.333
    WALL_CHOICES = [0, 1, 2, 3]
    WALL_WEIGHTS = [40, 30, 20, 10]

    def __init__(self, target_rule_list: List[ObjectRule]):
        super(InteractionGoal, self).__init__()
        self._target_rule_list = target_rule_list
        self._bounds_list = []
        self._target_list = []
        self._distractor_list = []
        self._wall_list = None
        self._is_distractor_list_done = False

    # override
    def compute_objects(self, wall_material_name: str, wall_colors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        return {
            'target': self.generate_target_list(),
            'distractor': self.generate_distractor_list(),
            'wall': self.generate_wall_list(wall_material_name, wall_colors)
        }

    def generate_distractor_list(self) -> List[Dict[str, Any]]:
        """Generates and returns the distractors in this goal."""
        if not self._is_distractor_list_done:
            # Automatically generate a random number of distractors with random parameters.
            distractor_rule_list = []
            for _ in range(random.randint(0, InteractionGoal.MAX_DISTRACTORS) + 1):
                distractor_rule_list.append(self.get_distractor_rule(position_in_receptacle = \
                        (random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE)))
            self.__generate_object_list(self._distractor_list, distractor_rule_list, self._target_list, \
                    self._distractor_list)
            self._is_distractor_list_done = True
        return self._distractor_list

    def generate_target_list(self, end_index: int = None) -> List[Dict[str, Any]]:
        """Generates and returns the targets in this goal (or up to the end_index, if given)."""
        # Only generate each target up to the given end_index, or generate all targets if no end_index was given.
        end_index_to_generate = (end_index if end_index is not None else len(self._target_rule_list))
        if len(self._target_list) < end_index_to_generate:
            # Keep all existing targets; only generate new targets that don't yet exist.
            incomplete_target_rule_list = self._target_rule_list[len(self._target_list):end_index_to_generate]
            self.__generate_object_list(self._target_list, incomplete_target_rule_list, self._target_list, \
                    self._distractor_list)
        return self._target_list

    def generate_wall_list(self, wall_material_name: str, wall_colors: List[str]) -> List[Dict[str, Any]]:
        """Generates and returns the walls (other than the room's starting walls) in this goal."""
        if self._wall_list is None:
            self._wall_list = []
            for _ in range(random.choices(InteractionGoal.WALL_CHOICES, weights=InteractionGoal.WALL_WEIGHTS, k=1)[0]):
                wall = generate_wall(wall_material_name, wall_colors, self._performer_start['position'], \
                        self._bounds_list)
                if wall:
                    self._wall_list.append(wall)
                    self._bounds_list.append(wall['shows'][0]['bounding_box'])
                else:
                    logging.warning('cannot generate a dynamic wall object')
        return self._wall_list

    def get_bounds_list(self) -> List[List[Dict[str, float]]]:
        """Returns the bounding rectangles of all objects in this goal."""
        return self._bounds_list

    def get_confusor_rule(self, target_definition: Dict[str, Any]) -> ObjectRule:
        """Returns the rule for any confusors compatible with this goal."""
        return ConfusorObjectRule(target_definition = target_definition)

    def get_distractor_list(self) -> List[Dict[str, Any]]:
        """Returns the distractors in this goal."""
        return self._distractor_list

    def get_distractor_rule(self, target_list: List[Dict[str, Any]] = None, position_in_receptacle: bool = False) -> \
            ObjectRule:
        """Returns the rule for any distractors compatible with this goal."""
        return DistractorObjectRule(target_list = (target_list if target_list is not None else self._target_list), \
                position_in_receptacle = position_in_receptacle)

    def get_obstructor_rule(self, target_definition: Dict[str, Any], obstruct_vision: bool = False) -> ObjectRule:
        """Returns the rule for any obstructors compatible with this goal."""
        return ObstructorObjectRule(target_definition = target_definition, obstruct_vision = obstruct_vision, \
                performer_start = self.get_performer_start())

    def get_target_list(self) -> List[Dict[str, Any]]:
        """Returns the targets in this goal."""
        return self._target_list

    def get_target_rule_list(self) -> List[ObjectRule]:
        """Returns the rules for the targets associated with this goal."""
        return self._target_rule_list

    def __generate_object_list(self, object_list: List[Dict[str, Any]], rule_list: List[ObjectRule], \
            target_list: List[Dict[str, Any]], distractor_list: List[Dict[str, Any]]) -> None:
        """Generates new objects using the given rule_list and saves them in the given object_list. Will modify the
        given distractor_list and self._bounds_list"""

        for rule in rule_list:
            object_definition = rule.choose_definition()
            for _ in range(util.MAX_TRIES):
                object_location, bounds_list_modified = rule.choose_location(object_definition, \
                        self._performer_start, self._bounds_list)
                if rule.validate_location(object_location, target_list, self._performer_start):
                    break
                object_location = None
            if not object_location:
                raise exceptions.SceneException('cannot find a suitable object location')
            self._bounds_list = bounds_list_modified
            object_instance = instantiate_object(object_definition, object_location)
            object_list.append(object_instance)
            receptacle_instance = None
            if rule.position_in_receptacle:
                receptacle_instance = self.__move_into_receptacle(object_instance, self._performer_start, \
                        self._bounds_list)
            if rule.position_on_receptacle:
                receptacle_instance = self.__move_onto_receptacle(object_instance, self._performer_start, \
                        self._bounds_list)
            if receptacle_instance:
                distractor_list.append(receptacle_instance)

    def __move_into_receptacle(self, object_instance: Dict[str, Any], performer_start: Dict[str, Dict[str, float]], \
            bounds_list: List[List[Dict[str, float]]]) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object into the new receptacle. Will modify
        bounds_list."""
        receptacle = None
        # Only a pickupable object can be positioned inside a receptacle.
        if object_instance.get('pickupable', False):
            # Receptacles that can have objects positioned inside them are sometimes called "containers"
            receptacle = move_to_container(object_instance, bounds_list, performer_start['position'])
        return receptacle

    def __move_onto_receptacle(self, object_instance: Dict[str, Any], performer_start: Dict[str, Dict[str, float]], \
            bounds_list: List[List[Dict[str, float]]]) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object onto the new receptacle. Will modify
        bounds_list."""
        # TODO MCS-146 Position objects on top of receptacles.
        return None


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
        super(RetrievalGoal, self).__init__(target_rule_list = [
            PickupableObjectRule(
                position_in_receptacle = (random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE)
            )
        ])

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 1:
            raise exceptions.SceneException('need at least 1 object for this goal')

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

    def _find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
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
        super(TransferralGoal, self).__init__(target_rule_list = [
            PickupableObjectRule(
                position_in_receptacle = (random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE)
            ),
            TransferToObjectRule()
        ])

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 2:
            raise exceptions.SceneException(f'need at least 2 objects for this goal, was given {len(goal_objects)}')
        target1, target2 = goal_objects[0:2]
        if not target1.get('pickupable', False):
            raise exceptions.SceneException(f'first object must be "pickupable": {target1}')
        if not target2.get('stackTarget', False):
            raise exceptions.SceneException(f'second object must be "stackTarget": {target2}')
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

    def _find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
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


class TraversalGoal(InteractionGoal):
    """Locating and navigating to a specified object."""

    TEMPLATE = {
        'category': 'traversal',
        'domain_list': ['objects', 'places', 'object_solidity', 'navigation', 'localization'],
        'type_list': ['interactive', 'action_full', 'traversal'],
        'task_list': ['navigate', 'localize', 'identify'],
        'last_step': InteractionGoal.LAST_STEP
    }

    def __init__(self):
        super(TraversalGoal, self).__init__(target_rule_list = [
            FarOffObjectRule(
                position_in_receptacle = (random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE)
            )
        ])

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(goal_objects) < 1:
            raise exceptions.SceneException('need at least 1 object for this goal')

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

    def _find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        # Goal should be a singleton... I hope
        # TODO: (maybe) look at actual object if it's inside a parent (future ticket)
        return get_navigation_actions(self._performer_start, goal_objects[0], all_objects)[0]

