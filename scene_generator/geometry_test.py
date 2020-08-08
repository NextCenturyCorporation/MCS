import pytest

import exceptions
import geometry
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
        'x': ROOM_X_MIN - 1,
        'y': 0,
        'z': 0
    }
    assert point_within_room(outside1) is False
    outside2 = {
        'x': 0,
        'y': 0,
        'z': ROOM_Z_MAX + 1,
    }
    assert point_within_room(outside2) is False
    inside = {
        'x': (ROOM_X_MIN + ROOM_X_MAX)/2.0,
        'y': 0,
        'z': (ROOM_Z_MIN + ROOM_Z_MAX)/2.0,
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

 
def test_calc_obj_coords_identity():

    a = {'x': 2, 'y': 0, 'z': 2}
    b = {'x': 2, 'y': 0, 'z': -2}
    c = {'x': -2, 'y': 0, 'z': -2}
    d = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=0,
                                                 position_z=0,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=0,
                                                 offset_z=0,
                                                 rotation=0)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 0})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotate90():

    d = {'x': 2, 'y': 0, 'z': 2}
    a = {'x': 2, 'y': 0, 'z': -2}
    b = {'x': -2, 'y': 0, 'z': -2}
    c = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=0,
                                                 position_z=0,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=0,
                                                 offset_z=0,
                                                 rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotate180():

    c = {'x': 2, 'y': 0, 'z': 2}
    d = {'x': 2, 'y': 0, 'z': -2}
    a = {'x': -2, 'y': 0, 'z': -2}
    b = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=0,
                                                 position_z=0,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=0,
                                                 offset_z=0,
                                                 rotation=180)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 180})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotate270():

    b = {'x': 2, 'y': 0, 'z': 2}
    c = {'x': 2, 'y': 0, 'z': -2}
    d = {'x': -2, 'y': 0, 'z': -2}
    a = {'x': -2, 'y': 0, 'z': 2}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=0,
                                                 position_z=0,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=0,
                                                 offset_z=0,
                                                 rotation=270)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, None, {'x': 0, 'z': 0}, {'y': 270})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_nonorigin_identity():

    a = {'x': 3, 'y': 0, 'z': 3}
    b = {'x': 3, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=1,
                                                 position_z=1,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=0,
                                                 offset_z=0,
                                                 rotation=0)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, None, {'x': 1, 'z': 1}, {'y': 0})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_nonorigin_rotate90():

    d = {'x': 3, 'y': 0, 'z': 3}
    a = {'x': 3, 'y': 0, 'z': -1}
    b = {'x': -1, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=1,
                                                 position_z=1,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=0,
                                                 offset_z=0,
                                                 rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, None, {'x': 1, 'z': 1}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_identity_offset():

    a = {'x': 3, 'y': 0, 'z': 3}
    b = {'x': 3, 'y': 0, 'z': -1}
    c = {'x': -1, 'y': 0, 'z': -1}
    d = {'x': -1, 'y': 0, 'z': 3}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=0,
                                                 position_z=0,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=1,
                                                 offset_z=1,
                                                 rotation=0)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 0, 'z': 0}, {'y': 0})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset():

    d = {'x': 3, 'y': 0, 'z': 1}
    a = {'x': 3, 'y': 0, 'z': -3}
    b = {'x': -1, 'y': 0, 'z': -3}
    c = {'x': -1, 'y': 0, 'z': 1}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=0,
                                                 position_z=0,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=1,
                                                 offset_z=1,
                                                 rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 0, 'z': 0}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset_position_x():

    d = {'x': 10, 'y': 0, 'z': 1}
    a = {'x': 10, 'y': 0, 'z': -3}
    b = {'x': 6, 'y': 0, 'z': -3}
    c = {'x': 6, 'y': 0, 'z': 1}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=7,
                                                 position_z=0,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=1,
                                                 offset_z=1,
                                                 rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 7, 'z': 0}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset_position_z():

    d = {'x': 3, 'y': 0, 'z': 8}
    a = {'x': 3, 'y': 0, 'z': 4}
    b = {'x': -1, 'y': 0, 'z': 4}
    c = {'x': -1, 'y': 0, 'z': 8}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=0,
                                                 position_z=7,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=1,
                                                 offset_z=1,
                                                 rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 0, 'z': 7}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation90_offset_position_xz():

    d = {'x': 10, 'y': 0, 'z': 8}
    a = {'x': 10, 'y': 0, 'z': 4}
    b = {'x': 6, 'y': 0, 'z': 4}
    c = {'x': 6, 'y': 0, 'z': 8}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=7,
                                                 position_z=7,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=1,
                                                 offset_z=1,
                                                 rotation=90)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 7, 'z': 7}, {'y': 90})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test_calc_obj_coords_rotation45_offset_position_xz():

    d = {'x': 8.41421, 'y': 0, 'z': 9.82843}
    a = {'x': 11.24264, 'y': 0, 'z': 7}
    b = {'x': 8.41421, 'y': 0, 'z': 4.17157}
    c = {'x': 5.58579, 'y': 0, 'z': 7}
    new_a, new_b, new_c, new_d = calc_obj_coords(position_x=7,
                                                 position_z=7,
                                                 delta_x=2,
                                                 delta_z=2,
                                                 offset_x=1,
                                                 offset_z=1,
                                                 rotation=45)
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)

    new_a, new_b, new_c, new_d = generate_object_bounds({'x': 4, 'z': 4}, {'x': 1, 'z': 1}, {'x': 7, 'z': 7}, {'y': 45})
    assert new_a == pytest.approx(a)
    assert new_b == pytest.approx(b)
    assert new_c == pytest.approx(c)
    assert new_d == pytest.approx(d)


def test__object_collision():
    r1 = geometry.calc_obj_coords(-1.97, 1.75, .55, .445, -.01, .445, 315)
    r2 = geometry.calc_obj_coords(-3.04, .85, 1.75, .05, 0, 0, 315)
    assert sat_entry(r1, r2)
    r3 = geometry.calc_obj_coords(.04, .85, 1.75, .05, 0, 0, 315)
    assert not sat_entry(r1, r3)


def test_get_visible_segment():
    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 0}})
    expected = shapely.geometry.LineString([[0, 1], [0, ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 45}})
    expected = shapely.geometry.LineString([[math.sqrt(2) / 2.0, math.sqrt(2) / 2.0], [ROOM_X_MAX, ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 90}})
    expected = shapely.geometry.LineString([[1, 0], [ROOM_X_MAX, 0]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 135}})
    expected = shapely.geometry.LineString([[math.sqrt(2) / 2.0, -math.sqrt(2) / 2.0], [ROOM_X_MAX, -ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 180}})
    expected = shapely.geometry.LineString([[0, -1], [0, -ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 225}})
    expected = shapely.geometry.LineString([[-math.sqrt(2) / 2.0, -math.sqrt(2) / 2.0], [-ROOM_X_MAX, -ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 270}})
    expected = shapely.geometry.LineString([[-1, 0], [-ROOM_X_MAX, 0]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 315}})
    expected = shapely.geometry.LineString([[-math.sqrt(2) / 2.0, math.sqrt(2) / 2.0], [-ROOM_X_MAX, ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])


def test_get_visible_segment_with_position():
    actual = get_visible_segment({'position': {'x': 1, 'y': 0, 'z': 1}, 'rotation': {'y': 45}})
    expected = shapely.geometry.LineString([[math.sqrt(2) / 2.0 + 1, math.sqrt(2) / 2.0 + 1], [ROOM_X_MAX, ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    actual = get_visible_segment({'position': {'x': -5, 'y': 0, 'z': -5}, 'rotation': {'y': 45}})
    expected = shapely.geometry.LineString([[math.sqrt(2) / 2.0 - 5, math.sqrt(2) / 2.0 - 5], [ROOM_X_MAX, ROOM_Z_MAX]])
    actual_coords = list(actual.coords)
    expected_coords = list(expected.coords)
    assert actual_coords[0][0] == pytest.approx(expected_coords[0][0])
    assert actual_coords[0][1] == pytest.approx(expected_coords[0][1])
    assert actual_coords[1][0] == pytest.approx(expected_coords[1][0])
    assert actual_coords[1][1] == pytest.approx(expected_coords[1][1])

    assert get_visible_segment({'position': {'x': 4.5, 'y': 0, 'z': 0}, 'rotation': {'y': 45}}) is None
    assert get_visible_segment({'position': {'x': 0, 'y': 0, 'z': 4.5}, 'rotation': {'y': 45}}) is None
    assert get_visible_segment({'position': {'x': 4.5, 'y': 0, 'z': 4.5}, 'rotation': {'y': 45}}) is None
    assert get_visible_segment({'position': {'x': 5, 'y': 0, 'z': 0}, 'rotation': {'y': 45}}) is None


def test_get_position_in_front_of_performer():
    performer_start = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 0}}

    for target_definition in util.retrieve_full_object_definition_list(objects.get('PICKUPABLE')):
        target_half_size_x = target_definition['dimensions']['x'] / 2.0
        target_half_size_z = target_definition['dimensions']['z'] / 2.0

        performer_start['rotation']['y'] = 0
        positive_z = get_location_in_front_of_performer(performer_start, target_definition)
        assert 0 <= positive_z['position']['z'] <= ROOM_Z_MAX
        assert -target_half_size_x <= positive_z['position']['x'] <= target_half_size_x
        assert get_bounding_polygon(positive_z).intersection(shapely.geometry.LineString([[0, 1], [0, ROOM_Z_MAX]]))

        performer_start['rotation']['y'] = 90
        positive_x = get_location_in_front_of_performer(performer_start, target_definition)
        assert 0 <= positive_x['position']['x'] <= ROOM_X_MAX
        assert -target_half_size_z <= positive_x['position']['z'] <= target_half_size_z
        assert get_bounding_polygon(positive_x).intersection(shapely.geometry.LineString([[1, 0], [ROOM_X_MAX, 0]]))

        performer_start['rotation']['y'] = 180
        negative_z = get_location_in_front_of_performer(performer_start, target_definition)
        assert ROOM_Z_MIN <= negative_z['position']['z'] <= 0
        assert -target_half_size_x <= negative_z['position']['x'] <= target_half_size_x
        assert get_bounding_polygon(negative_z).intersection(shapely.geometry.LineString([[0, -1], [0, -ROOM_Z_MAX]]))

        performer_start['rotation']['y'] = 270
        negative_x = get_location_in_front_of_performer(performer_start, target_definition)
        assert ROOM_X_MIN <= negative_x['position']['x'] <= 0
        assert -target_half_size_z <= negative_x['position']['z'] <= target_half_size_z
        assert get_bounding_polygon(negative_x).intersection(shapely.geometry.LineString([[-1, 0], [-ROOM_X_MAX, 0]]))


def test_get_position_in_front_of_performer_next_to_room_wall():
    performer_start = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 0}}

    for target_definition in util.retrieve_full_object_definition_list(objects.get('PICKUPABLE')):
        performer_start['position']['z'] = ROOM_Z_MAX
        location = get_location_in_front_of_performer(performer_start, target_definition)
        assert location is None


def test_get_position_in_back_of_performer():
    performer_start = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 0}}

    for target_definition in util.retrieve_full_object_definition_list(objects.get('PICKUPABLE')):
        performer_start['rotation']['y'] = 0
        negative_z = get_location_in_back_of_performer(performer_start, target_definition)
        assert 0 >= negative_z['position']['z'] >= ROOM_Z_MIN
        assert ROOM_X_MAX >= negative_z['position']['x'] >= ROOM_X_MIN

        performer_start['rotation']['y'] = 90
        negative_x = get_location_in_back_of_performer(performer_start, target_definition)
        assert 0 >= negative_x['position']['x'] >= ROOM_X_MIN
        assert ROOM_Z_MAX >= negative_x['position']['z'] >= ROOM_Z_MIN

        performer_start['rotation']['y'] = 180
        positive_z = get_location_in_back_of_performer(performer_start, target_definition)
        assert ROOM_Z_MAX >= positive_z['position']['z'] >= 0
        assert ROOM_X_MAX >= positive_z['position']['x'] >= ROOM_X_MIN

        performer_start['rotation']['y'] = 270
        positive_x = get_location_in_back_of_performer(performer_start, target_definition)
        assert ROOM_X_MAX >= positive_x['position']['x'] >= 0
        assert ROOM_Z_MAX >= positive_x['position']['z'] >= ROOM_Z_MIN


def test_get_position_in_back_of_performer_next_to_room_wall():
    performer_start = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'y': 0}}

    for target_definition in util.retrieve_full_object_definition_list(objects.get('PICKUPABLE')):
        performer_start['position']['z'] = ROOM_Z_MIN
        location = get_location_in_back_of_performer(performer_start, target_definition)
        assert location is None


def test_are_adjacent():
    dimensions = {'x': 2, 'y': 2, 'z': 2}

    center = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    center['boundingBox'] = generate_object_bounds(dimensions, None, center['position'], center['rotation'])

    good_1 = {'position': {'x': 2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_1['boundingBox'] = generate_object_bounds(dimensions, None, good_1['position'], good_1['rotation'])
    assert are_adjacent(center, good_1)

    good_2 = {'position': {'x': -2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_2['boundingBox'] = generate_object_bounds(dimensions, None, good_2['position'], good_2['rotation'])
    assert are_adjacent(center, good_2)

    good_3 = {'position': {'x': 0, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_3['boundingBox'] = generate_object_bounds(dimensions, None, good_3['position'], good_3['rotation'])
    assert are_adjacent(center, good_3)

    good_4 = {'position': {'x': 0, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_4['boundingBox'] = generate_object_bounds(dimensions, None, good_4['position'], good_4['rotation'])
    assert are_adjacent(center, good_4)

    good_5 = {'position': {'x': 2, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_5['boundingBox'] = generate_object_bounds(dimensions, None, good_5['position'], good_5['rotation'])
    assert are_adjacent(center, good_5)

    good_6 = {'position': {'x': 2, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_6['boundingBox'] = generate_object_bounds(dimensions, None, good_6['position'], good_6['rotation'])
    assert are_adjacent(center, good_6)

    good_7 = {'position': {'x': -2, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_7['boundingBox'] = generate_object_bounds(dimensions, None, good_7['position'], good_7['rotation'])
    assert are_adjacent(center, good_7)

    good_8 = {'position': {'x': -2, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_8['boundingBox'] = generate_object_bounds(dimensions, None, good_8['position'], good_8['rotation'])
    assert are_adjacent(center, good_8)

    bad_1 = {'position': {'x': 3, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_1['boundingBox'] = generate_object_bounds(dimensions, None, bad_1['position'], bad_1['rotation'])
    assert not are_adjacent(center, bad_1)

    bad_2 = {'position': {'x': -3, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_2['boundingBox'] = generate_object_bounds(dimensions, None, bad_2['position'], bad_2['rotation'])
    assert not are_adjacent(center, bad_2)

    bad_3 = {'position': {'x': 0, 'y': 0, 'z': 3}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_3['boundingBox'] = generate_object_bounds(dimensions, None, bad_3['position'], bad_3['rotation'])
    assert not are_adjacent(center, bad_3)

    bad_4 = {'position': {'x': 0, 'y': 0, 'z': -3}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_4['boundingBox'] = generate_object_bounds(dimensions, None, bad_4['position'], bad_4['rotation'])
    assert not are_adjacent(center, bad_4)

    bad_5 = {'position': {'x': 2.5, 'y': 0, 'z': 2.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_5['boundingBox'] = generate_object_bounds(dimensions, None, bad_5['position'], bad_5['rotation'])
    assert not are_adjacent(center, bad_5)

    bad_6 = {'position': {'x': 2.5, 'y': 0, 'z': -2.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_6['boundingBox'] = generate_object_bounds(dimensions, None, bad_6['position'], bad_6['rotation'])
    assert not are_adjacent(center, bad_6)

    bad_7 = {'position': {'x': -2.5, 'y': 0, 'z': 2.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_7['boundingBox'] = generate_object_bounds(dimensions, None, bad_7['position'], bad_7['rotation'])
    assert not are_adjacent(center, bad_7)

    bad_8 = {'position': {'x': -2.5, 'y': 0, 'z': -2.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_8['boundingBox'] = generate_object_bounds(dimensions, None, bad_8['position'], bad_8['rotation'])
    assert not are_adjacent(center, bad_8)


def test_are_adjacent_with_offset():
    dimensions = {'x': 2, 'y': 2, 'z': 2}
    offset = {'x': -1, 'y': 0, 'z': 1}

    center = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    center['boundingBox'] = generate_object_bounds(dimensions, None, center['position'], center['rotation'])

    good_1 = {'position': {'x': 3, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_1['boundingBox'] = generate_object_bounds(dimensions, offset, good_1['position'], good_1['rotation'])
    assert are_adjacent(center, good_1)

    good_2 = {'position': {'x': -1, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_2['boundingBox'] = generate_object_bounds(dimensions, offset, good_2['position'], good_2['rotation'])
    assert are_adjacent(center, good_2)

    good_3 = {'position': {'x': 0, 'y': 0, 'z': 1}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_3['boundingBox'] = generate_object_bounds(dimensions, offset, good_3['position'], good_3['rotation'])
    assert are_adjacent(center, good_3)

    good_4 = {'position': {'x': 0, 'y': 0, 'z': -3}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_4['boundingBox'] = generate_object_bounds(dimensions, offset, good_4['position'], good_4['rotation'])
    assert are_adjacent(center, good_4)

    good_5 = {'position': {'x': 3, 'y': 0, 'z': 1}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_5['boundingBox'] = generate_object_bounds(dimensions, offset, good_5['position'], good_5['rotation'])
    assert are_adjacent(center, good_5)

    good_6 = {'position': {'x': 3, 'y': 0, 'z': -3}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_6['boundingBox'] = generate_object_bounds(dimensions, offset, good_6['position'], good_6['rotation'])
    assert are_adjacent(center, good_6)

    good_7 = {'position': {'x': -1, 'y': 0, 'z': 1}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_7['boundingBox'] = generate_object_bounds(dimensions, offset, good_7['position'], good_7['rotation'])
    assert are_adjacent(center, good_7)

    good_8 = {'position': {'x': -1, 'y': 0, 'z': -3}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    good_8['boundingBox'] = generate_object_bounds(dimensions, offset, good_8['position'], good_8['rotation'])
    assert are_adjacent(center, good_8)

    bad_1 = {'position': {'x': 4, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_1['boundingBox'] = generate_object_bounds(dimensions, offset, bad_1['position'], bad_1['rotation'])
    assert not are_adjacent(center, bad_1)

    bad_2 = {'position': {'x': -2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_2['boundingBox'] = generate_object_bounds(dimensions, offset, bad_2['position'], bad_2['rotation'])
    assert not are_adjacent(center, bad_2)

    bad_3 = {'position': {'x': 0, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_3['boundingBox'] = generate_object_bounds(dimensions, offset, bad_3['position'], bad_3['rotation'])
    assert not are_adjacent(center, bad_3)

    bad_4 = {'position': {'x': 0, 'y': 0, 'z': -4}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_4['boundingBox'] = generate_object_bounds(dimensions, offset, bad_4['position'], bad_4['rotation'])
    assert not are_adjacent(center, bad_4)

    bad_5 = {'position': {'x': 3.5, 'y': 0, 'z': 1.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_5['boundingBox'] = generate_object_bounds(dimensions, offset, bad_5['position'], bad_5['rotation'])
    assert not are_adjacent(center, bad_5)

    bad_6 = {'position': {'x': 3.5, 'y': 0, 'z': -3.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_6['boundingBox'] = generate_object_bounds(dimensions, offset, bad_6['position'], bad_6['rotation'])
    assert not are_adjacent(center, bad_6)

    bad_7 = {'position': {'x': -1.5, 'y': 0, 'z': 1.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_7['boundingBox'] = generate_object_bounds(dimensions, offset, bad_7['position'], bad_7['rotation'])
    assert not are_adjacent(center, bad_7)

    bad_8 = {'position': {'x': -1.5, 'y': 0, 'z': -3.5}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    bad_8['boundingBox'] = generate_object_bounds(dimensions, offset, bad_8['position'], bad_8['rotation'])
    assert not are_adjacent(center, bad_8)


def test_get_adjacent_location():
    # Set the performer start out-of-the-way.
    performer_start = {'position': {'x': ROOM_X_MAX, 'y': 0, 'z': ROOM_Z_MAX}, 'rotation': {'y': 0}}

    for target_definition in util.retrieve_full_object_definition_list(objects.get('PICKUPABLE')):
        target_location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        target_location['boundingBox'] = generate_object_bounds(target_definition['dimensions'], \
                (target_definition['offset'] if 'offset' in target_definition else None), target_location['position'], \
                target_location['rotation'])
        target_poly = get_bounding_polygon(target_location)

        for object_definition in util.retrieve_full_object_definition_list(objects.get('ALL')):
            location = get_adjacent_location(object_definition, target_definition, target_location, performer_start)
            assert location
            object_poly = get_bounding_polygon(location)
            assert object_poly.distance(target_poly) < 0.5


def test_get_adjacent_location_with_obstruct():
    # Set the performer start in the back of the room facing inward.
    performer_start = {'position': {'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, 'rotation': {'y': 0}}

    # Use the sofa in this test because it should obstruct any possible pickupable object.
    sofa_list = [item for item in objects.get('ALL') if 'type' in item and item['type'] == 'sofa_1']
    object_definition = util.finalize_object_definition(sofa_list[0])

    for target_definition in util.retrieve_full_object_definition_list(objects.get('PICKUPABLE')):
        target_location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        target_location['boundingBox'] = generate_object_bounds(target_definition['dimensions'], \
                (target_definition['offset'] if 'offset' in target_definition else None), target_location['position'], \
                target_location['rotation'])
        target_poly = get_bounding_polygon(target_location)

        location = get_adjacent_location(object_definition, target_definition, target_location, performer_start, True)
        assert location
        object_poly = get_bounding_polygon(location)
        assert object_poly.distance(target_poly) < 0.5
        assert does_fully_obstruct_target(performer_start['position'], target_location, object_poly)


def get_min_and_max_in_bounds(bounds):
    return bounds[2]['x'], bounds[0]['x'], bounds[2]['z'], bounds[0]['z']


def test_get_adjacent_location_on_side():
    # Set the performer start out-of-the-way.
    performer_start = {'position': {'x': ROOM_X_MAX, 'y': 0, 'z': ROOM_Z_MAX}, 'rotation': {'y': 0}}

    for target_definition in util.retrieve_full_object_definition_list(objects.get('PICKUPABLE')):
        target_offset = target_definition['offset'] if 'offset' in target_definition else {'x': 0, 'z': 0}
        target_location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        target_location['boundingBox'] = generate_object_bounds(target_definition['dimensions'], target_offset, \
                target_location['position'], target_location['rotation'])
        target_poly = get_bounding_polygon(target_location)

        target_x_min, target_x_max, target_z_min, target_z_max = get_min_and_max_in_bounds( \
                target_location['boundingBox'])

        for object_definition in util.retrieve_full_object_definition_list(objects.get('ALL')):
            object_offset = object_definition['offset'] if 'offset' in object_definition else {'x': 0, 'z': 0}

            location = get_adjacent_location_on_side(object_definition, target_definition, target_location, \
                    performer_start, Side.RIGHT, False)
            assert location
            x_min, x_max, z_min, z_max = get_min_and_max_in_bounds(location['boundingBox'])
            assert target_x_max <= x_min <= ROOM_X_MAX
            assert target_x_max <= x_max <= ROOM_X_MAX
            assert target_location['position']['z'] + target_offset['z'] == \
                    pytest.approx(location['position']['z'] + object_offset['z'])
            object_poly = get_bounding_polygon(location)
            assert object_poly.distance(target_poly) < 0.5

            location = get_adjacent_location_on_side(object_definition, target_definition, target_location, \
                    performer_start, Side.LEFT, False)
            assert location
            x_min, x_max, z_min, z_max = get_min_and_max_in_bounds(location['boundingBox'])
            assert ROOM_X_MIN <= x_min <= target_x_min
            assert ROOM_X_MIN <= x_max <= target_x_min
            assert target_location['position']['z'] + target_offset['z'] == \
                    pytest.approx(location['position']['z'] + object_offset['z'])
            object_poly = get_bounding_polygon(location)
            assert object_poly.distance(target_poly) < 0.5

            location = get_adjacent_location_on_side(object_definition, target_definition, target_location, \
                    performer_start, Side.FRONT, False)
            assert location
            x_min, x_max, z_min, z_max = get_min_and_max_in_bounds(location['boundingBox'])
            assert target_z_max <= z_min <= ROOM_Z_MAX
            assert target_z_max <= z_max <= ROOM_Z_MAX
            assert target_location['position']['x'] + target_offset['x'] == \
                    pytest.approx(location['position']['x'] + object_offset['x'])
            object_poly = get_bounding_polygon(location)
            assert object_poly.distance(target_poly) < 0.5

            location = get_adjacent_location_on_side(object_definition, target_definition, target_location, \
                    performer_start, Side.BACK, False)
            assert location
            x_min, x_max, z_min, z_max = get_min_and_max_in_bounds(location['boundingBox'])
            assert ROOM_Z_MIN <= z_min <= target_z_min
            assert ROOM_Z_MIN <= z_max <= target_z_min
            assert target_location['position']['x'] + target_offset['x'] == \
                    pytest.approx(location['position']['x'] + object_offset['x'])
            object_poly = get_bounding_polygon(location)
            assert object_poly.distance(target_poly) < 0.5


def test_get_adjacent_location_on_side_next_to_room_wall():
    # Set the performer start out-of-the-way.
    performer_start = {'position': {'x': ROOM_X_MAX, 'y': 0, 'z': ROOM_Z_MAX}, 'rotation': {'y': 0}}

    for target_definition in util.retrieve_full_object_definition_list(objects.get('ALL')):
        target_offset = target_definition['offset'] if 'offset' in target_definition else {'x': 0, 'z': 0}
        target_location = {'position': {'x': ROOM_X_MAX, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        target_location['boundingBox'] = generate_object_bounds(target_definition['dimensions'], target_offset, \
                target_location['position'], target_location['rotation'])

        for object_definition in util.retrieve_full_object_definition_list(objects.get('ALL')):
            location = get_adjacent_location_on_side(object_definition, target_definition, target_location, \
                    performer_start, Side.RIGHT, False)
            assert not location


def test_get_wider_and_taller_defs():
    for object_definition in util.retrieve_full_object_definition_list(objects.get('ALL')):
        object_dimensions = object_definition['closedDimensions'] if 'closedDimensions' in object_definition else \
                object_definition['dimensions']
        bigger_definition_list = get_wider_and_taller_defs(object_definition, False)
        for bigger_definition_result in bigger_definition_list:
            bigger_definition, angle = bigger_definition_result
            bigger_definition = util.finalize_object_definition(bigger_definition)
            bigger_dimensions = bigger_definition['closedDimensions'] if 'closedDimensions' in bigger_definition \
                    else bigger_definition['dimensions']
            assert bigger_definition['obstruct'] == 'navigation'
            assert bigger_dimensions['y'] >= 0.2
            if angle == 0:
                assert bigger_dimensions['x'] >= object_dimensions['x']
            else:
                # We rotate the bigger object so compare its side to the original object's front.
                assert bigger_dimensions['z'] >= object_dimensions['x']


def test_get_wider_and_taller_defs_obstruct_vision():
    for object_definition in util.retrieve_full_object_definition_list(objects.get('ALL')):
        object_dimensions = object_definition['closedDimensions'] if 'closedDimensions' in object_definition else \
                object_definition['dimensions']
        bigger_definition_list = get_wider_and_taller_defs(object_definition, True)
        for bigger_definition_result in bigger_definition_list:
            bigger_definition, angle = bigger_definition_result
            bigger_definition = util.finalize_object_definition(bigger_definition)
            bigger_dimensions = bigger_definition['closedDimensions'] if 'closedDimensions' in bigger_definition \
                    else bigger_definition['dimensions']
            assert bigger_definition['obstruct'] == 'vision'
            assert bigger_dimensions['y'] >= object_dimensions['y']
            if angle == 0:
                assert bigger_dimensions['x'] >= object_dimensions['x']
            else:
                # We rotate the bigger object so compare its side to the original object's front.
                assert bigger_dimensions['z'] >= object_dimensions['x']


def test_get_bounding_poly():
    # TODO
    pass


def test_rect_to_poly():
    rect = [{'x': 1, 'z': 2}, {'x': 3, 'z': 4}, {'x': 7, 'z': 0}, {'x': 5, 'z': -2}]
    expected = shapely.geometry.Polygon([(1, 2), (3, 4), (7, 0), (5, -2)])
    actual = geometry.rect_to_poly(rect)
    assert actual.equals(expected)


def test_find_performer_rect():
    expected1 = [{'x': -0.05, 'z': -0.05}, {'x': -0.05, 'z': 0.05}, {'x': 0.05, 'z': 0.05}, {'x': 0.05, 'z': -0.05}]
    actual1 = find_performer_rect({'x': 0, 'y': 0, 'z': 0})
    assert actual1 == expected1

    expected2 = [{'x': 0.95, 'z': 0.95}, {'x': 0.95, 'z': 1.05}, {'x': 1.05, 'z': 1.05}, {'x': 1.05, 'z': 0.95}]
    actual2 = find_performer_rect({'x': 1, 'y': 1, 'z': 1})
    assert actual2 == expected2


def test_set_location_rotation():
    for definition in util.retrieve_full_object_definition_list(objects.get('ALL')):
        offset = definition['offset'] if 'offset' in definition else {'x': 0, 'z': 0}

        location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        location = set_location_rotation(definition, location, 0)
        assert location['rotation']['y'] == 0
        assert location['boundingBox'][0]['x'] == pytest.approx(definition['dimensions']['x'] / 2 + offset['x'])
        assert location['boundingBox'][0]['z'] == pytest.approx(definition['dimensions']['z'] / 2 + offset['z'])
        assert location['boundingBox'][1]['x'] == pytest.approx(definition['dimensions']['x'] / 2 + offset['x'])
        assert location['boundingBox'][1]['z'] == pytest.approx(-definition['dimensions']['z'] / 2 + offset['z'])
        assert location['boundingBox'][2]['x'] == pytest.approx(-definition['dimensions']['x'] / 2 + offset['x'])
        assert location['boundingBox'][2]['z'] == pytest.approx(-definition['dimensions']['z'] / 2 + offset['z'])
        assert location['boundingBox'][3]['x'] == pytest.approx(-definition['dimensions']['x'] / 2 + offset['x'])
        assert location['boundingBox'][3]['z'] == pytest.approx(definition['dimensions']['z'] / 2 + offset['z'])

        location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        location = set_location_rotation(definition, location, 90)
        assert location['rotation']['y'] == 90
        assert location['boundingBox'][0]['x'] == pytest.approx(definition['dimensions']['z'] / 2 + offset['z'])
        assert location['boundingBox'][0]['z'] == pytest.approx(-definition['dimensions']['x'] / 2 - offset['x'])
        assert location['boundingBox'][1]['x'] == pytest.approx(-definition['dimensions']['z'] / 2 + offset['z'])
        assert location['boundingBox'][1]['z'] == pytest.approx(-definition['dimensions']['x'] / 2 - offset['x'])
        assert location['boundingBox'][2]['x'] == pytest.approx(-definition['dimensions']['z'] / 2 + offset['z'])
        assert location['boundingBox'][2]['z'] == pytest.approx(definition['dimensions']['x'] / 2 - offset['x'])
        assert location['boundingBox'][3]['x'] == pytest.approx(definition['dimensions']['z'] / 2 + offset['z'])
        assert location['boundingBox'][3]['z'] == pytest.approx(definition['dimensions']['x'] / 2 - offset['x'])

        location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        location = set_location_rotation(definition, location, 180)
        assert location['rotation']['y'] == 180
        assert location['boundingBox'][0]['x'] == pytest.approx(-definition['dimensions']['x'] / 2 - offset['x'])
        assert location['boundingBox'][0]['z'] == pytest.approx(-definition['dimensions']['z'] / 2 - offset['z'])
        assert location['boundingBox'][1]['x'] == pytest.approx(-definition['dimensions']['x'] / 2 - offset['x'])
        assert location['boundingBox'][1]['z'] == pytest.approx(definition['dimensions']['z'] / 2 - offset['z'])
        assert location['boundingBox'][2]['x'] == pytest.approx(definition['dimensions']['x'] / 2 - offset['x'])
        assert location['boundingBox'][2]['z'] == pytest.approx(definition['dimensions']['z'] / 2 - offset['z'])
        assert location['boundingBox'][3]['x'] == pytest.approx(definition['dimensions']['x'] / 2 - offset['x'])
        assert location['boundingBox'][3]['z'] == pytest.approx(-definition['dimensions']['z'] / 2 - offset['z'])

        location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
        location = set_location_rotation(definition, location, 270)
        assert location['rotation']['y'] == 270
        assert location['boundingBox'][0]['x'] == pytest.approx(-definition['dimensions']['z'] / 2 - offset['z'])
        assert location['boundingBox'][0]['z'] == pytest.approx(definition['dimensions']['x'] / 2 + offset['x'])
        assert location['boundingBox'][1]['x'] == pytest.approx(definition['dimensions']['z'] / 2 - offset['z'])
        assert location['boundingBox'][1]['z'] == pytest.approx(definition['dimensions']['x'] / 2 + offset['x'])
        assert location['boundingBox'][2]['x'] == pytest.approx(definition['dimensions']['z'] / 2 - offset['z'])
        assert location['boundingBox'][2]['z'] == pytest.approx(-definition['dimensions']['x'] / 2 + offset['x'])
        assert location['boundingBox'][3]['x'] == pytest.approx(-definition['dimensions']['z'] / 2 - offset['z'])
        assert location['boundingBox'][3]['z'] == pytest.approx(-definition['dimensions']['x'] / 2 + offset['x'])


def test_does_fully_obstruct_target():
    target_location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = generate_object_bounds({'x': 1, 'z': 1}, None, \
            target_location['position'], target_location['rotation'])

    obstructor_location = {'position': {'x': -2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 0, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 0, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)


def test_does_fully_obstruct_target_returns_false_too_small():
    target_location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = generate_object_bounds({'x': 1, 'z': 1}, None, \
            target_location['position'], target_location['rotation'])

    obstructor_location = {'position': {'x': -2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 0.5, 'z': 0.5}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 0.5, 'z': 0.5}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 0, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 0.5, 'z': 0.5}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 0, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 0.5, 'z': 0.5}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)


def test_does_fully_obstruct_target_returns_false_performer_start():
    target_location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = generate_object_bounds({'x': 1, 'z': 1}, None, \
            target_location['position'], target_location['rotation'])

    obstructor_location = {'position': {'x': -2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': 0}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 2, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': 0}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 0, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': 0}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': 0}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 0, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': 0}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': 0}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)


def test_does_fully_obstruct_target_returns_false_visible_corners():
    target_location = {'position': {'x': 0, 'y': 0, 'z': 0}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    target_location['boundingBox'] = generate_object_bounds({'x': 1, 'z': 1}, None, \
            target_location['position'], target_location['rotation'])

    obstructor_location = {'position': {'x': -2, 'y': 0, 'z': 1}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': -2, 'y': 0, 'z': -1}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MIN, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 2, 'y': 0, 'z': 1}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 2, 'y': 0, 'z': -1}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': ROOM_X_MAX, 'y': 0, 'z': 0}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 1, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': -1, 'y': 0, 'z': -2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MIN}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': 1, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)

    obstructor_location = {'position': {'x': -1, 'y': 0, 'z': 2}, 'rotation': {'x': 0, 'y': 0, 'z': 0}}
    obstructor_location['boundingBox'] = generate_object_bounds({'x': 2, 'z': 2}, None, \
            obstructor_location['position'], obstructor_location['rotation'])
    obstructor_poly = get_bounding_polygon(obstructor_location)
    assert not does_fully_obstruct_target({'x': 0, 'y': 0, 'z': ROOM_Z_MAX}, target_location, obstructor_poly)

