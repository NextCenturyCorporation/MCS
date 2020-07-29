from objects import *
import uuid
import random
from util import retrieve_full_object_definition_list


def test_create_occluder_normal():
    wall_material = ['test_material_wall', ['white']]
    pole_material = ['test_material_pole', ['brown']]
    x_position = random.uniform(-1, 1)
    x_scale = random.uniform(0.1, 2)

    occluder = create_occluder(wall_material, pole_material, x_position, x_scale)
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

    occluder = create_occluder(wall_material, pole_material, x_position, x_scale, True)
    assert len(occluder) == 2
    wall, pole = occluder
    # make sure we got them back in the right order
    assert wall['type'] == 'cube'
    assert pole['type'] == 'cylinder'
    assert wall['materials'] == ['test_material_wall']
    assert pole['materials'] == ['test_material_pole']
    assert wall['info'] == ['white']
    assert pole['info'] == ['brown']


def test_get_all_object_defs():
    all = get_all_object_defs()
    dup = get_all_object_defs()
    assert all is dup
    for obj_def in all:
        assert type(obj_def) is type({})


def test_get_enclosed_containers():
    containers = get_enclosed_containers()
    for container in containers:
        assert 'enclosedAreas' in container or 'chooseSize' in container \
            and 'enclosedAreas' in container['chooseSize'][0]


def test_get_intphys_objects():
    objs = get_intphys_objects()
    for obj in objs:
        assert 'intphysOptions' in obj


def test_all_objects_have_expected_properties():
    for object_definition in retrieve_full_object_definition_list(get_all_object_defs()):
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

