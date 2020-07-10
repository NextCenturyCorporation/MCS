import pytest

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


def test__object_collision():
    r1 = geometry.calc_obj_coords(-1.97, 1.75, .55, .445, -.01, .445, 315)
    r2 = geometry.calc_obj_coords(-3.04, .85, 1.75, .05, 0, 0, 315)
    assert sat_entry(r1, r2)
    r3 = geometry.calc_obj_coords(.04, .85, 1.75, .05, 0, 0, 315)
    assert not sat_entry(r1, r3)


def test_get_visible_segment():
    start = {
        'position': ORIGIN,
        'rotation': {
            'y': 0
        }
    }
    segment = get_visible_segment(start)
    expected_segment = shapely.geometry.LineString([[0, 1], [0, ROOM_DIMENSIONS[0][1]]])
    assert segment == expected_segment


def test_get_position_in_back_of_performer():
    target_def = objects.OBJECTS_PICKUPABLE_BALLS[0]
    start = {
        'position': ORIGIN,
        'rotation': {
            'y': 90
        }
    }
    negative_x = get_location_in_back_of_performer(start, target_def)
    assert 0 >= negative_x['position']['x'] >= ROOM_DIMENSIONS[0][0]
    assert ROOM_DIMENSIONS[1][1] >= negative_x['position']['z'] >= ROOM_DIMENSIONS[1][0]

    start['rotation']['y'] = 0
    negative_z = get_location_in_back_of_performer(start, target_def)
    assert 0 >= negative_z['position']['z'] >= ROOM_DIMENSIONS[1][0]
    assert ROOM_DIMENSIONS[0][1] >= negative_z['position']['z'] >= ROOM_DIMENSIONS[0][0]


def are_adjacent(obj_a: Dict[str, Any], obj_b: Dict[str, Any]) -> bool:
    poly_a = geometry.get_bounding_polygon(obj_a)
    poly_b = geometry.get_bounding_polygon(obj_b)
    distance = poly_a.distance(poly_b)
    return distance <= MAX_ADJACENT_DISTANCE


MAX_ADJACENT_DISTANCE = 0.5


def test_get_adjacent_location():
    target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
    target = util.instantiate_object(target_def, ORIGIN_LOCATION)
    obj_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))

    location = get_adjacent_location(obj_def, target, ORIGIN)
    assert location is not None

    # check that their bounding boxes are near each other
    obj = util.instantiate_object(obj_def, location)
    obj_bb = get_bounding_polygon(obj)
    target_bb = get_bounding_polygon(target)
    assert obj_bb.distance(target_bb) < 0.5
    

def test_get_adjacent_location_on_side():
    for side in list(Side):
        target_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        target = util.instantiate_object(target_def, ORIGIN_LOCATION)
        obj_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
        location = get_adjacent_location_on_side(obj_def, target, ORIGIN, side)
        assert location is not None
        angle = math.degrees(math.atan2(location['position']['z'], location['position']['x']))
        target_angle = target['shows'][0]['rotation']['y']
        delta = angle - target_angle
        expected_angle = 90 * side
        if expected_angle > 180:
            expected_angle -= 360
        # need to allow some tolerance because of object offsets
        assert delta == pytest.approx(expected_angle, abs=15)


def test_get_wider_and_taller_defs():
    obj_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
    dims = obj_def['dimensions']
    wt_defs = get_wider_and_taller_defs(obj_def)
    for wt_def_pair in wt_defs:
        wt_def, angle = wt_def_pair
        wt_def = util.finalize_object_definition(wt_def)
        assert wt_def['dimensions']['y'] >= dims['y']
        if angle == 0:
            assert wt_def['dimensions']['x'] >= dims['x']
        else:
            assert wt_def['dimensions']['z'] >= dims['x']


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

