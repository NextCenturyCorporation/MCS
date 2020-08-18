import pytest

import geometry
import objects
import util
from containers import put_object_in_container, put_objects_in_container, Orientation, can_enclose, \
    can_contain_both, how_can_contain, get_enclosable_containments, find_suitable_enclosable_list, \
    retrieve_enclosable_object_definition_list
from geometry_test import are_adjacent


PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS = ['duck_on_wheels', 'box_2', 'box_3']


def test_put_object_in_container():
    for obj_def in util.retrieve_full_object_definition_list(
            objects.get('PICKUPABLE')):
        obj_location = geometry.calc_obj_pos(
            {'x': 1, 'y': 0, 'z': 1}, [], obj_def)
        obj = util.instantiate_object(obj_def, obj_location)
        obj_bounds = obj['shows'][0]['boundingBox']

        containments = get_enclosable_containments([obj_def])
        if len(
                containments) == 0 and obj_def['type'] not in PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS:
            print(
                f'pickupable object should have at least one containment: {obj_def}')
            assert False

        for containment in containments:
            container_def, area_index, rotations = containment
            container_location = geometry.calc_obj_pos(
                {'x': -1, 'y': 0, 'z': -1}, [], container_def)
            container = util.instantiate_object(
                container_def, container_location)

            put_object_in_container(
                obj_def,
                obj,
                container,
                container_def,
                area_index,
                rotations[0])

            assert obj['locationParent'] == container['id']
            assert obj['shows'][0]['position']['x'] == container_def['enclosedAreas'][0]['position']['x']
            expected_position_y = container_def['enclosedAreas'][0]['position']['y'] - \
                (container_def['enclosedAreas'][area_index]['dimensions']['y'] / 2.0) + \
                obj_def.get('positionY', 0)
            assert obj['shows'][0]['position']['y'] == pytest.approx(
                expected_position_y)
            assert obj['shows'][0]['position']['z'] == container_def['enclosedAreas'][0]['position']['z']
            assert obj['shows'][0]['rotation']
            assert obj['shows'][0]['boundingBox']
            assert obj['shows'][0]['boundingBox'] != obj_bounds


def test_put_objects_in_container():
    for obj_a_def in util.retrieve_full_object_definition_list(
            objects.get('PICKUPABLE')):
        obj_a_location = geometry.calc_obj_pos(geometry.ORIGIN, [], obj_a_def)
        obj_a = util.instantiate_object(obj_a_def, obj_a_location)
        obj_a_bounds = obj_a['shows'][0]['boundingBox']

        for obj_b_def in util.retrieve_full_object_definition_list(
                objects.get('PICKUPABLE')):
            obj_b_location = geometry.calc_obj_pos(
                geometry.ORIGIN, [], obj_b_def)
            obj_b = util.instantiate_object(obj_b_def, obj_b_location)
            obj_b_bounds = obj_b['shows'][0]['boundingBox']

            containments = get_enclosable_containments([obj_a_def, obj_b_def])
            if len(containments) == 0 and obj_a_def['type'] not in PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS and \
                    obj_b_def['type'] not in PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS:
                print(
                    f'pair of pickupable objects should have at least one containment:\nobject_a={obj_a_def}\nobject_b={obj_b_def}')
                assert False

            for containment in containments:
                container_def, area_index, rotations = containment
                container_location = geometry.calc_obj_pos(
                    geometry.ORIGIN, [], container_def)
                container = util.instantiate_object(
                    container_def, container_location)

                put_objects_in_container(obj_a_def, obj_a, obj_b_def, obj_b, container, container_def, area_index,
                                         Orientation.SIDE_BY_SIDE, rotations[0], rotations[1])
                assert obj_a['locationParent'] == container['id']
                assert obj_b['locationParent'] == container['id']
                assert obj_a['shows'][0]['boundingBox']
                assert obj_b['shows'][0]['boundingBox']
                assert obj_a['shows'][0]['boundingBox'] != obj_a_bounds
                assert obj_b['shows'][0]['boundingBox'] != obj_b_bounds
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
    container_def = util.finalize_object_definition(
        retrieve_enclosable_object_definition_list()[0])
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
    container_def = util.finalize_object_definition(
        retrieve_enclosable_object_definition_list()[0])
    assert can_contain_both(container_def, small1, small2) is not None
    assert can_contain_both(container_def, small1, big) is None


def test_get_enclosable_containments():
    for target_definition in util.retrieve_full_object_definition_list(
            objects.get('PICKUPABLE')):
        containments = get_enclosable_containments([target_definition])
        if len(
                containments) == 0 and target_definition['type'] not in PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS:
            print(
                f'pickupable object should have at least one containment: {target_definition}')
            assert False
        for containment in containments:
            definition, index, angles = containment
            assert definition
            assert index >= 0
            assert angles


def test_get_enclosable_containments_multiple_object():
    target_definition_1 = {
        'dimensions': {
            'x': 0.01,
            'y': 0.01,
            'z': 0.01
        }
    }
    target_definition_2 = {
        'dimensions': {
            'x': 0.02,
            'y': 0.02,
            'z': 0.02
        }
    }
    containments = get_enclosable_containments(
        [target_definition_1, target_definition_2])
    assert len(containments) > 0
    for containment in containments:
        definition, index, angles = containment
        assert definition
        assert index >= 0
        assert angles


def test_find_suitable_enclosable_list():
    for target_definition in util.retrieve_full_object_definition_list(
            objects.get('PICKUPABLE')):
        enclosable_list = find_suitable_enclosable_list(target_definition)
        if len(
                enclosable_list) == 0 and target_definition['type'] not in PICKUPABLE_OBJECTS_WITHOUT_CONTAINMENTS:
            print(
                f'pickupable object should have at least one enclosable: {target_definition}')
            assert False
        assert True
