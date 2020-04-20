import pytest

from geometry import *
from separating_axis_theorem import sat_entry


def test_collision():
    a = {'x': 1, 'y': 0, 'z': 1}
    b = {'x': 1, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 1}

    rect = [a, b, c, d]
    p0 = {'x': 0, 'y': 0, 'z': 0}
    p1 = {'x': 11, 'y': 0, 'z': 11}

    assert collision(rect, p0) is True
    assert collision(rect, p1) is False


def test_rect_intersection():
    A = [{'x': 0, 'y': 0, 'z': 0}, {'x': 1, 'y': 0, 'z': 0}, {'x': 1, 'y': 0, 'z': 1}, {'x': 0, 'y': 0, 'z': 1}]
    B = [{'x': .25, 'y': 0, 'z': .25}, {'x': .75, 'y': 0, 'z': .25}, {'x': .75, 'y': 0, 'z': .75},
         {'x': .25, 'y': 0, 'z': .75}]
    C = [{'x': .8, 'y': 0, 'z': 1.2}, {'x': 1.1, 'y': 0, 'z': 1.8}, {'x': 2, 'y': 0, 'z': 1.5},
         {'x': 1.1, 'y': 0, 'z': .3}]
    D = [{'x': 1, 'y': 0, 'z': 0}, {'x': 2, 'y': 0, 'z': 1.5}, {'x': 3, 'y': 0, 'z': 0}, {'x': 2, 'y': 0, 'z': -1.5}]
    # A intersects B,C,D. B ints A , C ints A & D, D ints A C
    # Testing transitivity as well
    assert sat_entry(A, B) is True
    assert sat_entry(A, D) is True
    assert sat_entry(C, B) is False
    assert sat_entry(D, C) is True
    assert sat_entry(B, C) is False
    assert sat_entry(A, C) is True
    assert sat_entry(C, A) is True


def test_point_within_room():
    outside1 = {
        'x': ROOM_DIMENSIONS[0][0] - 1,
        'y': 0,
        'z': 0
    }
    assert point_within_room(outside1) is False
    outside2 = {
        'x': 0,
        'y': 0,
        'z': ROOM_DIMENSIONS[1][1] + 1,
    }
    assert point_within_room(outside2) is False
    inside = {
        'x': (ROOM_DIMENSIONS[0][0] + ROOM_DIMENSIONS[0][1])/2.0,
        'y': 0,
        'z': (ROOM_DIMENSIONS[1][0] + ROOM_DIMENSIONS[1][1])/2.0,
    }
    assert point_within_room(inside) is True

def test_mcs_157():
    bounding_box = [
        {
            "x": -1.0257359312880716,
            "y": 0,
            "z": -6.05350288425444
        },
        {
            "x": -2.7935028842544405,
            "y": 0,
            "z": -4.285735931288071
        },
        {
            "x": -1.8742640687119283,
            "y": 0,
            "z": -3.3664971157455597
        },
        {
            "x": -0.10649711574555965,
            "y": 0,
            "z": -5.1342640687119285
        }
    ]
    assert rect_within_room(bounding_box) is False

    
