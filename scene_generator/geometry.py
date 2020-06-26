import copy
import logging
import math
import random
from enum import IntEnum
from typing import List, Dict, Any, Optional, Callable, Tuple, Sequence

import shapely
from shapely import affinity
from shapely.geometry import LineString

import exceptions
import objects
import util
from separating_axis_theorem import sat_entry

# the following mins and maxes are inclusive
MIN_PERFORMER_POSITION = -4.8 + util.PERFORMER_HALF_WIDTH
MAX_PERFORMER_POSITION = 4.8 - util.PERFORMER_HALF_WIDTH
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
    performer_rect = find_performer_rect(performer_position)
    logging.debug(f'performer_rect = {performer_rect}')

    tries = 0
    collision_rects = other_rects + [performer_rect]
    while tries < util.MAX_TRIES:
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

    if tries < util.MAX_TRIES:
        new_object = {
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'position':  {'x': new_x, 'y': obj_def['position_y'], 'z': new_z},
            'bounding_box': rect
            }
        other_rects.append(rect)
        return new_object

    logging.debug(f'could not place object: {obj_def}')
    return None


def can_enclose(container: Dict[str, Any], target: Dict[str, Any]) -> Optional[float]:
    """iff each 'dimensions' of container is >= the corresponding dimension
    of target, returns 0 (degrees). Otherwise it returns 90 if
    target fits in container when it's rotated 90 degrees. Otherwise it
    returns None.
    """
    if container['dimensions']['x'] >= target['dimensions']['x'] and \
            container['dimensions']['y'] >= target['dimensions']['y'] and \
            container['dimensions']['z'] >= target['dimensions']['z']:
        return 0
    elif container['dimensions']['x'] >= target['dimensions']['z'] and \
            container['dimensions']['y'] >= target['dimensions']['y'] and \
            container['dimensions']['z'] >= target['dimensions']['x']:
        return 90
    else:
        return None


def how_can_contain(container: Dict[str, Any],
                    *targets: Dict[str, Any]) -> Optional[Tuple[int, List[float]]]:
    """Return the index of the container's "enclosed_areas" that all
     targets fit in, or None if they all do not fit in any of the
     enclosed_areas (or if the container doesn't have any). Does not
     try any rotation to see if that makes it possible to fit.
    """
    if 'enclosed_areas' not in container:
        return None
    for i in range(len(container['enclosed_areas'])):
        space = container['enclosed_areas'][i]
        angles = []
        fits = True
        for target in targets:
            angle = can_enclose(space, target)
            if angle is None:
                fits = False
                break
            angles.append(angle)
        if fits:
            return i, angles
    return None


def get_enclosable_containments(objs: Sequence[Dict[str, Any]],
                                container_defs: Sequence[Dict[str, Any]] = None) \
                                -> List[Tuple[Dict[str, Any], int, List[float]]]:
    """Return a list of object definitions for containers that can enclose
    all the pass objects objs. If container_defs is None, use
    objects.get_enclosed_containers().
    """
    if container_defs is None:
        container_defs = objects.get_enclosed_containers()
    valid_containments = []
    for container_def in container_defs:
        containment = how_can_contain(container_def, *objs)
        if containment is not None:
            index, angles = containment
            valid_containments.append((container_def, index, angles))
        elif 'choose' in container_def:
            # try choose
            for choice in container_def['choose']:
                containment = how_can_contain(choice, *objs)
                if containment is not None:
                    new_def = util.finalize_object_definition(container_def, choice)
                    index, angles = containment
                    valid_containments.append((new_def, index, angles))
    return valid_containments


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


def get_room_box() -> shapely.geometry.Polygon:
    room = shapely.geometry.box(ROOM_DIMENSIONS[0][0], ROOM_DIMENSIONS[1][0],
                                ROOM_DIMENSIONS[0][1], ROOM_DIMENSIONS[1][1])
    return room


def get_visible_segment(performer_start: Dict[str, Dict[str, float]]) \
        -> shapely.geometry.LineString:
    """Get a line segment that should be visible to the performer
    (straight ahead and at least MIN_START_DISTANCE_AWAY but within
    the room).
    """
    max_dimension = max(ROOM_DIMENSIONS[0][1] - ROOM_DIMENSIONS[0][0],
                        ROOM_DIMENSIONS[1][1] - ROOM_DIMENSIONS[1][0])
    # make it long enough for the far end to be outside the room
    view_segment = shapely.geometry.LineString([[0, MIN_START_DISTANCE_AWAY], [0, max_dimension * 2]])
    view_segment = affinity.rotate(view_segment, -performer_start['rotation']['y'], origin=(0, 0))
    view_segment = affinity.translate(view_segment, performer_start['position']['x'],
                                      performer_start['position']['z'])
    room = get_room_box()

    target_segment = room.intersection(view_segment)
    if target_segment.is_empty:
        raise exceptions.SceneException(f'performer too close to the wall, cannot place object in front of it (performer location={performer_start})')
    return target_segment


def get_location_in_front_of_performer(performer_start: Dict[str, Dict[str, float]],
                                       target_def: Dict[str, Any],
                                       rotation_func: Callable[[], float] = random_rotation) \
                                       -> Optional[Dict[str, Any]]:
    visible_segment = get_visible_segment(performer_start)

    def segment_xz():
        fraction = random.random()
        point = visible_segment.interpolate(fraction, normalized=True)
        return point.x, point.y

    return calc_obj_pos(performer_start['position'], [], target_def,
                        xz_func=segment_xz, rotation_func=rotation_func)


def get_location_behind_performer(performer_start: Dict[str, Dict[str, float]],
                                  target_def: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # First, find the part of the the room that's behind the performer
    # (i.e., the 180 degree arc in the opposite direction from its
    # orientation)
    max_dimension = max(ROOM_DIMENSIONS[0][1] - ROOM_DIMENSIONS[0][0],
                        ROOM_DIMENSIONS[1][1] - ROOM_DIMENSIONS[1][0])
    # if the performer were at the origin facing 0, this box would be behind it
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
                          performer_start: Dict[str, float]) -> Optional[Dict[str, Any]]:
    """Find a location such that, if obj_def is instantiated there, it
    will be next to target. Ensures that the object at the new
    location will not overlap the performer start, if necessary trying
    to put the new object on each cardinal side of the target.
    """
    sides = list(range(4))
    random.shuffle(sides)
    for side in sides:
        location = get_adjacent_location_on_side(obj_def, target, performer_start, side)
        if location is not None:
            return location
    return None


class Side(IntEnum):
    RIGHT = 0
    BACK = 1
    LEFT = 2
    FRONT = 3


def get_adjacent_location_on_side(obj_def: Dict[str, Any],
                                  target: Dict[str, Any],
                                  performer_start: Dict[str, float],
                                  side: Side) -> Optional[Dict[str, Any]]:
    """Get a location such that, if obj_def is instantiated there, it will
    be next to target. Side determines on which side of target to
    place it: 0 = right (positive x), 1 = behind (positive z), 2 =
    left (negative x) and 3 = in front (negative z). If the object
    would overlap the performer_start or would be outside the room,
    None is returned."
    """
    GAP = 0.05
    distance_dim = 'x' if side in (0, 2) else 'z'
    distance = obj_def['dimensions'][distance_dim]/2.0 + \
        target['dimensions'][distance_dim]/2.0 + GAP
    separator_segment = shapely.geometry.LineString([[0, 0], [distance, 0]])
    shows = target['shows'][0]
    rotation = -shows['rotation']['y'] + 90 * side
    separator_segment = affinity.rotate(separator_segment, rotation, origin=(0, 0))
    separator_segment = affinity.translate(separator_segment,
                                           shows['position']['x'],
                                           shows['position']['z'])
    x = separator_segment.coords[1][0]
    z = separator_segment.coords[1][1]
    dx = obj_def['dimensions']['x'] / 2.0
    dz = obj_def['dimensions']['z'] / 2.0
    bounding_box = shapely.geometry.box(x - dx, z - dz, x + dx, z + dz)
    bounding_box = affinity.rotate(bounding_box, -shows['rotation']['y'], origin=(0, 0))
    performer = shapely.geometry.Point(performer_start['x'], performer_start['z'])
    room = get_room_box()
    if not bounding_box.intersects(performer) and room.contains(bounding_box):
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


def get_wider_and_taller_defs(obj_def: Dict[str, Any]) \
        -> List[Dict[str, Any]]:
    dims = obj_def['dimensions']
    bigger_defs = []
    for new_def in objects.get_all_object_defs():
        if 'dimensions' in new_def:
            if new_def['dimensions']['x'] >= dims['x'] and \
               new_def['dimensions']['y'] >= dims['y']:
                bigger_defs.append(new_def)
        elif 'choose' in new_def:
            bigger_choices = []
            for choice in new_def['choose']:
                if choice['dimensions']['x'] >= dims['x'] and \
                   choice['dimensions']['y'] >= dims['y']:
                    bigger_choices.append(choice)
            if len(bigger_choices) > 0:
                if len(bigger_choices) == len(new_def['choose']):
                    bigger_defs.append(new_def)
                else:
                    bigger_def = copy.deepcopy(new_def)
                    bigger_def['choose'] = bigger_choices
                    bigger_defs.append(bigger_def)
    return bigger_defs


def get_bounding_polygon(obj: Dict[str, Any]) -> shapely.geometry.Polygon:
    show = obj['shows'][0]
    if 'bounding_box' in show:
        bb: List[Dict[str, float]] = show['bounding_box']
        poly = rect_to_poly(bb)
    else:
        x = show['position']['x']
        z = show['position']['z']
        dx = obj['dimensions']['x'] / 2.0
        dz = obj['dimensions']['z'] / 2.0
        poly = shapely.geometry.box(x - dx, z - dz, x + dx, z + dz)
        poly = shapely.affinity.rotate(poly, -show['rotation']['y'])
    return poly


def rect_to_poly(rect: List[Dict[str, Any]]) -> shapely.geometry.Polygon:
    points = [(point['x'], point['z']) for point in rect]
    return shapely.geometry.Polygon(points)


def find_performer_rect(performer_position: Dict[str, float]) -> List[Dict[str, float]]:
    return [
        {'x': performer_position['x'] - util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] - util.PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] - util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] + util.PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] + util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] + util.PERFORMER_HALF_WIDTH},
        {'x': performer_position['x'] + util.PERFORMER_HALF_WIDTH,
         'z': performer_position['z'] - util.PERFORMER_HALF_WIDTH}
    ]

