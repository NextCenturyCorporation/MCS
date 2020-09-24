import copy
import logging
import random
import uuid
from typing import Any, Dict, List, Optional, Tuple

import containers
import exceptions
import geometry
from interactive_goals import InteractiveGoal, RetrievalGoal, TraversalGoal
from interactive_plans import create_pair_plan, is_true, BoolPlan, \
    ConfusorLocationPlan, InteractivePlan, ObstructorPlan, TargetLocationPlan
import objects
import separating_axis_theorem
import sequences
import tags
import util


LAST_STEP = 600

# MAX_DISTRACTORS doesn't count the receptacles randomly generated to
# containerize other objects.
MAX_DISTRACTORS = 10
DISTRACTOR_ENCLOSED_RECEPTACLE_CHANCE = 0.333
DISTRACTOR_OPEN_RECEPTACLE_CHANCE = 0

WALL_CHOICES = [0, 1, 2, 3]
WALL_WEIGHTS = [40, 30, 20, 10]
WALL_MAX_WIDTH = 4
WALL_MIN_WIDTH = 1
WALL_Y = 1.5
WALL_HEIGHT = 3
WALL_DEPTH = 0.1
WALL_SEPARATION = 1


class AbstractObjectData():
    def __init__(
        self,
        definition: Dict[str, Any],
        template: Dict[str, Any]
    ) -> None:
        self.definition = definition
        self.template = template


class ObjectData(AbstractObjectData):
    def __init__(
        self,
        containerize_plan: BoolPlan,
        definition: Dict[str, Any],
        location_plan: Any,
        name: str,
        show: Tuple[bool, bool],
        template: Dict[str, Any]
    ) -> None:
        super().__init__(
            definition=definition,
            template=template
        )
        self.containerize = [None, None]
        if containerize_plan and containerize_plan != BoolPlan.NO_NO:
            self.containerize[0] = is_true(containerize_plan, 1)
            self.containerize[1] = is_true(containerize_plan, 2)
        self.instance = [None, None]
        self.location = [None, None]
        self.location_plan = location_plan
        self.name = name
        self.receptacle = [None, None]
        self.show = [show[0], show[1]]

    def is_back(self, scene_index: int) -> bool:
        return False

    def is_close(self, scene_index: int) -> bool:
        return False

    def is_front_and_or_back(self) -> bool:
        return (
            self.is_front(1) or self.is_back(1) or
            self.is_front(2) or self.is_back(2)
        )

    def is_front(self, scene_index: int) -> bool:
        return False

    def is_location_same(self) -> bool:
        return False

    def receptacle_or_object(self) -> Dict[str, Any]:
        return (self.receptacle[0] if self.receptacle[0] else
                (self.receptacle[1] if self.receptacle[1] else self.template))


class ConfusorData(ObjectData):
    def __init__(
        self,
        containerize_plan: BoolPlan,
        definition: Dict[str, Any],
        location_plan: ConfusorLocationPlan,
        show: Tuple[bool, bool],
        template: Dict[str, Any]
    ) -> None:
        super().__init__(
            containerize_plan=containerize_plan,
            definition=definition,
            location_plan=location_plan,
            name='confusor',
            show=show,
            template=template
        )

    def is_close(self, scene_index: int) -> bool:
        if scene_index == 1:
            return (
                self.location_plan == ConfusorLocationPlan.CLOSE_FAR or
                self.location_plan == ConfusorLocationPlan.CLOSE_CLOSE
            )

        if scene_index == 2:
            return (
                self.location_plan == ConfusorLocationPlan.NONE_CLOSE or
                self.location_plan == ConfusorLocationPlan.CLOSE_CLOSE
            )

        return False

    def is_back(self, scene_index: int) -> bool:
        if scene_index == 1:
            return self.location_plan == ConfusorLocationPlan.BACK_FRONT
        return False

    def is_front(self, scene_index: int) -> bool:
        if scene_index == 2:
            return self.location_plan == ConfusorLocationPlan.BACK_FRONT
        return False

    def is_location_same(self) -> bool:
        return (self.location_plan == ConfusorLocationPlan.CLOSE_CLOSE)


class ReceptacleData(AbstractObjectData):
    def __init__(
        self,
        definition: Dict[str, Any],
        template: Dict[str, Any],
        area_index: int,
        orientation: containers.Orientation,
        target_rotation: float,
        confusor_rotation: float
    ) -> None:
        super().__init__(
            definition=definition,
            template=template
        )
        self.area_index = area_index
        self.orientation = orientation
        self.target_rotation = target_rotation
        self.confusor_rotation = confusor_rotation


class TargetData(ObjectData):
    def __init__(
        self,
        choice: int,
        containerize_plan: BoolPlan,
        definition: Dict[str, Any],
        location_plan: TargetLocationPlan,
        template: Dict[str, Any]
    ) -> None:
        super().__init__(
            containerize_plan=containerize_plan,
            definition=definition,
            location_plan=location_plan,
            name='target',
            show=(True, True),
            template=template
        )
        self.choice = choice

    def is_back(self, scene_index: int) -> bool:
        if scene_index == 2:
            return self.location_plan == TargetLocationPlan.FRONT_BACK
        return False

    def is_front(self, scene_index: int) -> bool:
        if scene_index == 1:
            return (
                self.location_plan == TargetLocationPlan.FRONT_BACK or
                self.location_plan == TargetLocationPlan.FRONT_FRONT
            )

        if scene_index == 2:
            return self.location_plan == TargetLocationPlan.FRONT_FRONT

        return False

    def is_location_same(self) -> bool:
        return (
            self.location_plan == TargetLocationPlan.FRONT_FRONT or
            self.location_plan == TargetLocationPlan.RANDOM
        )


class InteractiveSequence(sequences.Sequence):
    """A sequence of interactive scenes that each have the same goals, targets,
    distractors, walls, materials, and performer starts, except for specific
    differences detailed in its plan."""

    def __init__(
        self,
        body_template: Dict[str, Any],
        goal: InteractiveGoal,
        plan: InteractivePlan
    ) -> None:
        self._goal = goal
        self._plan = plan
        self._no_random_obstructor = False
        super().__init__(
            ((plan.name + ' ') if plan.name else '') + goal.get_name(),
            body_template,
            goal.get_goal_template()
        )

    # Override
    def _create_scenes(
        self,
        body_template: Dict[str, Any],
        goal_template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        tries = 0
        while True:
            tries += 1
            try:
                logging.debug(
                    f'\n\n{self.get_name()} initialize scenes try {tries}\n')

                # Reset the half-finished scenes, all of their objects, their
                # bounds, and the performer start location on each new try.
                self._scene_1 = copy.deepcopy(body_template)
                self._scene_2 = copy.deepcopy(body_template)
                self._bounds_list = []
                self._common_target_list = []
                self._confusor_list_per_scene = [[], []]
                self._distractor_list = []
                self._interior_wall_list = []
                self._obstructor_list_per_scene = [[], []]
                self._receptacle_list_per_scene = [[], []]
                self._target_list_per_scene = [[], []]
                self._performer_start = self._generate_performer_start()

                self._initialize_all_objects()

                self._update_scene_at_index(self._scene_1, 1, goal_template)
                self._update_scene_at_index(self._scene_2, 2, goal_template)

                logging.debug(
                    f'\n\n{self.get_name()} initialize scenes is done\n ')

                break

            except exceptions.SceneException as e:
                logging.error(e)

        return [self._scene_1, self._scene_2]

    def _assign_confusor_location(
        self,
        confusor: ConfusorData,
        target: TargetData
    ) -> None:
        """Assign the confusor its location in each scene, as needed, either
        close to or far from the target."""

        for scene_index in [1, 2]:
            if not confusor.show[scene_index - 1]:
                continue

            if scene_index == 2 and confusor.location[0]:
                if confusor.is_location_same() and target.is_location_same():
                    confusor.location[1] = confusor.location[0]
                    continue

            if confusor.is_close(scene_index):
                confusor.location[scene_index - 1] = self._generate_close_to(
                    confusor.definition,
                    target.definition,
                    target.location[scene_index - 1],
                    self._performer_start
                )

            else:
                confusor.location[scene_index - 1] = self._generate_far_from(
                    confusor.definition,
                    target.location[scene_index - 1],
                    self._performer_start
                )

    def _assign_obstructor_location(
        self,
        target: TargetData,
        obstructor: ObjectData
    ) -> None:
        """Assign the obstructor its location in each scene, as needed, by
        moving the obstructor to the location of the target, and then moving
        the target behind the obstructor."""

        for scene_index in [1, 2]:
            if not obstructor.show[scene_index - 1]:
                continue

            # Generate an adjacent location so that the obstructor is
            # between the target and the performer start.
            location = geometry.get_adjacent_location(
                obstructor.definition,
                target.definition,
                target.location[scene_index - 1],
                self._performer_start,
                self._bounds_list,
                True
            )
            obstructor.location[scene_index - 1] = location

            if not obstructor.location[scene_index - 1]:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot position target directly '
                    f'behind obstructor:\n'
                    f'performer_start={self._performer_start}\n'
                    f'target_definition={target.definition}\n'
                    f'target_location={target.location[scene_index - 1]}\n'
                    f'obstructor_definition={obstructor.definition}')

        logging.debug(
            f'{self.get_name()} '
            f'obstructor location 1: {obstructor.location[0]}')
        logging.debug(
            f'{self.get_name()} '
            f'obstructor location 2: {obstructor.location[1]}')

    def _assign_target_and_confusor_locations(
        self,
        target: TargetData,
        confusor: Optional[ObjectData],
        obstructor: Optional[ObjectData]
    ) -> None:
        """Assign the target and the confusor their replantive locations in
        each scene, as needed, prioritizing locations in front of or in back of
        the performer start, with enough area for the obstructor, if needed."""

        # If an object is switched across scenes (in the same position),
        # use the larger object to generate the location to avoid collisions.
        # If positioned inside a receptacle, the receptacle will be larger.
        larger_object = target.receptacle_or_object()
        if confusor:
            larger_object = self._find_larger_object(
                larger_object,
                confusor.receptacle_or_object()
            )
        if obstructor:
            larger_object = self._find_larger_object(
                larger_object,
                obstructor.template
            )

        # If an object must be positioned relative to the performer_start,
        # find the locations both in front of and in back of the performer
        # using its position and rotation. Do this first because it may change
        # the performer_start.
        if target.is_front_and_or_back():
            location_front, location_back = self._generate_front_and_back(
                larger_object,
                target.is_back(2),
                target.choice
            )
            # Assumes target is either FRONT_BACK or BACK_FRONT
            target.location = (
                location_front,
                location_front if target.is_front(2) else location_back
            )
            if confusor and confusor.is_front_and_or_back():
                # Assumes confusor can't be FRONT_BACK, FRONT_FRONT, BACK_BACK
                confusor.location = (location_back, location_front)

        else:
            if confusor and confusor.is_front_and_or_back():
                location_front, location_back = self._generate_front_and_back(
                    confusor.receptacle_or_object(),
                    True
                )
                # Assumes confusor can't be FRONT_BACK, FRONT_FRONT, BACK_BACK
                confusor.location = (location_back, location_front)

            # If the target isn't positioned in the front and/or in the back,
            # (for now) it will be positioned randomly.
            target.location = self._generate_random_location(
                target.receptacle_or_object(),
                target.choice
            )

        logging.debug(
            f'{self.get_name()} target location 1: {target.location[0]}')
        logging.debug(
            f'{self.get_name()} target location 2: {target.location[1]}')

        if confusor:
            # If the confusor isn't positioned in the front and/or in the back,
            # (for now) it will be positioned close to or far from the target.
            if not confusor.is_front_and_or_back():
                self._assign_confusor_location(confusor, target)

            logging.debug(
                f'{self.get_name()} '
                f'confusor location 1: {confusor.location[0]}')
            logging.debug(
                f'{self.get_name()} '
                f'confusor location 2: {confusor.location[1]}')

        if (
            target.is_front_and_or_back() or
            confusor and confusor.is_front_and_or_back()
        ):
            # Ensure the random location of future distractors or walls won't
            # accidentally make them obstructors.
            self._no_random_obstructor = True

    def _choose_confusor(self, target: TargetData) -> Optional[ObjectData]:
        """Choose a confusor definition, create a confusor template, and
        return the confusor data to use in one or both scenes as needed.
        Assumes that both scenes won't ever need two different confusors.
        Return None if no scene needs a confusor."""

        show_in_scene_1 = is_true(self._plan.confusor, 1)
        show_in_scene_2 = is_true(self._plan.confusor, 2)

        if not show_in_scene_1 and not show_in_scene_2:
            return None

        confusor_definition = (
            self._plan.confusor_definition if self._plan.confusor_definition
            else self._choose_confusor_definition(target.definition)
        )

        # Create the confusor template at a base location, and later we'll
        # move it to its final location in each scene.
        confusor_template = util.instantiate_object(
            confusor_definition,
            geometry.ORIGIN_LOCATION
        )

        confusor = ConfusorData(
            containerize_plan=self._plan.confusor_containerize,
            definition=confusor_definition,
            location_plan=self._plan.confusor_location,
            show=(show_in_scene_1, show_in_scene_2),
            template=confusor_template
        )

        logging.debug(
            f'{self.get_name()} confusor template: {confusor_template}')

        return confusor

    def _choose_confusor_definition(
        self,
        target_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Choose and return a confusor definition for the given target."""
        confusor_definition = util.get_similar_definition(
            target_definition,
            objects.get('ALL')
        )
        if not confusor_definition:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot find suitable confusor '
                f'target={target_definition}')
        return confusor_definition

    def _choose_distractor_definition(
        self,
        target_confusor_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Choose and return a distractor definition for the given objects."""
        shape_list = [item['shape'][-1] for item in target_confusor_list]
        for _ in range(util.MAX_TRIES):
            definition = self._goal.choose_definition()
            shape = (
                definition['shape'][-1]
                if isinstance(definition['shape'], list)
                else definition['shape']
            )
            # Cannot have the same shape as an existing target or confusor
            # object, so we don't unintentionally generate a new confusor.
            if shape not in shape_list:
                break
            definition = None
        return definition

    def _choose_obstructor(
        self,
        obstructed_object: Dict[str, Any]
    ) -> Optional[ObjectData]:
        """Choose an obstructor definition, create an obstructor template,
        and return the obstructor data to use in one or both scenes as needed.
        Assumes that both scenes won't ever need two different obstructors.
        Return None if no scene needs an obstructor."""

        # Currently the obstructor will never appear in the first scene.
        show_in_scene_1 = False
        show_in_scene_2 = (self._plan.obstructor != ObstructorPlan.NONE_NONE)

        if not show_in_scene_1 and not show_in_scene_2:
            return None

        # TODO What if we can't find an obstructor for the object?
        obstructor_definition = (
            self._plan.obstructor_definition
            if self._plan.obstructor_definition
            else self._choose_obstructor_definition(
                obstructed_object,
                (self._plan.obstructor == ObstructorPlan.NONE_VISION)
            )
        )

        # Create the obstructor template at a base location, and later we'll
        # move it to its final location in each scene.
        obstructor_template = util.instantiate_object(
            obstructor_definition,
            geometry.ORIGIN_LOCATION
        )

        logging.debug(
            f'{self.get_name()} obstructor template: {obstructor_template}')

        return ObjectData(
            containerize_plan=None,
            definition=obstructor_definition,
            location_plan=None,
            name='obstructor',
            show=(show_in_scene_1, show_in_scene_2),
            template=obstructor_template
        )

    def _choose_obstructor_definition(
        self,
        target_definition: Dict[str, Any],
        obstruct_vision: bool
    ) -> Dict[str, Any]:
        """Choose and return an obstructor definition for the given target."""
        definition_list = geometry.get_wider_and_taller_defs(
            target_definition,
            obstruct_vision
        )
        if not definition_list:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot find suitable obstructor '
                f'target={self._target_definition}')
        definition, obstructor_angle = random.choice(definition_list)
        definition = util.finalize_object_definition(definition)
        if 'rotation' not in definition:
            definition['rotation'] = {
                'x': 0,
                'y': 0,
                'z': 0
            }
        # Note that this rotation must be also modified with the final
        # performer start Y.
        definition['rotation']['y'] += obstructor_angle
        return definition

    def _choose_receptacle(
        self,
        target: TargetData,
        confusor: Optional[ObjectData]
    ) -> Optional[ReceptacleData]:
        """Choose a receptacle definition, create a receptacle template, and
        return the receptacle data to use in one or both scenes as needed.
        Assumes that both scenes won't ever need two different receptacles.
        Return None if containerization is impossible."""

        definition_list = containers.retrieve_enclosable_definition_list()
        random.shuffle(definition_list)

        receptacle_definition = None
        area_index = None
        orientation = None
        target_rotation = None
        confusor_rotation = None

        # If needed, find an enclosable receptacle that can hold both the
        # target and the confusor together.
        if self._must_containerize_together(target, confusor):
            for receptacle_definition in definition_list:
                valid_containment = containers.can_contain_both(
                    receptacle_definition,
                    target.template,
                    confusor.template
                )
                if valid_containment:
                    break
                valid_containment = None

            if not valid_containment:
                return None

            (
                receptacle_definition,
                area_index,
                orientation,
                target_rotation,
                confusor_rotation
            ) = valid_containment

        # Else, find an enclosable receptacle that can hold either the target
        # or confusor individually.
        else:
            target_template = (
                target.template
                if (target.containerize[0] or target.containerize[1])
                else None
            )

            confusor_template = (
                confusor.template
                if (confusor and (
                    confusor.containerize[0] or confusor.containerize[1]
                ))
                else None
            )

            valid_containment_list = containers.get_enclosable_containments(
                (target_template, confusor_template),
                definition_list
            )

            if len(valid_containment_list) == 0:
                return None

            valid_containment = random.choice(valid_containment_list)
            receptacle_definition, area_index, angles = valid_containment
            target_rotation = angles[0]
            # The angles list should have a length of 2
            # if the confusor template is not None
            confusor_rotation = (angles[1] if len(angles) == 2 else None)

        # Create the receptacle template at a base location, and later we'll
        # move it to its final location in each scene.
        receptacle_template = util.instantiate_object(
            receptacle_definition,
            geometry.ORIGIN_LOCATION
        )

        receptacle = ReceptacleData(
            definition=receptacle_definition,
            template=receptacle_template,
            area_index=area_index,
            orientation=orientation,
            target_rotation=target_rotation,
            confusor_rotation=confusor_rotation
        )

        target.receptacle = [
            receptacle.template if target.containerize[0] else None,
            receptacle.template if target.containerize[1] else None
        ]

        if confusor:
            confusor.receptacle = [
                receptacle.template if confusor.containerize[0] else None,
                receptacle.template if confusor.containerize[1] else None
            ]

        logging.debug(
            f'{self.get_name()} receptacle template: {receptacle.template}')

        return receptacle

    def _choose_target(self) -> TargetData:
        """Choose a target definition, create a target template, and return
        the target data to use in both scenes. Assumes that both scenes won't
        ever need two different targets."""

        target_choice = 0
        # TODO Randomly choose a target from the goal to use in both scenes.
        # target_choice = random.randint(0, len(target_rule_list) - 1)

        # Create all targets in the sequence that are before the chosen target.
        self._common_target_list = self._create_target_list(
            [],
            end_index=target_choice
        )

        # Choose a definition for the chosen target to use in both scenes.
        target_definition = (
            self._plan.target_definition if self._plan.target_definition
            else self._goal.choose_target_definition(target_choice)
        )

        # Create the target template at a base location, and later we'll
        # move it to its final location in each scene.
        target_template = util.instantiate_object(
            target_definition,
            geometry.ORIGIN_LOCATION
        )

        target = TargetData(
            choice=target_choice,
            containerize_plan=self._plan.target_containerize,
            definition=target_definition,
            location_plan=self._plan.target_location,
            template=target_template
        )

        logging.debug(
            f'{self.get_name()} target template: {target_template}')

        return target

    def _create_interior_wall(
        self,
        wall_material: str,
        wall_colors: List[str],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]],
        keep_unobstructed_list: List[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Create and return a randomly positioned interior wall with the
        given material and colors. If keep_unobstructed_list is not None, the
        wall won't obstruct the line between the performer_start and the
        objects in keep_unobstructed_list."""

        tries = 0
        performer_rect = geometry.find_performer_rect(
            performer_start['position']
        )
        performer_poly = geometry.rect_to_poly(performer_rect)

        while tries < util.MAX_TRIES:
            rotation = random.choice((0, 90, 180, 270))
            x_position = geometry.random_position_x()
            z_position = geometry.random_position_z()
            x_width = round(
                random.uniform(WALL_MIN_WIDTH, WALL_MAX_WIDTH),
                geometry.POSITION_DIGITS
            )

            # Ensure the wall is not too close to the room's parallel walls.
            if (
                (rotation == 0 or rotation == 180) and
                (
                    z_position < (geometry.ROOM_Z_MIN + WALL_SEPARATION) or
                    z_position > (geometry.ROOM_Z_MAX - WALL_SEPARATION)
                )
            ) or (
                (rotation == 90 or rotation == 270) and
                (
                    x_position < (geometry.ROOM_X_MIN + WALL_SEPARATION) or
                    x_position > (geometry.ROOM_X_MAX - WALL_SEPARATION)
                )
            ):
                continue

            wall_rect = geometry.calc_obj_coords(
                x_position,
                z_position,
                x_width,
                WALL_DEPTH,
                0,
                0,
                rotation
            )
            wall_poly = geometry.rect_to_poly(wall_rect)

            # Ensure parallel walls are not too close one another.
            boundary_rect = geometry.calc_obj_coords(
                x_position,
                z_position,
                x_width + WALL_SEPARATION,
                WALL_DEPTH + WALL_SEPARATION,
                0,
                0,
                rotation
            )

            is_too_close = any(
                separating_axis_theorem.sat_entry(boundary_rect, bounds)
                for bounds in bounds_list
            )

            is_ok = (
                not wall_poly.intersects(performer_poly) and
                geometry.rect_within_room(wall_rect) and
                not is_too_close
            )

            if is_ok and keep_unobstructed_list:
                for instance in keep_unobstructed_list:
                    if (
                        'locationParent' not in instance and
                        geometry.does_fully_obstruct_target(
                            performer_start['position'],
                            instance,
                            wall_poly
                        )
                    ):
                        is_ok = False
                        break

            if is_ok:
                break

            tries += 1

        if tries < util.MAX_TRIES:
            interior_wall = {
                'id': 'wall_' + str(uuid.uuid4()),
                'materials': [wall_material],
                'type': 'cube',
                'kinematic': 'true',
                'structure': 'true',
                'mass': 200,
                'info': wall_colors
            }
            interior_wall['shows'] = [{
                'stepBegin': 0,
                'scale': {'x': x_width, 'y': WALL_HEIGHT, 'z': WALL_DEPTH},
                'rotation': {'x': 0, 'y': rotation, 'z': 0},
                'position': {'x': x_position, 'y': WALL_Y, 'z': z_position},
                'boundingBox': wall_rect
            }]
            return interior_wall

        return None

    def _create_target_list(
        self,
        target_validation_list: List[Dict[str, float]],
        start_index: int = None,
        end_index: int = None
    ) -> List[Dict[str, Any]]:
        """Create and return each of the goal's targets between the start_index
        and the end_index. Changes the bounds_list."""

        valid_start_index = 0 if start_index is None else start_index

        # Only create targets up to the given index, or create each of the
        # targets if no end_index was given. Keep each existing target.
        valid_end_index = (
            self._goal.get_target_count() if end_index is None else end_index
        )

        if valid_start_index >= valid_end_index:
            return []

        target_list = []
        for i in range(valid_start_index, valid_end_index):
            definition = self._goal.choose_target_definition(i)
            for _ in range(util.MAX_TRIES):
                location, bounds_list = self._goal.choose_location(
                    definition,
                    self._performer_start,
                    self._bounds_list
                )
                if self._goal.validate_target_location(
                    i,
                    location,
                    target_validation_list,
                    self._performer_start
                ):
                    break
                location = None
            if not location:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot find suitable location '
                    f'target={definition}')
            self._bounds_list = bounds_list
            instance = util.instantiate_object(definition, location)
            target_list.append(instance)

        return target_list

    def _find_larger_object(
        self,
        one: Dict[str, Any],
        two: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return the larger of the two given objects."""
        # TODO Handle if one object has larger X but other object has larger Z
        return one if (
            one['dimensions']['x'] > two['dimensions']['x'] or
            one['dimensions']['z'] > two['dimensions']['z']
        ) else two

    def _finalize_object_location(
        self,
        scene_index: int,
        object: ObjectData,
        receptacle: Optional[ReceptacleData],
        receptacle_id: Optional[str],
        rotation: Optional[float]
    ) -> None:
        """Finalize the location of the given object in the given scene, which
        may or may not be inside a copy of the given receptacle. Changes the
        bounds_list."""

        if object.containerize[scene_index - 1]:
            object.receptacle[scene_index - 1] = copy.deepcopy(
                receptacle.template
            )
            object.receptacle[scene_index - 1]['id'] = receptacle_id

            # Update the Y position of the location to use the positionY
            # from the receptacle definition.
            object.location[scene_index - 1]['position']['y'] = \
                receptacle.definition.get('positionY', 0)

            # Move the receptacle to take the original location of the object,
            # then position the object inside the receptacle.
            util.move_to_location(
                receptacle.definition,
                object.receptacle[scene_index - 1],
                object.location[scene_index - 1],
                geometry.generate_object_bounds(
                    receptacle.definition['dimensions'],
                    receptacle.definition['offset']
                    if 'offset' in receptacle.definition
                    else None,
                    object.location[scene_index - 1]['position'],
                    object.location[scene_index - 1]['rotation']
                ),
                object.definition
            )

            containers.put_object_in_container(
                object.definition,
                object.instance[scene_index - 1],
                object.receptacle[scene_index - 1],
                receptacle.definition,
                receptacle.area_index,
                rotation
            )

            self._bounds_list.append(
                object.receptacle[scene_index - 1]['shows'][0]['boundingBox']
            )

        else:
            util.move_to_location(
                object.definition,
                object.instance[scene_index - 1],
                object.location[scene_index - 1],
                geometry.generate_object_bounds(
                    object.definition['dimensions'],
                    object.definition['offset']
                    if 'offset' in object.definition
                    else None,
                    object.location[scene_index - 1]['position'],
                    object.location[scene_index - 1]['rotation']
                ),
                object.definition
            )

            self._bounds_list.append(
                object.instance[scene_index - 1]['shows'][0]['boundingBox']
            )

    def _finalize_obstructor_location(
        self,
        obstructor: Optional[ObjectData]
    ) -> None:
        """Finalize the location of the obstructor. Changes the bounds_list."""

        for scene_index in [1, 2]:
            if not obstructor or not obstructor.show[scene_index - 1]:
                continue

            obstructor.instance[scene_index - 1] = copy.deepcopy(
                obstructor.template
            )

            util.move_to_location(
                obstructor.definition,
                obstructor.instance[scene_index - 1],
                obstructor.location[scene_index - 1],
                geometry.generate_object_bounds(
                    obstructor.definition['dimensions'],
                    obstructor.definition['offset']
                    if 'offset' in obstructor.definition
                    else None,
                    obstructor.location[scene_index - 1]['position'],
                    obstructor.location[scene_index - 1]['rotation']
                ),
                obstructor.definition
            )

            self._bounds_list.append(
                obstructor.instance[scene_index - 1]['shows'][0]['boundingBox']
            )

    def _finalize_target_and_confusor_locations(
        self,
        target: TargetData,
        confusor: Optional[ObjectData],
        receptacle: Optional[ObjectData],
        confusor_receptacle_id: int
    ) -> None:
        """Finalize the location of the target and the confusor, which may or
        may not be inside one or two receptacles. Changes the bounds_list."""

        for scene_index in [1, 2]:
            target.instance[scene_index - 1] = copy.deepcopy(target.template)
            if confusor and confusor.show[scene_index - 1]:
                confusor.instance[scene_index - 1] = copy.deepcopy(
                    confusor.template
                )

            if self._must_containerize_together(target, confusor, scene_index):
                target.receptacle[scene_index - 1] = copy.deepcopy(
                    receptacle.template
                )

                # Update the Y position of the location to use the positionY
                # from the receptacle definition.
                target.location[scene_index - 1]['position']['y'] = \
                    receptacle.definition.get('positionY', 0)

                # Move the receptacle to take the original location of the
                # target, then position both the target and the confusor inside
                # the receptacle adjacent to one another.
                util.move_to_location(
                    receptacle.definition,
                    target.receptacle[scene_index - 1],
                    target.location[scene_index - 1],
                    geometry.generate_object_bounds(
                        receptacle.definition['dimensions'],
                        receptacle.definition['offset']
                        if 'offset' in receptacle.definition
                        else None,
                        target.location[scene_index - 1]['position'],
                        target.location[scene_index - 1]['rotation']
                    ),
                    target.definition
                )

                containers.put_objects_in_container(
                    target.definition,
                    target.instance[scene_index - 1],
                    confusor.definition,
                    confusor.instance[scene_index - 1],
                    target.receptacle[scene_index - 1],
                    receptacle.definition,
                    receptacle.area_index,
                    receptacle.orientation,
                    receptacle.target_rotation,
                    receptacle.confusor_rotation
                )

                self._bounds_list.append(
                    target.receptacle[scene_index - 1]['shows'][0][
                        'boundingBox'
                    ]
                )

            else:
                self._finalize_object_location(
                    scene_index,
                    target,
                    receptacle,
                    receptacle.template['id'] if receptacle else None,
                    receptacle.target_rotation if receptacle else None
                )

                if confusor and confusor.show[scene_index - 1]:
                    self._finalize_object_location(
                        scene_index,
                        confusor,
                        receptacle,
                        confusor_receptacle_id if receptacle else None,
                        receptacle.confusor_rotation if receptacle else None
                    )

    def _generate_common_goal_type_list(
        self,
        scene_index: int,
        prefix: str
    ) -> List[str]:
        """Return the type list of common scene tags for the goal of the scene
        with the given index."""

        type_list = [prefix, self.get_name()]

        type_list.append(f'{prefix} target {tags.get_containerize_tag(is_true(self._plan.target_containerize, scene_index))}')  # noqa: E501

        type_list.append(f'{prefix} confusor {tags.get_exists_tag(is_true(self._plan.confusor, scene_index))}')  # noqa: E501

        if is_true(self._plan.confusor, scene_index):
            type_list.append(f'{prefix} confusor {tags.get_containerize_tag(is_true(self._plan.confusor_containerize, scene_index))}')  # noqa: E501

        return type_list

    def _generate_front_and_back(
        self,
        definition: Dict[str, Any],
        generate_back: bool,
        is_target: int = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a location in front of and (if needed) in back of the
        performer's start location. May change the global performer_start if
        it's needed to generate the two locations. Return the front and back
        locations."""

        location_front = None
        location_back = None

        for _ in range(util.MAX_TRIES):
            location_front = self._identify_front(
                self._goal,
                self._performer_start,
                definition,
                is_target
            )
            if location_front:
                if generate_back:
                    location_back = self._identify_back(
                        self._goal,
                        self._performer_start,
                        definition,
                        is_target
                    )
                    if location_back:
                        break
                else:
                    break
            location_front = None
            location_back = None
            self._performer_start = self._generate_performer_start()

        if not generate_back and not location_front:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position performer start in '
                f'front of object={definition}')

        if generate_back and (not location_front or not location_back):
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position performer start in '
                f'front of and in back of object={definition}')

        return location_front, location_back

    def _generate_close_to(
        self,
        object_definition: Dict[str, Any],
        target_definition: Dict[str, Any],
        target_location: Dict[str, float],
        performer_start: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """Generate and return a new location close to the given target
        location."""

        location_close = geometry.get_adjacent_location(
            object_definition,
            target_definition,
            target_location,
            performer_start,
            self._bounds_list
        )

        if not location_close:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position close to target: '
                f'object={object_definition} target={target_definition}')

        return location_close

    def _generate_far_from(
        self,
        object_definition: Dict[str, Any],
        target_location: Dict[str, float],
        performer_start: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """Generate and return a new location far from the given target
        location."""

        for _ in range(util.MAX_TRIES):
            bounds_list_copy = copy.deepcopy(self._bounds_list)
            location_far = geometry.calc_obj_pos(
                performer_start['position'],
                bounds_list_copy,
                object_definition
            )
            if not geometry.are_adjacent(
                target_location,
                location_far,
                distance=geometry.MIN_OBJECTS_SEPARATION_DISTANCE
            ):
                break
            location_far = None

        if not location_far:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position far from target: '
                f'object={object_definition} target={target_location}')

        self._bounds_list = bounds_list_copy
        return location_far

    def _generate_performer_start(self) -> Dict[str, Dict[str, float]]:
        """Generate and return the performer's start location dict."""
        return {
            'position': {
                'x': round(random.uniform(
                    geometry.ROOM_X_MIN + util.PERFORMER_HALF_WIDTH,
                    geometry.ROOM_X_MAX - util.PERFORMER_HALF_WIDTH
                ), geometry.POSITION_DIGITS),
                'y': 0,
                'z': round(random.uniform(
                    geometry.ROOM_Z_MIN + util.PERFORMER_HALF_WIDTH,
                    geometry.ROOM_Z_MAX - util.PERFORMER_HALF_WIDTH
                ), geometry.POSITION_DIGITS)
            },
            'rotation': {
                'x': 0,
                'y': geometry.random_rotation(),
                'z': 0
            }
        }

    def _generate_random_location(
        self,
        definition: Dict[str, Any],
        target_choice: int
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a random location and return it twice."""

        for _ in range(util.MAX_TRIES):
            location, bounds_list = self._goal.choose_location(
                definition,
                self._performer_start,
                self._bounds_list
            )
            if self._goal.validate_target_location(
                target_choice,
                location,
                self._common_target_list,
                self._performer_start
            ):
                break
            location = None

        if not location:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot randomly position '
                f'target={definition}')

        self._bounds_list = bounds_list
        return location, location

    def _get_target_confusor_list(self) -> List[Dict[str, Any]]:
        combined = self._target_list_per_scene + self._confusor_list_per_scene
        return [
            instance for object_list in combined for instance in object_list
        ]

    def _identify_front(
        self,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        definition: Dict[str, Any],
        target_choice: int = None
    ) -> Dict[str, Any]:
        """Find and return a location in front of the given performer_start."""

        for _ in range(util.MAX_TRIES):
            location_front = geometry.get_location_in_front_of_performer(
                performer_start,
                definition
            )
            if location_front:
                if target_choice is None:
                    break
                elif goal.validate_target_location(
                    target_choice,
                    location_front,
                    self._common_target_list,
                    performer_start
                ):
                    break
            location_front = None

        return location_front

    def _identify_back(
        self,
        goal: InteractiveGoal,
        performer_start: Dict[str, float],
        definition: Dict[str, Any],
        target_choice: int = None
    ) -> Dict[str, Any]:
        """Find and return a location in back of the given performer_start."""

        for _ in range(util.MAX_TRIES):
            location_back = geometry.get_location_in_back_of_performer(
                performer_start,
                definition
            )
            if location_back:
                if target_choice is None:
                    break
                elif goal.validate_target_location(
                    target_choice,
                    location_back,
                    self._common_target_list,
                    performer_start
                ):
                    break
            location_back = None

        return location_back

    def _initialize_distractor_list(self) -> None:
        """Create this sequence's distractors. Changes the distractor_list and
        the bounds_list."""

        target_confusor_list = self._get_target_confusor_list()

        number = random.randint(0, MAX_DISTRACTORS)
        logging.debug(f'{self.get_name()} {number} distractors')

        for _ in range(number + 1):
            definition = self._choose_distractor_definition(
                target_confusor_list
            )

            for _ in range(util.MAX_TRIES):
                location, bounds_list = self._goal.choose_location(
                    definition,
                    self._performer_start,
                    self._bounds_list
                )
                is_ok = True
                if is_ok and self._no_random_obstructor:
                    for target_or_confusor in target_confusor_list:
                        if geometry.does_fully_obstruct_target(
                            self._performer_start['position'],
                            target_or_confusor,
                            geometry.get_bounding_polygon(location)
                        ):
                            is_ok = False
                            break
                if is_ok:
                    break
                location = False

            if not location:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot find suitable location '
                    f'distractor={definition}')

            self._bounds_list = bounds_list
            instance = util.instantiate_object(definition, location)
            self._distractor_list.append(instance)

            receptacle_instance = None
            if random.random() < DISTRACTOR_ENCLOSED_RECEPTACLE_CHANCE:
                receptacle_instance = self._move_into_receptacle(
                    definition,
                    instance,
                    self._performer_start,
                    self._bounds_list
                )
            if random.random() < DISTRACTOR_OPEN_RECEPTACLE_CHANCE:
                receptacle_instance = self._move_onto_receptacle(
                    instance,
                    self._performer_start,
                    self._bounds_list
                )
            if receptacle_instance:
                self._distractor_list.append(receptacle_instance)

    def _initialize_interior_wall_list(self) -> None:
        """Create this sequence's interior walls. Changes the
        interior_wall_list and the bounds_list."""

        # All scenes will have the same room wall material/colors.
        room_wall_material_name = self._scene_1['wallMaterial']
        room_wall_colors = self._scene_1['wallColors']

        keep_unobstructed_list = (
            self._get_target_confusor_list() if self._no_random_obstructor
            else None
        )

        number = random.choices(WALL_CHOICES, weights=WALL_WEIGHTS, k=1)[0]
        logging.debug(f'{self.get_name()} {number} interior walls')

        for _ in range(number + 1):
            wall = self._create_interior_wall(
                room_wall_material_name,
                room_wall_colors,
                self._performer_start,
                self._bounds_list,
                keep_unobstructed_list
            )
            if wall:
                self._interior_wall_list.append(wall)
                self._bounds_list.append(wall['shows'][0]['boundingBox'])

    def _initialize_all_objects(self) -> None:
        """
        Initialize this sequence's objects:
        - 1. Create objects that may change in each scene (like targets).
        - 2. Containerize objects as needed by this sequence's plan.
        - 3. Move objects into locations specific to each scene.
        - 4. Save objects specific to each scene.
        - 5. Create all other objects shared by both scenes (like distractors).
        """

        # Initialize ObjectData variables
        target = None
        confusor = None
        obstructor = None
        receptacle = None

        # Create the target, confusor, and receptacle to use in either scene as
        # needed. Keep trying if the receptacle must containerize the target
        # and/or the confusor but no choice is big enough to do so.
        for _ in range(util.MAX_TRIES):
            # Use the first goal for the pair now, and later copy it and modify
            # the copy that will be the second goal.
            target = self._choose_target()

            confusor = self._choose_confusor(target)

            if self._must_containerize_either(target, confusor):
                receptacle = self._choose_receptacle(target, confusor)

                # If no receptacle is big enough to containerize the target
                # and/or the confusor, choose a new target and a new confusor.
                if not receptacle:
                    target = None
                    confusor = None

            if target:
                break

        if not target:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot create enclosable receptacle')

        # Create the obstructor to use in either scene as needed.
        obstructor = self._choose_obstructor(
            # Use the larger of the receptacle or the target object.
            target.receptacle_or_object()
        )

        self._assign_target_and_confusor_locations(
            target,
            confusor,
            obstructor
        )

        # The performer_start won't be modified past here.
        logging.debug(
            f'{self.get_name()} performer start: {self._performer_start}')

        if obstructor:
            self._assign_obstructor_location(target, obstructor)

        # Create a new ID so it's not the same ID used by the target's instance
        # of the receptacle.
        confusor_receptacle_id = str(uuid.uuid4())

        self._finalize_target_and_confusor_locations(
            target,
            confusor,
            receptacle,
            confusor_receptacle_id
        )

        self._finalize_obstructor_location(obstructor)

        self._log_objects(target, confusor, obstructor)

        self._save_scene_objects(1, target, confusor, obstructor)
        self._save_scene_objects(2, target, confusor, obstructor)

        # Create all the rest of the common targets and add them to each scene.
        common_target_list = self._create_target_list(
            [
                target for target_list in self._target_list_per_scene
                for target in target_list
            ],
            start_index=(len(self._common_target_list) + 1)
        )
        self._target_list_per_scene[0].extend(common_target_list)
        self._target_list_per_scene[1].extend(common_target_list)

        self._initialize_distractor_list()
        self._initialize_interior_wall_list()

    def _log_objects(
        self,
        target: TargetData,
        confusor: Optional[ConfusorData],
        obstructor: Optional[ObjectData]
    ) -> None:
        """Log the given objects."""

        for item in [target, confusor, obstructor]:
            if item:
                for scene_index in [1, 2]:
                    if item.instance[scene_index - 1]:
                        logging.info(
                            f'{self.get_name()} '
                            f'{item.name}_{scene_index} '
                            f'{item.instance[scene_index - 1]["type"]} '
                            f'{item.instance[scene_index - 1]["id"]}')
                    else:
                        logging.info(
                            f'{self.get_name()} '
                            f'{item.name}_{scene_index} None')
                    if item.receptacle[scene_index - 1]:
                        logging.info(
                            f'{self.get_name()} '
                            f'{item.name}_receptacle_{scene_index} '
                            f'{item.receptacle[scene_index - 1]["type"]} '
                            f'{item.receptacle[scene_index - 1]["id"]}')
                    else:
                        logging.info(
                            f'{self.get_name()} '
                            f'{item.name}_receptacle_{scene_index} None')

    def _move_into_receptacle(
        self,
        object_definition: Dict[str, Any],
        object_instance: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]]
    ) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object into
        the new receptacle. Changes the bounds_list."""
        # Only a pickupable object can be positioned inside a receptacle.
        if not object_instance.get('pickupable', False):
            return None

        # Please note that an enclosable receptacle (that can have objects
        # positioned inside of it) may also be called a "container".
        definition_list = containers.retrieve_enclosable_definition_list()
        random.shuffle(definition_list)

        for definition in definition_list:
            receptacle_definition = util.finalize_object_definition(definition)
            containment = containers.how_can_contain(
                receptacle_definition,
                object_instance
            )
            if containment:
                location = geometry.calc_obj_pos(
                    performer_start['position'],
                    bounds_list,
                    receptacle_definition
                )
                if location:
                    receptacle_instance = util.instantiate_object(
                        receptacle_definition,
                        location
                    )
                    area, angles = containment
                    containers.put_object_in_container(
                        object_definition,
                        object_instance,
                        receptacle_instance,
                        receptacle_definition,
                        area,
                        angles[0]
                    )
                    return receptacle_instance
        return None

    def _move_onto_receptacle(
        self,
        object_instance: Dict[str, Any],
        performer_start: Dict[str, Dict[str, float]],
        bounds_list: List[List[Dict[str, float]]]
    ) -> Dict[str, Any]:
        """Create and return a receptacle object, moving the given object onto
        the new receptacle. Changes the bounds_list."""
        # TODO MCS-146 Position objects on top of receptacles.
        return None

    def _must_containerize_either(
        self,
        target: TargetData,
        confusor: Optional[ConfusorData]
    ) -> bool:
        """Return if either the target or the confusor must be positioned
        inside an enclosable receptacle in either scene."""
        return (target.containerize[0] or target.containerize[1] or (
            confusor and
            (confusor.containerize[0] or confusor.containerize[1])
        ))

    def _must_containerize_together(
        self,
        target: TargetData,
        confusor: Optional[ConfusorData],
        scene_index: int = None
    ) -> bool:
        """Return if both the target and the confusor must be positioned
        inside the same enclosable receptacle."""
        if scene_index is None:
            return (
                self._must_containerize_together(target, confusor, 0) or
                self._must_containerize_together(target, confusor, 1)
            )
        return (confusor and (
            target.containerize[scene_index - 1] and
            confusor.containerize[scene_index - 1] and
            confusor.is_close(scene_index)
        ))

    def _save_scene_objects(
        self,
        scene_index: int,
        target: TargetData,
        confusor: Optional[ConfusorData],
        obstructor: Optional[ObjectData]
    ) -> None:
        """Save the objects for the scene with the given index."""

        index = scene_index - 1

        self._target_list_per_scene[index] = self._common_target_list + \
            [target.instance[index]]

        if target.receptacle[index]:
            self._receptacle_list_per_scene[index].append(
                target.receptacle[index]
            )

        if confusor and confusor.instance[index]:
            self._confusor_list_per_scene[index].append(
                confusor.instance[index]
            )

            if confusor.receptacle[index]:
                self._receptacle_list_per_scene[index].append(
                    confusor.receptacle[index]
                )

        if obstructor and obstructor.instance[index]:
            self._obstructor_list_per_scene[index].append(
                obstructor.instance[index]
            )

    def _update_scene_at_index(
        self,
        scene: Dict[str, Any],
        scene_index: int,
        goal_template: Dict[str, Any]
    ) -> None:
        """Update the given scene with its metadata like all of its objects."""
        scene['performerStart'] = self._performer_start
        scene['goal'] = copy.deepcopy(goal_template)
        scene['goal']['last_step'] = LAST_STEP
        scene['goal'] = self._goal.update_goal_config(
            scene['goal'],
            self._target_list_per_scene[scene_index - 1]
        )
        scene = self._update_scene_objects(scene, {
            'target': self._target_list_per_scene[scene_index - 1],
            'confusor': self._confusor_list_per_scene[scene_index - 1],
            'distractor': (
                self._distractor_list +
                self._receptacle_list_per_scene[scene_index - 1]
            ),
            'obstructor': self._obstructor_list_per_scene[scene_index - 1],
            'wall': self._interior_wall_list
        })
        if scene_index == 1:
            self._update_scene_1_goal_type(scene)
        if scene_index == 2:
            self._update_scene_2_goal_type(scene)

    def _update_scene_1_goal_type(self, scene: Dict[str, Any]) -> None:
        """Update the goal's type list in scene 1."""

        prefix = 'pair scene 1'
        scene['goal']['type_list'].extend(
            self._generate_common_goal_type_list(1, prefix)
        )

        if (
            self._plan.target_location == TargetLocationPlan.FRONT_BACK or
            self._plan.target_location == TargetLocationPlan.FRONT_FRONT
        ):
            scene['goal']['type_list'].append(f'{prefix} target {tags.OBJECT_LOCATION_FRONT}')  # noqa: E501
        else:
            scene['goal']['type_list'].append(f'{prefix} target {tags.OBJECT_LOCATION_RANDOM}')  # noqa: E501

        if is_true(self._plan.confusor, 1):
            if self._plan.confusor_location == ConfusorLocationPlan.BACK_FRONT:
                scene['goal']['type_list'].append(f'{prefix} confusor {tags.OBJECT_LOCATION_BACK}')  # noqa: E501
            elif (
                self._plan.confusor_location ==
                ConfusorLocationPlan.CLOSE_FAR or
                self._plan.confusor_location ==
                ConfusorLocationPlan.CLOSE_CLOSE
            ):
                scene['goal']['type_list'].append(f'{prefix} confusor {tags.OBJECT_LOCATION_CLOSE}')  # noqa: E501

        scene['goal']['type_list'].append(f'{prefix} obstructor {tags.get_exists_tag(False)}')  # noqa: E501

    def _update_scene_2_goal_type(self, scene: Dict[str, Any]) -> None:
        """Update the goal's type list in scene 2."""

        prefix = 'pair scene 2'
        scene['goal']['type_list'].extend(
            self._generate_common_goal_type_list(2, prefix)
        )

        if self._plan.target_location == TargetLocationPlan.FRONT_BACK:
            scene['goal']['type_list'].append(f'{prefix} target {tags.OBJECT_LOCATION_BACK}')  # noqa: E501
        elif self._plan.target_location == TargetLocationPlan.FRONT_FRONT:
            scene['goal']['type_list'].append(f'{prefix} target {tags.OBJECT_LOCATION_FRONT}')  # noqa: E501
        else:
            scene['goal']['type_list'].append(f'{prefix} target {tags.OBJECT_LOCATION_RANDOM}')  # noqa: E501

        if is_true(self._plan.confusor, 2):
            if self._plan.confusor_location == ConfusorLocationPlan.BACK_FRONT:
                scene['goal']['type_list'].append(f'{prefix} confusor {tags.OBJECT_LOCATION_FRONT}')  # noqa: E501
            elif (
                self._plan.confusor_location ==
                ConfusorLocationPlan.NONE_CLOSE or
                self._plan.confusor_location ==
                ConfusorLocationPlan.CLOSE_CLOSE
            ):
                scene['goal']['type_list'].append(f'{prefix} confusor {tags.OBJECT_LOCATION_CLOSE}')  # noqa: E501
            elif (
                self._plan.confusor_location ==
                ConfusorLocationPlan.NONE_FAR or
                self._plan.confusor_location ==
                ConfusorLocationPlan.CLOSE_FAR
            ):
                scene['goal']['type_list'].append(f'{prefix} confusor {tags.OBJECT_LOCATION_FAR}')  # noqa: E501

        scene['goal']['type_list'].append(f'{prefix} obstructor {tags.get_exists_tag(self._plan.obstructor != ObstructorPlan.NONE_NONE)}')  # noqa: E501

        if self._plan.obstructor != ObstructorPlan.NONE_NONE:
            obstruct_vision = (tags.get_obstruct_vision_tag(
                self._plan.obstructor == ObstructorPlan.NONE_VISION))
            scene['goal']['type_list'].append(f'{prefix} obstructor {obstruct_vision}')  # noqa: E501


class InteractiveSequenceFactory(sequences.SequenceFactory):
    def __init__(self, goal: InteractiveGoal) -> None:
        super().__init__(goal.get_name().capitalize())
        self.goal = goal

    def build(self, body_template: Dict[str, Any]) -> sequences.Sequence:
        return InteractiveSequence(
            body_template,
            self.goal,
            InteractivePlan('')
        )


class InteractivePairFactory(sequences.SequenceFactory):
    def __init__(self, pair: int, goal: InteractiveGoal) -> None:
        super().__init__(
            'Pair' + str(pair) + '-' + goal.get_name().capitalize()
        )
        self.goal = goal
        self.pair = pair

    def build(self, body_template: Dict[str, Any]) -> sequences.Sequence:
        return InteractiveSequence(
            body_template,
            self.goal,
            create_pair_plan(self.pair)
        )


INTERACTIVE_SCENE_SEQUENCE_LIST = [
    # Singles
    InteractiveSequenceFactory(TraversalGoal()),
    InteractiveSequenceFactory(RetrievalGoal()),
    # Pairs
    InteractivePairFactory(1, TraversalGoal()),
    InteractivePairFactory(1, RetrievalGoal()),
    InteractivePairFactory(2, TraversalGoal()),
    InteractivePairFactory(2, RetrievalGoal()),
    InteractivePairFactory(5, TraversalGoal()),
    InteractivePairFactory(5, RetrievalGoal()),
    InteractivePairFactory(6, TraversalGoal()),
    InteractivePairFactory(6, RetrievalGoal()),
    InteractivePairFactory(7, TraversalGoal()),
    InteractivePairFactory(7, RetrievalGoal()),
    InteractivePairFactory(8, TraversalGoal()),
    InteractivePairFactory(8, RetrievalGoal()),
    InteractivePairFactory(9, TraversalGoal()),
    InteractivePairFactory(9, RetrievalGoal()),
    InteractivePairFactory(11, TraversalGoal()),
    InteractivePairFactory(11, RetrievalGoal())
]
