import logging
import uuid

import math
from typing import Dict, Any

import pytest

from machine_common_sense.mcs_controller_ai2thor import MAX_MOVE_DISTANCE, MAX_REACH_DISTANCE

import exceptions
import geometry
import objects
import scene_generator
from geometry import POSITION_DIGITS
from goals import *
from interaction_goals import move_to_container, parse_path_section, get_navigation_actions, trim_actions_to_reach, \
        PathfindingException
from util import MAX_TRIES, finalize_object_definition, instantiate_object


def test_move_to_container():
    # find a tiny object so we know it will fit in *something*
    for obj_def in objects.OBJECTS_PICKUPABLE:
        obj_def = finalize_object_definition(obj_def)
        if 'tiny' in obj_def['info']:
            obj = instantiate_object(obj_def, geometry.ORIGIN_LOCATION)
            tries = 0
            while tries < 100:
                container = move_to_container(obj, [], geometry.ORIGIN)
                if container:
                    break
                tries += 1
            if tries == 100:
                logging.error('could not put the object in any container')
            assert obj['locationParent'] == container['id']
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
        'params': {
            'amount': 1
        }
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
            'rotation': 45.0,
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
    actions, performer, heading = get_navigation_actions(start, goal_object, [goal_object])
    assert actions == expected_actions


def test_get_navigation_action_with_locationParent():
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': 45.0,
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
    actions, performer, heading = get_navigation_actions(start, goal_object, [container_object, goal_object])
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
    expected_actions = [{'action': 'RotateLook', 'params': {'rotation': 315.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': { 'amount': 1 }},
                        {'action': 'MoveAhead', 'params': { 'amount': 1 }},
                        {'action': 'MoveAhead', 'params': {'amount': 0.83}},
                        {'action': 'RotateLook', 'params': {'rotation': 45.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': { 'amount': 1 }},
                        {'action': 'MoveAhead', 'params': { 'amount': 1 }},
                        {'action': 'RotateLook', 'params': {'rotation': 45.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': { 'amount': 1 }},
                        {'action': 'MoveAhead', 'params': { 'amount': 1 }},
                        {'action': 'MoveAhead', 'params': {'amount': round((.9*math.sqrt(2)-1)/MAX_MOVE_DISTANCE, POSITION_DIGITS)}}]
    all_objs = [goal_obj, obstacle_obj]
    actions, performer, heading = get_navigation_actions(start, goal_obj, all_objs)
    assert actions == expected_actions


def test_trim_actions_to_reach():
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
        'params': {
            'amount': 1
        }
    }]
    actions, new_heading, performer = parse_path_section(path_section, 0, (0, 0), goal_boundary)
    target = {
        'shows': [{
            'position': {
                'x': 1,
                'y': 0,
                'z': 0
            }
        }]
    }
    actions, performer = trim_actions_to_reach(actions, performer, new_heading, target)
    assert actions == expected_actions


def test_RetrievalGoal_get_goal():
    goal_obj = RetrievalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': ['blue', 'rubber', 'ball'],
        'info_string': 'blue rubber ball',
        'type': 'sphere'
    }
    goal = goal_obj.get_config({ 'target': [obj] })
    assert goal['description'] == 'Find and pick up the blue rubber ball.'
    assert set(goal['info_list']) == {'target blue', 'target rubber', 'target ball', 'target blue rubber ball'}
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == ['blue', 'rubber', 'ball']


def test_TraversalGoal_get_goal():
    goal_obj = TraversalGoal()
    obj = {
        'id': str(uuid.uuid4()),
        'info': ['blue', 'rubber', 'ball'],
        'info_string': 'blue rubber ball',
        'type': 'sphere'
    }
    goal = goal_obj.get_config({ 'target': [obj] })
    assert goal['description'] == 'Find the blue rubber ball and move near it.'
    assert set(goal['info_list']) == {'target blue', 'target rubber', 'target ball', 'target blue rubber ball'}
    target = goal['metadata']['target']
    assert target['id'] == obj['id']
    assert target['info'] == ['blue', 'rubber', 'ball']


def test_TransferralGoal_get_goal_argcount():
    goal_obj = TransferralGoal()
    with pytest.raises(exceptions.SceneException):
        goal_obj.get_config({ 'target': ['one object'] })


def test_TransferralGoal_get_goal_argvalid():
    goal_obj = TransferralGoal()
    target_list = [{'attributes': ['']}, {'attributes': ['']}]
    with pytest.raises(exceptions.SceneException):
        goal_obj.get_config({ 'target': target_list })


def test__generate_transferral_goal():
    goal_obj = TransferralGoal()
    pickupable_id = str(uuid.uuid4())
    pickupable_obj = {
        'id': pickupable_id,
        'info': ['blue', 'rubber', 'ball'],
        'info_string': 'blue rubber ball',
        'pickupable': True,
        'type': 'sphere'
    }
    other_id = str(uuid.uuid4())
    other_obj = {
        'id': other_id,
        'info': ['yellow', 'wood', 'changing table'],
        'info_string': 'yellow wood changing table',
        'attributes': [],
        'type': 'changing_table',
        'stackTarget': True
    }
    goal = goal_obj.get_config({ 'target': [pickupable_obj, other_obj] })

    assert set(goal['info_list']) == {'target blue', 'target rubber', 'target ball', 'target blue rubber ball', \
            'target yellow', 'target wood', 'target changing table', 'target yellow wood changing table'}

    target1 = goal['metadata']['target_1']
    assert target1['id'] == pickupable_id
    assert target1['info'] == ['blue', 'rubber', 'ball']
    target2 = goal['metadata']['target_2']
    assert target2['id'] == other_id
    assert target2['info'] == ['yellow', 'wood', 'changing table']

    relationship = goal['metadata']['relationship']
    relationship_type = relationship[1]
    assert relationship_type in [g.value for g in TransferralGoal.RelationshipType]

    assert goal['description'] == 'Find and pick up the blue rubber ball and move it ' + \
            relationship_type + ' the yellow wood changing table.'


def test__generate_transferral_goal_with_nonstackable_goal():
    goal_obj = TransferralGoal()
    pickupable_id = str(uuid.uuid4())
    pickupable_obj = {
        'id': pickupable_id,
        'info': ['blue', 'rubber', 'ball'],
        'info_string': 'blue rubber ball',
        'pickupable': True,
        'type': 'sphere',
        'attributes': ['pickupable']
    }
    other_id = str(uuid.uuid4())
    other_obj = {
        'id': other_id,
        'info': ['yellow', 'wood', 'changing table'],
        'info_string': 'yellow wood changing table',
        'type': 'changing_table',
        'attributes': []
    }
    with pytest.raises(exceptions.SceneException) as excinfo:
        goal = goal_obj.get_config({ 'target': [pickupable_obj, other_obj] })
    assert "second object must be" in str(excinfo.value)


def test_TransferralGoal_ensure_pickup_action():
    """For MCS-270"""
    for _ in range(MAX_TRIES):
        goal_obj = TransferralGoal()
        body: Dict[str, Any] = scene_generator.OUTPUT_TEMPLATE
        try:
            goal_obj.update_body(body, True)
        except PathfindingException:
            pass
        if 'actions' in body['answer']:
            break

    # should have a PickupObject action
    assert any((action['action'] == 'PickupObject' for action in body['answer']['actions']))
    # last action one should be PutObject
    assert body['answer']['actions'][-1]['action'] == 'PutObject'


def test_TransferralGoal_navigate_near_objects():
    """For MCS-271"""
    for _ in range(MAX_TRIES):
        goal_obj = TransferralGoal()
        body: Dict[str, Any] = scene_generator.OUTPUT_TEMPLATE
        try:
            goal_obj.update_body(body, True)
        except PathfindingException:
            pass
        if 'actions' in body['answer']:
            break

    pickupable_id = body['goal']['metadata']['target_1']['id']
    container_id = body['goal']['metadata']['target_2']['id']
    pickupable_obj = next((obj for obj in body['objects'] if obj['id'] == pickupable_id))
    container_obj = next((obj for obj in body['objects'] if obj['id'] == container_id))
    if 'locationParent' in pickupable_obj:
        parent = next((obj for obj in body['objects'] if obj['id'] == pickupable_obj['locationParent']))
        pickupable_position = parent['shows'][0]['position']
        pass
    else:
        pickupable_position = pickupable_obj['shows'][0]['position']
    container_position = container_obj['shows'][0]['position']

    position = body['performerStart']['position']
    x = position['x']
    z = position['z']
    # 0 at start faces positive z, and rotations are clockwise
    heading = 90 - body['performerStart']['rotation']['y']
    for action in body['answer']['actions']:
        if action['action'] == 'PickupObject':
            # should be near pickupable object
            # TODO I think this needs to account for the dimensions of the pickupable object too?
            pickupable_distance = math.sqrt((x - pickupable_position['x'])**2 +
                                            (z - pickupable_position['z'])**2)
            assert pickupable_distance <= MAX_REACH_DISTANCE
        elif action['action'] == 'PutObject':
            # should be near container
            container_distance = math.sqrt((x - container_position['x'])**2 +
                                           (z - container_position['z'])**2)
            assert container_distance <= MAX_REACH_DISTANCE
        elif action['action'] == 'RotateLook':
            # subtract because rotations are clockwise
            heading = (heading - action['params']['rotation']) % 360.0
        elif action['action'] == 'MoveAhead':
            amount = action['params'].get('amount', 1)
            distance = amount * MAX_MOVE_DISTANCE
            radians = math.radians(heading)
            x += distance * math.cos(radians)
            z += distance * math.sin(radians)
        else:
            logging.error(f'unknown action "{action["action"]}"')
            assert False


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
    path = goal_obj._find_optimal_path(scene['objects'], scene['objects'])
    print(path)
    # TODO: uncomment when this is fixed
    assert path[-1]['action'] == 'RotateLook'


def test_traversal_performer_start_not_close_to_target():
    """Ensure the performerStart is not right next to the target object
    (for TraversalGoal). For MCS-158."""
    goal_obj = TraversalGoal()
    body = scene_generator.generate_body_template('158-performerStart')
    goal_obj.update_body(body, False)
    metadata = body['goal']['metadata']
    target_id = metadata['target']['id']
    target = next((obj for obj in body['objects'] if obj['id'] == target_id))
    target_position = target['shows'][0]['position']
    performer_start = body['performerStart']['position']
    dist = geometry.position_distance(target_position, performer_start)
    assert dist >= geometry.MINIMUM_START_DIST_FROM_TARGET


def test_transferral_targets_not_close_to_each_other():
    """Ensure that the targets for TransferralGoal aren't too close to
    each other. For MCS-158."""
    goal_obj = TransferralGoal()
    body = scene_generator.generate_body_template('158-performerStart')
    goal_obj.update_body(body, False)
    metadata = body['goal']['metadata']
    target1_id = metadata['target_1']['id']
    target2_id = metadata['target_2']['id']
    target1 = next((obj for obj in body['objects'] if obj['id'] == target1_id))
    target2 = next((obj for obj in body['objects'] if obj['id'] == target2_id))
    distance = geometry.position_distance(target1['shows'][0]['position'],
                                          target2['shows'][0]['position'])
    assert distance >= geometry.MINIMUM_TARGET_SEPARATION
