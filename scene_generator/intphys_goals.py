import copy
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


class IntPhysGoal(Goal, ABC):
    """Base class for Intuitive Physics goals. Subclasses must set TEMPLATE
    variable (for use in get_config)."""

    PLAUSIBLE = 'plausible'
    IMPLAUSIBLE = 'implausible'

    OBJECT_DEFINITION_LIST = objects.get('INTPHYS')
    FALL_DOWN_OBJECT_DEFINITION_LIST = objects.get('INTPHYS') + \
        objects.get('INTPHYS_NOVEL')

    # The X position so a moving object will exit the camera's view (depends on
    # the object's Z position).
    NEAR_MAX_X = 3.55
    FAR_MAX_X = 4.2

    # Factors to adjust an object's position using the sight angle from the
    # camera to the object so an occluder will properly hide the object.
    NEAR_SIGHT_ANGLE_FACTOR_X = 0.9
    FAR_SIGHT_ANGLE_FACTOR_X = 0.8

    OCCLUDER_MIN_SCALE_X = 0.25
    OCCLUDER_MAX_SCALE_X = 1.0
    OCCLUDER_SEPARATION_X = 0.5

    # The max X position so an occluder is seen within the camera's view.
    OCCLUDER_MAX_X = 3
    OCCLUDER_DEFAULT_MAX_X = OCCLUDER_MAX_X - \
        (OCCLUDER_MIN_SCALE_X / 2)

    OBJECT_NEAR_Z = 1.6
    OBJECT_FAR_Z = 2.7

    # The Y position so a fall-down object is above the camera's view.
    FALL_DOWN_OBJECT_Y = 3.8

    # Each occluder will take 6 steps to move and rotate.
    OCCLUDER_MOVEMENT_TIME = 6

    # An object will take 7 steps to fall.
    OBJECT_FALL_TIME = 7

    LAST_STEP_MOVE_ACROSS = 60
    LAST_STEP_FALL_DOWN = 40
    LAST_STEP_RAMP = 60
    LAST_STEP_RAMP_BUFFER = 20

    EARLIEST_ACTION_STEP = OCCLUDER_MOVEMENT_TIME * 2 + 1
    LATEST_ACTION_FALL_DOWN_STEP = LAST_STEP_FALL_DOWN - \
        OCCLUDER_MOVEMENT_TIME - (OBJECT_FALL_TIME * 2)

    RAMP_DOWNWARD_FORCE = -350

    BACKGROUND_MAX_X = 6.5
    BACKGROUND_MIN_Z = 3.25
    BACKGROUND_MAX_Z = 4.95

    class Position(Enum):
        RIGHT_FIRST_NEAR = auto()
        RIGHT_LAST_NEAR = auto()
        RIGHT_FIRST_FAR = auto()
        RIGHT_LAST_FAR = auto()
        LEFT_FIRST_NEAR = auto()
        LEFT_LAST_NEAR = auto()
        LEFT_FIRST_FAR = auto()
        LEFT_LAST_FAR = auto()

    # The X positions so move-across objects start outside the camera's view
    # and ensure multiple scale=1 objects won't collide with one another.
    MOVE_ACROSS_POSITIONS = {
        Position.RIGHT_FIRST_NEAR: (4.2, OBJECT_NEAR_Z),
        Position.RIGHT_LAST_NEAR: (5.3, OBJECT_NEAR_Z),
        Position.RIGHT_FIRST_FAR: (4.8, OBJECT_FAR_Z),
        Position.RIGHT_LAST_FAR: (5.9, OBJECT_FAR_Z),
        Position.LEFT_FIRST_NEAR: (-4.2, OBJECT_NEAR_Z),
        Position.LEFT_LAST_NEAR: (-5.3, OBJECT_NEAR_Z),
        Position.LEFT_FIRST_FAR: (-4.8, OBJECT_FAR_Z),
        Position.LEFT_LAST_FAR: (-5.9, OBJECT_FAR_Z)
    }

    MOVE_ACROSS_CONSTRAINTS = {
        Position.RIGHT_FIRST_NEAR: (
            Position.LEFT_FIRST_NEAR,
            Position.LEFT_LAST_NEAR
        ),
        Position.RIGHT_LAST_NEAR: (
            Position.LEFT_FIRST_NEAR,
            Position.LEFT_LAST_NEAR
        ),
        Position.RIGHT_FIRST_FAR: (
            Position.LEFT_FIRST_FAR,
            Position.LEFT_LAST_FAR
        ),
        Position.RIGHT_LAST_FAR: (
            Position.LEFT_FIRST_FAR,
            Position.LEFT_LAST_FAR
        ),
        Position.LEFT_FIRST_NEAR: (
            Position.RIGHT_FIRST_NEAR,
            Position.RIGHT_LAST_NEAR
        ),
        Position.LEFT_LAST_NEAR: (
            Position.RIGHT_FIRST_NEAR,
            Position.RIGHT_LAST_NEAR
        ),
        Position.LEFT_FIRST_FAR: (
            Position.RIGHT_FIRST_FAR,
            Position.RIGHT_LAST_FAR
        ),
        Position.LEFT_LAST_FAR: (
            Position.RIGHT_FIRST_FAR,
            Position.RIGHT_LAST_FAR
        )
    }

    # Object in key position must have acceleration <=
    # acceleration for object in value position (e.g., object in
    # RIGHT_LAST_NEAR must have acceleration <= acceleration for
    # object in RIGHT_FIRST_NEAR).
    MOVE_ACROSS_ORDERINGS = {
        Position.RIGHT_LAST_NEAR: (
            Position.RIGHT_FIRST_NEAR
        ),
        Position.RIGHT_LAST_FAR: (
            Position.RIGHT_FIRST_FAR
        ),
        Position.LEFT_LAST_NEAR: (
            Position.LEFT_FIRST_NEAR
        ),
        Position.LEFT_LAST_FAR: (
            Position.LEFT_FIRST_FAR
        )
    }

    def __init__(self, name: str, is_fall_down=False, is_move_across=False):
        super(IntPhysGoal, self).__init__(name)
        if is_fall_down:
            self._scene_setup_function = IntPhysGoal._generate_fall_down
        elif is_move_across:
            self._scene_setup_function = IntPhysGoal._generate_move_across
        else:
            self._scene_setup_function = random.choice([
                IntPhysGoal._generate_move_across,
                IntPhysGoal._generate_fall_down
            ])

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

    def _find_optimal_path(
        self,
        goal_objects: List[Dict[str, Any]],
        all_objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return []

    def compute_objects(
        self,
        room_wall_material_name: str,
        room_wall_colors: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        wall_material_list = [
            material
            for material in materials.OCCLUDER_MATERIALS
            if material[0] != room_wall_material_name
        ]
        moving_list, occluder_list = self._scene_setup_function(
            self,
            wall_material_list
        )
        background_list = self._generate_background_object_list()
        return {
            'target': [moving_list[0]],
            'distractor': moving_list[1:],
            'background object': background_list,
            'occluder': occluder_list
        }

    def update_body(
        self,
        body: Dict[str, Any],
        find_path: bool
    ) -> Dict[str, Any]:
        body = super(IntPhysGoal, self).update_body(body, find_path)
        body['passive'] = True
        body['answer'] = {
            'choice': IntPhysGoal.PLAUSIBLE
        }
        return body

    def _get_subclass_config(
        self,
        goal_objects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        goal = copy.deepcopy(self.TEMPLATE)
        goal['last_step'] = self._last_step
        goal['action_list'] = [['Pass']] * goal['last_step']
        if self._scene_setup_function:
            if self.is_move_across():
                goal['type_list'].append(tags.INTPHYS_MOVE_ACROSS)
            if self.is_fall_down():
                goal['type_list'].append(tags.INTPHYS_FALL_DOWN)
        return goal

    def _calculate_separation_distance(
        self,
        x_position_1: float,
        x_size_1: float,
        x_position_2: float,
        x_size_2: float
    ) -> bool:
        """Return the distance separating the two occluders (or one object and
        one occluder) with the given X positions and X sizes. A negative
        distance means that the two objects are too close to one another."""
        distance = abs(x_position_1 - x_position_2)
        separation = (x_size_1 + x_size_2) / 2.0
        return distance - (separation + IntPhysGoal.OCCLUDER_SEPARATION_X)

    def _choose_fall_down_object_number(self) -> int:
        """Return the number of objects for the fall-down scene."""
        return random.choice((1, 2))

    def _choose_fall_down_occluder_number(self) -> int:
        """Return the number of occluders for the fall-down scene."""
        return random.choice((1, 2))

    def _choose_move_across_object_number(self) -> int:
        """Return the number of objects for the move-across scene."""
        return random.choices((1, 2, 3), (40, 30, 30))[0]

    def _choose_move_across_occluder_number(self) -> int:
        """Return the number of occluders for the move-across scene."""
        return random.choices((1, 2, 3), (50, 30, 20))[0]

    def _generate_background_object_list(self) -> List[Dict[str, Any]]:
        def random_x():
            return util.random_real(-IntPhysGoal.BACKGROUND_MAX_X,
                                    IntPhysGoal.BACKGROUND_MAX_X,
                                    util.MIN_RANDOM_INTERVAL)

        def random_z():
            # Choose values so each background object is positioned between the
            # moving IntPhys objects and the back wall of the room.
            return util.random_real(IntPhysGoal.BACKGROUND_MIN_Z,
                                    IntPhysGoal.BACKGROUND_MAX_Z,
                                    util.MIN_RANDOM_INTERVAL)

        background_number = random.choices((0, 1, 2, 3, 4, 5),
                                           (50, 10, 10, 10, 10, 10))[0]
        background_object_list = []
        background_bounds_list = []
        background_definition_list = objects.get('NOT_PICKUPABLE')

        for _ in range(background_number):
            location = None
            while not location:
                background_definition = finalize_object_definition(
                    random.choice(background_definition_list))
                location = geometry.calc_obj_pos(geometry.ORIGIN,
                                                 background_bounds_list,
                                                 background_definition,
                                                 random_x, random_z)
                if location:
                    # Ensure entire bounds is within background
                    for point in location['boundingBox']:
                        x = point['x']
                        z = point['z']
                        if (
                            x < -IntPhysGoal.BACKGROUND_MAX_X or
                            x > IntPhysGoal.BACKGROUND_MAX_X or
                            z < IntPhysGoal.BACKGROUND_MIN_Z or
                            z > IntPhysGoal.BACKGROUND_MAX_Z
                        ):
                            # If not, reset and try again
                            location = None
                            del background_bounds_list[-1]
                            break
            background_object = instantiate_object(background_definition,
                                                   location)
            background_object_list.append(background_object)

        return background_object_list

    def _generate_fall_down(
        self,
        occluder_wall_material_list: List[Tuple]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate and return fall-down objects and occluders."""
        self._last_step = IntPhysGoal.LAST_STEP_FALL_DOWN
        object_list = self._generate_fall_down_object_list()
        occluder_list = self._generate_fall_down_paired_occluder_list(
            object_list, occluder_wall_material_list)
        self._generate_occluder_list(
            self._choose_fall_down_occluder_number() -
            int(len(occluder_list) / 2),
            occluder_list,
            occluder_wall_material_list,
            True
        )
        return object_list, occluder_list

    def _generate_fall_down_object_list(self) -> List[Dict[str, Any]]:
        """Generate and return fall-down objects."""
        object_list = []
        for _ in range(self._choose_fall_down_object_number()):
            successful = False
            for _ in range(util.MAX_TRIES):
                # Ensure the random X position is within the camera's view.
                x_position = util.random_real(
                    -IntPhysGoal.OCCLUDER_DEFAULT_MAX_X,
                    IntPhysGoal.OCCLUDER_DEFAULT_MAX_X,
                    util.MIN_RANDOM_INTERVAL
                )

                z_position = random.choice(
                    (IntPhysGoal.OBJECT_NEAR_Z, IntPhysGoal.OBJECT_FAR_Z)
                )
                factor = self.retrieve_sight_angle_position_factor(z_position)

                # Each object must have an occluder so ensure that they're each
                # positioned far enough away from one another.
                too_close = False
                for instance in object_list:
                    second_factor = self.retrieve_sight_angle_position_factor(
                        instance['shows'][0]['position']['z']
                    )
                    too_close = self._calculate_separation_distance(
                        x_position * factor,
                        IntPhysGoal.OCCLUDER_MAX_SCALE_X,
                        instance['shows'][0]['position']['x'] * second_factor,
                        IntPhysGoal.OCCLUDER_MAX_SCALE_X
                    ) < 0
                    if too_close:
                        break
                if not too_close:
                    successful = True
                    break
            if not successful:
                raise exceptions.SceneException(
                    f'Cannot position object to fall down object_list='
                    f'{object_list}')

            location = {
                'position': {
                    'x': x_position,
                    'y': IntPhysGoal.FALL_DOWN_OBJECT_Y,
                    'z': random.choice(
                        (IntPhysGoal.OBJECT_NEAR_Z, IntPhysGoal.OBJECT_FAR_Z)
                    )
                }
            }

            object_definition = random.choice(
                IntPhysGoal.FALL_DOWN_OBJECT_DEFINITION_LIST
            )
            instance = instantiate_object(object_definition, location)
            instance['shows'][0]['stepBegin'] = random.randint(
                IntPhysGoal.EARLIEST_ACTION_STEP,
                IntPhysGoal.LATEST_ACTION_FALL_DOWN_STEP
            )
            object_list.append(instance)

        return object_list

    def _generate_fall_down_paired_occluder(
        self,
        paired_object: Dict[str, Any],
        occluder_list: List[Dict[str, Any]],
        occluder_wall_material_list: List[Tuple]
    ) -> List[Dict[str, Any]]:
        """Generate and return one fall-down paired occluder that must be
        positioned underneath the paired object."""
        paired_x = paired_object['shows'][0]['position']['x']
        # For a non-occluder, the size is its dimensions, NOT its scale!
        paired_size = paired_object['dimensions']['x']
        min_scale = min(max(paired_size, IntPhysGoal.OCCLUDER_MIN_SCALE_X),
                        IntPhysGoal.OCCLUDER_MAX_SCALE_X)
        max_scale = IntPhysGoal.OCCLUDER_MAX_SCALE_X

        # Adjust the X position using the sight angle from the camera
        # to the object so an occluder will properly hide the object.
        paired_z = paired_object['shows'][0]['position']['z']
        x_position = paired_x * \
            self.retrieve_sight_angle_position_factor(paired_z)

        for occluder in occluder_list:
            occluder_x = occluder['shows'][0]['position']['x']
            occluder_size = occluder['shows'][0]['scale']['x']
            # Ensure that each occluder is positioned far enough away from one
            # another (this should be done previously, but check again).
            distance = self._calculate_separation_distance(
                occluder_x,
                occluder_size,
                x_position,
                paired_size
            )
            if distance < 0:
                print(f'OBJECT={paired_object}\nOCCLUDER_LIST={occluder_list}')
                raise exceptions.SceneException(
                    f'IntPhys fall-down objects were positioned too close '
                    f'distance={distance} object_position={x_position} '
                    f'object_size={paired_size} '
                    f'occluder_position={occluder_x} '
                    f'occluder_size={occluder_size}')
            if distance < (max_scale - min_scale):
                max_scale = min_scale + distance

        # Choose a random size.
        if max_scale <= min_scale:
            x_scale = min_scale
        else:
            x_scale = util.random_real(min_scale, max_scale,
                                       util.MIN_RANDOM_INTERVAL)

        return objects.create_occluder(
            random.choice(occluder_wall_material_list),
            random.choice(materials.METAL_MATERIALS),
            x_position,
            x_scale,
            True
        )

    def _generate_fall_down_paired_occluder_list(
        self,
        object_list: List[Dict[str, Any]],
        occluder_wall_material_list: List[Tuple]
    ) -> List[Dict[str, Any]]:
        """Generate and return needed fall-down paired occluders."""
        paired_list = self._identify_fall_down_paired_list(object_list)
        occluder_list = []
        for paired_object in paired_list:
            occluder = self._generate_fall_down_paired_occluder(
                paired_object,
                occluder_list,
                occluder_wall_material_list
            )
            if not occluder:
                raise exceptions.SceneException(
                    f'Cannot create fall-down paired occluder object='
                    f'{paired_object} occluder_list={occluder_list}')
            occluder_list.extend(occluder)
        return occluder_list

    def _generate_move_across(
        self,
        occluder_wall_material_list: List[Tuple]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate and return move-across objects and occluders."""
        self._last_step = IntPhysGoal.LAST_STEP_MOVE_ACROSS
        object_list = self._generate_move_across_object_list(
            self._last_step - IntPhysGoal.OCCLUDER_MOVEMENT_TIME)
        occluder_list = self._generate_move_across_paired_occluder_list(
            object_list, occluder_wall_material_list)
        self._generate_occluder_list(
            self._choose_move_across_occluder_number() -
            int(len(occluder_list) / 2),
            occluder_list,
            occluder_wall_material_list,
            False
        )
        return object_list, occluder_list

    def _generate_move_across_object_list(
        self,
        last_action_step: int,
        definition_list: List[Dict[str, Any]] = OBJECT_DEFINITION_LIST,
        earliest_action_step: int = EARLIEST_ACTION_STEP,
        position_list: Iterable = frozenset(Position)
    ) -> List[Dict[str, Any]]:
        """Generate and return move-across objects."""
        available_locations = set(position_list)
        location_assignment = {}
        object_list = []

        for _ in range(self._choose_move_across_object_number()):
            location = random.choice(list(available_locations))
            available_locations.remove(location)
            for constraint in IntPhysGoal.MOVE_ACROSS_CONSTRAINTS[location]:
                available_locations.discard(constraint)
            object_definition = finalize_object_definition(
                random.choice(definition_list))

            # The object's intphys options list forces and starting Y position.
            intphys_options = object_definition['intphysOptions'].copy()
            while len(intphys_options) > 0:
                intphys_option = random.choice(intphys_options)
                if (
                    location in IntPhysGoal.MOVE_ACROSS_ORDERINGS and
                    IntPhysGoal.MOVE_ACROSS_ORDERINGS[location]
                    in location_assignment
                ):
                    # Ensure this object won't outrun an object in front of it
                    # by comparing their relative acceleration.
                    acceleration = abs(intphys_option['force']['x'] /
                                       object_definition['mass'])
                    other_object = location_assignment[
                        IntPhysGoal.MOVE_ACROSS_ORDERINGS[location]
                    ]
                    other_acceleration = abs(
                        other_object['intphysOption']['force']['x'] /
                        other_object['mass']
                    )
                    if not (acceleration > other_acceleration):
                        break
                    elif len(intphys_options) == 1:
                        # If this object is faster, then swap locations.
                        location_assignment[location] = other_object
                        location = IntPhysGoal.MOVE_ACROSS_ORDERINGS[location]
                        # This location will be assigned later.
                        location_assignment[location] = None
                        break
                else:
                    break
                intphys_options.remove(intphys_option)

            object_location = {
                'position': {
                    'x': IntPhysGoal.MOVE_ACROSS_POSITIONS[location][0],
                    'y': intphys_option['y'] + object_definition['positionY'],
                    'z': IntPhysGoal.MOVE_ACROSS_POSITIONS[location][1]
                }
            }

            instance = instantiate_object(object_definition, object_location)
            if 'savedIntphysOptions' in object_definition:
                # Save intphysOptions needed by GravityQuartet for steep ramps.
                intphys_option['savedOptions'] = object_definition[
                    'savedIntphysOptions'
                ]

            location_assignment[location] = instance
            position_by_step = copy.deepcopy(intphys_option['positionByStep'])
            object_position_x = IntPhysGoal.MOVE_ACROSS_POSITIONS[location][0]

            # Add or subtract the object's X to each position.
            adjusted_position_list = []
            for position in position_by_step:
                if location in (
                    IntPhysGoal.Position.RIGHT_FIRST_NEAR,
                    IntPhysGoal.Position.RIGHT_LAST_NEAR,
                    IntPhysGoal.Position.RIGHT_FIRST_FAR,
                    IntPhysGoal.Position.RIGHT_LAST_FAR
                ):
                    position = object_position_x - position
                else:
                    position = object_position_x + position
                adjusted_position_list.append(position)

            # Identify the X in which the object will exit the camera's view.
            if location in (
                IntPhysGoal.Position.RIGHT_FIRST_NEAR,
                IntPhysGoal.Position.RIGHT_LAST_NEAR,
                IntPhysGoal.Position.LEFT_FIRST_NEAR,
                IntPhysGoal.Position.LEFT_LAST_NEAR
            ):
                max_x = IntPhysGoal.NEAR_MAX_X + \
                    (object_definition['scale']['x'] / 2.0) / \
                    IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
            else:
                max_x = IntPhysGoal.FAR_MAX_X + \
                    object_definition['scale']['x'] / 2.0 / \
                    IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X

            # Remove each extraneous X position.
            filtered_position_by_step = [
                position for position in adjusted_position_list if (
                    abs(position) <= max_x
                )
            ]
            intphys_option['positionByStep'] = filtered_position_by_step

            # The object should not begin before an object in front of it.
            min_step_begin = earliest_action_step
            if (
                location in IntPhysGoal.MOVE_ACROSS_ORDERINGS and
                IntPhysGoal.MOVE_ACROSS_ORDERINGS[location]
                in location_assignment
            ):
                min_step_begin = location_assignment[
                    IntPhysGoal.MOVE_ACROSS_ORDERINGS[location]
                ]['shows'][0]['stepBegin']

            # The object should be able to end before the last action step.
            max_step_begin = last_action_step - len(filtered_position_by_step)

            # Choose the action step in which the object will appear.
            if min_step_begin >= max_step_begin:
                step_begin = min_step_begin
            else:
                step_begin = random.randint(min_step_begin, max_step_begin)

            instance['shows'][0]['stepBegin'] = step_begin
            instance['forces'] = [{
                'stepBegin': step_begin,
                'stepEnd': last_action_step,
                'vector': intphys_option['force']
            }]

            # Reverse the force if moving right-to-left.
            if location in (
                IntPhysGoal.Position.RIGHT_FIRST_NEAR,
                IntPhysGoal.Position.RIGHT_LAST_NEAR,
                IntPhysGoal.Position.RIGHT_FIRST_FAR,
                IntPhysGoal.Position.RIGHT_LAST_FAR
            ):
                instance['forces'][0]['vector']['x'] *= -1

            intphys_option['positionY'] = object_definition['positionY']
            instance['intphysOption'] = intphys_option
            object_list.append(instance)

        return object_list

    def _generate_move_across_paired_occluder(
        self,
        paired_object: Dict[str, Any],
        occluder_list: List[Dict[str, Any]],
        occluder_wall_material_list: List[Tuple]
    ) -> List[Dict[str, Any]]:
        """Generate and return one move-across paired occluder that must be
        positioned at one of the paired object's position_by_step so that it
        will properly hide the paired object during the implausible event."""
        successful = False
        for _ in range(util.MAX_TRIES):
            # Object may be a cube on its corner, so use diagonal distance.
            paired_size = math.sqrt(2) * paired_object['dimensions']['x']
            min_scale = min(max(paired_size, IntPhysGoal.OCCLUDER_MIN_SCALE_X),
                            IntPhysGoal.OCCLUDER_MAX_SCALE_X)

            # Choose a random size.
            x_scale = util.random_real(
                min_scale,
                IntPhysGoal.OCCLUDER_MAX_SCALE_X,
                util.MIN_RANDOM_INTERVAL
            )

            # Choose a random position.
            # The position must correspond with one of the object's positions.
            position_by_step = paired_object['intphysOption']['positionByStep']
            max_x_position = IntPhysGoal.OCCLUDER_MAX_X - x_scale / 2
            while True:
                position_index = random.randrange(len(position_by_step))
                paired_x = position_by_step[position_index]
                if -max_x_position <= paired_x <= max_x_position:
                    break

            # Adjust the X position using the sight angle from the camera
            # to the object so an occluder will properly hide the object.
            paired_z = paired_object['shows'][0]['position']['z']
            x_position = paired_x * \
                self.retrieve_sight_angle_position_factor(paired_z)

            # Ensure the new occluder isn't too close to an existing occluder.
            too_close = False
            for occluder in occluder_list:
                too_close = self._calculate_separation_distance(
                    occluder['shows'][0]['position']['x'],
                    occluder['shows'][0]['scale']['x'],
                    x_position,
                    x_scale
                ) < 0
                if too_close:
                    break
            if not too_close:
                # Save occluderIndices needed by quartets.
                occluder_indices = paired_object['intphysOption'].get(
                    'occluderIndices', [])
                occluder_indices.append(position_index)
                paired_object['intphysOption']['occluderIndices'] = occluder_indices  # noqa: E501
                successful = True
                break
        if successful:
            return objects.create_occluder(
                random.choice(occluder_wall_material_list),
                random.choice(materials.METAL_MATERIALS),
                x_position,
                x_scale
            )
        return None

    def _generate_move_across_paired_occluder_list(
        self,
        object_list: List[Dict[str, Any]],
        occluder_wall_material_list: List[Tuple]
    ) -> List[Dict[str, Any]]:
        """Generate and return needed move-across paired occluders."""
        paired_list = self._identify_move_across_paired_list(object_list)
        occluder_list = []
        for paired_object in paired_list:
            occluder = self._generate_move_across_paired_occluder(
                paired_object,
                occluder_list,
                occluder_wall_material_list
            )
            if not occluder:
                raise exceptions.SceneException(
                    f'Cannot create move-across paired object='
                    f'{paired_object} occluder_list={occluder_list}')
            occluder_list.extend(occluder)
        return occluder_list

    def _generate_occluder(
        self,
        occluder_list: List[Dict[str, Any]],
        occluder_wall_material_list: List[Tuple],
        sideways: bool
    ) -> List[Dict[str, Any]]:
        """Generate and return a single occluder."""
        successful = False
        for _ in range(util.MAX_TRIES):
            # Choose a random size.
            x_scale = util.random_real(
                IntPhysGoal.OCCLUDER_MIN_SCALE_X,
                IntPhysGoal.OCCLUDER_MAX_SCALE_X,
                util.MIN_RANDOM_INTERVAL
            )
            x_position = self._generate_occluder_position(x_scale,
                                                          occluder_list)
            if x_position is not None:
                successful = True
                break
        if successful:
            return objects.create_occluder(
                random.choice(occluder_wall_material_list),
                random.choice(materials.METAL_MATERIALS),
                x_position,
                x_scale,
                sideways
            )
        return None

    def _generate_occluder_list(
        self,
        number: int,
        occluder_list: List[Dict[str, Any]],
        occluder_wall_material_list: List[Tuple],
        sideways: bool
    ) -> None:
        """Generate occluders and add them to the given occluder_list."""
        for _ in range(number):
            occluder = self._generate_occluder(occluder_list,
                                               occluder_wall_material_list,
                                               sideways)
            if not occluder:
                raise exceptions.SceneException(
                    f'Cannot create occluder occluder_list={occluder_list}')
            occluder_list.extend(occluder)

    def _generate_occluder_position(
        self,
        x_scale: float,
        occluder_list: List[Dict[str, Any]]
    ) -> float:
        """Generate and return a random X position for a new occluder with the
        given X scale that isn't too close to an existing occluder from the
        given list."""
        max_x = IntPhysGoal.OCCLUDER_MAX_X - x_scale / 2.0
        max_x = int(max_x / util.MIN_RANDOM_INTERVAL) * \
            util.MIN_RANDOM_INTERVAL

        for _ in range(util.MAX_TRIES):
            # Choose a random position.
            x_position = util.random_real(-max_x, max_x,
                                          util.MIN_RANDOM_INTERVAL)

            # Ensure the new occluder isn't too close to an existing occluder.
            too_close = False
            for occluder in occluder_list:
                too_close = self._calculate_separation_distance(
                    occluder['shows'][0]['position']['x'],
                    occluder['shows'][0]['scale']['x'],
                    x_position,
                    x_scale
                ) < 0
                if too_close:
                    break
            if not too_close:
                return x_position

        return None

    def _identify_fall_down_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Return objects that must be paired with occluders in fall-down
        scenes."""
        return object_list

    def _identify_move_across_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Return objects that must be paired with occluders in move-across
        scenes."""
        return [object_list[0]]

    def is_fall_down(self) -> bool:
        return self._scene_setup_function == IntPhysGoal._generate_fall_down

    def is_move_across(self) -> bool:
        return self._scene_setup_function == IntPhysGoal._generate_move_across

    def retrieve_sight_angle_position_factor(self, z_position: float) -> bool:
        """Return an X-position-factor using the sight angle between the camera
        and an object with the given Z position so an occluder will properly
        hide the object."""
        return (
            IntPhysGoal.NEAR_SIGHT_ANGLE_FACTOR_X
            if z_position == IntPhysGoal.OBJECT_NEAR_Z
            else IntPhysGoal.FAR_SIGHT_ANGLE_FACTOR_X
        )


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

    def __init__(self, ramp_type: Optional[ramps.Ramp] = None,
                 roll_down: Optional[bool] = None, use_fastest: bool = False):
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
            raise ValueError(
                'cannot get ramp type before compute_objects is called')
        return self._ramp_type in (
            ramps.Ramp.RAMP_90, ramps.Ramp.RAMP_30_90, ramps.Ramp.RAMP_45_90)

    def get_ramp_type(self) -> ramps.Ramp:
        if self._ramp_type is None:
            raise ValueError(
                'cannot get ramp type before compute_objects is called')
        return self._ramp_type

    def is_left_to_right(self) -> bool:
        if self._left_to_right is None:
            raise ValueError(
                'cannot get left-to-right-ness before compute_objects '
                'is called')
        return self._left_to_right

    def compute_objects(
        self, wall_material_name: str, wall_colors: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        (
            ramp_type,
            left_to_right,
            ramp_objs,
            moving_objs
        ) = self._get_ramp_and_objects(wall_material_name)
        self._ramp_type = ramp_type
        self._left_to_right = left_to_right
        background_objs = self._generate_background_object_list()

        return {
            'target': [moving_objs[0]],
            'distractor': moving_objs[1:],
            'background object': background_objs,
            'ramp': ramp_objs
        }

    def _create_random_ramp(
            self) -> Tuple[ramps.Ramp, bool, float, List[Dict[str, Any]]]:
        material_name = random.choice(materials.OCCLUDER_MATERIALS)[0]
        x_position_percent = random.random()
        left_to_right = random.choice((True, False))
        ramp_type, x_term, ramp_objs = ramps.create_ramp(
            material_name, x_position_percent, left_to_right, self._ramp_type)
        self._ramp_type = ramp_type
        return ramp_type, left_to_right, x_term, ramp_objs

    def _get_ramp_and_objects(
        self, room_wall_material_name: str
    ) -> Tuple[ramps.Ramp, bool, List[Dict[str, Any]], List[Dict[str, Any]]]:

        (
            ramp_type,
            left_to_right,
            x_term,
            ramp_objs
        ) = self._create_random_ramp()
        # only want intphys_options where y == 0
        valid_defs = []
        for obj_def in IntPhysGoal.OBJECT_DEFINITION_LIST:
            # Want to avoid cubes in the gravity tests at this time MCS-269
            if obj_def['type'] != 'cube':
                new_od = obj_def.copy()
                valid_intphys = [
                    intphys
                    for intphys in obj_def['intphysOptions']
                    if intphys['y'] == 0
                ]
                if len(valid_intphys) != 0:
                    new_od['savedIntphysOptions'] = copy.deepcopy(
                        valid_intphys)
                    if self.is_ramp_steep() and self._use_fastest:
                        # use the intphys with the highest force.x for each
                        # object
                        sorted_intphys = sorted(
                            valid_intphys,
                            key=lambda intphys: intphys['force']['x']
                        )
                        valid_intphys = [sorted_intphys[-1]]
                    new_od['intphysOptions'] = valid_intphys
                    valid_defs.append(new_od)
        if self.is_ramp_steep():
            # Don't put objects in places where they'd have to roll up
            # 90 degree (i.e., vertical) ramps.
            if left_to_right:
                position_list = {
                    IntPhysGoal.Position.LEFT_FIRST_NEAR,
                    IntPhysGoal.Position.LEFT_LAST_NEAR,
                    IntPhysGoal.Position.LEFT_FIRST_FAR,
                    IntPhysGoal.Position.LEFT_LAST_FAR
                }
            else:
                position_list = {
                    IntPhysGoal.Position.RIGHT_FIRST_NEAR,
                    IntPhysGoal.Position.RIGHT_LAST_NEAR,
                    IntPhysGoal.Position.RIGHT_FIRST_FAR,
                    IntPhysGoal.Position.RIGHT_LAST_FAR
                }
        elif self._roll_down is not None:
            # enforce rolling up or down the ramp as specified
            if (
                self._roll_down and
                left_to_right or
                not self._roll_down and
                not left_to_right
            ):
                position_list = {
                    IntPhysGoal.Position.LEFT_FIRST_NEAR,
                    IntPhysGoal.Position.LEFT_LAST_NEAR,
                    IntPhysGoal.Position.LEFT_FIRST_FAR,
                    IntPhysGoal.Position.LEFT_LAST_FAR
                }
            else:
                position_list = {
                    IntPhysGoal.Position.RIGHT_FIRST_NEAR,
                    IntPhysGoal.Position.RIGHT_LAST_NEAR,
                    IntPhysGoal.Position.RIGHT_FIRST_FAR,
                    IntPhysGoal.Position.RIGHT_LAST_FAR
                }
        else:
            position_list = set(IntPhysGoal.Position)

        self._last_step = IntPhysGoal.LAST_STEP_RAMP
        # Add a buffer to the ramp's last step to account for extra steps
        # needed by objects moving up the ramps.
        objs = self._generate_move_across_object_list(
            self._last_step - IntPhysGoal.LAST_STEP_RAMP_BUFFER,
            valid_defs,
            0,
            position_list
        )
        # adjust height to be on top of ramp if necessary
        for i in range(len(objs)):
            obj = objs[i]
            obj['intphysOption']['moving_object'] = True
            obj['intphysOption']['ramp_x_term'] = x_term
            # Add a downward force to all objects moving down the
            # ramps so that they will move more realistically.
            if (
                (left_to_right and obj['shows'][0]['position']['x'] < 0) or
                (not left_to_right and obj['shows'][0]['position']['x'] > 0)
            ):
                obj['shows'][0]['position']['y'] += ramps.RAMP_OBJECT_HEIGHTS[
                    ramp_type
                ]
                obj['forces'][0]['vector']['y'] = obj['mass'] * \
                    IntPhysGoal.RAMP_DOWNWARD_FORCE

        return ramp_type, left_to_right, ramp_objs, objs

    def _get_subclass_config(
            self, goal_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
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

    def __init__(self, is_fall_down=False, is_move_across=False):
        super(ObjectPermanenceGoal, self).__init__(
            'object permanence',
            is_fall_down,
            is_move_across
        )


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

    def __init__(self, is_fall_down=False, is_move_across=False):
        super(ShapeConstancyGoal, self).__init__(
            'shape constancy',
            is_fall_down,
            is_move_across
        )


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

    def __init__(self, is_fall_down=False, is_move_across=False):
        super(SpatioTemporalContinuityGoal, self).__init__(
            'spatio temporal continuity',
            is_fall_down,
            is_move_across
        )

    def _choose_fall_down_object_number(self) -> int:
        return 1

    def _choose_fall_down_occluder_number(self) -> int:
        return 2

    def _choose_move_across_occluder_number(self) -> int:
        return random.choices((2, 3), (60, 40))[0]

    def _identify_fall_down_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # Generate two occluders paired with the first object (the target):
        # one in the target's original position, and one in a new position.
        target_copy = copy.deepcopy(object_list[0])
        target_size = target_copy['dimensions']['x']
        factor = self.retrieve_sight_angle_position_factor(
            target_copy['shows'][0]['position']['z']
        )
        # Create a temp occluder with max scale to ensure that the copied
        # target won't be positioned too close to the original target.
        temp_occluder_pair = objects.create_occluder(
            random.choice(materials.OCCLUDER_MATERIALS),
            random.choice(materials.METAL_MATERIALS),
            target_copy['shows'][0]['position']['x'] * factor,
            IntPhysGoal.OCCLUDER_MAX_SCALE_X,
            True
        )
        # Generate a new random X position for the copied target.
        position = self._generate_occluder_position(target_size,
                                                    temp_occluder_pair)
        target_copy['shows'][0]['position']['x'] = position / factor
        # The copied target must be the second object in the returned list.
        print(f'ORIGINAL={object_list[0]}\nCOPY={target_copy}')
        return [object_list[0], target_copy]

    def _identify_move_across_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # Generate two occluders paired with the first object (the target).
        return [object_list[0], object_list[0]]
