import uuid
import goals
import pytest


def test__generate_id_goal():
    obj = {
        'id': uuid.uuid4(),
        'info': [uuid.uuid4()],
    }
    object_list = [ obj ]
    goal = goals._generate_id_goal(object_list)
    assert goal['info_list'] == obj['info']
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == obj['info']


def test__generate_transportation_goal_argcount():
    with pytest.raises(ValueError):
        goals._generate_transportation_goal(['one object'])


def test__generate_transportation_goal_argvalid():
    with pytest.raises(ValueError):
        goals._generate_transportation_goal([{'attributes': ['']},
                                             {'attributes': ['']}])


def test__generate_transportation_goal():
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
    goal = goals._generate_transportation_goal([pickupable_obj, other_obj])
    
    combined_info = goal['info_list']
    assert set(combined_info) == {pickupable_info_item, other_info_item, extra_info}
    
    target1 = goal['metadata']['target_1']
    assert target1['id'] == pickupable_id
    assert target1['info'] == [ pickupable_info_item, extra_info ]
    target2 = goal['metadata']['target_2']
    assert target2['id'] == other_id
    assert target2['info'] == [ other_info_item, extra_info ]

    relationship = goal['metadata']['relationship']
    relationship_type = relationship[0]
    assert relationship_type in [g.value for g in goals.RelationshipType]