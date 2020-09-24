import random
from enum import Enum, auto
from typing import Any, Dict, Optional

import exceptions


CONTAINERIZE_CHANCE = 0.333


class BoolPlan(Enum):
    YES_YES = auto()
    YES_NO = auto()
    NO_NO = auto()
    NO_YES = auto()


class ConfusorLocationPlan(Enum):
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


class ObstructorPlan(Enum):
    # No obstructor
    NONE_NONE = auto()
    # Obstruct navigation only (and not vision)
    NONE_NAVIGATION = auto()
    # Obstruct navigation and vision
    NONE_VISION = auto()


class TargetLocationPlan(Enum):
    # Either in back of or in from of the performer
    FRONT_BACK = auto()
    # The same position in front of the performer
    FRONT_FRONT = auto()
    # The same random position
    RANDOM = auto()


def is_true(bool_plan: BoolPlan, scene_index: int) -> bool:
    """Return if the given plan is true in the scene with the given index."""
    if scene_index == 1:
        return (bool_plan == BoolPlan.YES_NO or bool_plan == BoolPlan.YES_YES)
    if scene_index == 2:
        return (bool_plan == BoolPlan.NO_YES or bool_plan == BoolPlan.YES_YES)
    raise exceptions.SceneException(
        f'Scene index must be 1 or 2 but was {scene_index}')


class InteractivePlan():
    """Configurable interactive setup options."""

    def __init__(
        self,
        name: str,
        target_definition: Optional[Dict[str, Any]] = None,
        target_containerize: BoolPlan = BoolPlan.NO_NO,
        target_location: TargetLocationPlan = TargetLocationPlan.RANDOM,
        confusor: BoolPlan = BoolPlan.NO_NO,
        confusor_definition: Optional[Dict[str, Any]] = None,
        confusor_containerize: BoolPlan = BoolPlan.NO_NO,
        confusor_location: ConfusorLocationPlan =
        ConfusorLocationPlan.CLOSE_CLOSE,
        obstructor: ObstructorPlan = ObstructorPlan.NONE_NONE,
        obstructor_definition: Optional[Dict[str, Any]] = None
    ) -> None:
        self.name = name
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

    def get_name(self) -> str:
        return self.name


def create_plan_pair_1() -> InteractivePlan:
    """(1A) The Target Object is immediately visible (starting in view of
    the camera) OR (1B) behind the camera (must rotate to see the
    object). For each pair, the object may or may not be inside a
    container (like a box). See MCS-232.
    """
    containerize = (
        BoolPlan.YES_YES if random.random() < CONTAINERIZE_CHANCE
        else BoolPlan.NO_NO
    )
    return InteractivePlan(
        name='pair 1',
        target_containerize=containerize,
        target_location=TargetLocationPlan.FRONT_BACK
    )


def create_plan_pair_2() -> InteractivePlan:
    """(2A) The Target Object is immediately visible OR (2B) is hidden
    behind a larger object that itself is immediately visible. For
    each pair, the object may or may not be inside a container (like a
    box). See MCS-239.
    """
    containerize = (
        BoolPlan.YES_YES if random.random() < CONTAINERIZE_CHANCE
        else BoolPlan.NO_NO
    )
    # TODO MCS-320 Let target be containerized
    containerize = BoolPlan.NO_NO
    return InteractivePlan(
        name='pair 2',
        target_containerize=containerize,
        target_location=TargetLocationPlan.FRONT_FRONT,
        obstructor=ObstructorPlan.NONE_VISION
    )


def create_plan_pair_3() -> InteractivePlan:
    """(3A) The Target Object is positioned normally, without a Similar
    Object in the scene, OR (3B) with a Similar Object in the scene,
    and directly adjacent to it. For each pair, the objects may or may
    not be inside a container, but only if the container is big enough
    to hold both together; otherwise, no container will be used in
    that pair.
    """
    containerize = (
        BoolPlan.YES_YES if random.random() < CONTAINERIZE_CHANCE
        else BoolPlan.NO_NO
    )
    return InteractivePlan(
        name='pair 3',
        target_containerize=containerize,
        confusor=BoolPlan.NO_YES,
        confusor_containerize=containerize,
        confusor_location=ConfusorLocationPlan.NONE_CLOSE
    )


def create_plan_pair_4() -> InteractivePlan:
    """(4A) The Target Object is positioned normally, without a Similar Object
    in the scene, OR (4B) with a Similar Object in the scene, but far away
    from it.  For each pair, the objects may or may not be inside identical
    containers, but only if the container is big enough to hold both
    individually; otherwise, no container will be used in that pair."""
    containerize = (
        BoolPlan.YES_YES if random.random() < CONTAINERIZE_CHANCE
        else BoolPlan.NO_NO
    )
    return InteractivePlan(
        name='pair 4',
        target_containerize=containerize,
        confusor=BoolPlan.NO_YES,
        confusor_containerize=containerize,
        confusor_location=ConfusorLocationPlan.NONE_FAR
    )


def create_plan_pair_5() -> InteractivePlan:
    """(5A) The Target Object is positioned directly adjacent to a Similar
    Object OR (5B) far away from a Similar Object. For each pair, the
    objects may or may not be inside identical containers, but only if
    the container is big enough to hold both together; otherwise, no
    container will be used in that pair.
    """
    containerize = (
        BoolPlan.YES_YES if random.random() < CONTAINERIZE_CHANCE
        else BoolPlan.NO_NO
    )
    return InteractivePlan(
        name='pair 5',
        target_containerize=containerize,
        confusor=BoolPlan.YES_YES,
        confusor_containerize=containerize,
        confusor_location=ConfusorLocationPlan.CLOSE_FAR
    )


def create_plan_pair_6() -> InteractivePlan:
    """(6A) The Target Object is positioned immediately visible and a
    Similar Object is not immediately visible OR (6B) the Target
    Object is positioned not immediately visible and a Similar Object
    is immediately visible. For each pair, the objects may or may not
    be inside identical containers, but only if the container is big
    enough to hold both individually; otherwise, no container will be
    used in that pair. See MCS-233.
    """
    containerize = (
        BoolPlan.YES_YES if random.random() < CONTAINERIZE_CHANCE
        else BoolPlan.NO_NO
    )
    return InteractivePlan(
        name='pair 6',
        target_containerize=containerize,
        target_location=TargetLocationPlan.FRONT_BACK,
        confusor=BoolPlan.YES_YES,
        confusor_containerize=containerize,
        confusor_location=ConfusorLocationPlan.BACK_FRONT
    )


def create_plan_pair_7() -> InteractivePlan:
    """(7) Like pair (6), but the Target Object is always inside a container,
    and the Similar Object is never inside a container."""
    return InteractivePlan(
        name='pair 7',
        target_containerize=BoolPlan.YES_YES,
        target_location=TargetLocationPlan.FRONT_BACK,
        confusor=BoolPlan.YES_YES,
        confusor_location=ConfusorLocationPlan.BACK_FRONT
    )


def create_plan_pair_8() -> InteractivePlan:
    """(8A) The Target Object is positioned adjacent to a Similar Object
    OR (8B) the Target Object is positioned adjacent to a Similar Object,
    but the Target Object is inside a container. See MCS-238."""
    return InteractivePlan(
        name='pair 8',
        target_containerize=BoolPlan.NO_YES,
        confusor=BoolPlan.YES_YES,
        confusor_location=ConfusorLocationPlan.CLOSE_CLOSE
    )


def create_plan_pair_9() -> InteractivePlan:
    """(9A) The Target Object is immediately visible and can be approached
    in a relatively direct line OR (9B) the Target Object is immediately
    visible but getting to it would require navigating around a large
    piece of furniture (or some other obstacle). For instance, from the
    AIs vantage point, it can see the target object positioned beyond
    the coffee table, so to get to it, the AI would need to maneuver
    around the coffee table.  For each pair, the object may or may not
    be inside an open container (like a box)."""
    containerize = (
        BoolPlan.YES_YES if random.random() < CONTAINERIZE_CHANCE
        else BoolPlan.NO_NO
    )
    # TODO MCS-320 Let target be containerized
    containerize = BoolPlan.NO_NO
    return InteractivePlan(
        name='pair 9',
        target_containerize=containerize,
        target_location=TargetLocationPlan.FRONT_FRONT,
        obstructor=ObstructorPlan.NONE_NAVIGATION
    )


def create_plan_pair_11() -> InteractivePlan:
    """(11A) The Target Object and a Similar Object are positioned
    adjacent to each other and immediately visible OR
    (11B) the Target Object and a Similar Object are positioned
    adjacent to each other and NOT immediately visible."""
    return InteractivePlan(
        name='pair 11',
        target_location=TargetLocationPlan.FRONT_BACK,
        confusor=BoolPlan.YES_YES,
        confusor_location=ConfusorLocationPlan.CLOSE_CLOSE
    )


def create_pair_plan(pair: int) -> InteractivePlan:
    if pair == 1:
        return create_plan_pair_1()
    if pair == 2:
        return create_plan_pair_2()
    if pair == 3:
        return create_plan_pair_3()
    if pair == 4:
        return create_plan_pair_4()
    if pair == 5:
        return create_plan_pair_5()
    if pair == 6:
        return create_plan_pair_6()
    if pair == 7:
        return create_plan_pair_7()
    if pair == 8:
        return create_plan_pair_8()
    if pair == 9:
        return create_plan_pair_9()
    if pair == 11:
        return create_plan_pair_11()
    raise exceptions.SceneException(
        f'Interactive pair number {pair} is not yet ready')
