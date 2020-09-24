from enum import Enum, auto
from typing import Dict, Any, Optional, Tuple, Sequence, List

import geometry
import objects
import util


def put_object_in_container(obj_def: Dict[str, Any], obj: Dict[str, Any],
                            container: Dict[str, Any],
                            container_def: Dict[str, Any], area_index: int,
                            rotation: Optional[float] = None) -> None:

    area = container_def['enclosedAreas'][area_index]
    obj['locationParent'] = container['id']

    obj['shows'][0]['position'] = area['position'].copy()
    obj['shows'][0]['position']['y'] += - \
        (area['dimensions']['y'] / 2.0) + obj_def.get('positionY', 0)

    if 'rotation' not in obj['shows'][0]:
        obj['shows'][0]['rotation'] = geometry.ORIGIN.copy()
    if rotation is not None:
        obj['shows'][0]['rotation']['y'] = rotation

    # if it had a boundingBox, it's not valid any more
    obj.pop('boundingBox', None)

    obj['shows'][0]['boundingBox'] = geometry.generate_object_bounds(
        obj_def['dimensions'],
        (obj_def['offset'] if 'offset' in obj_def else None),
        obj['shows'][0]['position'],
        obj['shows'][0]['rotation']
    )

    if 'isParentOf' not in container:
        container['isParentOf'] = []
    container['isParentOf'].append(obj['id'])


class Orientation(Enum):
    SIDE_BY_SIDE = auto()
    FRONT_TO_BACK = auto()


def put_objects_in_container(obj_def_a: Dict[str, Any], obj_a: Dict[str, Any],
                             obj_def_b: Dict[str, Any], obj_b: Dict[str, Any],
                             container: Dict[str, Any],
                             container_def: Dict[str, Any], area_index: int,
                             orientation: Orientation, rot_a: float,
                             rot_b: float) -> None:
    """Put two objects in the same enclosed area of a
    container. orientation determines how they are laid out with
    respect to each other within the container. rot_a and rot_b must
    be either 0 or 90.
    """
    if rot_a not in (0, 90):
        raise ValueError(
            f'only 0 and 90 degree rotations supported for object a, '
            f'not {rot_a}')
    if rot_b not in (0, 90):
        raise ValueError(
            f'only 0 and 90 degree rotations supported for object b, '
            f'not {rot_b}')

    # TODO This function should probably verify that both objects can fit
    # together inside the container...

    area = container_def['enclosedAreas'][area_index]
    obj_a['locationParent'] = container['id']
    obj_b['locationParent'] = container['id']
    shows_a = obj_a['shows'][0]
    shows_b = obj_b['shows'][0]

    if orientation == Orientation.SIDE_BY_SIDE:
        if rot_a == 0:
            width_a = obj_a['dimensions']['x']
        elif rot_a == 90:
            width_a = obj_a['dimensions']['z']
        shows_a['position'] = area['position'].copy()
        shows_a['position']['x'] -= width_a / 2.0
        if rot_b == 0:
            width_b = obj_b['dimensions']['x']
        elif rot_b == 90:
            width_b = obj_b['dimensions']['z']
        shows_b['position'] = area['position'].copy()
        shows_b['position']['x'] += width_b / 2.0

    elif orientation == Orientation.FRONT_TO_BACK:
        if rot_a == 0:
            height_a = obj_a['dimensions']['z']
        elif rot_a == 90:
            height_a = obj_a['dimensions']['x']
        shows_a['position'] = area['position'].copy()
        shows_a['position']['z'] -= height_a / 2.0
        if rot_b == 0:
            height_b = obj_b['dimensions']['z']
        elif rot_b == 90:
            height_b = obj_b['dimensions']['x']
        shows_b['position'] = area['position'].copy()
        shows_b['position']['z'] += height_b / 2.0

    shows_a['position']['y'] += - \
        (area['dimensions']['y'] / 2.0) + obj_def_a.get('positionY', 0)
    shows_b['position']['y'] += - \
        (area['dimensions']['y'] / 2.0) + obj_def_b.get('positionY', 0)
    shows_a['rotation'] = {'y': rot_a}
    shows_b['rotation'] = {'y': rot_b}

    # any boundingBox they may have had is not valid any more
    shows_a.pop('boundingBox', None)
    shows_b.pop('boundingBox', None)

    shows_a['boundingBox'] = geometry.generate_object_bounds(
        obj_def_a['dimensions'],
        (obj_def_a['offset'] if 'offset' in obj_def_a else None),
        shows_a['position'],
        shows_a['rotation']
    )
    shows_b['boundingBox'] = geometry.generate_object_bounds(
        obj_def_b['dimensions'],
        (obj_def_b['offset'] if 'offset' in obj_def_b else None),
        shows_b['position'],
        shows_b['rotation']
    )

    if 'isParentOf' not in container:
        container['isParentOf'] = []
    container['isParentOf'].append(obj_a['id'])
    container['isParentOf'].append(obj_b['id'])


def can_enclose(area: Dict[str, Any],
                target: Dict[str, Any]) -> Optional[float]:
    """iff each 'dimensions' of area is >= the corresponding dimension
    of target, returns 0 (degrees). Otherwise it returns 90 if
    target fits in area when it's rotated 90 degrees. Otherwise it
    returns None.
    """
    if area['dimensions']['x'] >= target['dimensions']['x'] and \
            area['dimensions']['y'] >= target['dimensions']['y'] and \
            area['dimensions']['z'] >= target['dimensions']['z']:
        return 0
    elif area['dimensions']['x'] >= target['dimensions']['z'] and \
            area['dimensions']['y'] >= target['dimensions']['y'] and \
            area['dimensions']['z'] >= target['dimensions']['x']:
        return 90
    else:
        return None


def how_can_contain(container: Dict[str, Any],
                    *targets: Dict[str, Any]) \
        -> Optional[Tuple[int, List[float]]]:
    """Return the index of the container's "enclosedAreas" that all
     targets fit in, or None if they all do not fit in any of the
     enclosedAreas (or if the container doesn't have any). Does not
     try any rotation to see if that makes it possible to fit.
    """
    if 'enclosedAreas' not in container:
        return None
    for i in range(len(container['enclosedAreas'])):
        space = container['enclosedAreas'][i]
        angles = []
        fits = True
        for target in targets:
            if target:
                angle = can_enclose(space, target)
                if angle is None:
                    fits = False
                    break
                angles.append(angle)
        if fits:
            return i, angles
    return None


def get_enclosable_containments(objs: Sequence[Dict[str, Any]],
                                container_defs: Sequence[
                                    Dict[str, Any]] = None) \
        -> List[Tuple[Dict[str, Any], int, List[float]]]:
    """Return a list of object definitions for containers that can enclose all
    the pass objects objs."""
    if container_defs is None:
        container_defs = retrieve_enclosable_definition_list()
    valid_containments = []
    for container_def in container_defs:
        possible_enclosable_definition_list = util.finalize_each_object_definition_choice(  # noqa: E501
            container_def)
        for (
            possible_enclosable_definition
        ) in possible_enclosable_definition_list:
            containment = how_can_contain(
                possible_enclosable_definition, *objs)
            if containment:
                index, angles = containment
                valid_containments.append(
                    (possible_enclosable_definition, index, angles))
    return valid_containments


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


def can_contain_both(container_def: Dict[str, Any], obj_a: Dict[str, Any],
                     obj_b: Dict[str, Any]) \
        -> Optional[Tuple[Dict[str, Any], int, Orientation, float, float]]:
    possible_enclosable_definition_list = util.finalize_each_object_definition_choice(  # noqa: E501
        container_def)
    for possible_enclosable_definition in possible_enclosable_definition_list:
        result = _eas_can_contain_both(
            possible_enclosable_definition['enclosedAreas'], obj_a, obj_b)
        if result:
            index, orientation, angle_a, angle_b = result
            new_def = util.finalize_object_definition(container_def)
            return new_def, index, orientation, angle_a, angle_b
    return None


def retrieve_enclosable_definition_list() -> List[Dict[str, Any]]:
    output_list = []
    for object_definition in util.retrieve_full_object_definition_list(
            objects.get('ALL')):
        if 'enclosedAreas' in object_definition and len(
                object_definition['enclosedAreas']) > 0:
            output_list.append(object_definition)
    return output_list
