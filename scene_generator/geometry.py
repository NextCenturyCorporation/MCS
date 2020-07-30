import copy
import logging
import math
import random
from enum import IntEnum
from typing import List, Dict, Any, Optional, Callable, Tuple

import shapely
from shapely import affinity
from shapely.geometry import LineString

import exceptions
import objects
import util
from separating_axis_theorem import sat_entry

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

MAX_ADJACENT_DISTANCE = 0.5


def random_position_x() -> float:
    return round(random.uniform(ROOM_DIMENSIONS[0][0], ROOM_DIMENSIONS[0][1]), POSITION_DIGITS)


def random_position_z() -> float:
    return round(random.uniform(ROOM_DIMENSIONS[1][0], ROOM_DIMENSIONS[1][1]), POSITION_DIGITS)


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
                    offset_z: float, rotation: float, position_y: float = 0) -> List[Dict[str, float]]:
    """Returns an array of points that are the coordinates of the rectangle """
    radian_amount = math.pi * (2 - rotation / 180.0)

    rotate_sin = math.sin(radian_amount)
    rotate_cos = math.cos(radian_amount)
    x_plus = delta_x + offset_x
    x_minus = -delta_x + offset_x
    z_plus = delta_z + offset_z
    z_minus = -delta_z + offset_z
    
    a = {'x': position_x + x_plus * rotate_cos - z_plus * rotate_sin, 'y': position_y, 'z': position_z + x_plus * rotate_sin + z_plus * rotate_cos}
    b = {'x': position_x + x_plus * rotate_cos - z_minus * rotate_sin, 'y': position_y, 'z': position_z + x_plus * rotate_sin + z_minus * rotate_cos}
    c = {'x': position_x + x_minus * rotate_cos - z_minus * rotate_sin, 'y': position_y, 'z': position_z + x_minus * rotate_sin + z_minus * rotate_cos}
    d = {'x': position_x + x_minus * rotate_cos - z_plus * rotate_sin, 'y': position_y, 'z': position_z + x_minus * rotate_sin + z_plus * rotate_cos}

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
                 x_func: Callable[[], float] = random_position_x,
                 z_func: Callable[[], float] = random_position_z,
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

    tries = 0
    collision_rects = other_rects + [performer_rect]
    while tries < util.MAX_TRIES:
        rotation_x = (obj_def['rotation']['x'] if 'rotation' in obj_def else 0)
        rotation_y = (obj_def['rotation']['y'] if 'rotation' in obj_def else 0) + rotation_func()
        rotation_z = (obj_def['rotation']['z'] if 'rotation' in obj_def else 0)
        if xz_func is not None:
            new_x, new_z = xz_func()
        else:
            new_x = x_func()
            new_z = z_func()

        rect = calc_obj_coords(new_x, new_z, dx, dz, offset_x, offset_z, rotation_y)
        if rect_within_room(rect) and not any(sat_entry(rect, other_rect) for other_rect in collision_rects):
            break
        tries += 1

    if tries < util.MAX_TRIES:
        new_object = {
            'rotation': {'x': rotation_x, 'y': rotation_y, 'z': rotation_z},
            'position':  {'x': new_x, 'y': obj_def.get('position_y', 0), 'z': new_z},
            'bounding_box': rect
        }
        other_rects.append(rect)
        return new_object

    logging.debug(f'could not place object: {obj_def}')
    return None


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
    the room). Return None if no visible segment is possible.
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
        logging.debug(f'performer too close to the wall, cannot place object in front of it (performer location={performer_start})')
        return None
    return target_segment


def get_location_in_front_of_performer(performer_start: Dict[str, Dict[str, float]],
                                       target_def: Dict[str, Any],
                                       rotation_func: Callable[[], float] = random_rotation) \
                                       -> Optional[Dict[str, Any]]:
    visible_segment = get_visible_segment(performer_start)
    if not visible_segment:
        return None

    def segment_xz():
        fraction = random.random()
        point = visible_segment.interpolate(fraction, normalized=True)
        return point.x, point.y

    return calc_obj_pos(performer_start['position'], [], target_def,
                        xz_func=segment_xz, rotation_func=rotation_func)


def get_location_in_back_of_performer(performer_start: Dict[str, Dict[str, float]],
                                      target_def: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # First, find the part of the the room that's behind the performer
    # (i.e., the 180 degree arc in the opposite direction from its
    # orientation)
    min_x = ROOM_DIMENSIONS[0][0]
    max_x = ROOM_DIMENSIONS[0][1]
    min_z = ROOM_DIMENSIONS[1][0]
    max_z = ROOM_DIMENSIONS[1][1]
    max_dimension = max(ROOM_DIMENSIONS[0][1] - ROOM_DIMENSIONS[0][0],
                        ROOM_DIMENSIONS[1][1] - ROOM_DIMENSIONS[1][0])
    # if the performer were at the origin facing 0, this box would be behind it
    base_rear = shapely.geometry.box(-(max_x - min_x)/2, -(max_z - min_z)/2, (max_x - min_x)/2, 0)
    performer_point = shapely.geometry.Point(performer_start['position']['x'],
                                             performer_start['position']['z'])
    translated_rear = affinity.translate(base_rear, performer_point.x, performer_point.y)
    performer_rear = affinity.rotate(translated_rear, -performer_start['rotation']['y'],
                                     origin=performer_point)
    bounds = [
        min(max_x, max(min_x, performer_rear.bounds[0])),
        min(max_z, max(min_z, performer_rear.bounds[1])),
        min(max_x, max(min_x, performer_rear.bounds[2])),
        min(max_z, max(min_z, performer_rear.bounds[3]))
    ]

    def compute_xz():
        # pick a random x within the polygon's bounding rectangle
        while True:
            x = util.random_real(bounds[0], bounds[2])
            # intersect a vertical line with the poly at that x
            vertical_line = shapely.geometry.LineString([[x, bounds[1]], [x, bounds[3]]])
            target_segment = vertical_line.intersection(performer_rear)
            if not target_segment.is_empty:
                break
        # unlikely, but possible to get just a point here
        if target_segment.geom_type == 'Point':
            location = target_segment
        else:
            # pick a random value along that vertical line
            fraction = random.random()
            location = target_segment.interpolate(fraction, normalized=True)
        return location.x, location.y

    return calc_obj_pos(performer_start['position'], [], target_def, xz_func=compute_xz)


def get_adjacent_location(obj_def: Dict[str, Any], target: Dict[str, Any], \
        performer_start: Dict[str, Dict[str, float]], obstruct: bool = False) -> Optional[Dict[str, Any]]:
    """Find a location such that, if obj_def is instantiated there, it
    will be next to target. Ensures that the object at the new
    location will not overlap the performer start, if necessary trying
    to put the new object on each cardinal side of the target.
    """
    sides = list(range(4))
    random.shuffle(sides)
    for side in sides:
        location = get_adjacent_location_on_side(obj_def, target, performer_start, side, obstruct)
        if location:
            # If obstruct, position the target so that the object is between it and the performer start.
            if obstruct:
                if does_obstruct_target(performer_start['position'], target, get_bounding_polygon(location)):
                    return location
            else:
                return location
    return None


class Side(IntEnum):
    RIGHT = 0
    BACK = 1
    LEFT = 2
    FRONT = 3


def get_adjacent_location_on_side(obj_def: Dict[str, Any], target: Dict[str, Any], \
        performer_start: Dict[str, Dict[str, float]], side: Side, obstruct: bool) -> Optional[Dict[str, Any]]:
    """Get a location such that, if obj_def is instantiated there, it will
    be next to target. Side determines on which side of target to
    place it: 0 = right (positive x), 1 = behind (positive z), 2 =
    left (negative x) and 3 = in front (negative z). If the object
    would overlap the performer_start or would be outside the room,
    None is returned."
    """
    GAP = 0.05
    distance_dim = 'x' if side in (0, 2) else 'z'

    dimensions = obj_def['dimensions']
    offset_x = obj_def['offset']['x'] if 'offset' in obj_def else 0.0
    offset_z = obj_def['offset']['z'] if 'offset' in obj_def else 0.0
    if obstruct and 'closed_dimensions' in obj_def:
        dimensions = obj_def['closed_dimensions']
        offset_x = obj_def['closed_offset']['x'] if 'closed_offset' in obj_def else offset_x
        offset_z = obj_def['closed_offset']['z'] if 'closed_offset' in obj_def else offset_z

    distance = dimensions[distance_dim]/2.0 + target['dimensions'][distance_dim]/2.0 + GAP
    separator_segment = shapely.geometry.LineString([[0, 0], [distance, 0]])
    shows = target['shows'][0]
    rotation = -shows['rotation']['y'] + 90 * side
    separator_segment = affinity.rotate(separator_segment, rotation, origin=(0, 0))
    separator_segment = affinity.translate(separator_segment,
                                           shows['position']['x'],
                                           shows['position']['z'])
    x = separator_segment.coords[1][0] + offset_x
    z = separator_segment.coords[1][1] + offset_z
    dx = dimensions['x'] / 2.0
    dz = dimensions['z'] / 2.0
    rect = calc_obj_coords(x, z, dx, dz, offset_x, offset_z, shows['rotation']['y'])
    poly = rect_to_poly(rect)
    performer = shapely.geometry.Point(performer_start['position']['x'], performer_start['position']['z'])
    target_bounds = get_bounding_polygon(target)
    room = get_room_box()

    if not poly.intersects(performer) and not poly.intersects(target_bounds) and room.contains(poly):
        location = {
            'position': {
                'x': x,
                'y': obj_def.get('position_y', 0),
                'z': z
            },
            'rotation': {
                'x': 0,
                'y': shows['rotation']['y'],
                'z': 0
            },
            'bounding_box': rect
        }
    else:
        location = None
    return location


def get_wider_and_taller_defs(obj_def: Dict[str, Any], obstruct_vision: bool) -> List[Tuple[Dict[str, Any], float]]:
    """Return all object definitions both taller and either wider or
    deeper. If wider (x-axis), angle 0 is returned; if deeper
    (z-axis), 90 degrees is returned. Objects returned may be equal in
    dimensions, not just strictly greater.
    """
    defs = copy.deepcopy(objects.get_all_object_defs())
    random.shuffle(defs)
    possible_defs = []
    for new_def in defs:
        if 'choose' in new_def:
            for choice in new_def['choose']:
                possible_defs.append(util.finalize_object_definition(copy.deepcopy(new_def), choice))
        else:
            possible_defs.append(util.finalize_object_definition(copy.deepcopy(new_def)))
    bigger_defs = []
    for big_def in possible_defs:
        # Only look at definitions with the obstruct property.
        if 'obstruct' in big_def and big_def['obstruct'] == ('vision' if obstruct_vision else 'navigation'):
            obj_dimensions = obj_def['closed_dimensions'] if 'closed_dimensions' in obj_def else obj_def['dimensions']
            big_dimensions = big_def['closed_dimensions'] if 'closed_dimensions' in big_def else big_def['dimensions']
            # Only need a bigger Y dimension if the object must obstruct vision.
            if (not obstruct_vision or big_dimensions['y'] >= obj_dimensions['y']):
                if big_dimensions['x'] >= obj_dimensions['x']:
                    bigger_defs.append((big_def, 0))
                elif big_dimensions['z'] >= obj_dimensions['x']:
                    bigger_defs.append((big_def, 90))
    return bigger_defs


def get_bounding_polygon(object_or_location: Dict[str, Any]) -> shapely.geometry.Polygon:
    if 'bounding_box' in object_or_location:
        bounding_box: List[Dict[str, float]] = object_or_location['bounding_box']
        poly = rect_to_poly(bounding_box)
    else:
        show = object_or_location['shows'][0]
        if 'bounding_box' in show:
            bounding_box: List[Dict[str, float]] = show['bounding_box']
            poly = rect_to_poly(bounding_box)
        else:
            # TODO I think we need to consider the affect of the object's offsets on its poly here
            x = show['position']['x']
            z = show['position']['z']
            dx = object_or_location['dimensions']['x'] / 2.0
            dz = object_or_location['dimensions']['z'] / 2.0
            poly = shapely.geometry.box(x - dx, z - dz, x + dx, z + dz)
            poly = shapely.affinity.rotate(poly, -show['rotation']['y'])
    return poly


def are_adjacent(obj_a: Dict[str, Any], obj_b: Dict[str, Any], max_adj_dist: float = None) -> bool:
    poly_a = get_bounding_polygon(obj_a)
    poly_b = get_bounding_polygon(obj_b)
    distance = poly_a.distance(poly_b)
    
    return distance <= max_adj_dist if max_adj_dist is not None else distance <= MAX_ADJACENT_DISTANCE


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


def set_location_rotation(definition: Dict[str, Any], location: Dict[str, float], rotation_y: float) -> \
        Dict[str, float]:
    """Updates the Y rotation and the bounding box of the given location and returns the location."""
    location['rotation']['y'] = rotation_y
    location['bounding_box'] = generate_object_bounds(definition['dimensions'], \
            (definition['offset'] if 'offset' in definition else None), location['position'], location['rotation'])
    return location


def generate_object_bounds(dimensions: Dict[str, float], offset: Dict[str, float], position: Dict[str, float], \
        rotation: Dict[str, float]) -> List[Dict[str, float]]:
    """Returns the bounds for the object with the given properties."""
    x = position['x']
    z = position['z']
    dx = dimensions['x'] / 2.0
    dz = dimensions['z'] / 2.0
    offset_x = offset['x'] if offset else 0.0
    offset_z = offset['z'] if offset else 0.0
    return calc_obj_coords(x, z, dx, dz, offset_x, offset_z, rotation['y'])


def does_obstruct_target(performer_start_position: Dict[str, float], target: Dict[str, Any], \
        object_poly: shapely.geometry.Polygon) -> bool:
    """Returns whether the given object_poly obstructs each line between the given performer_start_position and
    all four corners of the given target object."""

    obstruct = True
    performer_start_coordinates = (performer_start_position['x'], performer_start_position['z'])
    for corner in target['shows'][0]['bounding_box']:
        target_corner_coordinates = (corner['x'], corner['z'])
        line_to_target = shapely.geometry.LineString([performer_start_coordinates, target_corner_coordinates])
        if not object_poly.intersects(line_to_target):
            obstruct = False
            break
    return obstruct

