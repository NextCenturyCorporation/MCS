import copy
import logging
from abc import ABC
from enum import Enum, auto
import random
from typing import Dict, Any, List, Iterable, Tuple, Optional

import exceptions
import geometry
import materials
import math
import objects
import ramps
import tags
import util
from goal import Goal, GoalCategory
from util import finalize_object_definition, instantiate_object


MAX_WALL_WIDTH = 4
MIN_WALL_WIDTH = 1
WALL_Y_POS = 1.5
WALL_HEIGHT = 3
WALL_DEPTH = 0.1


class IntPhysGoal(Goal, ABC):
    """Base class for Intuitive Physics goals. Subclasses must set TEMPLATE variable (for use in get_config)."""

    PLAUSIBLE = 'plausible'
    IMPLAUSIBLE = 'implausible'

    # The 3.55 or 4.2 is the position at which the object will leave the camera's viewport, and is dependent on the
    # object's Z position (either 1.6 or 2.7). The * 1.2 is to account for the camera's perspective.
    VIEWPORT_LIMIT_NEAR = 3.55
    VIEWPORT_LIMIT_FAR = 4.2
    VIEWPORT_PERSPECTIVE_FACTOR = 1.2
    OBJECT_NEAR_Z = 1.6
    OBJECT_FAR_Z = 2.7
    MIN_OCCLUDER_SCALE = 0.25
    MAX_OCCLUDER_SCALE = 1.0
    NEAR_X_PERSPECTIVE_FACTOR = 0.9
    FAR_X_PERSPECTIVE_FACTOR = 0.8
    # In each IntPhys scene containing occluders, the first 12 steps
    # involve moving and rotating the occluders, so the action should
    # start on step 13 at the earliest. The
    # objects-moving-across-behind-occluders scenes have 60 steps, and
    # the objects-falling-down-behind-occluders scenes have 40. The
    # last 6 steps of the scene involve moving and rotating the
    # occluders again. For objects-falling-down-behind-occluders
    # scenes, we reserve 8 steps for falling, and 8 steps for
    # post-falling actions, meaning that the objects can appear and
    # begin falling anytime between steps 13 and 20, inclusive.
    EARLIEST_ACTION_START_STEP = 13
    LATEST_ACTION_FALL_DOWN_START_STEP = 20
    LAST_STEP_MOVE_ACROSS = 60
    LAST_STEP_FALL_DOWN = 40
    LAST_STEP_RAMP = 60
    LAST_STEP_RAMP_BUFFER = 20
    RAMP_DOWNWARD_FORCE = -350
    DEFAULT_TORQUE = {
        'stepBegin': 0,
        'stepEnd': 60,
        'vector': {
            'x': 0,
            'y': 0,
            'z': 0
        }
    }

    class Position(Enum):
        RIGHT_FIRST_NEAR = auto()
        RIGHT_LAST_NEAR = auto()
        RIGHT_FIRST_FAR = auto()
        RIGHT_LAST_FAR = auto()
        LEFT_FIRST_NEAR = auto()
        LEFT_LAST_NEAR = auto()
        LEFT_FIRST_FAR = auto()
        LEFT_LAST_FAR = auto()

    OBJECT_POSITIONS = {
        Position.RIGHT_FIRST_NEAR: (4.2, OBJECT_NEAR_Z),
        Position.RIGHT_LAST_NEAR: (5.3, OBJECT_NEAR_Z),
        Position.RIGHT_FIRST_FAR: (4.8, OBJECT_FAR_Z),
        Position.RIGHT_LAST_FAR: (5.9, OBJECT_FAR_Z),
        Position.LEFT_FIRST_NEAR: (-4.2, OBJECT_NEAR_Z),
        Position.LEFT_LAST_NEAR: (-5.3, OBJECT_NEAR_Z),
        Position.LEFT_FIRST_FAR: (-4.8, OBJECT_FAR_Z),
        Position.LEFT_LAST_FAR: (-5.9, OBJECT_FAR_Z)
    }

    def __init__(self, name: str):
        super(IntPhysGoal, self).__init__(name)
        self._object_creator = None
        self._object_defs = objects.get('INTPHYS')

    def _compute_performer_start(self) -> Dict[str, Dict[str, float]]:
        if self._performer_start is None:
            self._performer_start = {
                'position': {
                    'x': 0,
                    'y': 0,
                    'z': -4.5
                },
                'rotation': {
                    'y': 0
                }
            }
        return self._performer_start

    def update_body(self, body: Dict[str, Any], find_path: bool) -> Dict[str, Any]:
        body = super(IntPhysGoal, self).update_body(body, find_path)
        for obj in self._tag_to_objects['target']:
            obj['torques'] = [IntPhysGoal.DEFAULT_TORQUE]

        body['observation'] = True
        body['answer'] = {
            'choice': IntPhysGoal.PLAUSIBLE
        }
        return body

    def _find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        return []

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        goal = copy.deepcopy(self.TEMPLATE)
        goal['last_step'] = self._last_step
        goal['action_list'] = [['Pass']] * goal['last_step']
        if self._object_creator:
            if self._object_creator == IntPhysGoal._get_objects_and_occluders_moving_across:
                goal['type_list'].append(tags.INTPHYS_MOVE_ACROSS)
            elif self._object_creator == IntPhysGoal._get_objects_falling_down:
                goal['type_list'].append(tags.INTPHYS_FALL_DOWN)
        return goal

    def compute_objects(self, wall_material_name: str, wall_colors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        self._object_creator = random.choice([IntPhysGoal._get_objects_and_occluders_moving_across,
                                              IntPhysGoal._get_objects_falling_down])
        self._last_step = IntPhysGoal.LAST_STEP_FALL_DOWN
        moving_objs, occluder_objs = self._object_creator(self, wall_material_name)
        background_objs = self._compute_scenery()

        return {
            'target': [moving_objs[0]],
            'distractor': moving_objs[1:],
            'background object': background_objs,
            'occluder': occluder_objs
        }

    def _compute_scenery(self):
        MIN_VISIBLE_X = -6.5
        MAX_VISIBLE_X = 6.5
        MIN_Z = 3.25
        MAX_Z = 4.95

        def random_x():
            return util.random_real(MIN_VISIBLE_X, MAX_VISIBLE_X, util.MIN_RANDOM_INTERVAL)

        def random_z():
            # Choose values so the scenery is placed between the
            # moving IntPhys objects and the room's wall.
            return util.random_real(MIN_Z, MAX_Z, util.MIN_RANDOM_INTERVAL)

        scenery_count = random.choices((0, 1, 2, 3, 4, 5),
                                             (50, 10, 10, 10, 10, 10))[0]
        scenery_list = []
        scenery_rects = []
        scenery_defs = objects.get('MOVEABLE') + objects.get('IMMOBILE')
        for _ in range(scenery_count):
            location = None
            while location is None:
                scenery_def = finalize_object_definition(random.choice(scenery_defs))
                location = geometry.calc_obj_pos(geometry.ORIGIN, scenery_rects, scenery_def,
                                                 random_x, random_z)
                if location is not None:
                    # check that the bounds are valid
                    for point in location['boundingBox']:
                        x = point['x']
                        z = point['z']
                        if x < MIN_VISIBLE_X or x > MAX_VISIBLE_X or \
                           z < MIN_Z or z > MAX_Z:
                            # reset location so we try again
                            location = None
                            break
            scenery_obj = instantiate_object(scenery_def, location)
            scenery_list.append(scenery_obj)
        return scenery_list

    def _get_num_occluders(self) -> int:
        """Return number of occluders for the scene."""
        return random.choices((1, 2, 3, 4), (40, 20, 20, 20))[0]

    def _get_num_paired_occluders(self) -> int:
        """Return how many occluders must be paired with a target object."""
        return 1

    def _get_paired_occluder(self, paired_obj, occluder_list, non_room_wall_materials, pole_materials):
        occluder_fits = False
        for _ in range(util.MAX_TRIES):
            x_diagonal = math.sqrt(2) * paired_obj['shows'][0]['scale']['x']
            min_scale = min(max(x_diagonal,
                                IntPhysGoal.MIN_OCCLUDER_SCALE),
                            IntPhysGoal.MAX_OCCLUDER_SCALE)
            # object could be a cube on its corner, so use the diagonal distance
            x_scale = util.random_real(min_scale, IntPhysGoal.MAX_OCCLUDER_SCALE, util.MIN_RANDOM_INTERVAL)
            position_by_step = paired_obj['intphysOption']['position_by_step']
            paired_z = paired_obj['shows'][0]['position']['z']
            min_paired_x_position = -3 + x_scale / 2
            max_paired_x_position = 3 - x_scale / 2
            while True:
                position_index = random.randrange(len(position_by_step))
                paired_x = position_by_step[position_index]
                if min_paired_x_position <= paired_x <= max_paired_x_position:
                    break
            if paired_z == IntPhysGoal.OBJECT_NEAR_Z:
                occluder_x = paired_x * IntPhysGoal.NEAR_X_PERSPECTIVE_FACTOR
            elif paired_z == IntPhysGoal.OBJECT_FAR_Z:
                occluder_x = paired_x * IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
            else:
                logging.warning(f'Unsupported z for occluder target "{paired_obj["id"]}": {paired_z}')
                occluder_x = paired_x
            found_collision = False
            for other_occluder in occluder_list:
                if geometry.occluders_too_close(other_occluder, occluder_x, x_scale):
                    found_collision = True
                    break
            if not found_collision:
                # occluder_indices are needed by quartets
                occluder_indices = paired_obj['intphysOption'].get('occluder_indices', [])
                occluder_indices.append(position_index)
                paired_obj['intphysOption']['occluder_indices'] = occluder_indices
                occluder_fits = True
                break
        if occluder_fits:
            occluder_objs = objects.create_occluder(random.choice(non_room_wall_materials),
                                                    random.choice(pole_materials),
                                                    occluder_x, x_scale)
        else:
            occluder_objs = None
        return occluder_objs

    def _get_occluders(self, obj_list: List[Dict[str, Any]],
                       room_wall_material_name: str) -> List[Dict[str, Any]]:
        """Get occluders to for objects in obj_list."""
        num_occluders = self._get_num_occluders()
        num_paired_occluders = self._get_num_paired_occluders()
        non_room_wall_materials = [m for m in materials.CEILING_AND_WALL_MATERIALS
                                   if m[0] != room_wall_material_name]
        occluder_list = []
        # First add paired occluders. We want to position each paired
        # occluder at the same X position that its corresponding
        # object will be at the end/start of a random step during its
        # movement across the scene described by
        # position_by_step. This will let us add an implausible event
        # (make the object disappear, teleport it, or replace it with
        # another object) at that specific step.
        for i in range(num_paired_occluders):
            paired_obj = obj_list[i]
            occluder_objs = self._get_paired_occluder(paired_obj, occluder_list, non_room_wall_materials,
                                                      materials.METAL_MATERIALS)
            if occluder_objs is not None:
                occluder_list.extend(occluder_objs)
            else:
                logging.warning('could not fit required occluder')
                raise exceptions.SceneException(f'Could not add minimum number of occluders ({num_paired_occluders})')
        self._add_occluders(occluder_list, num_occluders - num_paired_occluders, non_room_wall_materials, False)
        return occluder_list

    def _add_occluders(self, occluder_list: List[Dict[str, Any]],
                       num_to_add: int, non_room_wall_materials: List[Tuple],
                       sideways: bool) -> None:
        """Create additional, non-paired occluders and add them to occluder_list."""
        for _ in range(num_to_add):
            occluder_fits = False
            for try_num in range(util.MAX_TRIES):
                # try random position and scale until we find one that fits (or try too many times)
                min_scale = IntPhysGoal.MIN_OCCLUDER_SCALE
                x_scale = util.random_real(min_scale, IntPhysGoal.MAX_OCCLUDER_SCALE, util.MIN_RANDOM_INTERVAL)
                limit = 3.0 - x_scale / 2.0
                limit = int(limit / util.MIN_RANDOM_INTERVAL) * util.MIN_RANDOM_INTERVAL
                occluder_x = util.random_real(-limit, limit, util.MIN_RANDOM_INTERVAL)
                found_collision = False
                for other_occluder in occluder_list:
                    if geometry.occluders_too_close(other_occluder, occluder_x, x_scale):
                        found_collision = True
                        break
                if not found_collision:
                    occluder_fits = True
                    break
            if occluder_fits:
                occluder_objs = objects.create_occluder(random.choice(non_room_wall_materials),
                                                        random.choice(materials.METAL_MATERIALS),
                                                        occluder_x, x_scale, sideways)
                occluder_list.extend(occluder_objs)
            else:
                logging.debug(f'could not fit occluder at x={occluder_x}')

    def _get_objects_and_occluders_moving_across(self, room_wall_material_name: str) \
        -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Get objects to move across the scene and occluders for them. Returns (objects, occluders) pair."""
        self._last_step = IntPhysGoal.LAST_STEP_MOVE_ACROSS
        # Subtract 5 for end occluder movement and rotation
        new_objects = self._get_objects_moving_across(room_wall_material_name, self._last_step - 5, self._object_defs)
        occluders = self._get_occluders(new_objects, room_wall_material_name)
        return new_objects, occluders

    def _get_num_objects_moving_across(self) -> int:
        return random.choices((1, 2, 3), (40, 30, 30))[0]

    def _get_objects_moving_across(self, room_wall_material_name: str, last_action_end_step: int,
                                   valid_defs: List[Dict[str, Any]],
                                   earliest_action_start_step: int = EARLIEST_ACTION_START_STEP,
                                   valid_positions: Iterable = frozenset(Position),
                                   positions: Optional[List[Position]] = None) -> List[Dict[str, Any]]:
        """Get objects to move across the scene. Returns objects."""
        num_objects = self._get_num_objects_moving_across()
        # The following x positions start outside the camera viewport
        # and ensure that objects with scale 1 don't collide with each
        # other.

        exclusions = {
            IntPhysGoal.Position.RIGHT_FIRST_NEAR: (IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR),
            IntPhysGoal.Position.RIGHT_LAST_NEAR: (IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR),
            IntPhysGoal.Position.RIGHT_FIRST_FAR: (IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR),
            IntPhysGoal.Position.RIGHT_LAST_FAR: (IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR),
            IntPhysGoal.Position.LEFT_FIRST_NEAR: (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR),
            IntPhysGoal.Position.LEFT_LAST_NEAR: (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR),
            IntPhysGoal.Position.LEFT_FIRST_FAR: (IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR),
            IntPhysGoal.Position.LEFT_LAST_FAR: (IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR)
        }
        # Object in key position must have acceleration <=
        # acceleration for object in value position (e.g., object in
        # RIGHT_LAST_NEAR must have acceleration <= acceleration for
        # object in RIGHT_FIRST_NEAR).
        acceleration_ordering = {
            IntPhysGoal.Position.RIGHT_LAST_NEAR: IntPhysGoal.Position.RIGHT_FIRST_NEAR,
            IntPhysGoal.Position.RIGHT_LAST_FAR: IntPhysGoal.Position.RIGHT_FIRST_FAR,
            IntPhysGoal.Position.LEFT_LAST_NEAR: IntPhysGoal.Position.LEFT_FIRST_NEAR,
            IntPhysGoal.Position.LEFT_LAST_FAR: IntPhysGoal.Position.LEFT_FIRST_FAR
        }
        available_locations = set(valid_positions)
        location_assignments = {}
        new_objects = []
        for i in range(num_objects):
            location = random.choice(list(available_locations))
            available_locations.remove(location)
            for loc in exclusions[location]:
                available_locations.discard(loc)
            obj_def = finalize_object_definition(random.choice(valid_defs))
            remaining_intphys_options = obj_def['intphysOptions'].copy()
            while len(remaining_intphys_options) > 0:
                intphys_option = random.choice(remaining_intphys_options)
                if location in acceleration_ordering and \
                   acceleration_ordering[location] in location_assignments:
                    # ensure the objects won't collide
                    acceleration = abs(intphys_option['force']['x'] / obj_def['mass'])
                    other_obj = location_assignments[acceleration_ordering[location]]
                    other_acceleration = abs(other_obj['intphysOption']['force']['x'] / other_obj['mass'])

                    collision = acceleration > other_acceleration
                    if not collision:
                        break
                    elif len(remaining_intphys_options) == 1:
                        # last chance, so just swap the items to make their relative acceleration "ok"
                        location_assignments[location] = other_obj
                        location = acceleration_ordering[location]
                        location_assignments[location] = None # to be assigned later
                        break
                else:
                    break
                remaining_intphys_options.remove(intphys_option)

            object_location = {
                'position': {
                    'x': IntPhysGoal.OBJECT_POSITIONS[location][0],
                    'y': intphys_option['y'] + obj_def['positionY'],
                    'z': IntPhysGoal.OBJECT_POSITIONS[location][1]
                }
            }
            obj = instantiate_object(obj_def, object_location)
            if 'saved_intphys_options' in obj_def:
                # needed by GravityQuartet for steep ramps
                intphys_option['saved_options'] = obj_def['saved_intphys_options']
            location_assignments[location] = obj
            position_by_step = copy.deepcopy(intphys_option['position_by_step'])
            object_position_x = IntPhysGoal.OBJECT_POSITIONS[location][0]
            # adjust position_by_step and remove outliers
            new_positions = []
            for position in position_by_step:
                if location in (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR, IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR):
                    position = object_position_x - position
                else:
                    position = object_position_x + position
                new_positions.append(position)
            if location in (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR, IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR):
                max_x = IntPhysGoal.VIEWPORT_LIMIT_NEAR + obj_def['scale']['x'] / 2.0 * IntPhysGoal.VIEWPORT_PERSPECTIVE_FACTOR
            else:
                max_x = IntPhysGoal.VIEWPORT_LIMIT_FAR + obj_def['scale']['x'] / 2.0 * IntPhysGoal.VIEWPORT_PERSPECTIVE_FACTOR
            filtered_position_by_step = [position for position in new_positions if (abs(position) <= max_x)]
            intphys_option['position_by_step'] = filtered_position_by_step

            # set shows.stepBegin
            min_step_begin = earliest_action_start_step
            if location in acceleration_ordering and acceleration_ordering[location] in location_assignments:
                min_step_begin = location_assignments[acceleration_ordering[location]]['shows'][0]['stepBegin']
            max_step_begin = last_action_end_step - len(filtered_position_by_step)
            if min_step_begin >= max_step_begin:
                stepBegin = min_step_begin
            else:
                stepBegin = random.randint(min_step_begin, max_step_begin)
            obj['shows'][0]['stepBegin'] = stepBegin
            obj['forces'] = [{
                'stepBegin': stepBegin,
                'stepEnd': last_action_end_step,
                'vector': intphys_option['force']
            }]
            if location in (IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR, IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR):
                obj['forces'][0]['vector']['x'] *= -1
            intphys_option['positionY'] = obj_def['positionY']
            obj['intphysOption'] = intphys_option
            new_objects.append(obj)
            if positions is not None:
                positions.append(location)

        return new_objects

    def _get_num_occluders_falling_down(self, num_objects: int) -> int:
        return 2 if num_objects == 2 else random.choice((1, 2))

    def _get_objects_falling_down(self, room_wall_material_name: str) \
        -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        MIN_OCCLUDER_SEPARATION = 0.5
        # Choose between traditional and novel objects.
        # Only use novel objects in "falling down" scenes for now, since we don't have their intphys_options yet.
        self._object_defs = objects.get('INTPHYS') + objects.get('INTPHYS_NOVEL')

        # min scale for each occluder / 2, plus 0.5 separation
        # divided by the smaller scale factor for distance from viewpoint
        min_obj_distance = (IntPhysGoal.MIN_OCCLUDER_SCALE/2 + IntPhysGoal.MIN_OCCLUDER_SCALE/2 +
                            MIN_OCCLUDER_SEPARATION) / IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
        num_objects = random.choice((1, 2))
        object_list = []
        for i in range(num_objects):
            found_space = False
            # It doesn't matter how close the objects are to each
            # other, but each one must have an occluder, and those
            # have to be a certain distance apart, so these objects
            # do, too.
            for _ in range(util.MAX_TRIES):
                # Choose x so the occluder (for this object) is fully
                # in the camera's viewport and with a gap so we can
                # see when an object enters/leaves the scene.
                x_position = util.random_real(-2.5, 2.5, util.MIN_RANDOM_INTERVAL)
                too_close = False
                for obj in object_list:
                    distance = abs(obj['shows'][0]['position']['x'] - x_position)
                    too_close = distance < min_obj_distance
                    if too_close:
                        break
                if not too_close:
                    found_space = True
                    break
            if not found_space:
                raise exceptions.SceneException(f'Could not place {i+1} objects to fall down')
            location = {
                'position': {
                    'x': x_position,
                    'y': 3.8, # ensure the object starts above the camera viewport
                    'z': random.choice((IntPhysGoal.OBJECT_NEAR_Z, IntPhysGoal.OBJECT_FAR_Z))
                }
            }
            obj_def = random.choice(self._object_defs)
            obj = instantiate_object(obj_def, location)
            obj['shows'][0]['stepBegin'] = random.randint(IntPhysGoal.EARLIEST_ACTION_START_STEP,
                                                          IntPhysGoal.LATEST_ACTION_FALL_DOWN_START_STEP)
            obj['intphysOption'] = {
                'positionY': obj_def['positionY']
            }
            object_list.append(obj)
        # place required occluders, then (maybe) some random ones
        num_occluders = self._get_num_occluders_falling_down(num_objects)
        logging.debug(f'num_objects = {num_objects}\tnum_occluders = {num_occluders}')
        occluders = []
        non_room_wall_materials = [m for m in materials.CEILING_AND_WALL_MATERIALS
                                   if m[0] != room_wall_material_name]
        for i in range(num_objects):
            paired_obj = object_list[i]
            min_scale = min(max(paired_obj['shows'][0]['scale']['x'], IntPhysGoal.MIN_OCCLUDER_SCALE), 1)
            x_position = paired_obj['shows'][0]['position']['x']
            paired_z = paired_obj['shows'][0]['position']['z']
            factor = IntPhysGoal.NEAR_X_PERSPECTIVE_FACTOR if paired_z == IntPhysGoal.OBJECT_NEAR_Z \
                else IntPhysGoal.FAR_X_PERSPECTIVE_FACTOR
            # Determine the biggest scale we could use for the new
            # occluder (up to 1) so it isn't too close to any of the
            # others.
            max_scale = IntPhysGoal.MAX_OCCLUDER_SCALE
            for occluder in occluders:
                distance = abs(occluder['shows'][0]['position']['x'] - x_position)
                scale = 2 * (distance - occluder['shows'][0]['scale']['x'] / 2.0 - MIN_OCCLUDER_SEPARATION)
                if scale < 0:
                    raise exceptions.SceneException(f'Placed objects too close together after all ({distance})')
                if scale < max_scale:
                    max_scale = scale
            if max_scale <= min_scale:
                x_scale = min_scale
            else:
                x_scale = util.random_real(min_scale, max_scale, util.MIN_RANDOM_INTERVAL)
            adjusted_x = x_position * factor
            occluder_pair = objects.create_occluder(random.choice(non_room_wall_materials),
                                                    random.choice(materials.METAL_MATERIALS),
                                                    adjusted_x, x_scale, True)
            # occluded_id needed by SpatioTemporalContinuityQuartet
            if 'intphysOption' not in occluder_pair[0]:
                occluder_pair[0]['intphysOption'] = {}
            occluder_pair[0]['intphysOption']['occluded_id'] = paired_obj['id']
            occluders.extend(occluder_pair)
        self._add_occluders(occluders, num_occluders - num_objects, non_room_wall_materials, True)

        return object_list, occluders


class GravityGoal(IntPhysGoal):
    TEMPLATE = {
        'category': GoalCategory.INTPHYS.value,
        'domain_list': [
            tags.DOMAIN_OBJECTS,
            tags.DOMAIN_OBJECTS_GRAVITY,
            tags.DOMAIN_OBJECTS_MOTION,
            tags.DOMAIN_OBJECTS_SOLIDITY
        ],
        'type_list': [
            tags.PASSIVE,
            tags.ACTION_NONE,
            GoalCategory.INTPHYS.value,
            tags.INTPHYS_GRAVITY
        ],
        'description': '',
        'metadata': {
            'choose': [IntPhysGoal.PLAUSIBLE, IntPhysGoal.IMPLAUSIBLE]
        }
    }

    def __init__(self, ramp_type: Optional[ramps.Ramp] = None, roll_down: Optional[bool] = None, use_fastest: bool = False):
        """Caller can specify ramp type and whether the objects roll down or
        up the ramp, if desired. If not specified, a random choice
        will be made. In the case of steep ramps (i.e., with 90 degree
        angles), roll_down is ignored.
        """
        super(GravityGoal, self).__init__('gravity')
        self._ramp_type: Optional[ramps.Ramp] = ramp_type
        self._roll_down = roll_down
        self._left_to_right: Optional[bool] = None
        self._use_fastest = use_fastest

    def is_ramp_steep(self) -> bool:
        if self._ramp_type is None:
            raise ValueError('cannot get ramp type before compute_objects is called')
        return self._ramp_type in (ramps.Ramp.RAMP_90, ramps.Ramp.RAMP_30_90, ramps.Ramp.RAMP_45_90)

    def get_ramp_type(self) -> ramps.Ramp:
        if self._ramp_type is None:
            raise ValueError('cannot get ramp type before compute_objects is called')
        return self._ramp_type

    def is_left_to_right(self) -> bool:
        if self._left_to_right is None:
            raise ValueError('cannot get left-to-right-ness before compute_objects is called')
        return self._left_to_right

    def compute_objects(self, wall_material_name: str, wall_colors: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        ramp_type, left_to_right, ramp_objs, moving_objs = self._get_ramp_and_objects(wall_material_name)
        self._ramp_type = ramp_type
        self._left_to_right = left_to_right
        background_objs = self._compute_scenery()

        return {
            'target': [moving_objs[0]],
            'distractor': moving_objs[1:],
            'background object': background_objs,
            'ramp': ramp_objs
        }

    def _create_random_ramp(self) -> Tuple[ramps.Ramp, bool, float, List[Dict[str, Any]]]:
        material_name = random.choice(materials.OCCLUDER_MATERIALS)[0]
        x_position_percent = random.random()
        left_to_right = random.choice((True, False))
        ramp_type, x_term, ramp_objs = ramps.create_ramp(material_name, x_position_percent, left_to_right, self._ramp_type)
        self._ramp_type = ramp_type
        return ramp_type, left_to_right, x_term, ramp_objs

    def _get_ramp_and_objects(self, room_wall_material_name: str) -> \
        Tuple[ramps.Ramp, bool, List[Dict[str, Any]], List[Dict[str, Any]]]:

        ramp_type, left_to_right, x_term, ramp_objs = self._create_random_ramp()
        # only want intphys_options where y == 0
        valid_defs = []
        for obj_def in self._object_defs:
            # Want to avoid cubes in the gravity tests at this time MCS-269
            if obj_def['type'] != 'cube':
                new_od = obj_def.copy()
                valid_intphys = [intphys for intphys in obj_def['intphysOptions'] if intphys['y'] == 0]
                if len(valid_intphys) != 0:
                    new_od['saved_intphys_options'] = copy.deepcopy(valid_intphys)
                    if self.is_ramp_steep() and self._use_fastest:
                        # use the intphys with the highest force.x for each object
                        sorted_intphys = sorted(valid_intphys, key=lambda intphys: intphys['force']['x'])
                        valid_intphys = [sorted_intphys[-1]]
                    new_od['intphysOptions'] = valid_intphys
                    valid_defs.append(new_od)
        if self.is_ramp_steep():
            # Don't put objects in places where they'd have to roll up
            # 90 degree (i.e., vertical) ramps.
            if left_to_right:
                valid_positions = { IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR,
                                    IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR }
            else:
                valid_positions = { IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR,
                                    IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR }
        elif self._roll_down is not None:
            # enforce rolling up or down the ramp as specified
            if self._roll_down and left_to_right or not self._roll_down and not left_to_right:
                valid_positions = { IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR,
                                    IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR }
            else:
                valid_positions = { IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR,
                                    IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR }
        else:
            valid_positions = set(IntPhysGoal.Position)
        positions = []

        self._last_step = IntPhysGoal.LAST_STEP_RAMP
        # Add a buffer to the ramp's last step to account for extra steps needed by objects moving up the ramps.
        objs = self._get_objects_moving_across(room_wall_material_name, self._last_step - IntPhysGoal.LAST_STEP_RAMP_BUFFER,
                                               valid_defs, 0, valid_positions, positions)
        # adjust height to be on top of ramp if necessary
        for i in range(len(objs)):
            obj = objs[i]
            obj['intphysOption']['moving_object'] = True
            obj['intphysOption']['ramp_x_term'] = x_term
            position = positions[i]
            # Add a downward force to all objects moving down the
            # ramps so that they will move more realistically.
            if left_to_right and position in (
                    IntPhysGoal.Position.LEFT_FIRST_NEAR, IntPhysGoal.Position.LEFT_LAST_NEAR,
                    IntPhysGoal.Position.LEFT_FIRST_FAR, IntPhysGoal.Position.LEFT_LAST_FAR) or \
                    not left_to_right and position in (
                        IntPhysGoal.Position.RIGHT_FIRST_NEAR, IntPhysGoal.Position.RIGHT_LAST_NEAR,
                        IntPhysGoal.Position.RIGHT_FIRST_FAR, IntPhysGoal.Position.RIGHT_LAST_FAR):
                obj['shows'][0]['position']['y'] += ramps.RAMP_OBJECT_HEIGHTS[ramp_type]
                obj['forces'][0]['vector']['y'] = obj['mass'] * IntPhysGoal.RAMP_DOWNWARD_FORCE

        return ramp_type, left_to_right, ramp_objs, objs

    def _get_subclass_config(self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        goal = super(GravityGoal, self)._get_subclass_config(goal_objects)
        goal['type_list'].append(tags.get_ramp_tag(self._ramp_type.value))
        return goal


class ObjectPermanenceGoal(IntPhysGoal):
    TEMPLATE = {
        'category': GoalCategory.INTPHYS.value,
        'domain_list': [
            tags.DOMAIN_OBJECTS,
            tags.DOMAIN_OBJECTS_MOTION,
            tags.DOMAIN_OBJECTS_PERMANENCE,
            tags.DOMAIN_OBJECTS_SOLIDITY
        ],
        'type_list': [
            tags.PASSIVE,
            tags.ACTION_NONE,
            GoalCategory.INTPHYS.value,
            tags.INTPHYS_OBJECT_PERMANENCE
        ],
        'description': '',
        'metadata': {
            'choose': [IntPhysGoal.PLAUSIBLE, IntPhysGoal.IMPLAUSIBLE]
        }
    }

    def __init__(self):
        super(ObjectPermanenceGoal, self).__init__('object permanence')


class ShapeConstancyGoal(IntPhysGoal):
    TEMPLATE = {
        'category': GoalCategory.INTPHYS.value,
        'domain_list': [
            tags.DOMAIN_OBJECTS,
            tags.DOMAIN_OBJECTS_MOTION,
            tags.DOMAIN_OBJECTS_PERMANENCE,
            tags.DOMAIN_OBJECTS_SOLIDITY
        ],
        'type_list': [
            tags.PASSIVE,
            tags.ACTION_NONE,
            GoalCategory.INTPHYS.value,
            tags.INTPHYS_SHAPE_CONSTANCY
        ],
        'description': '',
        'metadata': {
            'choose': [IntPhysGoal.PLAUSIBLE, IntPhysGoal.IMPLAUSIBLE]
        }
    }

    def __init__(self):
        super(ShapeConstancyGoal, self).__init__('shape constancy')


class SpatioTemporalContinuityGoal(IntPhysGoal):
    TEMPLATE = {
        'category': GoalCategory.INTPHYS.value,
        'domain_list': [
            tags.DOMAIN_OBJECTS,
            tags.DOMAIN_OBJECTS_MOTION,
            tags.DOMAIN_OBJECTS_PERMANENCE,
            tags.DOMAIN_OBJECTS_SOLIDITY
        ],
        'type_list': [
            tags.PASSIVE,
            tags.ACTION_NONE,
            GoalCategory.INTPHYS.value,
            tags.INTPHYS_SPATIO_TEMPORAL_CONTINUITY
        ],
        'description': '',
        'metadata': {
            'choose': [IntPhysGoal.PLAUSIBLE, IntPhysGoal.IMPLAUSIBLE]
        }
    }

    def __init__(self):
        super(SpatioTemporalContinuityGoal, self).__init__('spatio temporal continuity')

    def _get_num_occluders(self) -> int:
        return random.choices((2, 3, 4), (40, 30, 30))[0]

    def _get_num_paired_occluders(self) -> int:
        return 2

    def _get_occluders(self, obj_list: List[Dict[str, Any]],
                       room_wall_material_name: str) -> List[Dict[str, Any]]:
        num_occluders = self._get_num_occluders()
        non_room_wall_materials = [m for m in materials.CEILING_AND_WALL_MATERIALS
                                   if m[0] != room_wall_material_name]
        target = obj_list[0]
        occluder_list = []
        for _ in range(2):
            occluder_objs = self._get_paired_occluder(target, occluder_list, non_room_wall_materials,
                                                      materials.METAL_MATERIALS)
            if occluder_objs is None:
                raise exceptions.SceneException(f'Could not add minimum number of occluders')
            occluder_list.extend(occluder_objs)

        self._add_occluders(occluder_list, num_occluders - 2, non_room_wall_materials, False)

        return occluder_list

    def _get_num_occluders_falling_down(self, num_objects: int) -> int:
        return 2
