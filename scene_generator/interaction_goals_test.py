import logging
import uuid

import math
import pytest
from machine_common_sense.mcs_controller_ai2thor import MAX_MOVE_DISTANCE

import geometry
import objects
from geometry import POSITION_DIGITS
from goals import *
from interaction_goals import move_to_container, parse_path_section, get_navigation_actions
from util import finalize_object_definition, instantiate_object


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
            'rotation': 315.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.1**2) / MAX_MOVE_DISTANCE, POSITION_DIGITS)
        }
    }]
    actions, new_heading, performer = parse_path_section(path_section, 0, (0, 0), [])
    assert actions == expected_actions


def test_parse_path_section_fractional():
    path_section = ((0, 0), (1, 0))
    goal_boundary = [{
        'x': 1.1,
        'y': 0,
        'z': 0.1
    }, {
        'x': 1.1,
        'y': 0,
        'z': -0.1
    }, {
        'x': 0.9,
        'y': 0,
        'z': -0.1
    }, {
        'x': 0.9,
        'y': 0,
        'z': 0.1
    }]
    expected_actions = [{
        'action': 'MoveAhead',
        'params': {}
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(0.4 / MAX_MOVE_DISTANCE, POSITION_DIGITS)
        }
    }]
    actions, new_heading, performer = parse_path_section(path_section, 0, (0, 0), goal_boundary)
    assert actions == expected_actions


def test_get_navigation_action():
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': 315.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.09**2) / MAX_MOVE_DISTANCE, POSITION_DIGITS)
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
        'id': 'goal',
        'shows': [{
            'position': {
                'x': 0.1,
                'y': 0.5,
                'z': 0.1
            },
            'bounding_box': [
                {
                    'x': 0.11,
                    'y': 0.5,
                    'z': 0.11
                },
                {
                    'x': 0.09,
                    'y': 0.5,
                    'z': 0.11
                },
                {
                    'x': 0.09,
                    'y': 0.5,
                    'z': 0.09
                },
                {
                    'x': 0.11,
                    'y': 0.5,
                    'z': 0.09
                },
            ]
        }]
    }
    actions = get_navigation_actions(start, goal_object, [goal_object])
    assert actions == expected_actions


def test_get_navigation_action_with_locationParent():
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': 315.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.09**2) / MAX_MOVE_DISTANCE, POSITION_DIGITS)
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
            },
            'bounding_box': [
                {
                    'x': 0.11,
                    'y': 0,
                    'z': 0.11
                },
                {
                    'x': 0.09,
                    'y': 0,
                    'z': 0.11
                },
                {
                    'x': 0.09,
                    'y': 0,
                    'z': 0.09
                },
                {
                    'x': 0.11,
                    'y': 0,
                    'z': 0.09
                },
            ]
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


def test_get_navigation_action_with_turning():
    """Test get_navigation_actions when you have to turn because of
    navigating around an obstacle:
                G

             ----------
             |        |
             ----------

                S

    (S is start, G is goal)
    """
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
    goal_obj = {
        'id': 'goal-01',
        'shows': [{
            'position': {
                'x': 0,
                'y': 0,
                'z': 3
            },
            'bounding_box': [
                {
                    'x': 0.1,
                    'y': 0,
                    'z': 3.1
                },
                {
                    'x': 0.1,
                    'y': 0,
                    'z': 2.9
                },
                {
                    'x': -0.1,
                    'y': 0,
                    'z': 2.9
                },
                {
                    'x': -0.1,
                    'y': 0,
                    'z': 3.1
                }
            ]
        }]
    }
    obstacle_obj = {
        'id': 'obstacle-01',
        'shows': [{
            'position': {
                'x': 1,
                'y': 0,
                'z': 1.5
            },
            'bounding_box': [
                {
                    'x': 2,
                    'y': 0,
                    'z': 2
                },
                {
                    'x': 2,
                    'y': 0,
                    'z': 1
                },
                {
                    'x': -1,
                    'y': 0,
                    'z': 1
                },
                {
                    'x': -1,
                    'y': 0,
                    'z': 2
                },
                
            ]
        }]
    }
    expected_actions = [{'action': 'RotateLook', 'params': {'rotation': 225.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': {}}, {'action': 'MoveAhead', 'params': {}},
                        {'action': 'MoveAhead', 'params': {'amount': 0.83}},
                        {'action': 'RotateLook', 'params': {'rotation': 45.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': {}}, {'action': 'MoveAhead', 'params': {}},
                        {'action': 'RotateLook', 'params': {'rotation': 45.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': {}}, {'action': 'MoveAhead', 'params': {}},
                        {'action': 'MoveAhead', 'params': {'amount': round((.9*math.sqrt(2)-1)/MAX_MOVE_DISTANCE, POSITION_DIGITS)}}]
    all_objs = [goal_obj, obstacle_obj]
    actions = get_navigation_actions(start, goal_obj, all_objs)
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


def test_add_RotateLook_to_action_list_before_Pickup_or_Put_Object():

    """For MCS-161"""
    # make scene with a small target object
    scene = {
        'name': 'mcs-161',
        'performerStart': {
            'position': {
                'x': 0,
                'y': 0,
                'z': 0
            },
            'rotation': {
                'y': 0
            }
        },
        'objects': [{
            'id': 'object-01',
            'type': 'sphere',
            'dimensions': {
                'x': 0.02,
                'y': 0.02,
                'z': 0.02
            },
            'shows': [{
                'position': {
                    'x': 0,
                    'y': 0,
                    'z': 2
                },
                'stepBegin': 0,
                'scale': {
                    'x': 0.02,
                    'y': 0.02,
                    'z': 0.02
                },
                'bounding_box': [
                    {
                        'x': 0.01,
                        'y': 0,
                        'z': 2.01,
                    },
                    {
                        'x': 0.01,
                        'y': 0,
                        'z': 1.99,
                    },
                    {
                        'x': -0.01,
                        'y': 0,
                        'z': 1.99,
                    },
                    {
                        'x': -0.01,
                        'y': 0,
                        'z': 2.01,
                    },
                ]
            }],
        }]
    }
    # check that path finding looks down at it

    goal_obj = RetrievalGoal()
    goal_obj._performer_start = scene['performerStart']
    path = goal_obj.find_optimal_path(scene['objects'], scene['objects'])
    print(path)
    # TODO: uncomment when this is fixed
    # assert path[-1]['action'] == 'RotateLook'
