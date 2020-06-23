import uuid

import geometry
import materials
import objects
from goals import *
from util import finalize_object_definition, instantiate_object, check_same_and_different, get_similar_defs


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
        'type': str(uuid.uuid4()),
        'info': [str(uuid.uuid4()), str(uuid.uuid4())],
        'mass': random.random(),
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
    for prop in ('type', 'mass'):
        assert object_def[prop] == obj[prop]
    for attribute in object_def['attributes']:
        assert obj[attribute] is True
    assert obj['shows'][0]['position'] == object_location['position']
    assert obj['shows'][0]['rotation'] == object_location['rotation']


def test_instantiate_object_offset():
    offset = {
        'x': random.random(),
        'z': random.random()
    }
    object_def = {
        'type': str(uuid.uuid4()),
        'info': [str(uuid.uuid4()), str(uuid.uuid4())],
        'mass': random.random(),
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
    material_category = ['plastic']
    materials_list = materials.PLASTIC_MATERIALS
    object_def = {
        'type': str(uuid.uuid4()),
        'info': [str(uuid.uuid4()), str(uuid.uuid4())],
        'mass': random.random(),
        'scale': 1.0,
        'attributes': [],
        'materialCategory': material_category
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
    assert obj['materials'][0] in (mat[0] for mat in materials_list)


def test_instantiate_object_salient_materials():
    salient_materials = ["plastic", "hollow"]
    object_def = {
        'type': str(uuid.uuid4()),
        'info': [str(uuid.uuid4()), str(uuid.uuid4())],
        'mass': random.random(),
        'scale': 1.0,
        'attributes': [],
        'salientMaterials': salient_materials
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
    assert obj['salientMaterials'] == salient_materials
    for sm in salient_materials:
        assert sm in obj['info']


def test_instantiate_object_size():
    object_def = {
        'type': str(uuid.uuid4()),
        'info': [str(uuid.uuid4()), str(uuid.uuid4())],
        'mass': random.random(),
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
    similar_defs = get_similar_defs(obj, ('type', 'materialCategory'), ('mass',))
    for obj_def in similar_defs:
        assert check_same_and_different(obj_def, obj, ('type', 'materialCategory'), ('mass',))

