import copy
from enum import Enum, auto
from typing import Dict, Any, Optional, Tuple, Sequence, List

import geometry
import objects
import util


def put_object_in_container(obj: Dict[str, Any],
                            container: Dict[str, Any],
                            container_def: Dict[str, Any],
                            area_index: int,
                            rotation: Optional[float] = None) -> None:
    area = container_def['enclosed_areas'][area_index]
    obj['locationParent'] = container['id']
    obj['shows'][0]['position'] = area['position'].copy()
    if 'rotation' not in obj['shows'][0]:
        obj['shows'][0]['rotation'] = geometry.ORIGIN.copy()
    if rotation is not None:
        obj['shows'][0]['rotation']['y'] = rotation
    # if it had a bounding_box, it's not valid any more
    obj.pop('bounding_box', None)


class Orientation(Enum):
    SIDE_BY_SIDE = auto()
    FRONT_TO_BACK = auto()


def put_objects_in_container(obj_a: Dict[str, Any],
                             obj_b: Dict[str, Any],
                             container: Dict[str, Any],
                             container_def: Dict[str, Any],
                             area_index: int,
                             orientation: Orientation,
                             rot_a: float,
                             rot_b: float) -> None:
    """Put two objects in the same enclosed area of a
    container. orientation determines how they are laid out with
    respect to each other within the container. rot_a and rot_b must
    be either 0 or 90.
    """
    if rot_a not in (0, 90):
        raise ValueError('only 0 and 90 degree rotations supported for object a, not {rot_a}')
    if rot_b not in (0, 90):
        raise ValueError('only 0 and 90 degree rotations supported for object b, not {rot_b}')

    area_position = container_def['enclosed_areas'][area_index]['position']
    obj_a['locationParent'] = container['id']
    obj_b['locationParent'] = container['id']
    shows_a = obj_a['shows'][0]
    shows_b = obj_b['shows'][0]
    if orientation == Orientation.SIDE_BY_SIDE:
        if rot_a == 0:
            width_a = obj_a['dimensions']['x']
        elif rot_a == 90:
            width_a = obj_a['dimensions']['z']
        shows_a['position'] = area_position.copy()
        shows_a['position']['x'] -= width_a / 2.0
        if rot_b == 0:
            width_b = obj_b['dimensions']['x']
        elif rot_a == 90:
            width_b = obj_b['dimensions']['z']
        shows_b['position'] = area_position.copy()
        shows_b['position']['x'] += width_b / 2.0
    elif orientation == Orientation.FRONT_TO_BACK:
        if rot_a == 0:
            height_a = obj_a['dimensions']['z']
        elif rot_a == 90:
            height_a = obj_a['dimensions']['x']
        shows_a['position'] = area_position.copy()
        shows_a['position']['z'] -= height_a / 2.0
        if rot_b == 0:
            height_b = obj_b['dimensions']['z']
        elif rot_b == 90:
            height_b = obj_b['dimensions']['x']
        shows_b['position'] = area_position.copy()
        shows_b['position']['z'] += height_b / 2.0
    shows_a['rotation'] = { 'y': rot_a }
    shows_b['rotation'] = { 'y': rot_b }
    # any bounding_box they may have had is not valid any more
    shows_a.pop('bounding_box', None)
    shows_b.pop('bounding_box', None)


def can_enclose(objectA: Dict[str, Any], objectB: Dict[str, Any]) -> bool:
    """Return True iff each 'dimensions' of objectA is >= the corresponding dimension of objectB."""
    return objectA['dimensions']['x'] >= objectB['dimensions']['x'] and \
        objectA['dimensions']['y'] >= objectB['dimensions']['y'] and \
        objectA['dimensions']['z'] >= objectB['dimensions']['z']


def can_contain(container_def: Dict[str, Any],
                *targets: Dict[str, Any]) -> Optional[int]:
    """Return the index of the container's "enclosed_areas" that all
     targets fit in, or None if they all do not fit in any of the
     enclosed_areas (or if the container doesn't have any). Does not
     try any rotation to see if that makes it possible to fit.
    """
    if 'enclosed_areas' not in container_def:
        return None
    for i in range(len(container_def['enclosed_areas'])):
        space = container_def['enclosed_areas'][i]
        fits = True
        for target in targets:
            if not can_enclose(space, target):
                fits = False
                break
        if fits:
            return i
    return None


def _ea_can_contain_both(ea_def: Dict[str, Any],
                         obj_a: Dict[str, Any], obj_b: Dict[str, Any]) \
                         -> Optional[Tuple[Orientation, float, float]]:
    ax = obj_a['dimensions']['x']
    bx = obj_b['dimensions']['x']
    az = obj_a['dimensions']['z']
    bz = obj_b['dimensions']['z']
    cx = ea_def['dimensions']['x']
    cz = ea_def['dimensions']['z']
    # first try side-by-side
    width = ax + bx
    depth = max(az, bz)
    if cx >= width and cz >= depth:
        return Orientation.SIDE_BY_SIDE, 0, 0

    # rotate b 90 degrees
    width = ax + bz
    depth = max(az, bx)
    if cx >= width and cz >= depth:
        return Orientation.SIDE_BY_SIDE, 0, 90

    # rotate a 90 degrees
    width = az + bx
    depth = max(ax, bz)
    if cx >= width and cz >= depth:
        return Orientation.SIDE_BY_SIDE, 90, 0

    # rotate both 90 degrees
    width = az + bz
    depth = max(ax, bx)
    if cx >= width and cz >= depth:
        return Orientation.SIDE_BY_SIDE, 90, 90

    # try front-to-back
    width = max(ax, bx)
    depth = az + bz
    if cx >= width and cz >= depth:
        return Orientation.FRONT_TO_BACK, 0, 0

    # rotate b 90 degrees
    width = max(ax, bz)
    depth = az + bx
    if cx >= width and cz >= depth:
        return Orientation.FRONT_TO_BACK, 0, 90

    # rotate a 90 degrees
    width = max(az, bx)
    depth = ax + bz
    if cx >= width and cz >= depth:
        return Orientation.FRONT_TO_BACK, 90, 0

    # rotate both 90 degrees
    width = max(az, bz)
    depth = ax + bx
    if cx >= width and cz >= depth:
        return Orientation.FRONT_TO_BACK, 90, 90

    return None


def _eas_can_contain_both(enclosed_areas: Sequence[Dict[str, Any]],
                         obj_a: Dict[str, Any], obj_b: Dict[str, Any]) \
                         -> Optional[Tuple[int, Orientation, float, float]]:
    for i in range(len(enclosed_areas)):
        ea = enclosed_areas[i]
        result = _ea_can_contain_both(ea, obj_a, obj_b)
        if result is not None:
            orientation, rotation_a, rotation_b = result
            return i, orientation, rotation_a, rotation_b
    return None


def can_contain_both(container_def: Dict[str, Any],
                     obj_a: Dict[str, Any], obj_b: Dict[str, Any]) \
                     -> Optional[Tuple[Dict[str, Any], int, Orientation, float, float]]:
    if 'enclosed_areas' in container_def:
        result = _eas_can_contain_both(container_def['enclosed_areas'], obj_a, obj_b)
        if result is None:
            return None
        index, orientation, angle_a, angle_b = result
        return container_def, index, orientation, angle_a, angle_b
    elif 'choose' in container_def:
        found_choice = None
        for choice in container_def['choose']:
            if 'enclosed_areas' in choice:
                result = _eas_can_contain_both(choice['enclosed_areas'],
                                               obj_a, obj_b)
                if result is not None:
                    index, orientation, angle_a, angle_b = result
                    new_def = util.finalize_object_definition(container_def, choice)
                    return new_def, index, orientation, angle_a, angle_b
    return None


def get_enclosable_container_defs(objs: Sequence[Dict[str, Any]],
                                  container_defs: Sequence[Dict[str, Any]] = None) \
                                  -> List[Dict[str, Any]]:
    """Return a list of object definitions for containers that can enclose
    all the passed objects objs. If container_defs is None, use
    objects.get_enclosed_containers().
    """
    if container_defs is None:
        container_defs = objects.get_enclosed_containers()
    valid_container_defs = []
    for container_def in container_defs:
        index = can_contain(container_def, *objs)
        if index is not None:
            valid_container_defs.append(container_def)
        elif 'choose' in container_def:
            # try choose
            valid_choices = []
            for choice in container_def['choose']:
                index = can_contain(choice, *objs)
                if index is not None:
                    valid_choices.append(choice)
            if len(valid_choices) > 0:
                if len(valid_choices) == len(container_def['choose']):
                    valid_container_defs.append(container_def)
                else:
                    new_def = copy.deepcopy(container_def)
                    new_def['choose'] = valid_choices
                    valid_container_defs.append(new_def)
    return valid_container_defs
