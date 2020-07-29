import uuid

import geometry
import materials
import objects
from goals import *
from util import finalize_object_definition, instantiate_object, check_same_and_different, get_similar_defs, \
        random_real, move_to_location, retrieve_full_object_definition_list


PACIFIER = {
    "type": "pacifier",
    "color": "blue",
    "shape": "pacifier",
    "size": "tiny",
    "salientMaterials": ["plastic"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.07,
        "y": 0.04,
        "z": 0.05
    },
    "mass": 0.125,
    "offset": {
        "x": 0,
        "y": 0.02,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


def test_random_real():
    n = random_real(0, 1, 0.1)
    assert 0 <= n <= 1
    # need to multiply by 10 and mod by 1 instead of 0.1 to avoid weird roundoff
    assert n * 10 % 1 < 1e-8


def test_finalize_object_definition():
    dimensions = {'x': 1, 'y': 1, 'z': 1}
    mass = 12.34
    material_category = ['plastic']
    salient_materials = ['plastic', 'hollow']
    object_def = {
        'type': 'type1',
        'mass': 56.78,
        'chooseMaterial': [{
            'materialCategory': material_category,
            'salientMaterials': salient_materials
        }],
        'chooseSize': [{
            'dimensions': dimensions,
            'mass': mass
        }]
    }
    obj = finalize_object_definition(object_def)
    assert obj['dimensions'] == dimensions
    assert obj['mass'] == mass
    assert obj['materialCategory'] == material_category
    assert obj['salientMaterials'] == salient_materials


def test_instantiate_object():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'attributes': ['foo', 'bar'],
        'scale': {'x': 1, 'y': 1, 'z': 1}
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
    assert obj['dimensions'] == object_def['dimensions']
    assert obj['goal_string'] == 'huge massive sofa'
    assert obj['info'] == ['huge', 'massive', 'sofa']
    assert obj['mass'] == 12.34
    assert obj['novelColor'] is False
    assert obj['novelCombination'] is False
    assert obj['novelShape'] is False
    assert obj['shape'] == ['sofa']
    assert obj['size'] == 'huge'
    assert obj['foo'] is True
    assert obj['bar'] is True
    assert obj['shows'][0]['stepBegin'] == 0
    assert obj['shows'][0]['position'] == object_location['position']
    assert obj['shows'][0]['rotation'] == object_location['rotation']
    assert obj['shows'][0]['scale'] == object_def['scale']


def test_instantiate_object_choose():
    object_def = {
        'type': 'sofa_1',
        'chooseSize': [{
            'novelShape': True,
            'shape': 'sofa',
            'size': 'medium',
            'attributes': ['moveable'],
            'dimensions': {'x': 0.5, 'y': 0.25, 'z': 0.25},
            'mass': 12.34,
            'scale': {'x': 0.5, 'y': 0.5, 'z': 0.5}
        }, {
            'shape': 'sofa',
            'size': 'huge',
            'attributes': [],
            'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
            'mass': 56.78,
            'scale': {'x': 1, 'y': 1, 'z': 1}
        }]
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
    assert obj['size'] == 'medium' or obj['size'] == 'huge'
    if obj['size'] == 'medium':
        assert obj['moveable']
        assert obj['novelShape']
        assert obj['info'] == ['medium', 'heavy', 'sofa', 'novel sofa']
        assert obj['goal_string'] == 'medium heavy sofa'
        assert obj['dimensions'] == {'x': 0.5, 'y': 0.25, 'z': 0.25}
        assert obj['mass'] == 12.34
        assert obj['shows'][0]['scale'] == {'x': 0.5, 'y': 0.5, 'z': 0.5}
    if obj['size'] == 'huge':
        assert 'moveable' not in obj
        assert not obj['novelShape']
        assert obj['info'] == ['huge', 'massive', 'sofa']
        assert obj['goal_string'] == 'huge massive sofa'
        assert obj['dimensions'] == {'x': 1, 'y': 0.5, 'z': 0.5}
        assert obj['mass'] == 56.78
        assert obj['shows'][0]['scale'] == {'x': 1, 'y': 1, 'z': 1}


def test_instantiate_object_heavy_moveable():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'attributes': ['moveable'],
        'scale': {'x': 1, 'y': 1, 'z': 1}
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
    assert obj['moveable'] is True


def test_instantiate_object_light_pickupable():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'attributes': ['moveable', 'pickupable'],
        'scale': {'x': 1, 'y': 1, 'z': 1}
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
    assert obj['moveable'] is True
    assert obj['pickupable'] is True


def test_instantiate_object_offset():
    offset = {
        'x': random.random(),
        'z': random.random()
    }
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
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


def test_instantiate_object_rotation():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
        'attributes': [],
        'rotation': {'x': 1, 'y': 2, 'z': 3}
    }
    object_location = {
        'position': {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0
        },
        'rotation': {
            'x': 30.0,
            'y': 60.0,
            'z': 90.0
        }
    }
    obj = instantiate_object(object_def, object_location)
    assert obj['shows'][0]['rotation'] == {'x': 31.0, 'y': 62.0, 'z': 93.0}


def test_instantiate_object_materials():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
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
    assert obj['color'] == ['blue', 'yellow']
    assert obj['goal_string'] == 'huge massive blue yellow sofa'
    assert obj['info'] == ['huge', 'massive', 'blue', 'yellow', 'sofa']


def test_instantiate_object_multiple_materials():
    materials.TEST1_MATERIALS = [('test_material_1', ['blue'])]
    materials.TEST2_MATERIALS = [('test_material_2', ['yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
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
    assert obj['color'] == ['blue', 'yellow']
    assert obj['goal_string'] == 'huge massive blue yellow sofa'
    assert obj['info'] == ['huge', 'massive', 'blue', 'yellow', 'sofa']


def test_instantiate_object_salient_materials():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
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


def test_instantiate_object_size():
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'shape': 'sofa',
        'size': 'huge',
        'mass': 12.34,
        'scale': {'x': 1, 'y': 1, 'z': 1},
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
        'shape': 'ball',
        'color': 'blue',
        'size': 'tiny',
        'ignore': 'prop'
    }
    b = {
        'shape': 'ball',
        'color': 'yellow',
        'size': 'tiny',
        'ignore': 42
    }
    assert check_same_and_different(a, b, [], []) is True
    assert check_same_and_different(a, b, ('shape', 'size'), ('color',)) is True
    assert check_same_and_different(a, b, ('shape', 'color'), ('size',)) is False
    assert check_same_and_different(a, b, ('color', 'size'), ('shape',)) is False


def test_check_same_and_different_with_list():
    a = {
        'shape': ['ball'],
        'color': ['blue'],
        'size': 'tiny',
        'ignore': 'prop'
    }
    b = {
        'shape': ['ball'],
        'color': ['yellow'],
        'size': 'tiny',
        'ignore': 42
    }
    assert check_same_and_different(a, b, ('shape'), ('color',)) is True
    assert check_same_and_different(a, b, ('color'), ('shape',)) is False


def test_check_same_and_different_with_dimensions():
    object_1 = {
        'id': 'object_1',
        'shape': 'ball',
        'color': 'blue',
        'dimensions': {'x': 1, 'y': 1, 'z': 1},
        'size': 'medium'
    }
    object_2 = {
        'id': 'object_2',
        'shape': 'ball',
        'color': 'blue',
        'dimensions': {'x': 1, 'y': 1, 'z': 1},
        'size': 'medium'
    }
    object_3 = {
        'id': 'object_3',
        'shape': 'ball',
        'color': 'blue',
        'dimensions': {'x': 1.1, 'y': 1.1, 'z': 1.1},
        'size': 'medium'
    }
    object_4 = {
        'id': 'object_4',
        'shape': 'ball',
        'color': 'blue',
        'dimensions': {'x': 0.9, 'y': 0.9, 'z': 0.9},
        'size': 'medium'
    }
    object_5 = {
        'id': 'object_5',
        'shape': 'ball',
        'color': 'blue',
        'dimensions': {'x': 1.2, 'y': 1.2, 'z': 1.2},
        'size': 'medium'
    }
    object_6 = {
        'id': 'object_6',
        'shape': 'ball',
        'color': 'blue',
        'dimensions': {'x': 0.8, 'y': 0.8, 'z': 0.8},
        'size': 'medium'
    }
    assert check_same_and_different(object_1, object_2, ('shape','dimensions'), ('id',)) is True
    assert check_same_and_different(object_1, object_3, ('shape','dimensions'), ('id',)) is True
    assert check_same_and_different(object_1, object_4, ('shape','dimensions'), ('id',)) is True
    assert check_same_and_different(object_1, object_5, ('shape','dimensions'), ('id',)) is False
    assert check_same_and_different(object_1, object_6, ('shape','dimensions'), ('id',)) is False
    assert check_same_and_different(object_1, object_2, ('shape',), ('id','dimensions')) is False
    assert check_same_and_different(object_1, object_3, ('shape',), ('id','dimensions')) is False
    assert check_same_and_different(object_1, object_4, ('shape',), ('id','dimensions')) is False
    assert check_same_and_different(object_1, object_5, ('shape',), ('id','dimensions')) is True
    assert check_same_and_different(object_1, object_6, ('shape',), ('id','dimensions')) is True


def test_check_same_and_different_pacifier():
    assert check_same_and_different(PACIFIER, PACIFIER, ('shape', 'dimensions'), ('materialCategory',)) is False
    assert check_same_and_different(PACIFIER, PACIFIER, ('shape', 'materialCategory'), ('dimensions',)) is False
    assert check_same_and_different(PACIFIER, PACIFIER, ('dimensions', 'materialCategory'), ('shape',)) is False


def test_get_similar_defs_color():
    object_definition_list = retrieve_full_object_definition_list(objects.get_all_object_defs())
    for object_definition in object_definition_list:
        object_instance = instantiate_object(object_definition, geometry.ORIGIN_LOCATION)
        similar_list = get_similar_defs(object_instance, object_definition_list, ('dimensions', 'shape'), ('color',))
        for similar_definition in similar_list:
            similar_instance = instantiate_object(similar_definition, geometry.ORIGIN_LOCATION)
            assert check_same_and_different(similar_instance, object_instance, ('dimensions', 'shape'), ('color',))


def test_get_similar_defs_shape():
    object_definition_list = retrieve_full_object_definition_list(objects.get_all_object_defs())
    for object_definition in object_definition_list:
        object_instance = instantiate_object(object_definition, geometry.ORIGIN_LOCATION)
        similar_list = get_similar_defs(object_instance, object_definition_list, ('color', 'dimensions'), ('shape',))
        for similar_definition in similar_list:
            similar_instance = instantiate_object(similar_definition, geometry.ORIGIN_LOCATION)
            assert check_same_and_different(similar_instance, object_instance, ('color', 'dimensions'), ('shape',))


def test_get_similar_defs_size():
    object_definition_list = retrieve_full_object_definition_list(objects.get_all_object_defs())
    for object_definition in object_definition_list:
        object_instance = instantiate_object(object_definition, geometry.ORIGIN_LOCATION)
        similar_list = get_similar_defs(object_instance, object_definition_list, ('color', 'shape'), ('dimensions',))
        for similar_definition in similar_list:
            similar_instance = instantiate_object(similar_definition, geometry.ORIGIN_LOCATION)
            assert check_same_and_different(similar_instance, object_instance, ('color', 'shape'), ('dimensions',))


def test_instantiate_object_novel_color():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'novelColor': True,
        'shape': 'sofa',
        'size': 'huge',
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


def test_instantiate_object_novel_combination():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'novelCombination': True,
        'shape': 'sofa',
        'size': 'huge',
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


def test_instantiate_object_novel_shape():
    materials.TEST_MATERIALS = [('test_material', ['blue', 'yellow'])]
    object_def = {
        'type': 'sofa_1',
        'dimensions': {'x': 1, 'y': 0.5, 'z': 0.5},
        'novelShape': True,
        'shape': 'sofa',
        'size': 'huge',
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


def test_move_to_location():
    instance = {'shows': [{'position': {'x': -1, 'y': 0, 'z': -1}, 'rotation': {'x': 0, 'y': 90, 'z': 0}}]}
    location = {
        'position': {'x': 2, 'y': 0, 'z': 2},
        'rotation': {'x': 0, 'y': 0, 'z': 0},
        'bounding_box': [{'x': 3, 'z': 3}, {'x': 3, 'z': 1}, {'x': 1, 'z': 1}, {'x': 1, 'z': 3}]
    }
    actual = move_to_location({}, instance, location)
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 2, 'y': 0, 'z': 2}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['bounding_box'] == [{'x': 3, 'z': 3}, {'x': 3, 'z': 1}, {'x': 1, 'z': 1}, \
            {'x': 1, 'z': 3}]

    definition = {'offset': {'x': 0.1, 'z': -0.5}}
    actual = move_to_location(definition, instance, location)
    assert actual == instance
    assert instance['shows'][0]['position'] == {'x': 1.9, 'y': 0, 'z': 2.5}
    assert instance['shows'][0]['rotation'] == {'x': 0, 'y': 0, 'z': 0}
    assert instance['shows'][0]['bounding_box'] == [{'x': 3, 'z': 3}, {'x': 3, 'z': 1}, {'x': 1, 'z': 1}, \
            {'x': 1, 'z': 3}]


def test_retrieve_full_object_definition_list():
    list_1 = [{ 'type': 'ball', 'mass': 1 }]
    actual_1 = retrieve_full_object_definition_list(list_1)
    assert len(actual_1) == 1

    list_2 = [{ 'type': 'ball', 'chooseSize': [{ 'mass': 1 }, { 'mass': 2 }] }]
    actual_2 = retrieve_full_object_definition_list(list_2)
    assert len(actual_2) == 2

    list_3 = [
        { 'type': 'sofa' },
        { 'type': 'ball', 'chooseSize': [{ 'mass': 1 }, { 'mass': 2 }] }
    ]
    actual_3 = retrieve_full_object_definition_list(list_3)
    assert len(actual_3) == 3

    list_4 = [
        { 'type': 'sofa', 'chooseSize': [{ 'mass': 1 }, { 'mass': 3 }] },
        { 'type': 'ball', 'chooseSize': [{ 'mass': 1 }, { 'mass': 2 }] }
    ]
    actual_4 = retrieve_full_object_definition_list(list_4)
    assert len(actual_4) == 4

