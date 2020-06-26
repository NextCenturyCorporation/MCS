from objects import *
import uuid
import random


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
    assert wall['info_string'] == 'white'
    assert pole['info_string'] == 'brown'
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
    assert wall['info_string'] == 'white'
    assert pole['info_string'] == 'brown'

    
def test_get_all_object_defs():
    all = get_all_object_defs()
    dup = get_all_object_defs()
    assert all is dup
    for obj_def in all:
        assert type(obj_def) is type({})
