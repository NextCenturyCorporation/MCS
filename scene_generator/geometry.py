import logging
import math
import random
from typing import List, Dict, Any, Optional

from separating_axis_theorem import sat_entry

MAX_TRIES = 100
PERFORMER_WIDTH = 0.1
# the following mins and maxes are inclusive
MIN_PERFORMER_POSITION = -4.8 + PERFORMER_WIDTH / 2.0
MAX_PERFORMER_POSITION = 4.8 - PERFORMER_WIDTH / 2.0
POSITION_DIGITS = 2
VALID_ROTATIONS = (0, 45, 90, 135, 180, 225, 270, 315)

ROOM_DIMENSIONS = ((-4.95, 4.95), (-4.95, 4.95))


ORIGIN = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0
}

ORIGIN_LOCATION = {
    'position': {
        'x': 0.0,
        'y': 0.0,
        'z': 0.0
    },
    'rotation': {
        'x': 0.0,
        'y': 0.0,
        'z': 0.0
    }
}


def random_position() -> float:
    return round(random.uniform(MIN_PERFORMER_POSITION, MAX_PERFORMER_POSITION), POSITION_DIGITS)


def random_rotation() -> float:
    return random.choice(VALID_ROTATIONS)


def dot_prod_dict(v1: Dict[Any, float], v2: Dict[Any, float]) -> float:
    return sum(v1[key] * v2.get(key, 0) for key in v1)


def collision(test_rect: List[Dict[str, float]], test_point: Dict[str, float]):
    # assuming test_rect is an array4 points in order... Clockwise or CCW does not matter
    # points are {x,y,z}
    #
    # From https://math.stackexchange.com/a/190373
    A = test_rect[0]
    B = test_rect[1]
    C = test_rect[2]

    vectorAB = {'x': B['x'] - A['x'], 'y': B['y'] - A['y'], 'z': B['z'] - A['z']}
    vectorBC = {'x': C['x'] - B['x'], 'y': C['y'] - B['y'], 'z': C['z'] - B['z']}

    vectorAM = {'x': test_point['x'] - A['x'], 'y': test_point['y'] - A['y'], 'z': test_point['z'] - A['z']}
    vectorBM = {'x': test_point['x'] - B['x'], 'y': test_point['y'] - B['y'], 'z': test_point['z'] - B['z']}

    return (0 <= dot_prod_dict(vectorAB, vectorAM) <= dot_prod_dict(vectorAB, vectorAB)) & (
                0 <= dot_prod_dict(vectorBC, vectorBM) <= dot_prod_dict(vectorBC, vectorBC))


def calc_obj_coords(position_x: float, position_z: float, delta_x: float, delta_z: float, offset_x: float,
                    offset_z: float, rotation: float) -> List[Dict[str, float]]:
    """Returns an array of points that are the coordinates of the rectangle """
    radian_amount = math.pi * (2 - rotation / 180.0)

    rotate_sin = math.sin(radian_amount)
    rotate_cos = math.cos(radian_amount)
    x_plus = delta_x + offset_x
    x_minus = -delta_x + offset_x
    z_plus = delta_z + offset_z
    z_minus = -delta_z + offset_z
    
    a = {'x': position_x + x_plus * rotate_cos - z_plus * rotate_sin, 'y': 0, 'z': position_z + x_plus * rotate_sin + z_plus * rotate_cos}
    b = {'x': position_x + x_plus * rotate_cos - z_minus * rotate_sin, 'y': 0, 'z': position_z + x_plus * rotate_sin + z_minus * rotate_cos}
    c = {'x': position_x + x_minus * rotate_cos - z_minus * rotate_sin, 'y': 0, 'z': position_z + x_minus * rotate_sin + z_minus * rotate_cos}
    d = {'x': position_x + x_minus * rotate_cos - z_plus * rotate_sin, 'y': 0, 'z': position_z + x_minus * rotate_sin + z_plus * rotate_cos}

    return [a, b, c, d]


def point_within_room(point: Dict[str, float]) -> bool:
    return ROOM_DIMENSIONS[0][0] <= point['x'] <= ROOM_DIMENSIONS[0][1] and \
           ROOM_DIMENSIONS[1][0] <= point['z'] <= ROOM_DIMENSIONS[1][1]


def rect_within_room(rect: List[Dict[str, float]]) -> bool:
    """Return True iff the passed rectangle is entirely within the bounds of the room."""
    return all(point_within_room(point) for point in rect)


def calc_obj_pos(performer_position: Dict[str, float],
                 other_rects: List[List[Dict[str, float]]],
                 obj_def: Dict[str, Any],
                 x_func=random_position,
                 z_func=random_position,
                 rotation_func=random_rotation):

    """Returns new object with rotation & position if we can place the
object in the frame, None otherwise."""

    dx = obj_def['dimensions']['x'] / 2.0
    dz = obj_def['dimensions']['z'] / 2.0
    if 'offset' in obj_def:
        offset_x = obj_def['offset']['x']
        offset_z = obj_def['offset']['z']
    else:
        offset_x = 0.0
        offset_z = 0.0

    # reserve space around the performer
    performer_rect = [
        {'x': performer_position['x'] - PERFORMER_WIDTH / 2.0,
         'z': performer_position['z'] - PERFORMER_WIDTH / 2.0},
        {'x': performer_position['x'] - PERFORMER_WIDTH / 2.0,
         'z': performer_position['z'] + PERFORMER_WIDTH / 2.0},
        {'x': performer_position['x'] + PERFORMER_WIDTH / 2.0,
         'z': performer_position['z'] + PERFORMER_WIDTH / 2.0},
        {'x': performer_position['x'] + PERFORMER_WIDTH / 2.0,
         'z': performer_position['z'] - PERFORMER_WIDTH / 2.0}
    ]
    logging.debug(f'performer_rect = {performer_rect}')

    tries = 0
    collision_rects = other_rects + [performer_rect]
    while tries < MAX_TRIES:
        rotation = rotation_func()
        new_x = x_func()
        new_z = z_func()

        rect = calc_obj_coords(new_x, new_z, dx, dz, offset_x, offset_z, rotation)
        if rect_within_room(rect) and \
           (len(other_rects) == 0 or not any(sat_entry(rect, other_rect) for other_rect in collision_rects)):
            break
        tries += 1

    if tries < MAX_TRIES:
        new_object = {
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'position':  {'x': new_x, 'y': obj_def['position_y'], 'z': new_z},
            'bounding_box': rect
            }
        other_rects.append(rect)
        return new_object

    logging.debug(f'could not place object: {obj_def}')
    return None


def can_enclose(objectA: Dict[str, Any], objectB: Dict[str, Any]) -> bool:
    """Return True iff each 'dimensions' of objectA is >= the corresponding dimension of objectB."""
    return objectA['dimensions']['x'] >= objectB['dimensions']['x'] and \
        objectA['dimensions']['y'] >= objectB['dimensions']['y'] and \
        objectA['dimensions']['z'] >= objectB['dimensions']['z']


def can_contain(container: Dict[str, Any], target: Dict[str, Any]) -> Optional[int]:
    """Return the index of the container's "enclosed_areas" that the target fits in, or None if it does not fit in any
     of them (or if the container doesn't have any). Does not try any rotation to see if that makes it possible to
     fit."""
    if 'enclosed_areas' not in container:
        return None
    for i in range(len(container['enclosed_areas'])):
        space = container['enclosed_areas'][i]
        if can_enclose(space, target):
            return i
    return None


def occluders_too_close(occluder, x_position, x_scale):
    """Return True iff a new occluder at x_position with scale x_scale
    would be too close to existing occluder occluder."""
    existing_scale = occluder['shows'][0]['scale']['x']
    min_distance = existing_scale / 2.0 + x_scale / 2.0 + 0.5
    existing_x = occluder['shows'][0]['position']['x']
    return abs(existing_x - x_position) < min_distance
