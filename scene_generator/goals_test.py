from goals import *
import pytest
import uuid


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


def test_move_to_container():
    # find a tiny object so we know it will fit in *something*
    for obj_def in objects.OBJECTS_PICKUPABLE:
        obj_def = finalize_object_definition(obj_def)
        if 'tiny' in obj_def['info']:
            obj = instantiate_object(obj_def, geometry.ORIGIN_LOCATION)
            all_objects = [obj]
            tries = 0
            while tries < 100:
                if move_to_container(obj, all_objects, [], geometry.ORIGIN):
                    break
                tries += 1
            if tries == 100:
                logging.error('could not put the object in any container')
            container_id = all_objects[1]['id']
            assert obj['locationParent'] == container_id
            return
    assert False, 'could not find a tiny object'


def test_RetrievalGoal_get_goal():
    goal_obj = RetrievalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
        'type': 'sphere'
    }
    object_list = [obj]
    goal = goal_obj.get_config(object_list)
    assert goal['info_list'] == obj['info']
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == obj['info']


def test_Goal_duplicate_object():
    goal_obj = RetrievalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
        'type': 'sphere',
        "info": ["tiny", "ball"],
        "choose": [{
            "mass": 0.25,
            "materialCategory": ["plastic"],
            "salientMaterials": ["plastic", "hollow"]
        }, {
            "mass": 0.5625,
            "materialCategory": ["rubber"],
            "salientMaterials": ["rubber"]
        }, {
            "mass": 0.5625,
            "materialCategory": ["block_blank"],
            "salientMaterials": ["wood"]
        }, {
            "mass": 0.5625,
            "materialCategory": ["wood"],
            "salientMaterials": ["wood"]
        }, {
            "mass": 1,
            "materialCategory": ["metal"],
            "salientMaterials": ["metal"]
        }],
        "attributes": ["moveable", "pickupable"],
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "position_y": 0.05,
        "scale": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        }
    }
    sphere = instantiate_object(obj, {})
    object_list = [obj]
    bounding_rect = [[{'x': 3.7346446609406727, 'y': 0, 'z': 4.23}, {'x': 3.77, 'y': 0, 'z': 4.265355339059328}, {'x': 3.8053553390593273, 'y': 0, 'z': 4.23}, {'x': 3.77, 'y': 0, 'z': 4.194644660940673}], [{'x': 3.846, 'y': 0, 'z': -1.9685000000000001}, {'x': 3.846, 'y': 0, 'z': -2.4715000000000003}, {'x': 3.1340000000000003, 'y': 0, 'z': -2.4715000000000003}, {'x': 3.1340000000000003, 'y': 0, 'z': -1.9685000000000001}]]
    performer_position = {'x': 0.77, 'y': 0, 'z': -0.41}
    goal = goal_obj.get_config(object_list)
    foo = goal_obj.add_objects([sphere], bounding_rect, performer_position)
    assert foo is None


def test_TraversalGoal_get_goal():
    goal_obj = TraversalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
        'type': 'sphere'
    }
    object_list = [obj]
    goal = goal_obj.get_config(object_list)
    assert goal['info_list'] == obj['info']
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == obj['info']


def test_TransferralGoal_get_goal_argcount():
    goal_obj = TransferralGoal()
    with pytest.raises(ValueError):
        goal_obj.get_config(['one object'])


def test_TransferralGoal_get_goal_argvalid():
    goal_obj = TransferralGoal()
    with pytest.raises(ValueError):
        goal_obj.get_config([{'attributes': ['']}, {'attributes': ['']}])


def test__generate_transferral_goal():
    goal_obj = TransferralGoal()
    extra_info = str(uuid.uuid4())
    pickupable_id = str(uuid.uuid4())
    pickupable_info_item = str(uuid.uuid4())
    pickupable_obj = {
        'id': pickupable_id,
        'info': [pickupable_info_item, extra_info],
        'pickupable': True,
        'type': 'sphere'
    }
    other_id = str(uuid.uuid4())
    other_info_item = str(uuid.uuid4())
    other_obj = {
        'id': other_id,
        'info': [other_info_item, extra_info],
        'attributes': [],
        'type': 'changing_table'
    }
    goal = goal_obj.get_config([pickupable_obj, other_obj])

    combined_info = goal['info_list']
    assert set(combined_info) == {pickupable_info_item, other_info_item, extra_info}

    target1 = goal['metadata']['target_1']
    assert target1['id'] == pickupable_id
    assert target1['info'] == [pickupable_info_item, extra_info]
    target2 = goal['metadata']['target_2']
    assert target2['id'] == other_id
    assert target2['info'] == [other_info_item, extra_info]

    relationship = goal['metadata']['relationship']
    relationship_type = relationship[1]
    assert relationship_type in [g.value for g in TransferralGoal.RelationshipType]
