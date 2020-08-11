import copy
import logging
import random
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
import uuid

import shapely

import containers
import exceptions
import geometry
import goals
from interaction_goals import DistractorObjectRule, InteractionGoal, ObjectRule
import objects
import tags
import util


class BoolPairOption(Enum):
    YES_YES = auto()
    YES_NO = auto()
    NO_NO = auto()
    NO_YES = auto()


class ConfusorLocationPairOption(Enum):
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


class TargetLocationPairOption(Enum):
    # Either in back of or in from of the performer
    FRONT_BACK = auto()
    # The same position in front of the performer
    FRONT_FRONT = auto()
    # The same random position
    RANDOM = auto()


class ObstructorPairOption(Enum):
    # No obstructor
    NONE_NONE = auto()
    # Obstruct navigation only (and not vision)
    NONE_NAVIGATION = auto()
    # Obstruct navigation and vision
    NONE_VISION = auto()


class SceneOptions():
    def __init__(self, target_definition: Dict[str, Any] = None, \
            target_containerize: BoolPairOption = BoolPairOption.NO_NO, \
            target_location: TargetLocationPairOption = TargetLocationPairOption.RANDOM, \
            confusor: BoolPairOption = BoolPairOption.NO_NO, confusor_definition: Dict[str, Any] = None,
            confusor_containerize: BoolPairOption = BoolPairOption.NO_NO, \
            confusor_location: ConfusorLocationPairOption = ConfusorLocationPairOption.CLOSE_CLOSE, \
            obstructor: ObstructorPairOption = ObstructorPairOption.NONE_NONE, \
            obstructor_definition: Dict[str, Any] = None):
        self.target_definition = target_definition
        self.target_containerize = target_containerize
        self.target_location = target_location
        # The confusor is always for the target object, but we may want to change that in the future.
        self.confusor = confusor
        self.confusor_definition = confusor_definition
        self.confusor_containerize = confusor_containerize
        self.confusor_location = confusor_location
        # The obstructor is always for the target object, but we may want to change that in the future.
        self.obstructor = obstructor
        self.obstructor_definition = obstructor_definition


class DistractorNeverObstructsTargetObjectRule(DistractorObjectRule):
    def validate_location(self, object_location: Dict[str, Any], target_list: List[Dict[str, Any]], \
            performer_start: Dict[str, Dict[str, float]]) -> bool:
        for target_or_confusor in self._target_confusor_list:
            if geometry.does_fully_obstruct_target(performer_start['position'], target_or_confusor, \
                    geometry.get_bounding_polygon(object_location)):
                return False
        return True


class InteractionPair():
    """A pair of interactive scenes that each have the same goals, targets, distractors, walls, materials, and
    performer starts, except for specifically configured scene options."""

    def __init__(self, number: int, template: Dict[str, Any], goal_name: str, find_path: bool, options: SceneOptions):
        self._number = number
        self._options = options
        tries = 0
        while True:
            tries += 1
            try:
                self._scene_1 = copy.deepcopy(template)
                self._scene_2 = copy.deepcopy(template)
                self._goal_1 = goals.get_goal_by_name(goal_name) if goal_name else goals.choose_goal('interaction')
                logging.debug(f'\n\n{self.get_name()} initialize goal {self._goal_1.get_name()} (try {tries})\n')
                self._initialize_each_goal()
                self._goal_1.update_body(self._scene_1, find_path)
                self._goal_2.update_body(self._scene_2, find_path)
                self._scene_1['goal']['type_list'] = self._scene_1['goal']['type_list'] + \
                        self._get_goal_type_list_1(self._options)
                self._scene_2['goal']['type_list'] = self._scene_2['goal']['type_list'] + \
                        self._get_goal_type_list_2(self._options)
                logging.debug(f'\n\n{self.get_name()} initialize goal {self._goal_1.get_name()} done\n')
                break
            except exceptions.SceneException as e:
                logging.error(e)

    def get_name(self) -> str:
        """Return the name of this pair."""
        return 'pair ' + str(self._number)

    def get_scenes(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Return both scenes of this pair."""
        return self._scene_1, self._scene_2

    def _get_both_goal_type_list(self, options: SceneOptions, prefix: str, \
            is_true_func: Callable[[BoolPairOption], bool]) -> List[str]:
        """Return the type list for a goal using the given scene options."""

        type_list = [self.get_name()]
        type_list.append(f'{prefix} target {tags.get_containerize_tag(is_true_func(options.target_containerize))}')
        type_list.append(f'{prefix} confusor {tags.get_exists_tag(is_true_func(options.confusor))}')

        if is_true_func(options.confusor):
            type_list.append( \
                    f'{prefix} confusor {tags.get_containerize_tag(is_true_func(options.confusor_containerize))}')

        return type_list

    def _get_goal_type_list_1(self, options: SceneOptions) -> List[str]:
        """Return the type list for goal 1 using the given scene options."""

        prefix = 'pair scene 1'
        type_list = self._get_both_goal_type_list(options, prefix, self._is_true_goal_1)

        if options.target_location == TargetLocationPairOption.FRONT_BACK or \
                options.target_location == TargetLocationPairOption.FRONT_FRONT:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_FRONT}')
        else:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_RANDOM}')

        if self._is_true_goal_1(options.confusor):
            if options.confusor_location == ConfusorLocationPairOption.BACK_FRONT:
                type_list.append(f'{prefix} confusor {tags.OBJECT_LOCATION_BACK}')
            elif options.confusor_location == ConfusorLocationPairOption.CLOSE_CLOSE or \
                    options.confusor_location == ConfusorLocationPairOption.CLOSE_FAR:
                type_list.append(f'{prefix} confusor {tags.OBJECT_LOCATION_CLOSE}')

        type_list.append(f'{prefix} obstructor {tags.get_exists_tag(False)}')

        return type_list

    def _get_goal_type_list_2(self, options: SceneOptions) -> List[str]:
        """Return the type list for goal 2 using the given scene options."""

        prefix = 'pair scene 2'
        type_list = self._get_both_goal_type_list(options, prefix, self._is_true_goal_2)

        if options.target_location == TargetLocationPairOption.FRONT_BACK:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_BACK}')
        elif options.target_location == TargetLocationPairOption.FRONT_FRONT:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_FRONT}')
        else:
            type_list.append(f'{prefix} target {tags.OBJECT_LOCATION_RANDOM}')

        if self._is_true_goal_2(options.confusor):
            if options.confusor_location == ConfusorLocationPairOption.BACK_FRONT:
                type_list.append(f'{prefix} confusor {tags.OBJECT_LOCATION_FRONT}')
            elif options.confusor_location == ConfusorLocationPairOption.CLOSE_CLOSE or \
                    options.confusor_location == ConfusorLocationPairOption.NONE_CLOSE:
                type_list.append(f'{prefix} confusor {tags.OBJECT_LOCATION_CLOSE}')
            elif options.confusor_location == ConfusorLocationPairOption.CLOSE_FAR or \
                    options.confusor_location == ConfusorLocationPairOption.NONE_FAR:
                type_list.append(f'{prefix} confusor {tags.OBJECT_LOCATION_FAR}')

        type_list.append( \
                f'{prefix} obstructor {tags.get_exists_tag(options.obstructor != ObstructorPairOption.NONE_NONE)}')

        if options.obstructor != ObstructorPairOption.NONE_NONE:
            obstruct_vision = (tags.get_obstruct_vision_tag(options.obstructor == ObstructorPairOption.NONE_VISION))
            type_list.append(f'{prefix} obstructor {obstruct_vision}')

        return type_list

    def _initialize_each_goal(self) -> None:
        """
        Initialize the goals for the two scenes in this pair and all their objects:
        - Create the objects specific to this pair (target, confusor, obstructor).
        - Containerize this pair's objects if needed by this pair's setup or if randomly chosen.
        - Move this pair's objects into locations specific to each scene.
        - Create the rest of the objects (targets, distractors, walls) in the goal for the first scene.
        - Copy the first scene's goal to make the second scene's goal and replace this pair's objects.
        """
        # Use the first goal for the pair now, and later copy it and modify the copy that will be the second goal.
        goal_1_target_rule_list = self._goal_1.get_target_rule_list()

        target_choice = 0
        # TODO Randomly choose a target from the goal to use in both scenes.
        # target_choice = random.randint(0, len(goal_1_target_rule_list) - 1)

        # Create all the targets in the goal that must come before the chosen one.
        self._goal_1.generate_target_list(target_choice)

        # Save each existing target and its bounding rectangles for later.
        goal_1_target_list = self._goal_1.get_target_list()
        shared_bounds_list = self._goal_1.get_bounds_list()

        must_containerize_target = self._options.target_containerize != BoolPairOption.NO_NO
        must_containerize_confusor = self._options.confusor_containerize != BoolPairOption.NO_NO

        target_receptacle_definition_list = None

        for _ in range(util.MAX_TRIES):
            # Choose a definition for the chosen target to use in both scenes.
            target_definition = self._options.target_definition if self._options.target_definition else \
                    goal_1_target_rule_list[target_choice].choose_definition()

            # Create the target template now at a location, and later it'll move to its location for each scene.
            # Assumes that both scenes have the same target (will this always be true in the future?)
            target_template = util.instantiate_object(target_definition, geometry.ORIGIN_LOCATION)

            # If we must containerize the target, ensure it's not too big for any of the containers.
            if must_containerize_target:
                target_receptacle_definition_list = containers.find_suitable_enclosable_list(target_template)
                if len(target_receptacle_definition_list) > 0:
                    break
            else:
                break
            target_definition = None
            target_template = None

        if not target_definition or not target_template:
            raise exceptions.SceneException(f'{self.get_name()} cannot create good target (maybe all choices are too big?)')

        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} target template: {target_template}')

        confusor_definition = None
        confusor_template = None
        confusor_receptacle_definition_list = None
        obstructor_definition = None
        obstructor_template = None
        receptacle_definition = None
        receptacle_template = None
        area_index = None
        orientation = None
        target_rotation = None
        confusor_rotation = None

        # Create the confusor to use in either scene if needed.
        # Assumes that both scenes have the same confusor (will this always be true in the future?)
        if self._options.confusor != BoolPairOption.NO_NO:
            for _ in range(util.MAX_TRIES):
                confusor_definition = self._options.confusor_definition if self._options.confusor_definition else \
                        self._goal_1.get_confusor_rule(target_template).choose_definition()
                # Create the confusor template now at a location, and later it'll move to its location for each scene.
                confusor_template = util.instantiate_object(confusor_definition, geometry.ORIGIN_LOCATION)

                # If we must containerize the confusor, ensure it's not too big for any of the containers.
                if must_containerize_confusor:
                    confusor_receptacle_definition_list = containers.find_suitable_enclosable_list(confusor_template, \
                            target_receptacle_definition_list if must_containerize_target else None)
                    if len(confusor_receptacle_definition_list) > 0:
                        break
                else:
                    break
                confusor_definition = None
                confusor_template = None

            if not confusor_definition or not confusor_template:
                raise exceptions.SceneException(f'{self.get_name()} cannot create good confusor (maybe all choices are too big?)')

        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} confusor template: {confusor_template}')

        is_confusor_close_in_goal_1 = (self._options.confusor_location == ConfusorLocationPairOption.CLOSE_CLOSE or \
                self._options.confusor_location == ConfusorLocationPairOption.CLOSE_FAR)

        is_confusor_close_in_goal_2 = (self._options.confusor_location == ConfusorLocationPairOption.CLOSE_CLOSE or \
                self._options.confusor_location == ConfusorLocationPairOption.NONE_CLOSE)

        # Create the receptacle to use in either scene that will containerize the target and/or confusor if needed.
        # Assumes that both scenes have the same receptacle (will this always be true in the future?)
        if must_containerize_target or must_containerize_confusor:
            must_hold_both = (self._is_true_goal_1(self._options.confusor) and \
                    self._is_true_goal_1(self._options.target_containerize) and \
                    self._is_true_goal_1(self._options.confusor_containerize) and is_confusor_close_in_goal_1) or \
                    (self._is_true_goal_2(self._options.confusor) and \
                    self._is_true_goal_2(self._options.target_containerize) and \
                    self._is_true_goal_2(self._options.confusor_containerize) and is_confusor_close_in_goal_2)

            # If the confusor will be close to the target in either scene, the receptacle must be able to hold both.
            if must_hold_both:
                receptacle_data = self._create_receptacle_around_both(target_definition, confusor_definition)
                if not receptacle_data:
                    raise exceptions.SceneException(f'{self.get_name()} cannot create enclosable receptacle around both: target={target_definition} confusor={confusor_definition}')
                receptacle_definition, area_index, target_rotation, confusor_rotation, orientation = receptacle_data
            # Else ensure that a receptacle can hold the target or confusor individually.
            else:
                target_definition_if_containerize = target_definition if must_containerize_target else None
                confusor_definition_if_containerize = confusor_definition if must_containerize_confusor else None
                receptacle_data = self._create_receptacle_around_either(target_definition_if_containerize, \
                        confusor_definition_if_containerize)
                if not receptacle_data:
                    raise exceptions.SceneException(f'{self.get_name()} cannot create enclosable receptacle around either: target={target_definition_if_containerize} confusor={confusor_definition_if_containerize}')
                receptacle_definition, area_index, target_rotation, confusor_rotation = receptacle_data
            # Create the receptacle template now at a location, and later it'll move to its location for each scene.
            receptacle_template = util.instantiate_object(receptacle_definition, geometry.ORIGIN_LOCATION)

        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} receptacle template: {receptacle_template}')

        # If an object is switched across the scenes (in the same position), use the larger object to generate the
        # location to avoid any collisions (if positioned inside a receptacle, the receptacle must be larger).
        larger_of_target_or_receptacle = receptacle_template if must_containerize_target else target_template
        larger_of_confusor_or_receptacle = receptacle_template if must_containerize_confusor else confusor_template
        larger_of_target_or_confusor = self._find_larger_object(larger_of_target_or_receptacle, \
                larger_of_confusor_or_receptacle)

        # Create the obstructor to use in either scene if needed.
        # Assumes that both scenes have the same obstructor (will this always be true in the future?)
        if self._options.obstructor != ObstructorPairOption.NONE_NONE:
            obstruct_vision = (self._options.obstructor == ObstructorPairOption.NONE_VISION)
            obstructor_definition = self._options.obstructor_definition if self._options.obstructor_definition else \
                    self._goal_1.get_obstructor_rule(larger_of_target_or_receptacle, \
                    obstruct_vision).choose_definition()
            # Create the obstructor template now at a location, and later it'll move to its location for each scene.
            obstructor_template = util.instantiate_object(obstructor_definition, geometry.ORIGIN_LOCATION)

        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} obstructor template: {obstructor_template}')

        larger_of_target_or_obstructor = self._find_larger_object(larger_of_target_or_receptacle, \
                obstructor_template)
        larger_object = self._find_larger_object(larger_of_target_or_confusor, larger_of_target_or_obstructor)

        target_location_1 = None
        target_location_2 = None
        confusor_location_1 = None
        confusor_location_2 = None

        is_target_relative_to_performer_start = \
                (self._options.target_location == TargetLocationPairOption.FRONT_BACK or \
                self._options.target_location == TargetLocationPairOption.FRONT_FRONT)
        is_confusor_relative_to_performer_start = (confusor_template and self._options.confusor_location == \
                ConfusorLocationPairOption.BACK_FRONT)

        # If the target must be positioned relative to the performer_start, find locations both in front of and in back
        # of the performer based on its position/rotation. Do this first because it may change the performer_start.
        if is_target_relative_to_performer_start:
            location_front, location_back = self._generate_front_and_back(self._goal_1, larger_object, \
                    goal_1_target_rule_list[target_choice], True)
            target_location_1 = location_front
            target_location_2 = location_back if \
                    self._options.target_location == TargetLocationPairOption.FRONT_BACK else location_front
            if is_confusor_relative_to_performer_start:
                confusor_location_1 = location_back
                confusor_location_2 = location_front

        else:
            # If an object must be positioned relative to the performer_start, do it first.
            if is_confusor_relative_to_performer_start:
                location_front, location_back = self._generate_front_and_back(self._goal_1, \
                        larger_of_confusor_or_receptacle, goal_1_target_rule_list[target_choice], True)
                confusor_location_1 = location_back
                confusor_location_2 = location_front

            # If the target isn't positioned relative to the performer_start, it'll be positioned randomly.
            target_location_1, target_location_2 = self._generate_random_location(self._goal_1, \
                    larger_of_target_or_receptacle, goal_1_target_rule_list[target_choice], \
                    goal_1_target_list, shared_bounds_list)

            # Add more target location scene options here if needed in the future.

        # The performer_start shouldn't be modified past here.
        performer_start = self._goal_1.get_performer_start()

        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} performer start: {performer_start}')
        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} target location 1: {target_location_1}')
        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} target location 2: {target_location_2}')

        # If needed, exchange the target with the obstructor, then position the target directly behind the obstructor.
        obstructor_location_1 = self._generate_obstructor_location(False, target_definition, target_location_1, \
                obstructor_definition, performer_start)
        obstructor_location_2 = self._generate_obstructor_location( \
                (self._options.obstructor != ObstructorPairOption.NONE_NONE), target_definition, target_location_2, \
                obstructor_definition, performer_start)

        # If the confusor isn't positioned relative to the performer_start, it's positioned relative to the target.
        if confusor_template and not is_confusor_relative_to_performer_start:
            is_target_location_same_in_both = \
                    (self._options.target_location == TargetLocationPairOption.FRONT_FRONT or \
                    self._options.target_location == TargetLocationPairOption.RANDOM)
            confusor_location_1, confusor_location_2 = self._generate_confusor_location(confusor_definition, \
                    target_definition, target_template, target_location_1, target_location_2, performer_start, \
                    is_confusor_close_in_goal_1, is_confusor_close_in_goal_2, is_target_location_same_in_both)

        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} confusor location 1: {confusor_location_1}')
        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} confusor location 2: {confusor_location_2}')
        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} obstructor location 1: {obstructor_location_1}')
        logging.debug(f'{self.get_name()} {self._goal_1.get_name()} obstructor location 2: {obstructor_location_2}')

        # Create a new ID so it's not the same ID used by the target's receptacle_instance
        confusor_receptacle_id = str(uuid.uuid4())

        # Finalize the position of the target and the confusor in both scenes (they may be inside a receptacle).
        target_1, confusor_1, target_receptacle_1, confusor_receptacle_1 = self._finalize_target_confusor_position( \
                target_definition, target_template, target_location_1, \
                self._is_true_goal_1(self._options.target_containerize), \
                self._is_true_goal_1(self._options.confusor), is_confusor_close_in_goal_1, confusor_definition, \
                confusor_template, confusor_location_1, self._is_true_goal_1(self._options.confusor_containerize), \
                receptacle_definition, receptacle_template, area_index, target_rotation, confusor_rotation, \
                orientation, shared_bounds_list, confusor_receptacle_id)
        target_2, confusor_2, target_receptacle_2, confusor_receptacle_2 = self._finalize_target_confusor_position( \
                target_definition, target_template, target_location_2, \
                self._is_true_goal_2(self._options.target_containerize), \
                self._is_true_goal_2(self._options.confusor), is_confusor_close_in_goal_2, confusor_definition, \
                confusor_template, confusor_location_2, self._is_true_goal_2(self._options.confusor_containerize), \
                receptacle_definition, receptacle_template, area_index, target_rotation, confusor_rotation, \
                orientation, shared_bounds_list, confusor_receptacle_id)

        obstructor_1 = self._finalize_obstructor(False, obstructor_definition, obstructor_template, \
                obstructor_location_1, shared_bounds_list)
        obstructor_2 = self._finalize_obstructor((self._options.obstructor != ObstructorPairOption.NONE_NONE), \
                obstructor_definition, obstructor_template, obstructor_location_2, shared_bounds_list)

        logging.info(f'{self.get_name()} {self._goal_1.get_name()} target_1 {target_1["type"]} {target_1["id"]}')
        logging.info(f'{self.get_name()} {self._goal_1.get_name()} target_2 {target_2["type"]} {target_2["id"]}')
        logging.info(f'{self.get_name()} {self._goal_1.get_name()} target_receptacle_1 {((target_receptacle_1["type"] + " " + target_receptacle_1["id"]) if target_receptacle_1 else "None")}')
        logging.info(f'{self.get_name()} {self._goal_1.get_name()} target_receptacle_2 {((target_receptacle_2["type"] + " " + target_receptacle_2["id"]) if target_receptacle_2 else "None")}')
        logging.info(f'{self.get_name()} {self._goal_1.get_name()} confusor_1 {((confusor_1["type"] + " " + confusor_1["id"]) if confusor_1 else "None")}')
        logging.info(f'{self.get_name()} {self._goal_1.get_name()} confusor_2 {((confusor_2["type"] + " " + confusor_2["id"]) if confusor_2 else "None")}')
        logging.info(f'{self.get_name()} {self._goal_1.get_name()} obstructor_1 {((obstructor_1["type"] + " " + obstructor_1["id"]) if obstructor_1 else "None")}')
        logging.info(f'{self.get_name()} {self._goal_1.get_name()} obstructor_2 {((obstructor_2["type"] + " " + obstructor_2["id"]) if obstructor_2 else "None")}')

        confusor_list_1 = [confusor_1] if confusor_1 else []
        confusor_list_2 = [confusor_2] if confusor_2 else []
        distractor_list_1 = [instance for instance in [target_receptacle_1, confusor_receptacle_1] if instance]
        distractor_list_2 = [instance for instance in [target_receptacle_2, confusor_receptacle_2] if instance]
        obstructor_list_1 = [obstructor_1] if obstructor_1 else []
        obstructor_list_2 = [obstructor_2] if obstructor_2 else []

        if is_target_relative_to_performer_start or is_confusor_relative_to_performer_start:
            # Ensure that the random location of distractors or walls doesn't accidentally make them obstructors.
            self._goal_1.set_distractor_rule(DistractorNeverObstructsTargetObjectRule)
            self._goal_1.set_no_random_obstructor()

        self._finalize_goal_1(target_1, confusor_list_1, distractor_list_1, obstructor_list_1)
        self._finalize_goal_2(target_choice, confusor_list_1, distractor_list_1, obstructor_list_1, target_2, \
                confusor_list_2, distractor_list_2, obstructor_list_2)

    def _create_receptacle_around_both(self, target_instance: Dict[str, Any], confusor_instance: Dict[str, Any]) -> \
            Optional[Tuple[Dict[str, Any], int, float, float, containers.Orientation]]:
        """Create and return a receptacle that encloses the target and confusor together. If impossible return None."""

        # Find an enclosable receptacle that can hold both the target and the confusor together.
        receptacle_definition_list = containers.retrieve_enclosable_object_definition_list().copy()
        random.shuffle(receptacle_definition_list)
        for receptacle_definition in receptacle_definition_list:
            valid_containment = containers.can_contain_both(receptacle_definition, target_instance, confusor_instance)
            if valid_containment:
                break
            valid_containment = None
        if valid_containment:
            receptacle_definition, area_index, orientation, target_rotation, confusor_rotation = valid_containment
            return receptacle_definition, area_index, target_rotation, confusor_rotation, orientation
        return None

    def _create_receptacle_around_either(self, target_instance: Dict[str, Any], confusor_instance: Dict[str, Any]) -> \
            Optional[Tuple[Dict[str, Any], int, float, float]]:
        """Create and return a receptacle that encloses the target or confusor alone. If impossible return None."""

        # Find an enclosable receptacle that can hold either the target or the confusor individually.
        receptacle_definition_list = containers.retrieve_enclosable_object_definition_list().copy()
        random.shuffle(receptacle_definition_list)
        valid_containment_list = containers.get_enclosable_containments((target_instance, confusor_instance), \
                receptacle_definition_list)

        if len(valid_containment_list) == 0:
            return None

        valid_containment = random.choice(valid_containment_list)
        receptacle_definition, area_index, angles = valid_containment

        # The angles list should have a length of 2 if the confusor_instance is not None
        return receptacle_definition, area_index, angles[0], (angles[1] if len(angles) == 2 else None)

    def _finalize_goal_1(self, target_1: Dict[str, Any], confusor_list: List[Dict[str, Any]], \
            distractor_list: List[Dict[str, Any]], obstructor_list: List[Dict[str, Any]]) -> None:
        """Finalize the target and other objects in the first goal."""

        # Add the first version of each chosen object to the first goal.
        goal_1_target_list = self._goal_1.get_target_list()
        goal_1_target_list.append(target_1)
        goal_1_confusor_list = self._goal_1.get_confusor_list()
        for confusor in confusor_list:
            goal_1_confusor_list.append(confusor)
        goal_1_distractor_list = self._goal_1.get_distractor_list()
        for distractor in distractor_list:
            goal_1_distractor_list.append(distractor)
        goal_1_obstructor_list = self._goal_1.get_obstructor_list()
        for obstructor in obstructor_list:
            goal_1_obstructor_list.append(obstructor)

        # Generate the other random objects in the first goal, then copy them to the second goal.
        self._goal_1.compute_objects(self._scene_1['wallMaterial'], self._scene_1['wallColors'])

    def _finalize_goal_2(self, target_choice: int, confusor_list_1: List[Dict[str, Any]], \
            distractor_list_1: List[Dict[str, Any]], obstructor_list_1: List[Dict[str, Any]], \
            target_2: Dict[str, Any], confusor_list_2: List[Dict[str, Any]], \
            distractor_list_2: List[Dict[str, Any]], obstructor_list_2: List[Dict[str, Any]]) -> None:
        """Finalize the target and other objects in the first goal."""

        # Copy the random objects from the first goal to the second goal.
        self._goal_2 = copy.deepcopy(self._goal_1)

        # Exchange the first version of the target object with the second version to keep it at the same list index.
        goal_2_target_list = self._goal_2.get_target_list()
        goal_2_target_list[target_choice] = target_2

        # Remove the first version of each chosen object in the lists that were copied from the first goal.
        goal_2_confusor_list = self._goal_2.get_confusor_list()
        for confusor in confusor_list_1:
            goal_2_confusor_list.pop(0)
        goal_2_distractor_list = self._goal_2.get_distractor_list()
        for distractor in distractor_list_1:
            goal_2_distractor_list.pop(0)
        goal_2_obstructor_list = self._goal_2.get_obstructor_list()
        for obstructor in obstructor_list_1:
            goal_2_obstructor_list.pop(0)

        # Add the second version of each chosen object to the second goal.
        confusor_list_2.reverse()
        for confusor in confusor_list_2:
            goal_2_confusor_list.insert(0, confusor)
        distractor_list_2.reverse()
        for distractor in distractor_list_2:
            goal_2_distractor_list.insert(0, distractor)
        obstructor_list_2.reverse()
        for obstructor in obstructor_list_2:
            goal_2_obstructor_list.insert(0, obstructor)

    def _finalize_obstructor(self, show_obstructor: bool, obstructor_definition: Dict[str, Any], \
            obstructor_template: Dict[str, Any], obstructor_location: Dict[str, float], \
            bounds_list: List[List[Dict[str, float]]]) -> Dict[str, Any]:
        """Finalize the position of the obstructor object and return it (if any). Will modify the given bounds_list."""

        if show_obstructor:
            obstructor_instance = copy.deepcopy(obstructor_template)
            util.move_to_location(obstructor_definition, obstructor_instance, obstructor_location, \
                    geometry.generate_object_bounds(obstructor_definition['dimensions'], \
                    obstructor_definition['offset'] if 'offset' in obstructor_definition else None,
                    obstructor_location['position'], obstructor_location['rotation']), obstructor_definition)
            bounds_list.append(obstructor_instance['shows'][0]['boundingBox'])
            return obstructor_instance

        return None

    def _finalize_target_confusor_position(self, target_definition: Dict[str, Any], target_template: Dict[str, Any], \
            target_location: Dict[str, Any], containerize_target: bool, show_confusor: bool, is_confusor_close: bool, \
            confusor_definition: Dict[str, Any], confusor_template: Dict[str, Any], \
            confusor_location: Dict[str, Any], containerize_confusor: bool, receptacle_definition: Dict[str, Any], \
            receptacle_template: Dict[str, Any], area_index: int, target_rotation: float, confusor_rotation: float, \
            orientation: containers.Orientation, bounds_list: List[List[Dict[str, float]]], \
            confusor_receptacle_id: int) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """Finalize the position of the target and confusor, and return the target, confusor (if any), target
        receptacle (if any), and confusor receptacle (if any). Will modify the given bounds_list."""

        target_instance = copy.deepcopy(target_template)
        confusor_instance = copy.deepcopy(confusor_template) if (confusor_template and show_confusor) else None
        target_receptacle_instance = None
        confusor_receptacle_instance = None

        # If needed, position both the target and confusor together inside a receptacle.
        if containerize_target and containerize_confusor and show_confusor and is_confusor_close:
            target_receptacle_instance = copy.deepcopy(receptacle_template)
            # Update the Y position of the location to use the positionY from the receptacle definition.
            target_location['position']['y'] = receptacle_definition.get('positionY', 0)
            util.move_to_location(receptacle_definition, target_receptacle_instance, target_location, \
                    geometry.generate_object_bounds(receptacle_definition['dimensions'], \
                    receptacle_definition['offset'] if 'offset' in receptacle_definition else None, \
                    target_location['position'], target_location['rotation']), target_definition)
            containers.put_objects_in_container(target_definition, target_instance, confusor_definition, \
                    confusor_instance, target_receptacle_instance, receptacle_definition, area_index, orientation, \
                    target_rotation, confusor_rotation)
            bounds_list.append(target_receptacle_instance['shows'][0]['boundingBox'])

        else:
            if containerize_target:
                # Use the target location for its receptacle, then position the target inside its receptacle.
                target_receptacle_instance = copy.deepcopy(receptacle_template)
                # Update the Y position of the location to use the positionY from the receptacle definition.
                target_location['position']['y'] = receptacle_definition.get('positionY', 0)
                util.move_to_location(receptacle_definition, target_receptacle_instance, target_location, \
                    geometry.generate_object_bounds(receptacle_definition['dimensions'], \
                    receptacle_definition['offset'] if 'offset' in receptacle_definition else None, \
                    target_location['position'], target_location['rotation']), target_definition)
                containers.put_object_in_container(target_definition, target_instance, target_receptacle_instance, \
                        receptacle_definition, area_index, target_rotation)
                bounds_list.append(target_receptacle_instance['shows'][0]['boundingBox'])
            else:
                util.move_to_location(target_definition, target_instance, target_location, \
                    geometry.generate_object_bounds(target_definition['dimensions'], \
                    target_definition['offset'] if 'offset' in target_definition else None, \
                    target_location['position'], target_location['rotation']), target_definition)
                bounds_list.append(target_instance['shows'][0]['boundingBox'])
            if show_confusor:
                if containerize_confusor:
                    # Use the confusor location for its receptacle, then position the confusor inside its receptacle.
                    confusor_receptacle_instance = copy.deepcopy(receptacle_template)
                    # Update the Y position of the location to use the positionY from the receptacle definition.
                    confusor_location['position']['y'] = receptacle_definition.get('positionY', 0)
                    confusor_receptacle_instance['id'] = confusor_receptacle_id
                    util.move_to_location(receptacle_definition, confusor_receptacle_instance, confusor_location, \
                        geometry.generate_object_bounds(receptacle_definition['dimensions'], \
                        receptacle_definition['offset'] if 'offset' in receptacle_definition else None, \
                        confusor_location['position'], confusor_location['rotation']), confusor_definition)
                    containers.put_object_in_container(confusor_definition, confusor_instance, \
                            confusor_receptacle_instance, receptacle_definition, area_index, confusor_rotation)
                    bounds_list.append(confusor_receptacle_instance['shows'][0]['boundingBox'])
                else:
                    util.move_to_location(confusor_definition, confusor_instance, confusor_location, \
                        geometry.generate_object_bounds(confusor_definition['dimensions'], \
                        confusor_definition['offset'] if 'offset' in confusor_definition else None, \
                        confusor_location['position'], confusor_location['rotation']), confusor_definition)
                    bounds_list.append(confusor_instance['shows'][0]['boundingBox'])

        return target_instance, confusor_instance, target_receptacle_instance, confusor_receptacle_instance

    def _find_larger_object(self, object_one: Dict[str, Any], object_two: Dict[str, Any]) -> Dict[str, Any]:
        """Return the larger of the two given objects."""
        if not object_one and not object_two:
            return None
        if not object_one:
            return object_two
        if not object_two:
            return object_one
        # TODO Handle case if one object has larger X and other object has larger Z
        return object_one if (object_one['dimensions']['x'] > object_two['dimensions']['x'] or \
                object_one['dimensions']['z'] > object_two['dimensions']['z']) else object_two

    def _generate_confusor_location(self, confusor_definition: Dict[str, Any], target_definition: Dict[str, Any], \
            target_template: Dict[str, Any], target_location_1: Dict[str, float], 
            target_location_2: Dict[str, float], performer_start: Dict[str, Dict[str, float]], \
            is_confusor_close_in_goal_1: bool, is_confusor_close_in_goal_2: bool, \
            is_target_location_same_in_both: bool) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Generate and return the location for the confusor in both scenes positioned relative to the target."""

        # If the target location is the same in both scenes, just generate the confusor location once.
        if is_confusor_close_in_goal_1 and is_confusor_close_in_goal_2 and is_target_location_same_in_both:
            confusor_location = self._generate_location_close_to_object(confusor_definition, target_definition, \
                    target_location_1, performer_start)
            return confusor_location, confusor_location

        confusor_location_1 = None
        confusor_location_2 = None

        if is_confusor_close_in_goal_1:
            confusor_location_1 = self._generate_location_close_to_object(confusor_definition, target_definition, \
                    target_location_1, performer_start)
        else:
            confusor_location_1 = self._generate_location_far_from_object(confusor_definition, target_location_1, \
                    performer_start)

        if is_confusor_close_in_goal_2:
            confusor_location_2 = self._generate_location_close_to_object(confusor_definition, target_definition, \
                    target_location_2, performer_start)
        else:
            confusor_location_2 = self._generate_location_far_from_object(confusor_definition, target_location_2, \
                    performer_start)

        # Add more confusor location scene options here if needed in the future.

        return confusor_location_1, confusor_location_2

    def _generate_front_and_back(self, goal: InteractionGoal, object_definition: Dict[str, Any], \
            object_rule: ObjectRule, generate_back: bool) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a location both in front of and in back of the performer_start. Will modify the performer_start
        in the given goal if needed to generate the two locations. Return the front and back locations."""

        performer_start = goal.get_performer_start()
        location_front = None
        location_back = None

        for _ in range(util.MAX_TRIES):
            # TODO Use existing target bounds?
            location_front = self._identify_front(object_definition, object_rule, performer_start)
            if location_front:
                if generate_back:
                    location_back = self._identify_back(object_definition, object_rule, performer_start)
                    if location_back:
                        break
                else:
                    break
            location_front = None
            location_back = None
            performer_start = goal.reset_performer_start()

        if not generate_back and not location_front:
            raise exceptions.SceneException(f'{self.get_name()} cannot position performer start in front of object={object_definition}')

        if generate_back and (not location_front or not location_back):
            raise exceptions.SceneException(f'{self.get_name()} cannot position performer start in front of and in back of object={object_definition}')

        return location_front, location_back

    def _generate_location_close_to_object(self, object_definition: Dict[str, Any], target_definition: Dict[str, Any], \
            target_location: Dict[str, float], performer_start: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Generate and return a new location close to the given target_location."""
        # TODO Use existing target bounds?
        location_close = geometry.get_adjacent_location(object_definition, target_definition, target_location, \
                performer_start)
        if not location_close:
            raise exceptions.SceneException(f'{self.get_name()} cannot position close to target: object={object_definition} target={target_definition}')
        return location_close

    def _generate_location_far_from_object(self, object_definition: Dict[str, Any], target_location: Dict[str, float], \
            performer_start: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Generate and return a new location far away the given target location."""
        for _ in range(util.MAX_TRIES):
            # TODO Use existing target bounds?
            location_far = geometry.calc_obj_pos(performer_start['position'], [], object_definition)
            if not geometry.are_adjacent(target_location, location_far, distance = \
                    geometry.MIN_OBJECTS_SEPARATION_DISTANCE):
                break
            location_far = None
        if not location_far:
            raise exceptions.SceneException(f'{self.get_name()} cannot position far from target: object={object_definition} target={target_location}')
        return location_far

    def _generate_obstructor_location(self, show_obstructor: bool, target_definition: Dict[str, Any], \
            target_location: Dict[str, float], obstructor_definition: Dict[str, Any], \
            performer_start: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """If needed, find and return a location for the given obstructor directly in front of the given target."""

        if show_obstructor and obstructor_definition:
            # Generate an adjacent location so that the obstructor is between the target and the performer start.
            # TODO Use existing target bounds?
            obstructor_location = geometry.get_adjacent_location(obstructor_definition, target_definition, \
                    target_location, performer_start, True)
            if not obstructor_location:
                raise exceptions.SceneException(f'{self.get_name()} cannot position target directly behind obstructor: performer_start={performer_start} target={target_definition} obstructor={obstructor_definition}')
            return obstructor_location

        return None

    def _generate_random_location(self, goal: InteractionGoal, object_definition: Dict[str, Any], \
            object_rule: ObjectRule, target_list: List[Dict[str, Any]], \
            bounds_list: List[List[Dict[str, float]]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generate a random location and return it twice."""

        for _ in range(util.MAX_TRIES):
            # TODO Use existing target bounds?
            object_location, bounds = object_rule.choose_location(object_definition, goal.get_performer_start(), \
                    bounds_list)
            if object_rule.validate_location(object_location, target_list, goal.get_performer_start()):
                break
            object_location = None
        if not object_location:
            raise exceptions.SceneException(f'{self.get_name()} cannot randomly position object={object_definition}')
        return object_location, object_location

    def _identify_front(self, object_definition: Dict[str, Any], object_rule: ObjectRule, \
            performer_start: Dict[str, float]) -> Dict[str, Any]:
        """Find and return a location in front of the given performer_start."""

        for _ in range(util.MAX_TRIES):
            location_front = geometry.get_location_in_front_of_performer(performer_start, object_definition)
            if location_front and object_rule.validate_location(location_front, [], performer_start):
                break
            location_front = None
        return location_front

    def _identify_back(self, object_definition: Dict[str, Any], object_rule: ObjectRule, \
            performer_start: Dict[str, float]) -> Dict[str, Any]:
        """Find and return a location in back of the given performer_start."""

        for _ in range(util.MAX_TRIES):
            location_back = geometry.get_location_in_back_of_performer(performer_start, object_definition)
            if location_back and object_rule.validate_location(location_back, [], performer_start):
                break
            location_back = None
        return location_back

    def _is_true_goal_1(self, bool_pair: BoolPairOption):
        """Return if the given scene options bool_pair is true in the first goal."""
        return bool_pair == BoolPairOption.YES_NO or bool_pair == BoolPairOption.YES_YES

    def _is_true_goal_2(self, bool_pair: BoolPairOption):
        """Return if the given scene options bool_pair is true in the second goal."""
        return bool_pair == BoolPairOption.NO_YES or bool_pair == BoolPairOption.YES_YES

class Pair1(InteractionPair):
    """(1A) The Target Object is immediately visible (starting in view of
    the camera) OR (1B) behind the camera (must rotate to see the
    object). For each pair, the object may or may not be inside a
    container (like a box). See MCS-232.
    """

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        containerize = BoolPairOption.YES_YES if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE else \
                BoolPairOption.NO_NO
        super(Pair1, self).__init__(1, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = containerize, target_location = TargetLocationPairOption.FRONT_BACK))


class Pair6(InteractionPair):
    """(6A) The Target Object is positioned immediately visible and a
    Similar Object is not immediately visible OR (6B) the Target
    Object is positioned not immediately visible and a Similar Object
    is immediately visible. For each pair, the objects may or may not
    be inside identical containers, but only if the container is big
    enough to hold both individually; otherwise, no container will be
    used in that pair. See MCS-233.
    """

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        containerize = BoolPairOption.YES_YES if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE else \
                BoolPairOption.NO_NO
        super(Pair6, self).__init__(6, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = containerize, target_location = TargetLocationPairOption.FRONT_BACK, \
                confusor = BoolPairOption.YES_YES, confusor_containerize = containerize, \
                confusor_location = ConfusorLocationPairOption.BACK_FRONT))


class Pair2(InteractionPair):
    """(2A) The Target Object is immediately visible OR (2B) is hidden
    behind a larger object that itself is immediately visible. For
    each pair, the object may or may not be inside a container (like a
    box). See MCS-239.
    """

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        containerize = BoolPairOption.YES_YES if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE else \
                BoolPairOption.NO_NO
        # TODO MCS-320 Let target be containerized
        containerize = BoolPairOption.NO_NO
        super(Pair2, self).__init__(2, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = containerize, target_location = TargetLocationPairOption.FRONT_FRONT, \
                obstructor = ObstructorPairOption.NONE_VISION))


class Pair7(InteractionPair):
    """(7) Like pair (6), but the Target Object is always inside a container, and the Similar Object is never inside a
    container."""

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        super(Pair7, self).__init__(7, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = BoolPairOption.YES_YES, target_location = TargetLocationPairOption.FRONT_BACK, \
                confusor = BoolPairOption.YES_YES, confusor_location = ConfusorLocationPairOption.BACK_FRONT))


class Pair3(InteractionPair):
    """(3A) The Target Object is positioned normally, without a Similar
    Object in the scene, OR (3B) with a Similar Object in the scene,
    and directly adjacent to it. For each pair, the objects may or may
    not be inside a container, but only if the container is big enough
    to hold both together; otherwise, no container will be used in
    that pair.
    """

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        containerize = BoolPairOption.YES_YES if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE else \
                BoolPairOption.NO_NO
        super(Pair3, self).__init__(3, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = containerize, confusor = BoolPairOption.NO_YES, \
                confusor_containerize = containerize, confusor_location = ConfusorLocationPairOption.NONE_CLOSE))


class Pair4(InteractionPair):
    """(4A) The Target Object is positioned normally, without a Similar Object
    in the scene, OR (4B) with a Similar Object in the scene, but far away
    from it.  For each pair, the objects may or may not be inside identical
    containers, but only if the container is big enough to hold both
    individually; otherwise, no container will be used in that pair."""

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        containerize = BoolPairOption.YES_YES if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE else \
                BoolPairOption.NO_NO
        super(Pair4, self).__init__(4, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = containerize, confusor = BoolPairOption.NO_YES, \
                confusor_containerize = containerize, confusor_location = ConfusorLocationPairOption.NONE_FAR))


class Pair5(InteractionPair):
    """(5A) The Target Object is positioned directly adjacent to a Similar
    Object OR (5B) far away from a Similar Object. For each pair, the
    objects may or may not be inside identical containers, but only if
    the container is big enough to hold both together; otherwise, no
    container will be used in that pair.
    """

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        containerize = BoolPairOption.YES_YES if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE else \
                BoolPairOption.NO_NO
        super(Pair5, self).__init__(5, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = containerize, confusor = BoolPairOption.YES_YES, \
                confusor_containerize = containerize, confusor_location = ConfusorLocationPairOption.CLOSE_FAR))


class Pair8(InteractionPair):
    """(8A) The Target Object is positioned adjacent to a Similar Object OR (8B) the Target Object is positioned
    adjacent to a Similar Object, but the Target Object is inside a container. See MCS-238."""

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        super(Pair8, self).__init__(8, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = BoolPairOption.NO_YES, confusor = BoolPairOption.YES_YES, \
                confusor_location = ConfusorLocationPairOption.CLOSE_CLOSE))


class Pair9(InteractionPair):
    """(9A) The Target Object is immediately visible and can be approached in a relatively direct line OR (9B) the
    Target Object is immediately visible but getting to it would require navigating around a large piece of furniture
    (or some other obstacle). For instance, from the AIs vantage point, it can see the target object positioned beyond
    the coffee table, so to get to it, the AI would need to maneuver around the coffee table.  For each pair, the
    object may or may not be inside an open container (like a box)."""

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        containerize = BoolPairOption.YES_YES if random.random() < InteractionGoal.OBJECT_RECEPTACLE_CHANCE else \
                BoolPairOption.NO_NO
        # TODO MCS-320 Let target be containerized
        containerize = BoolPairOption.NO_NO
        super(Pair9, self).__init__(9, template, goal_name, find_path, options = SceneOptions( \
                target_containerize = containerize, target_location = TargetLocationPairOption.FRONT_FRONT, \
                obstructor = ObstructorPairOption.NONE_NAVIGATION))


class Pair11(InteractionPair):
    """(11A) The Target Object and a Similar Object are positioned adjacent to each other and immediately visible OR
    (11B) the Target Object and a Similar Object are positioned adjacent to each other and NOT immediately visible."""

    def __init__(self, template: Dict[str, Any], goal_name: str = None, find_path: bool = False):
        super(Pair11, self).__init__(11, template, goal_name, find_path, options = SceneOptions( \
                target_location = TargetLocationPairOption.FRONT_BACK, confusor = BoolPairOption.YES_YES,
                confusor_location = ConfusorLocationPairOption.CLOSE_CLOSE))


INTERACTION_PAIR_CLASSES = [
    Pair1,
    Pair2,
    Pair3,
    #Pair4, # Won't use
    #Pair5, # Won't use
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
    return [klass.__name__.replace('Pair', '') for klass in INTERACTION_PAIR_CLASSES]

