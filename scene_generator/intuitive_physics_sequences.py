import copy
import math
import random
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, Iterable, List, Tuple

import exceptions
import geometry
import materials
import objects
import occluders
import sequences
import tags
import util


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

OBJECT_NEAR_Z = 1.6
OBJECT_FAR_Z = 2.7

# The Y position so a fall-down object is above the camera's view.
FALL_DOWN_OBJECT_Y = 3.8

# An object will take 7 steps to fall.
OBJECT_FALL_TIME = 7

LAST_STEP_MOVE_ACROSS = 60
LAST_STEP_FALL_DOWN = 40
LAST_STEP_RAMP = 60
LAST_STEP_RAMP_BUFFER = 20

EARLIEST_ACTION_STEP = occluders.OCCLUDER_MOVEMENT_TIME * 2 + 1
LATEST_ACTION_FALL_DOWN_STEP = LAST_STEP_FALL_DOWN - \
    occluders.OCCLUDER_MOVEMENT_TIME - (OBJECT_FALL_TIME * 2)

BACKGROUND_MAX_X = 6.5
BACKGROUND_MIN_Z = 3.25
BACKGROUND_MAX_Z = 4.95

PERFORMER_START = {
    'position': {
        'x': 0,
        'y': 0,
        'z': -4.5
    },
    'rotation': {
        'y': 0
    }
}


class IntuitivePhysicsPosition(Enum):
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
    IntuitivePhysicsPosition.RIGHT_FIRST_NEAR: (4.2, OBJECT_NEAR_Z),
    IntuitivePhysicsPosition.RIGHT_LAST_NEAR: (5.3, OBJECT_NEAR_Z),
    IntuitivePhysicsPosition.RIGHT_FIRST_FAR: (4.8, OBJECT_FAR_Z),
    IntuitivePhysicsPosition.RIGHT_LAST_FAR: (5.9, OBJECT_FAR_Z),
    IntuitivePhysicsPosition.LEFT_FIRST_NEAR: (-4.2, OBJECT_NEAR_Z),
    IntuitivePhysicsPosition.LEFT_LAST_NEAR: (-5.3, OBJECT_NEAR_Z),
    IntuitivePhysicsPosition.LEFT_FIRST_FAR: (-4.8, OBJECT_FAR_Z),
    IntuitivePhysicsPosition.LEFT_LAST_FAR: (-5.9, OBJECT_FAR_Z)
}


MOVE_ACROSS_CONSTRAINTS = {
    IntuitivePhysicsPosition.RIGHT_FIRST_NEAR: (
        IntuitivePhysicsPosition.LEFT_FIRST_NEAR,
        IntuitivePhysicsPosition.LEFT_LAST_NEAR
    ),
    IntuitivePhysicsPosition.RIGHT_LAST_NEAR: (
        IntuitivePhysicsPosition.LEFT_FIRST_NEAR,
        IntuitivePhysicsPosition.LEFT_LAST_NEAR
    ),
    IntuitivePhysicsPosition.RIGHT_FIRST_FAR: (
        IntuitivePhysicsPosition.LEFT_FIRST_FAR,
        IntuitivePhysicsPosition.LEFT_LAST_FAR
    ),
    IntuitivePhysicsPosition.RIGHT_LAST_FAR: (
        IntuitivePhysicsPosition.LEFT_FIRST_FAR,
        IntuitivePhysicsPosition.LEFT_LAST_FAR
    ),
    IntuitivePhysicsPosition.LEFT_FIRST_NEAR: (
        IntuitivePhysicsPosition.RIGHT_FIRST_NEAR,
        IntuitivePhysicsPosition.RIGHT_LAST_NEAR
    ),
    IntuitivePhysicsPosition.LEFT_LAST_NEAR: (
        IntuitivePhysicsPosition.RIGHT_FIRST_NEAR,
        IntuitivePhysicsPosition.RIGHT_LAST_NEAR
    ),
    IntuitivePhysicsPosition.LEFT_FIRST_FAR: (
        IntuitivePhysicsPosition.RIGHT_FIRST_FAR,
        IntuitivePhysicsPosition.RIGHT_LAST_FAR
    ),
    IntuitivePhysicsPosition.LEFT_LAST_FAR: (
        IntuitivePhysicsPosition.RIGHT_FIRST_FAR,
        IntuitivePhysicsPosition.RIGHT_LAST_FAR
    )
}


# Object in key position must have acceleration <=
# acceleration for object in value position (e.g., object in
# RIGHT_LAST_NEAR must have acceleration <= acceleration for
# object in RIGHT_FIRST_NEAR).
MOVE_ACROSS_ORDERINGS = {
    IntuitivePhysicsPosition.RIGHT_LAST_NEAR: (
        IntuitivePhysicsPosition.RIGHT_FIRST_NEAR
    ),
    IntuitivePhysicsPosition.RIGHT_LAST_FAR: (
        IntuitivePhysicsPosition.RIGHT_FIRST_FAR
    ),
    IntuitivePhysicsPosition.LEFT_LAST_NEAR: (
        IntuitivePhysicsPosition.LEFT_FIRST_NEAR
    ),
    IntuitivePhysicsPosition.LEFT_LAST_FAR: (
        IntuitivePhysicsPosition.LEFT_FIRST_FAR
    )
}


def get_position_step(target: Dict[str, Any], x_position: float,
                      left_to_right: bool, forwards: bool) -> int:
    """Return the step at which the target will reach the x_position."""
    position_by_step = target['chosenMovement']['positionByStep']
    if forwards:
        index_range = range(len(position_by_step))
        counting_up = not left_to_right
    else:
        index_range = range(len(position_by_step) - 1, -1, -1)
        counting_up = left_to_right
    for i in index_range:
        position = position_by_step[i]
        if counting_up and position > x_position or \
           not counting_up and position < x_position:
            return i
    raise exceptions.SceneException(
        f'Cannot find corresponding step x_position={x_position} '
        f'position_by_step={position_by_step} left_to_right={left_to_right} '
        f'forwards={forwards}')


class IntuitivePhysicsSequence(sequences.Sequence, ABC):
    def __init__(
        self,
        name: str,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any],
        is_fall_down=False,
        is_move_across=False
    ) -> None:
        if not is_fall_down and not is_move_across:
            is_fall_down = random.choice([False, True])
            is_move_across = not is_fall_down
        if is_fall_down:
            self._last_step = LAST_STEP_FALL_DOWN
            self._scene_setup_function = (
                IntuitivePhysicsSequence._generate_fall_down
            )
        elif is_move_across:
            self._last_step = LAST_STEP_MOVE_ACROSS
            self._scene_setup_function = (
                IntuitivePhysicsSequence._generate_move_across
            )
        super().__init__(name, body_template, goal_template)

    @abstractmethod
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create and return a quartet of new intuitive physics scenes."""
        pass

    # Override
    def _create_scenes(
        self,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        scene = self._create_default_scene(body_template, goal_template)
        return self._create_intuitive_physics_scenes(scene)

    def _choose_fall_down_object_count(self) -> int:
        """Return the number of objects for the fall-down scene."""
        return random.choice((1, 2))

    def _choose_fall_down_occluder_count(self) -> int:
        """Return the number of occluders for the fall-down scene."""
        return random.choice((1, 2))

    def _choose_move_across_object_count(self) -> int:
        """Return the number of objects for the move-across scene."""
        return random.choices((1, 2, 3), (40, 30, 30))[0]

    def _choose_move_across_occluder_count(self) -> int:
        """Return the number of occluders for the move-across scene."""
        return random.choices((1, 2, 3), (50, 30, 20))[0]

    def _create_default_scene(
        self,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create and return this sequence's default scene JSON using the given
        templates that will be shared by each scene in this sequence."""
        scene = copy.deepcopy(body_template)
        scene['performerStart'] = PERFORMER_START
        scene['intuitivePhysics'] = True
        scene['answer'] = {
            'choice': PLAUSIBLE
        }

        scene['goal'] = copy.deepcopy(goal_template)
        scene['goal']['last_step'] = self._last_step
        scene['goal']['action_list'] = [['Pass']] * scene['goal']['last_step']
        scene['goal']['description'] = ''
        scene['goal']['metadata'] = {
            'choose': [PLAUSIBLE, IMPLAUSIBLE]
        }
        scene['goal']['type_list'] = scene['goal'].get('type_list', [])
        if self._scene_setup_function:
            if self.is_move_across():
                scene['goal']['type_list'].append(tags.MOVE_ACROSS)
            if self.is_fall_down():
                scene['goal']['type_list'].append(tags.FALL_DOWN)

        tag_to_objects = self._create_default_objects(
            scene['wallMaterial'],
            scene['wallColors']
        )
        scene = self._update_scene_objects(scene, tag_to_objects)

        return scene

    def _create_default_objects(
        self,
        room_wall_material_name: str,
        room_wall_colors: List[str]
    ) -> Dict[str, Any]:
        """Generate and return this sequence's objects in a dict of tags with
        their corresponding object lists."""
        occluder_wall_material_list = [
            material
            for material in materials.OCCLUDER_MATERIALS
            if material[0] != room_wall_material_name
        ]
        moving_list, occluder_list = self._scene_setup_function(
            self,
            occluder_wall_material_list
        )
        self._target_list = [moving_list[0]]
        self._distractor_list = moving_list[1:]
        self._occluder_list = occluder_list
        self._background_list = self._generate_background_object_list()
        return {
            'target': self._target_list,
            'distractor': self._distractor_list,
            'background object': self._background_list,
            'occluder': self._occluder_list
        }

    def _find_fall_down_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Return objects that must be paired with occluders in fall-down
        scenes."""
        return object_list

    def _find_move_across_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Return objects that must be paired with occluders in move-across
        scenes."""
        return [object_list[0]]

    def _generate_background_object_list(self) -> List[Dict[str, Any]]:
        """Generate and return the list of background (a.k.a. context) objects,
        behind the moving objects, positioned near the room's back wall."""

        def random_x():
            return util.random_real(-BACKGROUND_MAX_X, BACKGROUND_MAX_X,
                                    util.MIN_RANDOM_INTERVAL)

        def random_z():
            # Choose Z values so each background object is positioned between
            # moving objects and the back wall of the room.
            return util.random_real(BACKGROUND_MIN_Z, BACKGROUND_MAX_Z,
                                    util.MIN_RANDOM_INTERVAL)

        background_count = random.choices((0, 1, 2, 3, 4, 5),
                                          (50, 10, 10, 10, 10, 10))[0]
        background_object_list = []
        background_bounds_list = []
        background_definition_list = objects.get('NOT_PICKUPABLE')

        for _ in range(background_count):
            location = None
            while not location:
                background_definition = util.finalize_object_definition(
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
                            x < -BACKGROUND_MAX_X or x > BACKGROUND_MAX_X or
                            z < BACKGROUND_MIN_Z or z > BACKGROUND_MAX_Z
                        ):
                            # If not, reset and try again
                            location = None
                            del background_bounds_list[-1]
                            break
            background_object = util.instantiate_object(background_definition,
                                                        location)
            background_object_list.append(background_object)

        return background_object_list

    def _generate_fall_down(
        self,
        occluder_wall_material_list: List[Tuple]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate and return fall-down objects and occluders."""
        object_list = self._generate_fall_down_object_list()
        occluder_list = self._generate_fall_down_paired_occluder_list(
            object_list, occluder_wall_material_list)
        self._generate_occluder_list(
            self._choose_fall_down_occluder_count() -
            int(len(occluder_list) / 2),
            occluder_list,
            occluder_wall_material_list,
            True
        )
        return object_list, occluder_list

    def _generate_fall_down_object_list(self) -> List[Dict[str, Any]]:
        """Generate and return fall-down objects."""
        object_list = []
        for _ in range(self._choose_fall_down_object_count()):
            successful = False
            for _ in range(util.MAX_TRIES):
                # Ensure the random X position is within the camera's view.
                x_position = util.random_real(
                    -occluders.OCCLUDER_DEFAULT_MAX_X,
                    occluders.OCCLUDER_DEFAULT_MAX_X,
                    util.MIN_RANDOM_INTERVAL
                )

                z_position = random.choice((OBJECT_NEAR_Z, OBJECT_FAR_Z))
                factor = self._retrieve_sight_angle_position_factor(z_position)

                # Each object must have an occluder so ensure that they're each
                # positioned far enough away from one another.
                too_close = False
                for instance in object_list:
                    second_factor = self._retrieve_sight_angle_position_factor(
                        instance['shows'][0]['position']['z']
                    )
                    too_close = occluders.calculate_separation_distance(
                        x_position * factor,
                        occluders.OCCLUDER_MAX_SCALE_X,
                        instance['shows'][0]['position']['x'] * second_factor,
                        occluders.OCCLUDER_MAX_SCALE_X
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
                    'y': FALL_DOWN_OBJECT_Y,
                    'z': random.choice((OBJECT_NEAR_Z, OBJECT_FAR_Z))
                }
            }

            object_definition = random.choice(FALL_DOWN_OBJECT_DEFINITION_LIST)
            instance = util.instantiate_object(object_definition, location)
            instance['shows'][0]['stepBegin'] = random.randint(
                EARLIEST_ACTION_STEP,
                LATEST_ACTION_FALL_DOWN_STEP
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
        min_scale = min(max(paired_size, occluders.OCCLUDER_MIN_SCALE_X),
                        occluders.OCCLUDER_MAX_SCALE_X)
        max_scale = occluders.OCCLUDER_MAX_SCALE_X

        # Adjust the X position using the sight angle from the camera
        # to the object so an occluder will properly hide the object.
        paired_z = paired_object['shows'][0]['position']['z']
        x_position = paired_x * \
            self._retrieve_sight_angle_position_factor(paired_z)

        for occluder in occluder_list:
            occluder_x = occluder['shows'][0]['position']['x']
            occluder_size = occluder['shows'][0]['scale']['x']
            # Ensure that each occluder is positioned far enough away from one
            # another (this should be done previously, but check again).
            distance = occluders.calculate_separation_distance(
                occluder_x,
                occluder_size,
                x_position,
                paired_size
            )
            if distance < 0:
                print(f'OBJECT={paired_object}\nOCCLUDER_LIST={occluder_list}')
                raise exceptions.SceneException(
                    f'Two fall-down objects were positioned too close '
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

        return occluders.create_occluder(
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
        paired_list = self._find_fall_down_paired_list(object_list)
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
        object_list = self._generate_move_across_object_list(
            self._last_step - occluders.OCCLUDER_MOVEMENT_TIME)
        occluder_list = self._generate_move_across_paired_occluder_list(
            object_list, occluder_wall_material_list)
        self._generate_occluder_list(
            self._choose_move_across_occluder_count() -
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
        position_list: Iterable = frozenset(IntuitivePhysicsPosition)
    ) -> List[Dict[str, Any]]:
        """Generate and return move-across objects."""
        available_locations = set(position_list)
        location_assignment = {}
        object_list = []

        for _ in range(self._choose_move_across_object_count()):
            location = random.choice(list(available_locations))
            available_locations.remove(location)
            for constraint in MOVE_ACROSS_CONSTRAINTS[location]:
                available_locations.discard(constraint)
            object_definition = util.finalize_object_definition(
                random.choice(definition_list))

            # The object's list of possible forces and starting Y positions.
            movement_list = object_definition['intuitivePhysics'].copy()
            while len(movement_list) > 0:
                chosen_movement = random.choice(movement_list)
                if (
                    location in MOVE_ACROSS_ORDERINGS and
                    MOVE_ACROSS_ORDERINGS[location] in location_assignment
                ):
                    # Ensure this object won't outrun an object in front of it
                    # by comparing their relative acceleration.
                    acceleration = abs(chosen_movement['force']['x'] /
                                       object_definition['mass'])
                    other_object = location_assignment[
                        MOVE_ACROSS_ORDERINGS[location]
                    ]
                    other_acceleration = abs(
                        other_object['chosenMovement']['force']['x'] /
                        other_object['mass']
                    )
                    if not (acceleration > other_acceleration):
                        break
                    elif len(movement_list) == 1:
                        # If this object is faster, then swap locations.
                        location_assignment[location] = other_object
                        location = MOVE_ACROSS_ORDERINGS[location]
                        # This location will be assigned later.
                        location_assignment[location] = None
                        break
                else:
                    break
                movement_list.remove(chosen_movement)

            object_location = {
                'position': {
                    'x': MOVE_ACROSS_POSITIONS[location][0],
                    'y': chosen_movement['y'] + object_definition['positionY'],
                    'z': MOVE_ACROSS_POSITIONS[location][1]
                }
            }

            instance = util.instantiate_object(object_definition,
                                               object_location)
            location_assignment[location] = instance
            position_by_step = copy.deepcopy(chosen_movement['positionByStep'])
            object_position_x = MOVE_ACROSS_POSITIONS[location][0]

            # Add or subtract the object's X to each position.
            adjusted_position_list = []
            for position in position_by_step:
                if location in (
                    IntuitivePhysicsPosition.RIGHT_FIRST_NEAR,
                    IntuitivePhysicsPosition.RIGHT_LAST_NEAR,
                    IntuitivePhysicsPosition.RIGHT_FIRST_FAR,
                    IntuitivePhysicsPosition.RIGHT_LAST_FAR
                ):
                    position = object_position_x - position
                else:
                    position = object_position_x + position
                adjusted_position_list.append(position)

            # Identify the X in which the object will exit the camera's view.
            if location in (
                IntuitivePhysicsPosition.RIGHT_FIRST_NEAR,
                IntuitivePhysicsPosition.RIGHT_LAST_NEAR,
                IntuitivePhysicsPosition.LEFT_FIRST_NEAR,
                IntuitivePhysicsPosition.LEFT_LAST_NEAR
            ):
                max_x = NEAR_MAX_X + \
                    (object_definition['scale']['x'] / 2.0) / \
                    NEAR_SIGHT_ANGLE_FACTOR_X
            else:
                max_x = FAR_MAX_X + \
                    object_definition['scale']['x'] / 2.0 / \
                    FAR_SIGHT_ANGLE_FACTOR_X

            # Remove each extraneous X position.
            filtered_position_by_step = [
                position for position in adjusted_position_list if (
                    abs(position) <= max_x
                )
            ]
            chosen_movement['positionByStep'] = filtered_position_by_step

            # The object should not begin before an object in front of it.
            min_step_begin = earliest_action_step
            if (
                location in MOVE_ACROSS_ORDERINGS and
                MOVE_ACROSS_ORDERINGS[location] in location_assignment
            ):
                min_step_begin = location_assignment[
                    MOVE_ACROSS_ORDERINGS[location]
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
                'vector': chosen_movement['force']
            }]

            # Reverse the force if moving right-to-left.
            if location in (
                IntuitivePhysicsPosition.RIGHT_FIRST_NEAR,
                IntuitivePhysicsPosition.RIGHT_LAST_NEAR,
                IntuitivePhysicsPosition.RIGHT_FIRST_FAR,
                IntuitivePhysicsPosition.RIGHT_LAST_FAR
            ):
                instance['forces'][0]['vector']['x'] *= -1

            chosen_movement['positionY'] = object_definition['positionY']
            instance['chosenMovement'] = chosen_movement
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
            min_scale = min(max(paired_size, occluders.OCCLUDER_MIN_SCALE_X),
                            occluders.OCCLUDER_MAX_SCALE_X)

            # Choose a random size.
            x_scale = util.random_real(
                min_scale,
                occluders.OCCLUDER_MAX_SCALE_X,
                util.MIN_RANDOM_INTERVAL
            )

            # Choose a random position.
            # The position must correspond with one of the object's positions.
            position_list = paired_object['chosenMovement']['positionByStep']
            max_x_position = occluders.OCCLUDER_MAX_X - x_scale / 2
            while True:
                position_index = random.randrange(len(position_list))
                paired_x = position_list[position_index]
                if -max_x_position <= paired_x <= max_x_position:
                    break

            # Adjust the X position using the sight angle from the camera
            # to the object so an occluder will properly hide the object.
            paired_z = paired_object['shows'][0]['position']['z']
            x_position = paired_x * \
                self._retrieve_sight_angle_position_factor(paired_z)

            # Ensure the new occluder isn't too close to an existing occluder.
            too_close = False
            for occluder in occluder_list:
                too_close = occluders.calculate_separation_distance(
                    occluder['shows'][0]['position']['x'],
                    occluder['shows'][0]['scale']['x'],
                    x_position,
                    x_scale
                ) < 0
                if too_close:
                    break
            if not too_close:
                # Save occluderIndices needed by quartets.
                occluder_indices = paired_object['chosenMovement'].get(
                    'occluderIndices', [])
                occluder_indices.append(position_index)
                paired_object['chosenMovement']['occluderIndices'] = occluder_indices  # noqa: E501
                successful = True
                break
        if successful:
            return occluders.create_occluder(
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
        paired_list = self._find_move_across_paired_list(object_list)
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
                occluders.OCCLUDER_MIN_SCALE_X,
                occluders.OCCLUDER_MAX_SCALE_X,
                util.MIN_RANDOM_INTERVAL
            )
            x_position = occluders.generate_occluder_position(x_scale,
                                                              occluder_list)
            if x_position is not None:
                successful = True
                break
        if successful:
            return occluders.create_occluder(
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

    def _get_occluder_list(
        self,
        scene: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find and return each occluder object in the given scene."""
        # Find each occluder's ID in this sequence's shared object list.
        occluder_id_list = [occluder['id'] for occluder in self._occluder_list]
        # Then find each occluder in the given scene.
        occluder_list = []
        for instance in scene['objects']:
            if instance['id'] in occluder_id_list:
                occluder_list.append(instance)
        return occluder_list

    def _get_target(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Find and return the target object in the given scene."""
        # Find the target's ID in this sequence's shared object list.
        target_id = self._target_list[0]['id']
        # Then find the target in the given scene.
        for instance in scene['objects']:
            if instance['id'] == target_id:
                return instance
        return None

    def _retrieve_sight_angle_position_factor(self, z_position: float) -> bool:
        """Return an X-position-factor using the sight angle between the camera
        and an object with the given Z position so an occluder will properly
        hide the object."""
        return (
            NEAR_SIGHT_ANGLE_FACTOR_X if z_position == OBJECT_NEAR_Z
            else FAR_SIGHT_ANGLE_FACTOR_X
        )

    def is_fall_down(self) -> bool:
        """Return if this is a fall-down sequence."""
        return self._scene_setup_function == (
            IntuitivePhysicsSequence._generate_fall_down
        )

    def is_move_across(self) -> bool:
        """Return if this is a move-across sequence."""
        return self._scene_setup_function == (
            IntuitivePhysicsSequence._generate_move_across
        )


class ObjectPermanenceSequence(IntuitivePhysicsSequence):
    GOAL_TEMPLATE = {
        'category': tags.INTUITIVE_PHYSICS,
        'domain_list': [
            tags.DOMAIN_OBJECTS,
            tags.DOMAIN_OBJECTS_MOTION,
            tags.DOMAIN_OBJECTS_PERMANENCE,
            tags.DOMAIN_OBJECTS_SOLIDITY
        ],
        'type_list': [
            tags.PASSIVE,
            tags.ACTION_NONE,
            tags.INTUITIVE_PHYSICS,
            tags.OBJECT_PERMANENCE
        ]
    }

    def __init__(
        self,
        body_template: Dict[str, Any],
        is_fall_down=False,
        is_move_across=False
    ):
        super().__init__(
            tags.OBJECT_PERMANENCE.title(),
            body_template,
            ObjectPermanenceSequence.GOAL_TEMPLATE,
            is_fall_down,
            is_move_across
        )

    def _appear_behind_occluder(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder
            # in scene 1 of the quartet.
            occluder_index = target['chosenMovement']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                target['forces'][0]['stepBegin']
            # Set target's X position behind occluder.
            target_appear_x = target['chosenMovement']['positionByStep'][
                occluder_index
            ]
            target['shows'][0]['position']['x'] = target_appear_x

        elif self.is_fall_down():
            # Implausible event happens after target falls behind occluder
            # in scene 1 of the quartet.
            implausible_event_step = (
                OBJECT_FALL_TIME + target['shows'][0]['stepBegin']
            )
            # Set target's Y position stationary on the ground.
            target['shows'][0]['position']['y'] = target['offset']['y']

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Set target to appear at implausible event step.
        target['shows'][0]['stepBegin'] = implausible_event_step

    def _disappear_behind_occluder(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder
            # in scene 1 of the quartet.
            occluder_index = target['chosenMovement']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                target['forces'][0]['stepBegin']

        elif self.is_fall_down():
            # Implausible event happens after target falls behind occluder
            # in scene 1 of the quartet.
            implausible_event_step = (
                OBJECT_FALL_TIME + target['shows'][0]['stepBegin']
            )

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Set target to disappear at implausible event step.
        target['hides'] = [{
            'stepBegin': implausible_event_step
        }]

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        scene_1 = copy.deepcopy(default_scene)
        scene_1['goal']['type_list'].append(tags.OBJECT_PERMANENCE_Q1)

        scene_2 = copy.deepcopy(default_scene)
        scene_2['answer']['choice'] = IMPLAUSIBLE
        scene_2['goal']['type_list'].append(tags.OBJECT_PERMANENCE_Q2)
        self._disappear_behind_occluder(scene_2)

        scene_3 = copy.deepcopy(default_scene)
        scene_3['answer']['choice'] = IMPLAUSIBLE
        scene_3['goal']['type_list'].append(tags.OBJECT_PERMANENCE_Q3)
        self._appear_behind_occluder(scene_3)

        scene_4 = copy.deepcopy(default_scene)
        scene_4['goal']['type_list'].append(tags.OBJECT_PERMANENCE_Q4)
        # Remove the target from the scene.
        target_id = self._target_list[0]['id']
        for i in range(len(scene_4['objects'])):
            if scene_4['objects'][i]['id'] == target_id:
                del scene_4['objects'][i]
                break

        return [scene_1, scene_2, scene_3, scene_4]


class SpatioTemporalContinuitySequence(IntuitivePhysicsSequence):
    GOAL_TEMPLATE = {
        'category': tags.INTUITIVE_PHYSICS,
        'domain_list': [
            tags.DOMAIN_OBJECTS,
            tags.DOMAIN_OBJECTS_MOTION,
            tags.DOMAIN_OBJECTS_PERMANENCE,
            tags.DOMAIN_OBJECTS_SOLIDITY
        ],
        'type_list': [
            tags.PASSIVE,
            tags.ACTION_NONE,
            tags.INTUITIVE_PHYSICS,
            tags.SPATIO_TEMPORAL_CONTINUITY
        ]
    }

    def __init__(
        self,
        body_template: Dict[str, Any],
        is_fall_down=False,
        is_move_across=False
    ):
        super().__init__(
            tags.SPATIO_TEMPORAL_CONTINUITY.title(),
            body_template,
            SpatioTemporalContinuitySequence.GOAL_TEMPLATE,
            is_fall_down,
            is_move_across
        )

    def _adjust_target_max_step_begin(self, scene: Dict[str, Any]) -> None:
        # In move-across scenes, the target's step-begin must give it time to
        # finish moving in teleport-backward and move-later scenes.
        target = self._get_target(scene)
        occluder_index_1 = target['chosenMovement']['occluderIndices'][0]
        occluder_index_2 = target['chosenMovement']['occluderIndices'][1]
        old_step_begin = target['shows'][0]['stepBegin']
        new_step_begin = old_step_begin + \
            abs(occluder_index_1 - occluder_index_2)
        max_step_begin = scene['goal']['last_step'] - \
            len(target['chosenMovement']['positionByStep'])
        if new_step_begin > max_step_begin:
            diff = new_step_begin - max_step_begin
            if diff > old_step_begin:
                raise exceptions.SceneException(
                    f'Cannot adjust target\'s step begin and must redo '
                    f'old_step_begin={old_step_begin} '
                    f'new_step_begin={new_step_begin} '
                    f'max_step_begin={max_step_begin}')
            target['shows'][0]['stepBegin'] -= diff
            if 'forces' in target:
                target['forces'][0]['stepBegin'] -= diff

    def _teleport_forward(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)
        occluder_list = self._get_occluder_list(scene)

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder.
            # Teleport forward from the lower index to the higher index.
            occluder_index_1 = target['chosenMovement']['occluderIndices'][0]
            occluder_index_2 = target['chosenMovement']['occluderIndices'][1]
            if occluder_index_1 < occluder_index_2:
                occluder_start_index = occluder_index_1
                occluder_end_index = occluder_index_2
            else:
                occluder_start_index = occluder_index_2
                occluder_end_index = occluder_index_1
            target_teleport_x = target['chosenMovement']['positionByStep'][
                occluder_end_index
            ]
            target_position = {
                'x': target_teleport_x,
                'y': target['shows'][0]['position']['y'],
                'z': target['shows'][0]['position']['z']
            }
            implausible_event_step = occluder_start_index + \
                target['forces'][0]['stepBegin']

            if random.random() <= 0.5:
                # Delay the teleport to the step at which the target is
                # expected to appear from behind its second paired occluder.
                target['hides'] = [{
                    'stepBegin': implausible_event_step
                }]
                show_step = target['shows'][0]['stepBegin'] + \
                    occluder_end_index + 1
                target['shows'].append({
                    'stepBegin': show_step,
                    'position': target_position,
                    'rotation': target['shows'][0]['rotation']
                })
                scene['goal']['type_list'].append(
                    tags.TELEPORT_DELAYED)
            else:
                # Instantaneous teleport.
                target['teleports'] = [{
                    'stepBegin': implausible_event_step,
                    'stepEnd': implausible_event_step,
                    'position': target_position,
                    'rotation': target['shows'][0]['rotation']
                }]
                scene['goal']['type_list'].append(
                    tags.TELEPORT_INSTANTANEOUS)

        elif self.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                OBJECT_FALL_TIME + target['shows'][0]['stepBegin']
            )
            # Find the second occluder paired with the target.
            occluder_wall_2 = occluder_list[2]
            factor = self._retrieve_sight_angle_position_factor(
                target['shows'][0]['position']['z']
            )
            target_teleport_x = (
                occluder_wall_2['shows'][0]['position']['x'] / factor
            )
            target['teleports'] = [{
                'stepBegin': implausible_event_step,
                'stepEnd': implausible_event_step,
                'position': {
                    'x': target_teleport_x,
                    'y': target['shows'][0]['position']['y'],
                    'z': target['shows'][0]['position']['z']
                },
                'rotation': target['shows'][0]['rotation']
            }]

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

    def _teleport_backward(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)
        occluder_list = self._get_occluder_list(scene)

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder.
            # Teleport backward from the higher index to the lower index.
            occluder_index_1 = target['chosenMovement']['occluderIndices'][0]
            occluder_index_2 = target['chosenMovement']['occluderIndices'][1]
            if occluder_index_1 > occluder_index_2:
                occluder_start_index = occluder_index_1
                occluder_end_index = occluder_index_2
            else:
                occluder_start_index = occluder_index_2
                occluder_end_index = occluder_index_1
            target_teleport_x = target['chosenMovement']['positionByStep'][
                occluder_end_index
            ]
            implausible_event_step = occluder_start_index + \
                target['forces'][0]['stepBegin']

        # In fall-down scenes, swap the target from one occluder to another.
        elif self.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                OBJECT_FALL_TIME + target['shows'][0]['stepBegin']
            )
            # Find the second occluder paired with the target.
            occluder_wall_2 = occluder_list[2]
            original_x = target['shows'][0]['position']['x']
            factor = self._retrieve_sight_angle_position_factor(
                target['shows'][0]['position']['z']
            )
            # Swap starting X position, then teleport back to original X.
            target['shows'][0]['position']['x'] = (
                occluder_wall_2['shows'][0]['position']['x'] / factor
            )
            target_teleport_x = original_x

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        target['teleports'] = [{
            'stepBegin': implausible_event_step,
            'stepEnd': implausible_event_step,
            'position': {
                'x': target_teleport_x,
                'y': target['shows'][0]['position']['y'],
                'z': target['shows'][0]['position']['z']
            },
            'rotation': target['shows'][0]['rotation']
        }]

    def _move_later(self, scene: Dict[str, Any]) -> None:
        target = self._get_target(scene)
        occluder_list = self._get_occluder_list(scene)

        if self.is_move_across():
            # Delay movement so it lines up with teleport-backward movement.
            occluder_index_1 = target['chosenMovement']['occluderIndices'][0]
            occluder_index_2 = target['chosenMovement']['occluderIndices'][1]
            adjustment = abs(occluder_index_1 - occluder_index_2)
            target['shows'][0]['stepBegin'] += adjustment
            if 'forces' in target:
                target['forces'][0]['stepBegin'] += adjustment

        # In fall-down scenes, swap the target from one occluder to another.
        elif self.is_fall_down():
            # Find the second occluder paired with the target.
            occluder_wall_2 = occluder_list[2]
            factor = self._retrieve_sight_angle_position_factor(
                target['shows'][0]['position']['z']
            )
            # Swap starting X position.
            target['shows'][0]['position']['x'] = (
                occluder_wall_2['shows'][0]['position']['x'] / factor
            )

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if self.is_move_across():
            self._adjust_target_max_step_begin(default_scene)

        scene_1 = copy.deepcopy(default_scene)
        scene_1['goal']['type_list'].append(
            tags.SPATIO_TEMPORAL_CONTINUITY_Q1
        )

        scene_2 = copy.deepcopy(default_scene)
        scene_2['answer']['choice'] = IMPLAUSIBLE
        scene_2['goal']['type_list'].append(
            tags.SPATIO_TEMPORAL_CONTINUITY_Q2
        )
        self._teleport_forward(scene_2)

        scene_3 = copy.deepcopy(default_scene)
        scene_3['answer']['choice'] = IMPLAUSIBLE
        scene_3['goal']['type_list'].append(
            tags.SPATIO_TEMPORAL_CONTINUITY_Q3
        )
        self._teleport_backward(scene_3)

        scene_4 = copy.deepcopy(default_scene)
        scene_4['goal']['type_list'].append(
            tags.SPATIO_TEMPORAL_CONTINUITY_Q4
        )
        self._move_later(scene_4)

        return [scene_1, scene_2, scene_3, scene_4]

    # Override
    def _choose_fall_down_object_count(self) -> int:
        return 1

    # Override
    def _choose_fall_down_occluder_count(self) -> int:
        return 2

    # Override
    def _choose_move_across_occluder_count(self) -> int:
        return random.choices((2, 3), (60, 40))[0]

    # Override
    def _find_fall_down_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # Generate two occluders paired with the first object (the target):
        # one in the target's original position, and one in a new position.
        target_copy = copy.deepcopy(object_list[0])
        target_size = target_copy['dimensions']['x']
        factor = self._retrieve_sight_angle_position_factor(
            target_copy['shows'][0]['position']['z']
        )
        # Create a temp occluder with max scale to ensure that the copied
        # target won't be positioned too close to the original target.
        temp_occluder_pair = occluders.create_occluder(
            random.choice(materials.OCCLUDER_MATERIALS),
            random.choice(materials.METAL_MATERIALS),
            target_copy['shows'][0]['position']['x'] * factor,
            occluders.OCCLUDER_MAX_SCALE_X,
            True
        )
        # Generate a new random X position for the copied target.
        position = occluders.generate_occluder_position(target_size,
                                                        temp_occluder_pair)
        target_copy['shows'][0]['position']['x'] = position / factor
        # The copied target must be the second object in the returned list.
        print(f'ORIGINAL={object_list[0]}\nCOPY={target_copy}')
        return [object_list[0], target_copy]

    # Override
    def _find_move_across_paired_list(
        self,
        object_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # Generate two occluders paired with the first object (the target).
        return [object_list[0], object_list[0]]


class ShapeConstancySequence(IntuitivePhysicsSequence):
    GOAL_TEMPLATE = {
        'category': tags.INTUITIVE_PHYSICS,
        'domain_list': [
            tags.DOMAIN_OBJECTS,
            tags.DOMAIN_OBJECTS_MOTION,
            tags.DOMAIN_OBJECTS_PERMANENCE,
            tags.DOMAIN_OBJECTS_SOLIDITY
        ],
        'type_list': [
            tags.PASSIVE,
            tags.ACTION_NONE,
            tags.INTUITIVE_PHYSICS,
            tags.SHAPE_CONSTANCY
        ]
    }

    def __init__(
        self,
        body_template: Dict[str, Any],
        is_fall_down=False,
        is_move_across=False
    ):
        super().__init__(
            tags.SHAPE_CONSTANCY.title(),
            body_template,
            SpatioTemporalContinuitySequence.GOAL_TEMPLATE,
            is_fall_down,
            is_move_across
        )

    def _create_b(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        object_a = self._get_target(scene)

        # Use the X dimensions because the performer will always be facing that
        # side of the object.
        size_a = object_a['dimensions']['x']

        object_definition_list = (
            FALL_DOWN_OBJECT_DEFINITION_LIST if self.is_fall_down()
            else OBJECT_DEFINITION_LIST
        )
        possible_definition_list = []

        for object_definition in object_definition_list:
            if object_definition['type'] != object_a['type']:
                size_b = object_definition['dimensions']['x']
                # Ensure that object B is approx the same size as object A.
                # Object B must not be any bigger than object A or else it may
                # not be properly hidden by the paired occluder(s).
                if (
                    size_b <= size_a and
                    size_b >= (size_a - util.MAX_SIZE_DIFFERENCE)
                ):
                    possible_definition_list.append(object_definition)

        if len(possible_definition_list) == 0:
            raise exceptions.SceneException(
                f'Cannot find shape constancy substitute object {object_a}')

        definition_b = util.finalize_object_definition(
            random.choice(possible_definition_list)
        )
        object_b = util.instantiate_object(
            definition_b,
            object_a['originalLocation'],
            object_a['materialsList']
        )
        object_b['id'] = object_a['id']
        return object_b

    def _turn_a_into_b(self, scene: Dict[str, Any]) -> None:
        object_a = scene['objects'][0]
        object_b = copy.deepcopy(self._b_template)

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder.
            occluder_index = object_a['chosenMovement']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                object_a['forces'][0]['stepBegin']
            implausible_event_x = object_a['chosenMovement']['positionByStep'][
                occluder_index
            ]
            # Give object B the movement of object A.
            object_b['forces'] = copy.deepcopy(object_a['forces'])
            object_b['chosenMovement'] = object_a['chosenMovement']

        elif self.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                OBJECT_FALL_TIME + object_a['shows'][0]['stepBegin']
            )
            implausible_event_x = object_a['shows'][0]['position']['x']

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Hide object A at the implausible event step and show object B in
        # object A's old position behind the occluder.
        object_a['hides'] = [{
            'stepBegin': implausible_event_step
        }]
        object_b['shows'][0]['stepBegin'] = implausible_event_step
        object_b['shows'][0]['position']['x'] = implausible_event_x
        object_b['shows'][0]['position']['z'] = \
            object_a['shows'][0]['position']['z']

        # Add object B to the scene.
        scene['objects'].append(object_b)

    def _turn_b_into_a(self, scene: Dict[str, Any]) -> None:
        object_a = scene['objects'][0]
        object_b = copy.deepcopy(self._b_template)

        # Show object B at object A's starting position.
        object_b['shows'][0]['stepBegin'] = object_a['shows'][0]['stepBegin']
        object_b['shows'][0]['position']['x'] = \
            object_a['shows'][0]['position']['x']
        object_b['shows'][0]['position']['z'] = \
            object_a['shows'][0]['position']['z']

        if self.is_move_across():
            # Implausible event happens after target moves behind occluder.
            occluder_index = object_a['chosenMovement']['occluderIndices'][0]
            implausible_event_step = occluder_index + \
                object_a['forces'][0]['stepBegin']
            implausible_event_x = object_a['chosenMovement']['positionByStep'][
                occluder_index
            ]
            # Give object B the movement of object A.
            object_b['forces'] = copy.deepcopy(object_a['forces'])
            object_b['chosenMovement'] = object_a['chosenMovement']
            # Change the position of object A to behind the occluder.
            object_a['shows'][0]['position']['x'] = implausible_event_x

        elif self.is_fall_down():
            # Implausible event happens after target falls behind occluder.
            implausible_event_step = (
                OBJECT_FALL_TIME + object_a['shows'][0]['stepBegin']
            )
            # Swap object A with object B.
            object_b['shows'][0]['position']['y'] = \
                object_a['shows'][0]['position']['y']
            # Move object A to the ground.
            object_a['shows'][0]['position']['y'] = object_a['offset']['y']

        else:
            raise exceptions.SceneException('Unknown scene setup function!')

        # Wait to show object A at the implausible event step.
        object_a['shows'][0]['stepBegin'] = implausible_event_step

        # Hide object B at the implausible event step and show object A in
        # object B's old position behind the occluder.
        object_b['hides'] = [{
            'stepBegin': implausible_event_step
        }]

        # Add object B to the scene.
        scene['objects'].append(object_b)

    def _b_replaces_a(self, scene: Dict[str, Any]) -> None:
        object_a = scene['objects'][0]
        object_b = copy.deepcopy(self._b_template)
        # Give object A's starting position and movement to object B.
        # Don't accidentally copy the 'rotation' from the 'shows' list because
        # it's unique per object.
        object_b['shows'][0]['stepBegin'] = object_a['shows'][0]['stepBegin']
        object_b['shows'][0]['position'] = object_a['shows'][0]['position']
        if self.is_move_across():
            object_b['forces'] = object_a['forces']
            object_b['chosenMovement'] = object_a['chosenMovement']
        # Swap object A with object B.
        scene['objects'][0] = object_b

    # Override
    def _create_intuitive_physics_scenes(
        self,
        default_scene: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        self._b_template = self._create_b(default_scene)

        scene_1 = copy.deepcopy(default_scene)
        scene_1['goal']['type_list'].append(tags.SHAPE_CONSTANCY_Q1)

        scene_2 = copy.deepcopy(default_scene)
        # Object A moves behind an occluder, then object B emerges
        # from behind the occluder (implausible)
        scene_2['answer']['choice'] = IMPLAUSIBLE
        scene_2['goal']['type_list'].append(tags.SHAPE_CONSTANCY_Q2)
        self._turn_a_into_b(scene_2)
        scene_2 = self._update_scene_targets(
            scene_2,
            self._target_list + [scene_2['objects'][-1]]
        )

        scene_3 = copy.deepcopy(default_scene)
        # Object B moves behind an occluder (replacing object A's
        # movement), then object A emerges from behind the
        # occluder (implausible)
        scene_3['answer']['choice'] = IMPLAUSIBLE
        scene_3['goal']['type_list'].append(tags.SHAPE_CONSTANCY_Q3)
        self._turn_b_into_a(scene_3)
        scene_3 = self._update_scene_targets(
            scene_3,
            self._target_list + [scene_3['objects'][-1]]
        )

        scene_4 = copy.deepcopy(default_scene)
        # Object B moves normally (replacing object A's movement),
        # object A is never added to the scene (plausible)
        scene_4['goal']['type_list'].append(tags.SHAPE_CONSTANCY_Q4)
        self._b_replaces_a(scene_4)
        scene_4 = self._update_scene_targets(scene_4, [scene_4['objects'][0]])

        return [scene_1, scene_2, scene_3, scene_4]

    def _update_scene_targets(
        self,
        scene: Dict[str, Any],
        target_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update and return the given scene with info from targets in the
        given list because targets were added or removed."""
        goal_info_list = []
        for info in scene['goal']['info_list']:
            if not info.startswith('target'):
                goal_info_list.append(info)
        scene['goal']['info_list'] = self._update_list_with_object_info(
            'target',
            goal_info_list,
            target_list
        )
        return scene


class ObjectPermanenceSequenceFactory(sequences.SequenceFactory):
    def __init__(self) -> None:
        super().__init__('ObjectPermanence')

    def build(self, body_template: Dict[str, Any]) -> sequences.Sequence:
        return ObjectPermanenceSequence(body_template)


class ShapeConstancySequenceFactory(sequences.SequenceFactory):
    def __init__(self) -> None:
        super().__init__('ShapeConstancy')

    def build(self, body_template: Dict[str, Any]) -> sequences.Sequence:
        return ShapeConstancySequence(body_template)


class SpatioTemporalContinuitySequenceFactory(sequences.SequenceFactory):
    def __init__(self) -> None:
        super().__init__('SpatioTemporalContinuity')

    def build(self, body_template: Dict[str, Any]) -> sequences.Sequence:
        return SpatioTemporalContinuitySequence(body_template)


INTUITIVE_PHYSICS_SEQUENCE_LIST = [
    ObjectPermanenceSequenceFactory(),
    ShapeConstancySequenceFactory(),
    SpatioTemporalContinuitySequenceFactory()
]
