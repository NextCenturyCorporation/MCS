import copy
import logging
import math
import random
from typing import List, Dict, Any, Optional, Callable, Tuple, Sequence

import shapely
from shapely import affinity
from shapely.geometry import LineString

import exceptions
import objects
import util
from separating_axis_theorem import sat_entry

MAX_TRIES = 100
PERFORMER_WIDTH = 0.1
PERFORMER_HALF_WIDTH = PERFORMER_WIDTH / 2.0
# the following mins and maxes are inclusive
MIN_PERFORMER_POSITION = -4.8 + PERFORMER_HALF_WIDTH
MAX_PERFORMER_POSITION = 4.8 - PERFORMER_HALF_WIDTH
POSITION_DIGITS = 2
VALID_ROTATIONS = (0, 45, 90, 135, 180, 225, 270, 315)

ROOM_DIMENSIONS = ((-4.95, 4.95), (-4.95, 4.95))

MINIMUM_START_DIST_FROM_TARGET = 2
MINIMUM_TARGET_SEPARATION = 2
MIN_START_DISTANCE_AWAY = 1

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
                 x_func: Callable[[], float] = random_position,
                 z_func: Callable[[], float] = random_position,
                 rotation_func: Callable[[], float] = random_rotation,
                 xz_func: Callable[[], Tuple[float, float]] = None) \
                 -> Optional[Dict[str, Any]]:

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
        {'x': performer_position['x'] - PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] - PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] - PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] + PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] + PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] + PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] + PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] - PERFORMER_HALF_WIDTH}
    ]
    logging.debug(f'performer_rect = {performer_rect}')

    tries = 0
    collision_rects = other_rects + [performer_rect]
    while tries < MAX_TRIES:
        rotation = rotation_func()
        if xz_func is not None:
            new_x, new_z = xz_func()
        else:
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


def can_contain(container: Dict[str, Any],
                *targets: Dict[str, Any]) -> Optional[int]:
    """Return the index of the container's "enclosed_areas" that all
     targets fit in, or None if they all do not fit in any of the
     enclosed_areas (or if the container doesn't have any). Does not
     try any rotation to see if that makes it possible to fit.
    """
    if 'enclosed_areas' not in container:
        return None
    for i in range(len(container['enclosed_areas'])):
        space = container['enclosed_areas'][i]
        fits = True
        for target in targets:
            if not can_enclose(space, target):
                fits = False
                break
        if fits:
            return i
    return None


def get_enclosable_container_defs(objs: Sequence[Dict[str, Any]],
                                  container_defs: Sequence[Dict[str, Any]] = None) \
                                  -> List[Dict[str, Any]]:
    """Return a list of object definitions for containers that can enclose
    all the pass objects objs. If container_defs is None, use
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


def occluders_too_close(occluder: Dict[str, Any], x_position: float, x_scale: float) -> bool:
    """Return True iff a new occluder at x_position with scale x_scale
    would be too close to existing occluder occluder."""
    existing_scale = occluder['shows'][0]['scale']['x']
    min_distance = existing_scale / 2.0 + x_scale / 2.0 + 0.5
    existing_x = occluder['shows'][0]['position']['x']
    return abs(existing_x - x_position) < min_distance


def position_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Compute the distance between two positions."""
    return math.sqrt((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2 + (a['z'] - b['z'])**2)


def get_visible_segment(performer_start: Dict[str, Dict[str, float]]) \
        -> shapely.geometry.Point:
    logging.debug(f'>>>get_visible_segment: {performer_start}')
    max_dimension = max(ROOM_DIMENSIONS[0][1] - ROOM_DIMENSIONS[0][0],
                        ROOM_DIMENSIONS[1][1] - ROOM_DIMENSIONS[1][0])
    # make it long enough for the far end to be outside the room
    view_segment = shapely.geometry.LineString([[0, MIN_START_DISTANCE_AWAY], [0, max_dimension * 2]])
    view_segment = affinity.rotate(view_segment, -performer_start['rotation']['y'], origin=(0, 0))
    view_segment = affinity.translate(view_segment, performer_start['position']['x'],
                                      performer_start['position']['z'])
    room = shapely.geometry.box(ROOM_DIMENSIONS[0][0], ROOM_DIMENSIONS[1][0],
                                ROOM_DIMENSIONS[0][1], ROOM_DIMENSIONS[1][1])

    target_segment = room.intersection(view_segment)
    if target_segment.is_empty:
        raise exceptions.SceneException(f'performer too close to the wall, cannot place object in front of it (performer location={performer_start})')
    logging.debug(f'<<<get_visible_segment: {target_segment}')
    return target_segment


def get_location_in_front_of_performer(performer_start: Dict[str, Dict[str, float]],
                                       target_def: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    visible_segment = get_visible_segment(performer_start)

    def segment_xz():
        fraction = random.random()
        point = visible_segment.interpolate(fraction, normalized=True)
        return point.x, point.y

    return calc_obj_pos(performer_start['position'], [], target_def, xz_func=segment_xz)


def get_location_behind_performer(performer_start: Dict[str, Dict[str, float]],
                                  target_def: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # find the part of the the room that's behind the performer
    max_dimension = max(ROOM_DIMENSIONS[0][1] - ROOM_DIMENSIONS[0][0],
                        ROOM_DIMENSIONS[1][1] - ROOM_DIMENSIONS[1][0])
    # if the performer were at the origin facing 0, this would be behind it
    base_rear = shapely.geometry.box(-max_dimension*2, -max_dimension*2,
                                     max_dimension*2, 0)
    performer_point = shapely.geometry.Point(performer_start['position']['x'],
                                             performer_start['position']['z'])
    translated_rear = affinity.translate(base_rear, performer_point.x, performer_point.y)
    performer_rear = affinity.rotate(translated_rear, -performer_start['rotation']['y'],
                                     origin=performer_point)
    bounds = performer_rear.bounds

    def compute_xz():
        # pick a random x within the polygon's bounding rectangle
        x = util.random_real(bounds[0], bounds[2])
        # intersect a vertical line with the poly at that x
        vertical_line = shapely.geometry.LineString([[x, bounds[1]], [x, bounds[3]]])
        target_segment = vertical_line.intersection(performer_rear)
        # pick a random value along that vertical line
        fraction = random.random()
        location = target_segment.interpolate(fraction, normalized=True)
        return location.x, location.y

    return calc_obj_pos(performer_start['position'], [], target_def, xz_func=compute_xz)


def get_adjacent_location(obj_def: Dict[str, Any],
                          target: Dict[str, Any],
                          performer_start: Dict[str, float]) -> Dict[str, Any]:
    """Find a location such that, if obj_def is instantiated there, it
    will be next to target. Ensures that the object at the new
    location will not overlap the performer start, if necessary trying
    to put the new object on each cardinal side of the target.
    """
    for side in range(4):
        location = _adjacent_location(obj_def, target, performer_start, side)
        if location is not None:
            return location
    return None


def _adjacent_location(obj_def: Dict[str, Any],
                          target: Dict[str, Any],
                          performer_start: Dict[str, float],
                       side: int) -> Dict[str, Any]:
    if side < 0 or side > 3:
        raise ValueError(f'side must be 0-3 (not {side})')
    GAP = 0.01
    distance_dim = 'x' if side in (0, 2) else 'z'
    distance = obj_def['dimensions'][distance_dim]/2.0 + \
        target['dimensions'][distance_dim]/2.0 + GAP
    separator_segment = shapely.geometry.LineString([[0, 0], [distance, 0]])
    shows = target['shows'][0]
    rotation = -shows['rotation']['y'] + 90 * side
    separator_segment = affinity.rotate(separator_segment, rotation)
    separator_segment = affinity.translate(separator_segment,
                                           shows['position']['x'],
                                           shows['position']['z'])
    x = separator_segment.coords[1][0]
    z = separator_segment.coords[1][1]
    bounding_box = shapely.geometry.box(x - target['dimensions']['x'],
                                        z - target['dimensions']['z'],
                                        x + target['dimensions']['x'],
                                        z + target['dimensions']['z'])
    bounding_box = affinity.rotate(bounding_box, -shows['rotation']['y'])
    performer = shapely.geometry.Point(performer_start['x'], performer_start['z'])
    if not bounding_box.intersects(performer):
        location = {
            'position': {
                'x': x,
                'y': 0,
                'z': z
            },
            'rotation': {
                'y': shows['rotation']['y']
            }
        }
    else:
        location = None
    return location
