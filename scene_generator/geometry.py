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
from machine_common_sense.mcs_controller_ai2thor import PERFORMER_CAMERA_Y
from separating_axis_theorem import sat_entry

POSITION_DIGITS = 2
VALID_ROTATIONS = (0, 45, 90, 135, 180, 225, 270, 315)

ROOM_X_MIN = -4.95
ROOM_Z_MIN = -4.95
ROOM_X_MAX = 4.95
ROOM_Z_MAX = 4.95

MAX_OBJECTS_ADJACENT_DISTANCE = 0.5
MIN_OBJECTS_SEPARATION_DISTANCE = 2
MIN_FORWARD_VISIBILITY_DISTANCE = 1.25
MIN_GAP = 0.05

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


def random_position_x() -> float:
    return round(random.uniform(ROOM_X_MIN, ROOM_X_MAX), POSITION_DIGITS)


def random_position_z() -> float:
    return round(random.uniform(ROOM_Z_MIN, ROOM_Z_MAX), POSITION_DIGITS)


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

    vectorAB = {
        'x': B['x'] - A['x'],
        'y': B['y'] - A['y'],
        'z': B['z'] - A['z']}
    vectorBC = {
        'x': C['x'] - B['x'],
        'y': C['y'] - B['y'],
        'z': C['z'] - B['z']}

    vectorAM = {
        'x': test_point['x'] - A['x'],
        'y': test_point['y'] - A['y'],
        'z': test_point['z'] - A['z']}
    vectorBM = {
        'x': test_point['x'] - B['x'],
        'y': test_point['y'] - B['y'],
        'z': test_point['z'] - B['z']}

    return (
        0 <= dot_prod_dict(
            vectorAB,
            vectorAM) <= dot_prod_dict(
            vectorAB,
            vectorAB)) & (
                0 <= dot_prod_dict(
                    vectorBC,
                    vectorBM) <= dot_prod_dict(
                        vectorBC,
                    vectorBC))


def calc_obj_coords(position_x: float,
                    position_z: float,
                    delta_x: float,
                    delta_z: float,
                    offset_x: float,
                    offset_z: float,
                    rotation: float) -> List[Dict[str,
                                                  float]]:
    """Returns an array of points that are the coordinates of the rectangle """
    radian_amount = math.pi * (2 - rotation / 180.0)

    rotate_sin = math.sin(radian_amount)
    rotate_cos = math.cos(radian_amount)
    x_plus = delta_x + offset_x
    x_minus = -delta_x + offset_x
    z_plus = delta_z + offset_z
    z_minus = -delta_z + offset_z

    a = {'x': position_x + x_plus * rotate_cos - z_plus * rotate_sin,
         'y': 0, 'z': position_z + x_plus * rotate_sin + z_plus * rotate_cos}
    b = {'x': position_x + x_plus * rotate_cos - z_minus * rotate_sin,
         'y': 0, 'z': position_z + x_plus * rotate_sin + z_minus * rotate_cos}
    c = {'x': position_x + x_minus * rotate_cos - z_minus * rotate_sin,
         'y': 0, 'z': position_z + x_minus * rotate_sin + z_minus * rotate_cos}
    d = {'x': position_x + x_minus * rotate_cos - z_plus * rotate_sin,
         'y': 0, 'z': position_z + x_minus * rotate_sin + z_plus * rotate_cos}

    return [a, b, c, d]


def point_within_room(point: Dict[str, float]) -> bool:
    return ROOM_X_MIN <= point['x'] <= ROOM_X_MAX and ROOM_Z_MIN <= point['z'] <= ROOM_Z_MAX


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
        rotation_y = (obj_def['rotation']['y']
                      if 'rotation' in obj_def else 0) + rotation_func()
        rotation_z = (obj_def['rotation']['z'] if 'rotation' in obj_def else 0)
        if xz_func is not None:
            new_x, new_z = xz_func()
        else:
            new_x = x_func()
            new_z = z_func()

        if new_x is not None and new_z is not None:
            rect = calc_obj_coords(
                new_x, new_z, dx, dz, offset_x, offset_z, rotation_y)
            if rect_within_room(rect) and not any(sat_entry(
                    rect, other_rect) for other_rect in collision_rects):
                break
        tries += 1

    if tries < util.MAX_TRIES:
        new_object = {
            'rotation': {
                'x': rotation_x,
                'y': rotation_y,
                'z': rotation_z},
            'position': {
                'x': new_x,
                'y': obj_def.get(
                    'positionY',
                    0),
                'z': new_z},
            'boundingBox': rect}
        other_rects.append(rect)
        return new_object

    logging.debug(f'could not place object: {obj_def}')
    return None


def occluders_too_close(
        occluder: Dict[str, Any], x_position: float, x_scale: float) -> bool:
    """Return True iff a new occluder at x_position with scale x_scale
    would be too close to existing occluder occluder."""
    existing_scale = occluder['shows'][0]['scale']['x']
    min_distance = existing_scale / 2.0 + x_scale / 2.0 + 0.5
    existing_x = occluder['shows'][0]['position']['x']
    return abs(existing_x - x_position) < min_distance


def position_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Compute the distance between two positions."""
    return math.sqrt((a['x'] - b['x'])**2 + (a['y'] -
                                             b['y'])**2 + (a['z'] - b['z'])**2)


def get_room_box() -> shapely.geometry.Polygon:
    room = shapely.geometry.box(ROOM_X_MIN, ROOM_Z_MIN, ROOM_X_MAX, ROOM_Z_MAX)
    return room


def get_visible_segment(performer_start: Dict[str, Dict[str, float]]) \
        -> shapely.geometry.LineString:
    """Get a line segment that should be visible to the performer
    (straight ahead and at least MIN_FORWARD_VISIBILITY_DISTANCE but within
    the room). Return None if no visible segment is possible.
    """
    max_dimension = max(ROOM_X_MAX - ROOM_X_MIN, ROOM_Z_MAX - ROOM_Z_MIN)
    # make it long enough for the far end to be outside the room
    view_segment = shapely.geometry.LineString(
        [[0, MIN_FORWARD_VISIBILITY_DISTANCE], [0, max_dimension * 2]])
    view_segment = affinity.rotate(
        view_segment, -performer_start['rotation']['y'], origin=(0, 0))
    view_segment = affinity.translate(
        view_segment,
        performer_start['position']['x'],
        performer_start['position']['z'])
    room = get_room_box()

    target_segment = room.intersection(view_segment)
    if target_segment.is_empty:
        logging.debug(
            f'performer too close to the wall, cannot place object in front of it (performer location={performer_start})')
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
    # (i.e., the 180 degree arc in the opposite direction from its orientation)
    # if the performer were at the origin facing 0, this box would be behind it
    rear_poly = shapely.geometry.box(-(ROOM_X_MAX - ROOM_X_MIN) / 2.0, -(
        ROOM_Z_MAX - ROOM_Z_MIN) / 2.0, (ROOM_X_MAX - ROOM_X_MIN) / 2.0, 0)
    performer_point = shapely.geometry.Point(
        performer_start['position']['x'],
        performer_start['position']['z'])
    rear_poly = affinity.translate(
        rear_poly,
        performer_point.x,
        performer_point.y)
    rear_poly = affinity.rotate(
        rear_poly, -performer_start['rotation']['y'], origin=performer_point)

    # Restrict the rear bounds to the room's dimensions.
    rear_min_x = min(ROOM_X_MAX, max(ROOM_X_MIN, rear_poly.bounds[0]))
    rear_min_z = min(ROOM_Z_MAX, max(ROOM_Z_MIN, rear_poly.bounds[1]))
    rear_max_x = min(ROOM_X_MAX, max(ROOM_X_MIN, rear_poly.bounds[2]))
    rear_max_z = min(ROOM_Z_MAX, max(ROOM_Z_MIN, rear_poly.bounds[3]))
    rear_poly = shapely.geometry.box(
        rear_min_x, rear_min_z, rear_max_x, rear_max_z)

    def compute_xz():
        # pick a random x within the polygon's bounding rectangle
        for _ in range(util.MAX_TRIES):
            x = util.random_real(rear_min_x, rear_max_x)
            # intersect a vertical line with the poly at that x
            vertical_line = shapely.geometry.LineString(
                [[x, rear_min_z], [x, rear_max_z]])
            target_segment = vertical_line.intersection(rear_poly)
            if not target_segment.is_empty:
                break
            target_segment = None
        if not target_segment or target_segment.is_empty:
            return None, None
        # unlikely, but possible to get just a point here
        elif target_segment.geom_type == 'Point':
            location = target_segment
        else:
            # pick a random value along that vertical line
            fraction = random.random()
            location = target_segment.interpolate(fraction, normalized=True)
        return location.x, location.y

    return calc_obj_pos(
        performer_start['position'],
        [],
        target_def,
        xz_func=compute_xz)


def get_adjacent_location(obj_def: Dict[str,
                                        Any],
                          target_definition: Dict[str,
                                                  Any],
                          target_location: Dict[str,
                                                Any],
                          performer_start: Dict[str,
                                                Dict[str,
                                                     float]],
                          obstruct: bool = False) -> Optional[Dict[str,
                                                                   Any]]:
    """Find a location such that, if obj_def is instantiated there, it
    will be next to target. Ensures that the object at the new
    location will not overlap the performer start, if necessary trying
    to put the new object on each cardinal side of the target.
    """
    sides = list(range(4))
    random.shuffle(sides)
    for side in sides:
        location = get_adjacent_location_on_side(
            obj_def,
            target_definition,
            target_location,
            performer_start,
            side,
            obstruct)
        if location:
            # If obstruct, position the target so that the object is between it
            # and the performer start.
            if obstruct:
                location_poly = get_bounding_polygon(location)
                if does_fully_obstruct_target(
                        performer_start['position'],
                        target_location,
                        location_poly):
                    return location
            else:
                return location
    return None


class Side(IntEnum):
    RIGHT = 0
    BACK = 1
    LEFT = 2
    FRONT = 3


def get_adjacent_location_on_side(object_definition: Dict[str,
                                                          Any],
                                  target_definition: Dict[str,
                                                          Any],
                                  target_location: Dict[str,
                                                        Any],
                                  performer_start: Dict[str,
                                                        Dict[str,
                                                             float]],
                                  side: Side,
                                  obstruct: bool) -> Optional[Dict[str,
                                                                   Any]]:
    """Get a location such that, if object_definition is instantiated there, it will
    be next to target. Side determines on which side of target to
    place it: 0 = right (positive x), 1 = behind (positive z), 2 =
    left (negative x) and 3 = in front (negative z). If the object
    would overlap the performer_start or would be outside the room,
    None is returned."
    """
    object_dimensions = object_definition['dimensions']
    object_offset = object_definition['offset'] if 'offset' in object_definition else {
        'x': 0, 'z': 0}
    if obstruct and 'closedDimensions' in object_definition:
        object_dimensions = object_definition['closedDimensions']
        object_offset = object_definition['closedOffset'] if 'closedOffset' in object_definition else object_offset
    target_offset = target_definition['offset'] if 'offset' in target_definition else {
        'x': 0, 'z': 0}

    distance_prop = 'x' if side in (0, 2) else 'z'
    distance = object_dimensions[distance_prop] / 2.0 + \
        target_definition['dimensions'][distance_prop] / 2.0 + MIN_GAP

    # Create a line pointing from the origin to the right, then rotate that
    # line using the given side.
    separator_segment = shapely.geometry.LineString([[0, 0], [distance, 0]])
    separator_segment_rotation = -target_location['rotation']['y'] + 90 * side
    separator_segment = affinity.rotate(
        separator_segment, -separator_segment_rotation, origin=(0, 0))
    separator_segment = affinity.translate(
        separator_segment,
        (target_location['position']['x'] + target_offset['x']),
        (target_location['position']['z'] + target_offset['z']))

    x = separator_segment.coords[1][0] - object_offset['x']
    z = separator_segment.coords[1][1] - object_offset['z']
    dx = object_dimensions['x'] / 2.0
    dz = object_dimensions['z'] / 2.0
    rect = calc_obj_coords(
        x,
        z,
        dx,
        dz,
        object_offset['x'],
        object_offset['z'],
        target_location['rotation']['y'])
    poly = rect_to_poly(rect)
    performer = shapely.geometry.Point(
        performer_start['position']['x'],
        performer_start['position']['z'])
    target_rect = generate_object_bounds(
        target_definition['dimensions'],
        target_offset,
        target_location['position'],
        target_location['rotation'])
    target_poly = rect_to_poly(target_rect)
    room = get_room_box()

    if not poly.intersects(performer) and not poly.intersects(
            target_poly) and room.contains(poly):
        location = {
            'position': {
                'x': x,
                'y': object_definition.get('positionY', 0),
                'z': z
            },
            'rotation': {
                'x': 0,
                'y': target_location['rotation']['y'],
                'z': 0
            },
            'boundingBox': rect
        }
    else:
        location = None
    return location


def get_wider_and_taller_defs(
        obj_def: Dict[str, Any], obstruct_vision: bool) -> List[Tuple[Dict[str, Any], float]]:
    """Return all object definitions both taller and either wider or
    deeper. If wider (x-axis), angle 0 is returned; if deeper
    (z-axis), 90 degrees is returned. Objects returned may be equal in
    dimensions, not just strictly greater.
    """
    possible_defs = []
    bigger_defs = []
    for new_def in objects.get('ALL'):
        possible_defs = possible_defs + \
            util.finalize_each_object_definition_choice(new_def)
    for big_def in possible_defs:
        # Only look at definitions with the obstruct property.
        if 'obstruct' in big_def and big_def['obstruct'] == (
                'vision' if obstruct_vision else 'navigation'):
            obj_dimensions = obj_def['closedDimensions'] if 'closedDimensions' in obj_def else obj_def['dimensions']
            big_dimensions = big_def['closedDimensions'] if 'closedDimensions' in big_def else big_def['dimensions']
            cannot_walk_over = big_dimensions['y'] >= (
                PERFORMER_CAMERA_Y / 2.0)
            # Only need a bigger Y dimension if the object must obstruct
            # vision.
            if cannot_walk_over and (
                    not obstruct_vision or big_dimensions['y'] >= obj_dimensions['y']):
                if big_dimensions['x'] >= obj_dimensions['x']:
                    bigger_defs.append((big_def, 0))
                elif big_dimensions['z'] >= obj_dimensions['x']:
                    bigger_defs.append((big_def, 90))
    return bigger_defs


def get_bounding_polygon(
        object_or_location: Dict[str, Any]) -> shapely.geometry.Polygon:
    if 'boundingBox' in object_or_location:
        bounding_box: List[Dict[str, float]
                           ] = object_or_location['boundingBox']
        poly = rect_to_poly(bounding_box)
    else:
        show = object_or_location['shows'][0]
        if 'boundingBox' in show:
            bounding_box: List[Dict[str, float]] = show['boundingBox']
            poly = rect_to_poly(bounding_box)
        else:
            # TODO I think we need to consider the affect of the object's
            # offsets on its poly here
            x = show['position']['x']
            z = show['position']['z']
            dx = object_or_location['dimensions']['x'] / 2.0
            dz = object_or_location['dimensions']['z'] / 2.0
            poly = shapely.geometry.box(x - dx, z - dz, x + dx, z + dz)
            poly = shapely.affinity.rotate(poly, -show['rotation']['y'])
    return poly


def are_adjacent(obj_a: Dict[str, Any], obj_b: Dict[str, Any],
                 distance: float = MAX_OBJECTS_ADJACENT_DISTANCE) -> bool:
    poly_a = get_bounding_polygon(obj_a)
    poly_b = get_bounding_polygon(obj_b)
    actual_distance = poly_a.distance(poly_b)
    return actual_distance <= distance


def rect_to_poly(rect: List[Dict[str, Any]]) -> shapely.geometry.Polygon:
    points = [(point['x'], point['z']) for point in rect]
    return shapely.geometry.Polygon(points)


def find_performer_rect(
        performer_position: Dict[str, float]) -> List[Dict[str, float]]:
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


def set_location_rotation(
        definition: Dict[str, Any], location: Dict[str, float], rotation_y: float) -> Dict[str, float]:
    """Updates the Y rotation and the bounding box of the given location and returns the location."""
    location['rotation']['y'] = rotation_y
    location['boundingBox'] = generate_object_bounds(
        definition['dimensions'],
        (definition['offset'] if 'offset' in definition else None),
        location['position'],
        location['rotation'])
    return location


def generate_object_bounds(dimensions: Dict[str,
                                            float],
                           offset: Dict[str,
                                        float],
                           position: Dict[str,
                                          float],
                           rotation: Dict[str,
                                          float]) -> List[Dict[str,
                                                               float]]:
    """Returns the bounds for the object with the given properties."""
    x = position['x']
    z = position['z']
    dx = dimensions['x'] / 2.0
    dz = dimensions['z'] / 2.0
    offset_x = offset['x'] if offset else 0.0
    offset_z = offset['z'] if offset else 0.0
    return calc_obj_coords(x, z, dx, dz, offset_x, offset_z, rotation['y'])


def does_fully_obstruct_target(performer_start_position: Dict[str, float], target_or_location: Dict[str, Any],
                               object_poly: shapely.geometry.Polygon) -> bool:
    """Returns whether the given object_poly obstructs each line between the given performer_start_position and
    all four corners of the given target object or location."""

    return _does_obstruct_target_helper(
        performer_start_position,
        target_or_location,
        object_poly,
        fully=True)


def does_partly_obstruct_target(performer_start_position: Dict[str, float], target_or_location: Dict[str, Any],
                                object_poly: shapely.geometry.Polygon) -> bool:
    """Returns whether the given object_poly obstructs one line between the given performer_start_position and
    the four corners of the given target object or location."""

    return _does_obstruct_target_helper(
        performer_start_position,
        target_or_location,
        object_poly,
        fully=False)


def _does_obstruct_target_helper(performer_start_position: Dict[str,
                                                                float],
                                 target_or_location: Dict[str,
                                                          Any],
                                 object_poly: shapely.geometry.Polygon,
                                 fully: bool = False) -> bool:

    obstructing_corners = 0
    performer_start_coordinates = (
        performer_start_position['x'],
        performer_start_position['z'])
    bounds = target_or_location['boundingBox'] if 'boundingBox' in target_or_location else (
        target_or_location['shows'][0]['boundingBox'] if 'shows' in target_or_location else [])
    for corner in bounds:
        target_corner_coordinates = (corner['x'], corner['z'])
        line_to_target = shapely.geometry.LineString(
            [performer_start_coordinates, target_corner_coordinates])
        if object_poly.intersects(line_to_target):
            obstructing_corners += 1
    return obstructing_corners == 4 if fully else obstructing_corners > 0
