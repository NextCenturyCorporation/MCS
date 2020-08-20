import objects
import random
from util import retrieve_full_object_definition_list


def test_create_occluder_normal():
    wall_material = ['test_material_wall', ['white']]
    pole_material = ['test_material_pole', ['brown']]
    x_position = random.uniform(-1, 1)
    x_scale = random.uniform(0.1, 2)

    occluder = objects.create_occluder(
        wall_material,
        pole_material,
        x_position,
        x_scale)
    assert len(occluder) == 2
    wall, pole = occluder
    # make sure we got them back in the right order
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']
    for x in wall, pole:
        assert x['shows'][0]['position']['x'] == x_position


def test_create_occluder_sideways():
    wall_material = ['test_material_wall', ['white']]
    pole_material = ['test_material_pole', ['brown']]
    x_position = random.uniform(-1, 1)
    x_scale = random.uniform(0.1, 2)

    occluder = objects.create_occluder(
        wall_material,
        pole_material,
        x_position,
        x_scale,
        True)
    assert len(occluder) == 2
    wall, pole = occluder
    # make sure we got them back in the right order
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']


def test_all_objects_have_expected_properties():
    for object_definition in retrieve_full_object_definition_list(
        objects.get('ALL')
    ):
        print(f'{object_definition["type"]}')
        assert 'type' in object_definition
        assert 'size' in object_definition
        assert 'shape' in object_definition
        assert 'mass' in object_definition
        assert 'attributes' in object_definition
        assert 'dimensions' in object_definition
        assert 'materialCategory' in object_definition
        assert 'salientMaterials' in object_definition
        if len(object_definition['materialCategory']) == 0:
            assert 'color' in object_definition
        assert 'info' not in object_definition


def test_get():
    list_1 = objects.get('ALL')
    list_2 = objects.get('ALL')
    assert not (list_1 is list_2)
    assert list_1 == list_2
