import logging
import uuid

import math
from typing import Dict, Any

import pytest
from machine_common_sense.mcs_controller_ai2thor import MAX_MOVE_DISTANCE

import geometry
import objects
from geometry import POSITION_DIGITS
from goals import *
from interaction_goals import move_to_container, parse_path_section, get_navigation_actions, set_enclosed_info, \
    InteractionGoal
from util import finalize_object_definition, instantiate_object


def test_set_enclosed_info():
    goal = { 'type_list': [] }
    targets = [{}, {'locationParent': 'bogus'}]
    set_enclosed_info(goal, *targets)
    enclosed_info = set(goal['type_list'])
    assert enclosed_info == {'target_not_enclosed', 'target_enclosed'}


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


def test_parse_path_section():
    path_section = ((0, 0), (0.1, 0.1))
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': -45.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.1**2) / MAX_MOVE_DISTANCE, POSITION_DIGITS)
        }
    }]
    actions, new_heading = parse_path_section(path_section, 0)
    assert actions == expected_actions


def test_get_navigation_action():
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': -45.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.1**2) / MAX_MOVE_DISTANCE, POSITION_DIGITS)
        }
    }]
    start = {
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'y': 0
        }
    }
    goal_object = {
        'shows': [{
            'position': {
                'x': 0.1,
                'y': 0,
                'z': 0.1
            }
        }]
    }
    actions = get_navigation_actions(start, goal_object, [])
    assert actions == expected_actions
    
    
def test_get_navigation_action_with_locationParent():
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': -45.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.1**2) / MAX_MOVE_DISTANCE, POSITION_DIGITS)
        }
    }]
    start = {
        'position': {
            'x': 0,
            'y': 0,
            'z': 0
        },
        'rotation': {
            'y': 0
        }
    }
    container_object = {
        'id': 'container1',
        'shows': [{
            'position': {
                'x': 0.1,
                'y': 0,
                'z': 0.1
            }
        }]
    }
    goal_object = {
        'id': 'object1',
        'locationParent': 'container1',
        'shows': [{
            'position': {
                'x': -0.1,
                'y': 0,
                'z': 0
            }
        }]
    }
    actions = get_navigation_actions(start, goal_object, [container_object, goal_object])
    assert actions == expected_actions
    
    
def test_RetrievalGoal_get_goal():
    goal_obj = RetrievalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
        'type': 'sphere'
    }
    object_list = [obj]
    goal = goal_obj.get_config(object_list, object_list)
    assert goal['info_list'] == obj['info']
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == obj['info']


def test_TraversalGoal_get_goal():
    goal_obj = TraversalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': [str(uuid.uuid4())],
        'type': 'sphere'
    }
    object_list = [obj]
    goal = goal_obj.get_config(object_list, object_list)
    assert goal['info_list'] == obj['info']
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == obj['info']


def test_TransferralGoal_get_goal_argcount():
    goal_obj = TransferralGoal()
    with pytest.raises(ValueError):
        goal_obj.get_config(['one object'], ['one object'])


def test_TransferralGoal_get_goal_argvalid():
    goal_obj = TransferralGoal()
    with pytest.raises(ValueError):
        goal_obj.get_config([{'attributes': ['']}, {'attributes': ['']}], [])


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
        'type': 'changing_table',
        'stackTarget': True
    }
    obj_list = [pickupable_obj, other_obj]
    goal = goal_obj.get_config(obj_list, obj_list)

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


def test__generate_transferral_goal_with_nonstackable_goal():
    goal_obj = TransferralGoal()
    extra_info = str(uuid.uuid4())
    pickupable_id = str(uuid.uuid4())
    pickupable_info_item = str(uuid.uuid4())
    pickupable_obj = {
        'id': pickupable_id,
        'info': [pickupable_info_item, extra_info],
        'pickupable': True,
        'type': 'sphere',
        'attributes': ['pickupable']
    }
    other_id = str(uuid.uuid4())
    other_info_item = str(uuid.uuid4())
    other_obj = {
        'id': other_id,
        'info': [other_info_item, extra_info],
        'type': 'changing_table',
        'attributes': []
    }
    with pytest.raises(ValueError) as excinfo:
        goal = goal_obj.get_config([pickupable_obj, other_obj], [])
    assert "second object must be" in str(excinfo.value)


class DummyInteractionGoal(InteractionGoal):
    def find_optimal_path(self, goal_objects: List[Dict[str, Any]], all_objects: List[Dict[str, Any]]) -> \
            List[Dict[str, Any]]:
        return []


def test_InteractionGoal__set_target_def():
    goal_obj = DummyInteractionGoal()
    goal_obj._set_target_def()
    assert 'pickupable' in goal_obj._target_def['attributes']


def test_InteractionGoal__set_target_location():
    goal_obj = DummyInteractionGoal()
    goal_obj._set_performer_start()
    goal_obj._set_target_def()
    goal_obj._set_target_location()
    assert goal_obj._target_location is not None


def test_InteractionGoal_compute_objects():
    goal_obj = DummyInteractionGoal()
    goal_objs, objs, rects = goal_obj.compute_objects('dummy wall material')
    assert len(goal_objs) == 1
    assert len(objs) >= 1
    assert len(rects) >= 1
    assert len(objs) == len(rects)


def test_RetrievalGoal_get_config():
    goal_obj = RetrievalGoal()
    goal_obj._set_performer_start()
    goal_obj._set_target_def()
    goal_obj._set_target_location()
    target = instantiate_object(goal_obj._target_def, goal_obj._target_location)
    goal_objs = [target]
    all_objs = [target]
    config = goal_obj.get_config(goal_objs, all_objs)
    metadata = config['metadata']
    assert metadata['target']['id'] == target['id']
    assert metadata['target']['info'] == target['info']


def test_TransferralGoal__set_goal_objects():
    goal_obj = TransferralGoal()
    goal_obj._set_performer_start()
    goal_obj._set_goal_objects()
    assert len(goal_obj._goal_objects) == 1


def test_TransferralGoal_get_config():
    goal_obj = TransferralGoal()
    goal_objects, all_objects, bounding_rects = goal_obj.compute_objects('dummy material')
    config = goal_obj.get_config(goal_objects, all_objects)
    metadata = config['metadata']
    assert 'target_1' in metadata
    assert 'target_2' in metadata
    assert 'relationship' in metadata


def test_TransferralGoal_find_optimal_path():
    goal_obj = TransferralGoal()
    goal_objects, all_objects, bounding_rects = goal_obj.compute_objects('dummy material')
    actions = goal_obj.find_optimal_path(goal_objects, all_objects)
    pickup_action = next((action for action in actions if action['action'] == 'PickupObject'))
    assert pickup_action is not None
    assert actions[-1]['action'] == 'PutObject'


def test_TraversalGoal_compute_objects():
    goal_obj = TraversalGoal()
    goal_objects, all_objects, rects = goal_obj.compute_objects('dummy material')
    assert len(goal_objects) == 1
    assert len(all_objects) >= 1
    assert goal_objects[0] in all_objects


def test_TraversalGoal_get_config():
    goal_obj = TraversalGoal()
    goal_objects, all_objects, rects = goal_obj.compute_objects('dummy material')
    config = goal_obj.get_config(goal_objects, all_objects)
    target = goal_objects[0]
    metadata = config['metadata']
    assert metadata['target']['id'] == target['id']
    assert metadata['target']['info'] == target['info']
