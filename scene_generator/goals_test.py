from goals import *
import operator
import pytest
import uuid


def test_instantiate_object():
    object_def = {
        'type': uuid.uuid4(),
        'info': [uuid.uuid4(), uuid.uuid4()],
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
    for prop in ('type', 'info', 'mass'):
        assert object_def[prop] == obj[prop]
    for attribute in object_def['attributes']:
        assert obj[attribute] is True
    assert obj['shows'][0]['position'] == object_location['position']
    assert obj['shows'][0]['rotation'] == object_location['rotation']


def test_RetrievalGoal_get_goal():
    goal_obj = RetrievalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
    }
    object_list = [obj]
    goal = goal_obj.get_config(object_list)
    assert goal['info_list'] == obj['info']
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == obj['info']


def test_TraversalGoal_get_goal():
    goal_obj = TraversalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
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
        'pickupable': True
    }
    other_id = str(uuid.uuid4())
    other_info_item = str(uuid.uuid4())
    other_obj = {
        'id': other_id,
        'info': [other_info_item, extra_info],
        'attributes': []
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
