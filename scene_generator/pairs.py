import copy
import logging
import random
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
import uuid

import containers
import exceptions
import geometry
import goals
from interaction_goals import DistractorObjectRule, InteractionGoal, ObjectRule
import tags
import util


class BoolOption(Enum):
    YES_YES = auto()
    YES_NO = auto()
    NO_NO = auto()
    NO_YES = auto()


class ConfusorLocationOption(Enum):
    # Either in back of or in front of the performer
    BACK_FRONT = auto()
    # Very close to the target object
    CLOSE_CLOSE = auto()
    # Either very close to or far away from the target object
    CLOSE_FAR = auto()
    # Either doesn't exist or very close to the target object
    NONE_CLOSE = auto()
    # Either doesn't exist or far away from the target object
    NONE_FAR = auto()


class TargetLocationOption(Enum):
    # Either in back of or in from of the performer
    FRONT_BACK = auto()
    # The same position in front of the performer
    FRONT_FRONT = auto()
    # The same random position
    RANDOM = auto()


class ObstructorOption(Enum):
    # No obstructor
    NONE_NONE = auto()
    # Obstruct navigation only (and not vision)
    NONE_NAVIGATION = auto()
    # Obstruct navigation and vision
    NONE_VISION = auto()


def is_true_scene_1(bool_pair: BoolOption):
    """Return if the given setup options bool_pair is true in
    the first goal."""
    return (
        bool_pair == BoolOption.YES_NO or
        bool_pair == BoolOption.YES_YES
    )


def is_true_scene_2(bool_pair: BoolOption):
    """Return if the given setup options bool_pair is true in
    the second goal."""
    return (
        bool_pair == BoolOption.NO_YES or
        bool_pair == BoolOption.YES_YES
    )


class SetupOptions():
    def __init__(
        self,
        target_definition: Dict[str, Any] = None,
        target_containerize: BoolOption = BoolOption.NO_NO,
        target_location: TargetLocationOption =
        TargetLocationOption.RANDOM,
        confusor: BoolOption = BoolOption.NO_NO,
        confusor_definition: Dict[str, Any] = None,
        confusor_containerize: BoolOption = BoolOption.NO_NO,
        confusor_location: ConfusorLocationOption =
        ConfusorLocationOption.CLOSE_CLOSE,
        obstructor: ObstructorOption = ObstructorOption.NONE_NONE,
        obstructor_definition: Dict[str, Any] = None
    ) -> None:
        self.target_definition = target_definition
        self.target_containerize = target_containerize
        self.target_location = target_location
        # The confusor is always for the target object, but we may want to
        # change that in the future.
        self.confusor = confusor
        self.confusor_definition = confusor_definition
        self.confusor_containerize = confusor_containerize
        self.confusor_location = confusor_location
        # The obstructor is always for the target object, but we may want to
        # change that in the future.
        self.obstructor = obstructor
        self.obstructor_definition = obstructor_definition


class DistractorNeverObstructsTargetObjectRule(DistractorObjectRule):
    def validate_location(
        self,
        object_location: Dict[str, Any],
        target_list: List[Dict[str, Any]],
        performer_start: Dict[str, Dict[str, float]]
    ) -> bool:
        for target_or_confusor in self._target_confusor_list:
            if geometry.does_fully_obstruct_target(
                performer_start['position'],
                target_or_confusor,
                geometry.get_bounding_polygon(object_location)
            ):
                return False
        return True


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
        containerize_option: BoolOption,
        definition: Dict[str, Any],
        location_option: Any,
        name: str,
        show: Tuple[bool, bool],
        template: Dict[str, Any]
    ) -> None:
        super(ObjectData, self).__init__(
            definition=definition,
            template=template
        )
        self.containerize = [None, None]
        if containerize_option and containerize_option != BoolOption.NO_NO:
            self.containerize[0] = is_true_scene_1(containerize_option)
            self.containerize[1] = is_true_scene_2(containerize_option)
        self.instance = [None, None]
        self.location = [None, None]
        self.location_option = location_option
        self.name = name
        self.receptacle = [None, None]
        self.show = [show[0], show[1]]

    def is_back(self, scene_index: int) -> bool:
        return False

    def is_close(self, scene_index: int) -> bool:
        return False

    def is_front_and_or_back(self) -> bool:
        return (
            self.is_front(0) or self.is_back(0) or
            self.is_front(1) or self.is_back(1)
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
        containerize_option: BoolOption,
        definition: Dict[str, Any],
        location_option: ConfusorLocationOption,
        show: Tuple[bool, bool],
        template: Dict[str, Any]
    ) -> None:
        super(ConfusorData, self).__init__(
            containerize_option=containerize_option,
            definition=definition,
            location_option=location_option,
            name='confusor',
            show=show,
            template=template
        )

    def is_close(self, scene_index: int) -> bool:
        if scene_index == 0:
            return (
                self.location_option == ConfusorLocationOption.CLOSE_FAR or
                self.location_option == ConfusorLocationOption.CLOSE_CLOSE
            )

        if scene_index == 1:
            return (
                self.location_option == ConfusorLocationOption.NONE_CLOSE or
                self.location_option == ConfusorLocationOption.CLOSE_CLOSE
            )

        return False

    def is_back(self, scene_index: int) -> bool:
        if scene_index == 0:
            return self.location_option == ConfusorLocationOption.BACK_FRONT
        return False

    def is_front(self, scene_index: int) -> bool:
        if scene_index == 1:
            return self.location_option == ConfusorLocationOption.BACK_FRONT
        return False

    def is_location_same(self) -> bool:
        return (self.location_option == ConfusorLocationOption.CLOSE_CLOSE)


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
        super(ReceptacleData, self).__init__(
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
        containerize_option: BoolOption,
        definition: Dict[str, Any],
        location_option: TargetLocationOption,
        rule_list: List[ObjectRule],
        template: Dict[str, Any]
    ) -> None:
        super(TargetData, self).__init__(
            containerize_option=containerize_option,
            definition=definition,
            location_option=location_option,
            name='target',
            show=(True, True),
            template=template
        )
        self.choice = choice
        self.rule_list = rule_list

    def is_back(self, scene_index: int) -> bool:
        if scene_index == 1:
            return self.location_option == TargetLocationOption.FRONT_BACK
        return False

    def is_front(self, scene_index: int) -> bool:
        if scene_index == 0:
            return (
                self.location_option == TargetLocationOption.FRONT_BACK or
                self.location_option == TargetLocationOption.FRONT_FRONT
            )

        if scene_index == 1:
            return self.location_option == TargetLocationOption.FRONT_FRONT

        return False

    def is_location_same(self) -> bool:
        return (
            self.location_option == TargetLocationOption.FRONT_FRONT or
            self.location_option == TargetLocationOption.RANDOM
        )


def must_containerize_either(
    target: TargetData,
    confusor: Optional[ConfusorData]
) -> bool:
    """Return if either the target or the confusor must be positioned inside an
    enclosable receptacle in either scene."""
    return (target.containerize[0] or target.containerize[1] or (confusor and (
        confusor.containerize[0] or confusor.containerize[1])))


def must_containerize_together(
    target: TargetData,
    confusor: Optional[ConfusorData],
    scene_index: int = None
) -> bool:
    """Return if both the target and the confusor must be positioned inside the
    same enclosable receptacle."""
    if scene_index is None:
        return (
            must_containerize_together(target, confusor, 0) or
            must_containerize_together(target, confusor, 1)
        )
    return (confusor and (
        target.containerize[scene_index] and
        confusor.containerize[scene_index] and
        confusor.is_close(scene_index)
    ))


class InteractionPair():
    """A pair of interactive scenes that each have the same goals, targets,
    distractors, walls, materials, and performer starts, except for
    specifically configured pair scene setup options."""

    def __init__(
        self,
        pair_number: int,
        goal_template: Dict[str, Any],
        goal_name: str,
        find_path: bool,
        setup_options: SetupOptions
    ) -> None:
        self._pair_number = pair_number
        self._setup_options = setup_options
        self._initialize_pair(goal_template, goal_name, find_path)

    def get_goal_name(self) -> str:
        """Return the name (type) of the goal of this pair."""
        return self._goal_1.get_name()

    def get_name(self) -> str:
        """Return the name of this pair."""
        return 'pair ' + str(self._pair_number)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return both scenes of this pair."""
        return self._scene_1, self._scene_2

    def _assign_confusor_location(
        self,
        goal: InteractionGoal,
        confusor: ConfusorData,
        target: TargetData
    ) -> None:
        """Assign the confusor its location in each scene, as needed, either
        close to or far from the target."""

        for scene_index in [0, 1]:
            if not confusor.show[scene_index]:
                continue

            if scene_index == 1 and confusor.location[0]:
                if confusor.is_location_same() and target.is_location_same():
                    confusor.location[1] = confusor.location[0]
                    continue

            if confusor.is_close(scene_index):
                confusor.location[scene_index] = self._generate_close_to(
                    confusor.definition,
                    target.definition,
                    target.location[scene_index],
                    goal.get_performer_start()
                )

            else:
                confusor.location[scene_index] = self._generate_far_from(
                    confusor.definition,
                    target.location[scene_index],
                    goal.get_performer_start()
                )

    def _assign_obstructor_location(
        self,
        goal: InteractionGoal,
        target: TargetData,
        obstructor: ObjectData
    ) -> None:
        """Assign the obstructor its location in each scene, as needed, by
        moving the obstructor to the location of the target, and then moving
        the target behind the obstructor."""

        for scene_index in [0, 1]:
            if not obstructor.show[scene_index]:
                continue

            # Generate an adjacent location so that the obstructor is
            # between the target and the performer start.
            # TODO Use existing target bounds?
            obstructor.location[scene_index] = geometry.get_adjacent_location(
                obstructor.definition,
                target.definition,
                target.location[scene_index],
                goal.get_performer_start(),
                True
            )

            if not obstructor.location[scene_index]:
                raise exceptions.SceneException(
                    f'{self.get_name()} cannot position target directly '
                    f'behind obstructor: '
                    f'performer_start={goal.get_performer_start()} '
                    f'target={target.definition} '
                    f'obstructor={obstructor.definition}')

        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'obstructor location 1: {obstructor.location[0]}')
        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'obstructor location 2: {obstructor.location[1]}')

    def _assign_target_and_confusor_locations(
        self,
        goal: InteractionGoal,
        target: TargetData,
        confusor: Optional[ObjectData],
        obstructor: Optional[ObjectData]
    ) -> None:
        """Assign the target and the confusor their respective locations in
        each scene, as needed, prioritizing locations in front of or in back of
        the performer start, with enough area for the obstructor, if needed."""

        # If an object is switched across scenes (in the same position),
        # use the larger object to generate the location to avoid collisions.
        # If positioned inside a receptacle, the receptacle will be larger.
        larger_object = target.receptacle_or_object()
        if confusor:
            larger_object = self._find_larger_object(
                larger_object, confusor.receptacle_or_object())
        if obstructor:
            larger_object = self._find_larger_object(
                larger_object, obstructor.template)

        # If an object must be positioned relative to the performer_start,
        # find the locations both in front of and in back of the performer
        # using its position and rotation. Do this first because it may change
        # the performer_start.
        if target.is_front_and_or_back():
            location_front, location_back = self._generate_front_and_back(
                goal,
                larger_object,
                target.rule_list[target.choice],
                target.is_back(1)
            )
            # Assumes target is either FRONT_BACK or BACK_FRONT
            target.location = (
                location_front,
                location_front if target.is_front(1) else location_back
            )
            if confusor and confusor.is_front_and_or_back():
                # Assumes confusor can't be FRONT_BACK, FRONT_FRONT, BACK_BACK
                confusor.location = (location_back, location_front)

        else:
            if confusor and confusor.is_front_and_or_back():
                location_front, location_back = self._generate_front_and_back(
                    goal,
                    confusor.receptacle_or_object(),
                    target.rule_list[target.choice],
                    True
                )
                # Assumes confusor can't be FRONT_BACK, FRONT_FRONT, BACK_BACK
                confusor.location = (location_back, location_front)

            # If the target isn't positioned in the front and/or in the back,
            # (for now) it will be positioned randomly.
            target.location = self._generate_random_location(
                goal,
                target.receptacle_or_object(),
                target.rule_list[target.choice],
                goal.get_target_list(),
                goal.get_bounds_list()
            )

        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'target location 1: {target.location[0]}')
        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'target location 2: {target.location[1]}')

        if confusor:
            # If the confusor isn't positioned in the front and/or in the back,
            # (for now) it will be positioned close to or far from the target.
            if not confusor.is_front_and_or_back():
                self._assign_confusor_location(
                    goal,
                    confusor,
                    target
                )

            logging.debug(
                f'{self.get_name()} {self.get_goal_name()} '
                f'confusor location 1: {confusor.location[0]}')
            logging.debug(
                f'{self.get_name()} {self.get_goal_name()} '
                f'confusor location 2: {confusor.location[1]}')

        if (target.is_front_and_or_back() or confusor.is_front_and_or_back()):
            # Ensure that the random location of distractors or walls doesn't
            # accidentally make them obstructors.
            goal.set_distractor_rule(DistractorNeverObstructsTargetObjectRule)
            goal.set_no_random_obstructor()

    def _choose_confusor(
        self,
        goal: InteractionGoal,
        setup_options: SetupOptions,
        target: TargetData,
        pair_confusor_definition: Optional[Dict[str, Any]],
        show_in_scene_1: bool,
        show_in_scene_2: bool
    ) -> Optional[ObjectData]:
        """Chooses a confusor definition, creates a confusor template, and
        returns the confusor data to use in one or both scenes as needed.
        Assumes that both scenes won't ever need two different confusors.
        Returns None if no scene needs a confusor."""

        if not show_in_scene_1 and not show_in_scene_2:
            return None

        confusor_definition = (
            pair_confusor_definition if pair_confusor_definition
            else goal.get_confusor_rule(target.template).choose_definition()
        )

        # Create the confusor template at a base location, and later we'll
        # move it to its final location in each scene.
        confusor_template = util.instantiate_object(confusor_definition,
                                                    geometry.ORIGIN_LOCATION)

        confusor = ConfusorData(
            containerize_option=setup_options.confusor_containerize,
            definition=confusor_definition,
            location_option=setup_options.confusor_location,
            show=(show_in_scene_1, show_in_scene_2),
            template=confusor_template
        )

        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'confusor template: {confusor_template}')

        return confusor

    def _choose_obstructor(
        self,
        goal: InteractionGoal,
        pair_obstructor_definition: Optional[Dict[str, Any]],
        obstructed_object: Dict[str, Any],
        obstruct_vision: bool,
        show_in_scene_1: bool,
        show_in_scene_2: bool
    ) -> Optional[ObjectData]:
        """Chooses an obstructor definition, creates an obstructor template,
        and returns the obstructor data to use in one or both scenes as needed.
        Assumes that both scenes won't ever need two different obstructors.
        Returns None if no scene needs an obstructor."""

        if not show_in_scene_1 and not show_in_scene_2:
            return None

        # TODO What if we can't find an obstructor for the object?
        obstructor_definition = (
            pair_obstructor_definition
            if pair_obstructor_definition
            else goal.get_obstructor_rule(
                obstructed_object, obstruct_vision
            ).choose_definition()
        )

        # Create the obstructor template at a base location, and later we'll
        # move it to its final location in each scene.
        obstructor_template = util.instantiate_object(obstructor_definition,
                                                      geometry.ORIGIN_LOCATION)

        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'obstructor template: {obstructor_template}')

        return ObjectData(
            containerize_option=None,
            definition=obstructor_definition,
            location_option=None,
            name='obstructor',
            show=(show_in_scene_1, show_in_scene_2),
            template=obstructor_template
        )

    def _choose_receptacle(
        self,
        target: TargetData,
        confusor: Optional[ObjectData]
    ) -> Optional[ReceptacleData]:
        """Chooses a receptacle definition, creates a receptacle template, and
        returns the receptacle data to use in one or both scenes as needed.
        Assumes that both scenes won't ever need two different receptacles.
        Returns None if containerization is impossible."""

        receptacle_definition_list = containers.retrieve_enclosable_object_definition_list().copy()  # noqa: E501
        random.shuffle(receptacle_definition_list)

        receptacle_definition = None
        area_index = None
        orientation = None
        target_rotation = None
        confusor_rotation = None

        # If needed, find an enclosable receptacle that can hold both the
        # target and the confusor together.
        if must_containerize_together(target, confusor):
            for receptacle_definition in receptacle_definition_list:
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
                confusor.template if (confusor and (
                    confusor.containerize[0] or confusor.containerize[1]
                )) else None
            )

            valid_containment_list = containers.get_enclosable_containments(
                (target_template, confusor_template),
                receptacle_definition_list
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
        receptacle_template = util.instantiate_object(receptacle_definition,
                                                      geometry.ORIGIN_LOCATION)

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
            f'{self.get_name()} {self.get_goal_name()} receptacle '
            f'template: {receptacle.template}')

        return receptacle

    def _choose_target(
        self,
        goal: InteractionGoal,
        setup_options: SetupOptions,
        pair_target_definition: Optional[Dict[str, Any]]
    ) -> TargetData:
        """Chooses a target definition, creates a target template, and returns
        the target data to use in both scenes. Assumes that both scenes won't
        ever need two different targets."""

        target_rule_list = goal.get_target_rule_list()
        target_choice = 0
        # TODO Randomly choose a target from the goal to use in both scenes.
        # target_choice = random.randint(0, len(target_rule_list) - 1)

        # Create all targets in the goal that come before the chosen target.
        goal.generate_target_list(target_choice)

        # Choose a definition for the chosen target to use in both scenes.
        target_definition = (
            pair_target_definition
            if pair_target_definition
            else target_rule_list[target_choice].choose_definition()
        )

        # Create the target template at a base location, and later we'll
        # move it to its final location in each scene.
        target_template = util.instantiate_object(target_definition,
                                                  geometry.ORIGIN_LOCATION)

        target = TargetData(
            choice=target_choice,
            containerize_option=setup_options.target_containerize,
            definition=target_definition,
            location_option=setup_options.target_location,
            rule_list=target_rule_list,
            template=target_template
        )

        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'target template: {target_template}')

        return target

    def _create_common_goal_type_list(
        self,
        opts: SetupOptions,
        prefix: str,
        is_true_func: Callable[[BoolOption], bool]
    ) -> List[str]:
        """Return the type list for a goal using the given setup options."""

        type_list = [self.get_name()]

        type_list.append(
            f'{prefix} target {tags.get_containerize_tag(is_true_func(opts.target_containerize))}')  # noqa: E501

        type_list.append(
            f'{prefix} confusor {tags.get_exists_tag(is_true_func(opts.confusor))}')  # noqa: E501

        if is_true_func(opts.confusor):
            type_list.append(
                f'{prefix} confusor {tags.get_containerize_tag(is_true_func(opts.confusor_containerize))}')  # noqa: E501

        return type_list

    def _create_goal_type_list_1(self, opts: SetupOptions) -> List[str]:
        """Return the type list for goal 1 using the given setup options."""

        prefix = 'pair scene 1'
        type_list = self._create_common_goal_type_list(opts, prefix,
                                                       is_true_scene_1)

        if (
            opts.target_location == TargetLocationOption.FRONT_BACK or
            opts.target_location == TargetLocationOption.FRONT_FRONT
        ):
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_FRONT}')
        else:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_RANDOM}')

        if is_true_scene_1(opts.confusor):
            if opts.confusor_location == ConfusorLocationOption.BACK_FRONT:
                type_list.append(
                    f'{prefix} confusor {tags.OBJECT_LOCATION_BACK}')
            elif (
                opts.confusor_location ==
                ConfusorLocationOption.CLOSE_FAR or
                opts.confusor_location ==
                ConfusorLocationOption.CLOSE_CLOSE
            ):
                type_list.append(
                    f'{prefix} confusor {tags.OBJECT_LOCATION_CLOSE}')

        type_list.append(f'{prefix} obstructor {tags.get_exists_tag(False)}')

        return type_list

    def _create_goal_type_list_2(self, opts: SetupOptions) -> List[str]:
        """Return the type list for goal 2 using the given setup options."""

        prefix = 'pair scene 2'
        type_list = self._create_common_goal_type_list(opts, prefix,
                                                       is_true_scene_2)

        if opts.target_location == TargetLocationOption.FRONT_BACK:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_BACK}')
        elif opts.target_location == TargetLocationOption.FRONT_FRONT:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_FRONT}')
        else:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_RANDOM}')

        if is_true_scene_2(opts.confusor):
            if opts.confusor_location == ConfusorLocationOption.BACK_FRONT:
                type_list.append(
                    f'{prefix} confusor {tags.OBJECT_LOCATION_FRONT}')
            elif (
                opts.confusor_location ==
                ConfusorLocationOption.NONE_CLOSE or
                opts.confusor_location ==
                ConfusorLocationOption.CLOSE_CLOSE
            ):
                type_list.append(
                    f'{prefix} confusor {tags.OBJECT_LOCATION_CLOSE}')
            elif (
                opts.confusor_location ==
                ConfusorLocationOption.NONE_FAR or
                opts.confusor_location ==
                ConfusorLocationOption.CLOSE_FAR
            ):
                type_list.append(
                    f'{prefix} confusor {tags.OBJECT_LOCATION_FAR}')

        type_list.append(
            f'{prefix} obstructor {tags.get_exists_tag(opts.obstructor != ObstructorOption.NONE_NONE)}')  # noqa: E501

        if opts.obstructor != ObstructorOption.NONE_NONE:
            obstruct_vision = (tags.get_obstruct_vision_tag(
                opts.obstructor == ObstructorOption.NONE_VISION))
            type_list.append(f'{prefix} obstructor {obstruct_vision}')

        return type_list

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

    def _initialize_pair(
        self,
        goal_template: Dict[str, Any],
        goal_name: str,
        find_path: bool
    ) -> None:
        tries = 0
        while True:
            tries += 1
            try:
                # Reset both half-finished scenes on each new try.
                self._scene_1 = copy.deepcopy(goal_template)
                self._scene_2 = copy.deepcopy(goal_template)

                self._goal_1 = (
                    goals.get_goal_by_name(goal_name)
                    if goal_name
                    else goals.choose_goal('interaction')
                )

                logging.debug(
                    f'\n\n{self.get_name()} initialize goal '
                    f'{self.get_goal_name()} (try {tries})\n')

                # Initialize each goal, then update each goal body.
                self._initialize_scenes(self._setup_options)
                self._goal_1.update_body(self._scene_1, find_path)
                self._goal_2.update_body(self._scene_2, find_path)

                # Update the type_list in each goal body.
                self._scene_1['goal']['type_list'] = self._scene_1['goal'][
                    'type_list'
                ] + self._create_goal_type_list_1(self._setup_options)
                self._scene_2['goal']['type_list'] = self._scene_2['goal'][
                    'type_list'
                ] + self._create_goal_type_list_2(self._setup_options)

                logging.debug(
                    f'\n\n{self.get_name()} initialize goal '
                    f'{self.get_goal_name()} done\n')

                break

            except exceptions.SceneException as e:
                logging.error(e)

    def _initialize_scenes(self, setup_options: SetupOptions) -> None:
        """
        Initialize the scenes and goals in this pair and all their objects:
        - 1. Create all the objects specific to this pair.
        - 2. Containerize objects as needed by this pair's setup.
        - 3. Move objects into locations specific to each scene.
        - 4. Create the other objects (distractors, walls) in the 1st goal.
        - 5. Copy the 1st goal to make the 2nd and swap their objects.
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
            target = self._choose_target(
                self._goal_1,
                setup_options,
                setup_options.target_definition
            )

            confusor = self._choose_confusor(
                self._goal_1,
                setup_options,
                target,
                setup_options.confusor_definition,
                is_true_scene_1(setup_options.confusor),
                is_true_scene_2(setup_options.confusor)
            )

            if must_containerize_either(target, confusor):
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
            self._goal_1,
            setup_options.obstructor_definition,
            # Use the larger of the receptacle or the target object.
            target.receptacle_or_object(),
            (setup_options.obstructor == ObstructorOption.NONE_VISION),
            False,
            (setup_options.obstructor != ObstructorOption.NONE_NONE)
        )

        self._assign_target_and_confusor_locations(
            self._goal_1,
            target,
            confusor,
            obstructor
        )

        # The performer_start won't be modified past here.
        logging.debug(
            f'{self.get_name()} {self.get_goal_name()} '
            f'performer start: {self._goal_1.get_performer_start()}')

        if obstructor:
            self._assign_obstructor_location(
                self._goal_1,
                target,
                obstructor
            )

        # Create a new ID so it's not the same ID used by the target's instance
        # of the receptacle.
        confusor_receptacle_id = str(uuid.uuid4())

        self._finalize_target_and_confusor_locations(
            self._goal_1,
            target,
            confusor,
            receptacle,
            confusor_receptacle_id
        )

        self._finalize_obstructor_location(self._goal_1, obstructor)

        self._log_objects(target, confusor, obstructor)

        self._finish_goal_1(self._goal_1, target, confusor, obstructor)

        # Copy the random objects from the first goal to the second goal.
        self._goal_2 = copy.deepcopy(self._goal_1)

        self._finish_goal_2(self._goal_2, target, confusor, obstructor)

    def _finalize_object_location(
        self,
        scene_index: int,
        goal: InteractionGoal,
        object: ObjectData,
        receptacle: Optional[ReceptacleData],
        receptacle_id: Optional[str],
        rotation: Optional[float]
    ) -> None:
        """Finalize the location of the given object in the given scene, which
        may or may not be inside a copy of the given receptacle."""

        if object.containerize[scene_index]:
            object.receptacle[scene_index] = copy.deepcopy(receptacle.template)
            object.receptacle[scene_index]['id'] = receptacle_id

            # Update the Y position of the location to use the positionY
            # from the receptacle definition.
            object.location[scene_index]['position']['y'] = \
                receptacle.definition.get('positionY', 0)

            # Move the receptacle to take the original location of the object,
            # then position the object inside the receptacle.
            util.move_to_location(
                receptacle.definition,
                object.receptacle[scene_index],
                object.location[scene_index],
                geometry.generate_object_bounds(
                    receptacle.definition['dimensions'],
                    receptacle.definition['offset']
                    if 'offset' in receptacle.definition
                    else None,
                    object.location[scene_index]['position'],
                    object.location[scene_index]['rotation']
                ),
                object.definition
            )

            containers.put_object_in_container(
                object.definition,
                object.instance[scene_index],
                object.receptacle[scene_index],
                receptacle.definition,
                receptacle.area_index,
                rotation
            )

            goal.get_bounds_list().append(
                object.receptacle[scene_index]['shows'][0]['boundingBox'])

        else:
            util.move_to_location(
                object.definition,
                object.instance[scene_index],
                object.location[scene_index],
                geometry.generate_object_bounds(
                    object.definition['dimensions'],
                    object.definition['offset']
                    if 'offset' in object.definition
                    else None,
                    object.location[scene_index]['position'],
                    object.location[scene_index]['rotation']
                ),
                object.definition
            )

            goal.get_bounds_list().append(
                object.instance[scene_index]['shows'][0]['boundingBox'])

    def _finalize_obstructor_location(
        self,
        goal: InteractionGoal,
        obstructor: Optional[ObjectData]
    ) -> None:
        """Finalize the location of the obstructor."""

        for scene_index in [0, 1]:
            if not obstructor or not obstructor.show[scene_index]:
                continue

            obstructor.instance[scene_index] = copy.deepcopy(
                obstructor.template)

            util.move_to_location(
                obstructor.definition,
                obstructor.instance[scene_index],
                obstructor.location[scene_index],
                geometry.generate_object_bounds(
                    obstructor.definition['dimensions'],
                    obstructor.definition['offset']
                    if 'offset' in obstructor.definition
                    else None,
                    obstructor.location[scene_index]['position'],
                    obstructor.location[scene_index]['rotation']
                ),
                obstructor.definition
            )

            goal.get_bounds_list().append(
                obstructor.instance[scene_index]['shows'][0]['boundingBox'])

    def _finalize_target_and_confusor_locations(
        self,
        goal: InteractionGoal,
        target: TargetData,
        confusor: Optional[ObjectData],
        receptacle: Optional[ObjectData],
        confusor_receptacle_id: int
    ) -> None:
        """Finalize the location of the target and the confusor, which may or
        may not be inside one or two receptacles."""

        for scene_index in [0, 1]:
            target.instance[scene_index] = copy.deepcopy(target.template)
            if confusor and confusor.show[scene_index]:
                confusor.instance[scene_index] = copy.deepcopy(
                    confusor.template)

            if must_containerize_together(target, confusor, scene_index):
                target.receptacle[scene_index] = copy.deepcopy(
                    receptacle.template)

                # Update the Y position of the location to use the positionY
                # from the receptacle definition.
                target.location[scene_index]['position']['y'] = \
                    receptacle.definition.get('positionY', 0)

                # Move the receptacle to take the original location of the
                # target, then position both the target and the confusor inside
                # the receptacle adjacent to one another.
                util.move_to_location(
                    receptacle.definition,
                    target.receptacle[scene_index],
                    target.location[scene_index],
                    geometry.generate_object_bounds(
                        receptacle.definition['dimensions'],
                        receptacle.definition['offset']
                        if 'offset' in receptacle.definition
                        else None,
                        target.location[scene_index]['position'],
                        target.location[scene_index]['rotation']
                    ),
                    target.definition
                )

                containers.put_objects_in_container(
                    target.definition,
                    target.instance[scene_index],
                    confusor.definition,
                    confusor.instance[scene_index],
                    target.receptacle[scene_index],
                    receptacle.definition,
                    receptacle.area_index,
                    receptacle.orientation,
                    receptacle.target_rotation,
                    receptacle.confusor_rotation
                )

                goal.get_bounds_list().append(
                    target.receptacle[scene_index]['shows'][0]['boundingBox'])

            else:
                self._finalize_object_location(
                    scene_index,
                    goal,
                    target,
                    receptacle,
                    receptacle.template['id'] if receptacle else None,
                    receptacle.target_rotation if receptacle else None
                )

                if confusor and confusor.show[scene_index]:
                    self._finalize_object_location(
                        scene_index,
                        goal,
                        confusor,
                        receptacle,
                        confusor_receptacle_id if receptacle else None,
                        receptacle.confusor_rotation if receptacle else None
                    )

    def _finish_goal_1(
        self,
        goal: InteractionGoal,
        target: TargetData,
        confusor: Optional[ConfusorData],
        obstructor: Optional[ObjectData]
    ) -> None:
        """Finalize the target and other objects in the first goal."""

        goal_1_target_list = goal.get_target_list()
        goal_1_confusor_list = goal.get_confusor_list()
        goal_1_distractor_list = goal.get_distractor_list()
        goal_1_obstructor_list = goal.get_obstructor_list()

        # Add the first version of each chosen object to the first goal.
        goal_1_target_list.append(target.instance[0])
        if target.receptacle[0]:
            goal_1_distractor_list.append(target.receptacle[0])
        if confusor and confusor.instance[0]:
            goal_1_confusor_list.append(confusor.instance[0])
            if confusor.receptacle[0]:
                goal_1_distractor_list.append(confusor.receptacle[0])
        if obstructor and obstructor.instance[0]:
            goal_1_obstructor_list.append(obstructor.instance[0])

        # Generate the other random objects in the first goal, then copy them
        # to the second goal.
        goal.compute_objects(
            self._scene_1['wallMaterial'],
            self._scene_1['wallColors'])

    def _finish_goal_2(
        self,
        goal: InteractionGoal,
        target: TargetData,
        confusor: Optional[ConfusorData],
        obstructor: Optional[ObjectData]
    ) -> None:
        """Finalize the target and other objects in the second goal."""

        goal_2_target_list = goal.get_target_list()
        goal_2_confusor_list = goal.get_confusor_list()
        goal_2_distractor_list = goal.get_distractor_list()
        goal_2_obstructor_list = goal.get_obstructor_list()

        # Exchange the first version of the target object with the second
        # version to keep it at the same list index.
        goal_2_target_list[target.choice] = target.instance[1]

        # Remove the first version of each chosen object in the lists that were
        # copied from the first goal.
        if target.receptacle[0]:
            goal_2_distractor_list.pop(0)
        if confusor and confusor.instance[0]:
            goal_2_confusor_list.pop(0)
            if confusor.receptacle[0]:
                goal_2_distractor_list.pop(0)
        if obstructor and obstructor.instance[0]:
            goal_2_obstructor_list.pop(0)

        # Add the second version of each chosen object to the second goal.
        if confusor and confusor.instance[1]:
            goal_2_confusor_list.insert(0, confusor.instance[1])
            if confusor.receptacle[1]:
                goal_2_distractor_list.insert(0, confusor.receptacle[1])
        if obstructor and obstructor.instance[1]:
            goal_2_obstructor_list.insert(0, obstructor.instance[1])
        # Insert the target receptacle in front of the confusor receptacle.
        if target.receptacle[1]:
            goal_2_distractor_list.insert(0, target.receptacle[1])

    def _generate_front_and_back(
        self,
        goal: InteractionGoal,
        object_definition: Dict[str, Any],
        object_rule: ObjectRule,
        generate_back: bool
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a location both in front of and in back of the
        performer_start. Will modify the performer_start
        in the given goal if needed to generate the two locations.
        Return the front and back locations."""

        performer_start = goal.get_performer_start()
        location_front = None
        location_back = None

        for _ in range(util.MAX_TRIES):
            # TODO Use existing target bounds?
            location_front = self._identify_front(
                object_definition, object_rule, performer_start)
            if location_front:
                if generate_back:
                    location_back = self._identify_back(
                        object_definition, object_rule, performer_start)
                    if location_back:
                        break
                else:
                    break
            location_front = None
            location_back = None
            performer_start = goal.reset_performer_start()

        if not generate_back and not location_front:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position performer start in '
                f'front of object={object_definition}')

        if generate_back and (not location_front or not location_back):
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position performer start in '
                f'front of and in back of object={object_definition}')

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

        # TODO Use existing target bounds?
        location_close = geometry.get_adjacent_location(
            object_definition,
            target_definition,
            target_location,
            performer_start
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
            # TODO Use existing target bounds?
            location_far = geometry.calc_obj_pos(
                performer_start['position'], [], object_definition)
            if not geometry.are_adjacent(
                    target_location, location_far,
                    distance=geometry.MIN_OBJECTS_SEPARATION_DISTANCE):
                break
            location_far = None

        if not location_far:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot position far from target: '
                f'object={object_definition} target={target_location}')

        return location_far

    def _generate_random_location(
        self,
        goal: InteractionGoal,
        object_definition: Dict[str, Any],
        object_rule: ObjectRule,
        target_list: List[Dict[str, Any]],
        bounds_list: List[List[Dict[str, float]]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a random location and return it twice."""

        for _ in range(util.MAX_TRIES):
            # TODO Use existing target bounds?
            object_location, bounds = object_rule.choose_location(
                object_definition, goal.get_performer_start(), bounds_list
            )
            if object_rule.validate_location(
                    object_location, target_list, goal.get_performer_start()):
                break
            object_location = None
        if not object_location:
            raise exceptions.SceneException(
                f'{self.get_name()} cannot randomly position '
                f'object={object_definition}')
        return object_location, object_location

    def _identify_front(self, object_definition: Dict[str, Any],
                        object_rule: ObjectRule,
                        performer_start: Dict[str, float]) -> Dict[str, Any]:
        """Find and return a location in front of the given performer_start."""

        for _ in range(util.MAX_TRIES):
            location_front = geometry.get_location_in_front_of_performer(
                performer_start, object_definition)
            if location_front and object_rule.validate_location(
                    location_front, [], performer_start):
                break
            location_front = None
        return location_front

    def _identify_back(self, object_definition: Dict[str, Any],
                       object_rule: ObjectRule,
                       performer_start: Dict[str, float]) -> Dict[str, Any]:
        """Find and return a location in back of the given performer_start."""

        for _ in range(util.MAX_TRIES):
            location_back = geometry.get_location_in_back_of_performer(
                performer_start, object_definition)
            if location_back and object_rule.validate_location(
                    location_back, [], performer_start):
                break
            location_back = None
        return location_back

    def _log_objects(
        self,
        target: TargetData,
        confusor: Optional[ConfusorData],
        obstructor: Optional[ObjectData]
    ) -> None:
        """Log the given objects."""

        for object in [target, confusor, obstructor]:
            if object:
                for scene_index in [0, 1]:
                    if object.instance[scene_index]:
                        logging.info(
                            f'{self.get_name()} {self.get_goal_name()} '
                            f'{object.name}_{scene_index + 1} '
                            f'{object.instance[scene_index]["type"]} '
                            f'{object.instance[scene_index]["id"]}')
                    else:
                        logging.info(
                            f'{self.get_name()} {self.get_goal_name()} '
                            f'{object.name}_{scene_index + 1} None')
                    if object.receptacle[scene_index]:
                        logging.info(
                            f'{self.get_name()} {self.get_goal_name()} '
                            f'{object.name}_receptacle_{scene_index + 1} '
                            f'{object.receptacle[scene_index]["type"]} '
                            f'{object.receptacle[scene_index]["id"]}')
                    else:
                        logging.info(
                            f'{self.get_name()} {self.get_goal_name()} '
                            f'{object.name}_receptacle_{scene_index + 1} None')


class Pair1(InteractionPair):
    """(1A) The Target Object is immediately visible (starting in view of
    the camera) OR (1B) behind the camera (must rotate to see the
    object). For each pair, the object may or may not be inside a
    container (like a box). See MCS-232.
    """

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        containerize = (
            BoolOption.YES_YES
            if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE
            else BoolOption.NO_NO
        )
        super(Pair1, self).__init__(
            1,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=containerize,
                target_location=TargetLocationOption.FRONT_BACK
            )
        )


class Pair6(InteractionPair):
    """(6A) The Target Object is positioned immediately visible and a
    Similar Object is not immediately visible OR (6B) the Target
    Object is positioned not immediately visible and a Similar Object
    is immediately visible. For each pair, the objects may or may not
    be inside identical containers, but only if the container is big
    enough to hold both individually; otherwise, no container will be
    used in that pair. See MCS-233.
    """

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        containerize = (
            BoolOption.YES_YES
            if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE
            else BoolOption.NO_NO
        )
        super(Pair6, self).__init__(
            6,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=containerize,
                target_location=TargetLocationOption.FRONT_BACK,
                confusor=BoolOption.YES_YES,
                confusor_containerize=containerize,
                confusor_location=ConfusorLocationOption.BACK_FRONT
            )
        )


class Pair2(InteractionPair):
    """(2A) The Target Object is immediately visible OR (2B) is hidden
    behind a larger object that itself is immediately visible. For
    each pair, the object may or may not be inside a container (like a
    box). See MCS-239.
    """

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        containerize = (
            BoolOption.YES_YES
            if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE
            else BoolOption.NO_NO
        )
        # TODO MCS-320 Let target be containerized
        containerize = BoolOption.NO_NO
        super(Pair2, self).__init__(
            2,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=containerize,
                target_location=TargetLocationOption.FRONT_FRONT,
                obstructor=ObstructorOption.NONE_VISION
            )
        )


class Pair7(InteractionPair):
    """(7) Like pair (6), but the Target Object is always inside a container,
    and the Similar Object is never inside a container."""

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        super(Pair7, self).__init__(
            7,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=BoolOption.YES_YES,
                target_location=TargetLocationOption.FRONT_BACK,
                confusor=BoolOption.YES_YES,
                confusor_location=ConfusorLocationOption.BACK_FRONT
            )
        )


class Pair3(InteractionPair):
    """(3A) The Target Object is positioned normally, without a Similar
    Object in the scene, OR (3B) with a Similar Object in the scene,
    and directly adjacent to it. For each pair, the objects may or may
    not be inside a container, but only if the container is big enough
    to hold both together; otherwise, no container will be used in
    that pair.
    """

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        containerize = (
            BoolOption.YES_YES
            if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE
            else BoolOption.NO_NO
        )
        super(Pair3, self).__init__(
            3,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=containerize,
                confusor=BoolOption.NO_YES,
                confusor_containerize=containerize,
                confusor_location=ConfusorLocationOption.NONE_CLOSE
            )
        )


class Pair4(InteractionPair):
    """(4A) The Target Object is positioned normally, without a Similar Object
    in the scene, OR (4B) with a Similar Object in the scene, but far away
    from it.  For each pair, the objects may or may not be inside identical
    containers, but only if the container is big enough to hold both
    individually; otherwise, no container will be used in that pair."""

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False,
    ):
        containerize = (
            BoolOption.YES_YES
            if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE
            else BoolOption.NO_NO
        )
        super(Pair4, self).__init__(
            4,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=containerize,
                confusor=BoolOption.NO_YES,
                confusor_containerize=containerize,
                confusor_location=ConfusorLocationOption.NONE_FAR
            )
        )


class Pair5(InteractionPair):
    """(5A) The Target Object is positioned directly adjacent to a Similar
    Object OR (5B) far away from a Similar Object. For each pair, the
    objects may or may not be inside identical containers, but only if
    the container is big enough to hold both together; otherwise, no
    container will be used in that pair.
    """

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        containerize = (
            BoolOption.YES_YES
            if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE
            else BoolOption.NO_NO
        )
        super(Pair5, self).__init__(
            5,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=containerize,
                confusor=BoolOption.YES_YES,
                confusor_containerize=containerize,
                confusor_location=ConfusorLocationOption.CLOSE_FAR
            )
        )


class Pair8(InteractionPair):
    """(8A) The Target Object is positioned adjacent to a Similar Object
    OR (8B) the Target Object is positioned adjacent to a Similar Object,
    but the Target Object is inside a container. See MCS-238."""

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        super(Pair8, self).__init__(
            8,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=BoolOption.NO_YES,
                confusor=BoolOption.YES_YES,
                confusor_location=ConfusorLocationOption.CLOSE_CLOSE
            )
        )


class Pair9(InteractionPair):
    """(9A) The Target Object is immediately visible and can be approached
    in a relatively direct line OR (9B) the Target Object is immediately
    visible but getting to it would require navigating around a large
    piece of furniture (or some other obstacle). For instance, from the
    AIs vantage point, it can see the target object positioned beyond
    the coffee table, so to get to it, the AI would need to maneuver
    around the coffee table.  For each pair, the object may or may not
    be inside an open container (like a box)."""

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        containerize = (
            BoolOption.YES_YES
            if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE
            else BoolOption.NO_NO
        )
        # TODO MCS-320 Let target be containerized
        containerize = BoolOption.NO_NO
        super(Pair9, self).__init__(
            9,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_containerize=containerize,
                target_location=TargetLocationOption.FRONT_FRONT,
                obstructor=ObstructorOption.NONE_NAVIGATION
            )
        )


class Pair11(InteractionPair):
    """(11A) The Target Object and a Similar Object are positioned
    adjacent to each other and immediately visible OR
    (11B) the Target Object and a Similar Object are positioned
    adjacent to each other and NOT immediately visible."""

    def __init__(
        self,
        template: Dict[str, Any],
        goal_name: str = None,
        find_path: bool = False
    ):
        super(Pair11, self).__init__(
            11,
            template,
            goal_name,
            find_path,
            setup_options=SetupOptions(
                target_location=TargetLocationOption.FRONT_BACK,
                confusor=BoolOption.YES_YES,
                confusor_location=ConfusorLocationOption.CLOSE_CLOSE
            )
        )


INTERACTION_PAIR_CLASSES = [
    Pair1,
    Pair2,
    Pair3,
    # Pair4, # Won't use
    # Pair5, # Won't use
    Pair6,
    Pair7,
    Pair8,
    Pair9,
    Pair11
]


def get_pair_class(name: str) -> Type[InteractionPair]:
    class_name = 'Pair' + name
    klass = globals()[class_name]
    return klass


def get_pair_types() -> List[str]:
    return [klass.__name__.replace('Pair', '')
            for klass in INTERACTION_PAIR_CLASSES]
