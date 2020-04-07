from goals import *
import operator
import pytest
import uuid


def test_AttributeConstraint():
    equality_ac = AttributeConstraint(operator.eq, 'the answer', 42)
    obj = {'the answer': 42}
    assert equality_ac.is_true(obj)

    contains_ac = AttributeConstraint(list.__contains__, 'best color', 'red')
    obj = {'best color': ['green', 'red']}
    assert contains_ac.is_true(obj)


def test_IdGoal_get_goal():
    goal_obj = IdGoal()
    obj = {
        'id': uuid.uuid4(),
        'info': [uuid.uuid4()],
    }
    object_list = [obj]
    goal = goal_obj.get_config(object_list)
    assert goal['info_list'] == obj['info']
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == obj['info']


def test_TransportationGoal_get_goal_argcount():
    goal_obj = TransportationGoal()
    with pytest.raises(ValueError):
        goal_obj.get_config(['one object'])


def test_TransportationGoal_get_goal_argvalid():
    goal_obj = TransportationGoal()
    with pytest.raises(ValueError):
        goal_obj.get_config([{'attributes': ['']}, {'attributes': ['']}])


def test__generate_transportation_goal():
    goal_obj = TransportationGoal()
    extra_info = uuid.uuid4()
    pickupable_id = uuid.uuid4()
    pickupable_info_item = uuid.uuid4()
    pickupable_obj = {
        'id': pickupable_id,
        'info': [pickupable_info_item, extra_info],
        'attributes': ['pickupable']
    }
    other_id = uuid.uuid4()
    other_info_item = uuid.uuid4()
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
    assert relationship_type in [g.value for g in TransportationGoal.RelationshipType]
