import uuid

import geometry
import materials
import objects
from goals import *
from util import finalize_object_definition, instantiate_object, check_same_and_different, get_similar_defs, random_real


def test_random_real():
    n = random_real(0, 1, 0.1)
    assert 0 <= n <= 1
    # need to multiply by 10 and mod by 1 instead of 0.1 to avoid weird roundoff
    assert n * 10 % 1 < 1e-8


def test_finalize_object_definition():
    object_type = 'type1'
    mass = 12.34
    material_category = ['plastic']
    salient_materials = ['plastic', 'hollow']
    object_def = {
        'type': 'type2',
        'mass': 56.78,
        'choose': [{
            'type': object_type,
            'mass': mass,
            'materialCategory': material_category,
            'salientMaterials': salient_materials
        }]
    }
    obj = finalize_object_definition(object_def)
    assert obj['type'] == object_type
    assert obj['mass'] == mass
    assert obj['materialCategory'] == material_category
    assert obj['salientMaterials'] == salient_materials


def test_instantiate_object():
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'attributes': ['foo', 'bar'],
        'scale': 1.0
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert type(obj['id']) is str
    assert obj['type'] == 'sofa_1'
    assert obj['goal_string'] == 'huge massive sofa'
    assert obj['info'] == ['huge', 'massive', 'sofa']
    assert obj['info_string'] == 'huge massive sofa'
    assert obj['mass'] == 12.34
    assert obj['novel_color'] is False
    assert obj['novel_combination'] is False
    assert obj['novel_shape'] is False
    assert obj['shape'] == 'sofa'
    assert obj['foo'] is True
    assert obj['bar'] is True
    assert obj['shows'][0]['position'] == object_location['position']
    assert obj['shows'][0]['rotation'] == object_location['rotation']


def test_instantiate_object_heavy_moveable():
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'attributes': ['moveable'],
        'scale': 1.0
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['goal_string'] == 'huge heavy sofa'
    assert obj['info'] == ['huge', 'heavy', 'sofa']
    assert obj['info_string'] == 'huge heavy sofa'
    assert obj['moveable'] is True


def test_instantiate_object_light_pickupable():
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'attributes': ['moveable', 'pickupable'],
        'scale': 1.0
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['goal_string'] == 'huge light sofa'
    assert obj['info'] == ['huge', 'light', 'sofa']
    assert obj['info_string'] == 'huge light sofa'
    assert obj['moveable'] is True
    assert obj['pickupable'] is True


def test_instantiate_object_offset():
    offset = {
        'x': random.random(),
        'z': random.random()
    }
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'offset': offset
    }
    x = random.random()
    z = random.random()
    object_location = {
        'position': {
            'x': x,
            'y': 0.0,
            'z': z
        },
        'rotation': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    position = obj['shows'][0]['position']
    assert position['x'] == x - offset['x']
    assert position['z'] == z - offset['z']


def test_instantiate_object_materials():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['materials'] == ['test_material']
    assert obj['goal_string'] == 'huge massive blue yellow sofa'
    assert obj['info'] == ['huge', 'massive', 'blue', 'yellow', 'sofa']
    assert obj['info_string'] == 'huge massive blue yellow sofa'


def test_instantiate_object_multiple_materials():
    materials.TEST1_MATERIALS = [('test_material_1', ['blue'])]
    materials.TEST2_MATERIALS = [('test_material_2', ['yellow'])]
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test1', 'test2']
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['materials'] == ['test_material_1', 'test_material_2']
    assert obj['goal_string'] == 'huge massive blue yellow sofa'
    assert obj['info'] == ['huge', 'massive', 'blue', 'yellow', 'sofa']
    assert obj['info_string'] == 'huge massive blue yellow sofa'


def test_instantiate_object_salient_materials():
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'salientMaterials': ['fabric', 'wood']
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['salientMaterials'] == ['fabric', 'wood']
    assert obj['goal_string'] == 'huge massive fabric wood sofa'
    assert obj['info'] == ['huge', 'massive', 'fabric', 'wood', 'sofa']
    assert obj['info_string'] == 'huge massive fabric wood sofa'


def test_instantiate_object_size():
    object_def = {
        'type': 'sofa_1',
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
    }
    object_location = {
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
    size_mapping = {
        'pickupable': 'light',
        'moveable': 'heavy',
        'anythingelse': 'massive'
    }
    for attribute in size_mapping:
        size = size_mapping[attribute]
        object_def['attributes'] = [attribute]
        obj = instantiate_object(object_def, object_location)
        assert size in obj['info']


def test_check_same_and_different():
    a = {
        'type': 'ball',
        'color': 'blue',
        'size': 'tiny',
        'ignored': 'stuff'
    }
    b = {
        'type': 'ball',
        'color': 'red',
        'size': 'tiny',
        'ignored': 42
    }
    assert check_same_and_different(a, b, ('type', 'size'), ('color',)) is True
    assert check_same_and_different(a, b, ('type', 'color'), ('size',)) is False
    assert check_same_and_different(a, b, ('color', 'size'), ('type',)) is False


def test_get_similar_defs():
    original_def = objects.OBJECTS_PICKUPABLE_BALLS[0]
    obj = instantiate_object(original_def, geometry.ORIGIN)
    similar_defs = get_similar_defs(obj, objects.get_all_object_defs(), ('type', 'materialCategory'), ('mass',))
    for obj_def in similar_defs:
        obj_2 = instantiate_object(obj_def, geometry.ORIGIN)
        assert check_same_and_different(obj_2, obj, ('type', 'materialCategory'), ('mass',))


def test_instantiate_object_novel_color():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'novel_color': True,
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['goal_string'] == 'huge massive blue yellow sofa'
    assert obj['info'] == ['huge', 'massive', 'blue', 'yellow', 'sofa', 'novel blue', 'novel yellow']
    assert obj['info_string'] == '(novel color) huge massive blue yellow sofa'


def test_instantiate_object_novel_combination():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'novel_combination': True,
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['goal_string'] == 'huge massive blue yellow sofa'
    assert obj['info'] == ['huge', 'massive', 'blue', 'yellow', 'sofa', 'novel blue sofa', 'novel yellow sofa']
    assert obj['info_string'] == '(novel combination) huge massive blue yellow sofa'


def test_instantiate_object_novel_shape():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'novel_shape': True,
        'info': ['huge', 'sofa'],
        'mass': 12.34,
        'scale': 1.0,
        'attributes': [],
        'materialCategory': ['test']
    }
    object_location = {
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
    obj = instantiate_object(object_def, object_location)
    assert obj['goal_string'] == 'huge massive blue yellow sofa'
    assert obj['info'] == ['huge', 'massive', 'blue', 'yellow', 'sofa', 'novel sofa']
    assert obj['info_string'] == '(novel shape) huge massive blue yellow sofa'


