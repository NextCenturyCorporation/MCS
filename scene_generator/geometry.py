import logging
import math
import random

from separating_axis_theorem import sat_entry

MAX_TRIES = 100
# the following mins and maxes are inclusive
MIN_PERFORMER_POSITION = -4.8
MAX_PERFORMER_POSITION = 4.8
POSITION_DIGITS = 2
VALID_ROTATIONS = (0, 45, 90, 135, 180, 225, 270, 315)

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

def random_position():
    return round(random.uniform(MIN_PERFORMER_POSITION, MAX_PERFORMER_POSITION), POSITION_DIGITS)


def random_rotation():
    return random.choice(VALID_ROTATIONS)


def dot_prod_dict(v1, v2):
    return sum(v1[key] * v2.get(key, 0) for key in v1)


def collision(test_rect, test_point):
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


def calc_obj_coords(x, z, dx, dz, rotation):
    """Returns an array of points that are the coordinates of the rectangle """
    radian_amount = rotation * math.pi / 180.0

    rotate_sin = math.sin(radian_amount)
    rotate_cos = math.cos(radian_amount)
    a = { 'x': x+(dx*rotate_cos)-(dz*rotate_sin) , 'y' : 0 , 'z': z+dx*rotate_sin+dz*rotate_cos}
    b = { 'x': x+(dx*rotate_cos)+(dz*rotate_sin) , 'y' : 0 , 'z': z+dx*rotate_sin-dz*rotate_cos}
    c = { 'x': x-(dx*rotate_cos)+(dz*rotate_sin) , 'y' : 0 , 'z': z-dx*rotate_sin-dz*rotate_cos}
    d = { 'x': x-(dx*rotate_cos)-(dz*rotate_sin) , 'y' : 0 , 'z': z-dx*rotate_sin+dz*rotate_cos} 

    return [a, b, c, d]


def calc_obj_pos(performer_position, other_rects, old_object):
    """Returns new object with rotation & position if we can place the
object in the frame, None otherwise."""

    dx = old_object['dimensions']['x']
    dz = old_object['dimensions']['z']

    tries = 0
    while tries < MAX_TRIES:
        rotation = random_rotation()
        new_x = random_position()
        new_z = random_position()

        rect = calc_obj_coords(new_x, new_z, dx, dz, rotation)
        if not collision(rect, performer_position) and (
                len(other_rects) == 0 or not any(sat_entry(rect, other_rect) for other_rect in other_rects)):
            break
        tries += 1

    if tries < MAX_TRIES:
        new_object = {
            'rotation': {'x': 0, 'y': rotation, 'z': 0},
            'position':  {'x': new_x, 'y': old_object['position_y'], 'z': new_z}
            }
        other_rects.append(rect)
        return new_object

    logging.debug(f'could not place object: {old_object}')
    return None


def can_enclose(objectA, objectB):
    """Return True iff each 'dimensions' of objectA is >= the corresponding dimension of objectB."""
    return objectA['dimensions']['x'] >= objectB['dimensions']['x'] and \
        objectA['dimensions']['y'] >= objectB['dimensions']['y'] and \
        objectA['dimensions']['z'] >= objectB['dimensions']['z']


def can_contain(container, target):
    """Return the index of the container's "enclosed_areas" that the target fits in, or None if it does not fit in any of them (or if the container doesn't have any). Does not try any rotation to see if that makes it possible to fit."""
    if 'enclosed_areas' not in container:
        return None
    for i in range(len(container['enclosed_areas'])):
        space = container['enclosed_areas'][i]
        if can_enclose(space, target):
            return i
    return None
