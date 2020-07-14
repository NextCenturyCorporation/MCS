import random

import geometry
import objects
import util
from containers import put_object_in_container, put_objects_in_container, Orientation, can_enclose, \
    can_contain_both, how_can_contain
from geometry_test import are_adjacent


def test_put_object_in_container():
    obj_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
    obj_location = geometry.calc_obj_pos(geometry.ORIGIN, [], obj_def)
    obj = util.instantiate_object(obj_def, obj_location)
    container_def = util.finalize_object_definition(random.choice(objects.get_enclosed_containers()))
    container_location = geometry.calc_obj_pos(geometry.ORIGIN, [], container_def)
    container = util.instantiate_object(container_def, container_location)

    put_object_in_container(obj_def, obj, container, container_def, 0)
    assert obj['locationParent'] == container['id']
    assert obj['shows'][0]['position']['x'] == container_def['enclosed_areas'][0]['position']['x']
    assert obj['shows'][0]['position']['y'] == container_def['enclosed_areas'][0]['position']['y'] - \
            (container_def['enclosed_areas'][0]['dimensions']['y'] / 2.0) + obj_def.get('position_y', 0)
    assert obj['shows'][0]['position']['z'] == container_def['enclosed_areas'][0]['position']['z']


def test_put_objects_in_container():
    obj_a_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
    obj_a_location = geometry.calc_obj_pos(geometry.ORIGIN, [], obj_a_def)
    obj_a = util.instantiate_object(obj_a_def, obj_a_location)
    obj_b_def = util.finalize_object_definition(random.choice(objects.get_all_object_defs()))
    obj_b_location = geometry.calc_obj_pos(geometry.ORIGIN, [], obj_b_def)
    obj_b = util.instantiate_object(obj_b_def, obj_b_location)
    container_def = util.finalize_object_definition(random.choice(objects.get_enclosed_containers()))
    container_location = geometry.calc_obj_pos(geometry.ORIGIN, [], container_def)
    container = util.instantiate_object(container_def, container_location)

    put_objects_in_container(obj_a_def, obj_a, obj_b_def, obj_b, container, container_def, 0,
                             Orientation.SIDE_BY_SIDE, 0, 0)
    assert obj_a['locationParent'] == container['id']
    assert obj_b['locationParent'] == container['id']
    assert are_adjacent(obj_a, obj_b)


def test_can_enclose():
    small = {
        'dimensions': {
            'x': 1,
            'y': 1,
            'z': 1
        }
    }
    big = {
        'dimensions': {
            'x': 42,
            'y': 42,
            'z': 42
        }
    }
    assert can_enclose(big, small) is not None
    assert can_enclose(small, big) is None


def test_how_can_contain():
    small = {
        'dimensions': {
            'x': 0.01,
            'y': 0.01,
            'z': 0.01
        }
    }
    big = {
        'dimensions': {
            'x': 42,
            'y': 42,
            'z': 42
        }
    }
    container_def = util.finalize_object_definition(objects.get_enclosed_containers()[0])
    assert how_can_contain(container_def, small) is not None
    assert how_can_contain(container_def, big) is None
    assert how_can_contain(container_def, small, big) is None


def test_can_contain_both():
    small1 = {
        'dimensions': {
            'x': 0.01,
            'y': 0.01,
            'z': 0.01
        }
    }
    small2 = {
        'dimensions': {
            'x': 0.02,
            'y': 0.02,
            'z': 0.02
        }
    }
    big = {
        'dimensions': {
            'x': 42,
            'y': 42,
            'z': 42
        }
    }
    container_def = util.finalize_object_definition(objects.get_enclosed_containers()[0])
    assert can_contain_both(container_def, small1, small2) is not None
    assert can_contain_both(container_def, small1, big) is None
