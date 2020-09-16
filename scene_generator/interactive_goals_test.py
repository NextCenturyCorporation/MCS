import pytest
import uuid

""" TODO MCS-381
import math
from typing import Dict, Any
from machine_common_sense.controller_ai2thor import (
    MAX_MOVE_DISTANCE,
    MAX_REACH_DISTANCE
)
from scene_generator import OUTPUT_TEMPLATE
import util
"""

import geometry
from interactive_goals import RetrievalGoal, TransferralGoal, TraversalGoal


@pytest.mark.skip(reason="TODO MCS-381")
def test_parse_path_section_fractional():
    pass
    """
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
            'amount': round(0.4 / MAX_MOVE_DISTANCE, geometry.POSITION_DIGITS)
        }
    }]
    actions, new_heading, performer = parse_path_section(
        path_section, 0, (0, 0), goal_boundary)
    assert actions == expected_actions
    """


@pytest.mark.skip(reason="TODO MCS-381")
def test_get_navigation_action():
    pass
    """
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': 45.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.09**2) / MAX_MOVE_DISTANCE,
                            geometry.POSITION_DIGITS)
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
            'boundingBox': [
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
    actions, performer, heading = get_navigation_actions(
        start, goal_object, [goal_object])
    assert actions == expected_actions
    """


@pytest.mark.skip(reason="TODO MCS-381")
def test_get_navigation_action_with_locationParent():
    pass
    """
    expected_actions = [{
        'action': 'RotateLook',
        'params': {
            'rotation': 45.0,
            'horizon': 0.0
        }
    }, {
        'action': 'MoveAhead',
        'params': {
            'amount': round(math.sqrt(2 * 0.09**2) / MAX_MOVE_DISTANCE,
                            geometry.POSITION_DIGITS)
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
            'boundingBox': [
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
    actions, performer, heading = get_navigation_actions(
        start, goal_object, [container_object, goal_object])
    assert actions == expected_actions
    """


@pytest.mark.skip(reason="TODO MCS-381")
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
    pass
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
            'boundingBox': [
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
            'boundingBox': [
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
    expected_actions = [{'action': 'RotateLook', 'params': {'rotation': 315.0,
                                                            'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': {'amount': 1}},
                        {'action': 'MoveAhead', 'params': {'amount': 1}},
                        {'action': 'MoveAhead', 'params': {'amount': 0.83}},
                        {'action': 'RotateLook', 'params': {
                            'rotation': 45.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': {'amount': 1}},
                        {'action': 'MoveAhead', 'params': {'amount': 1}},
                        {'action': 'RotateLook', 'params': {
                            'rotation': 45.0, 'horizon': 0.0}},
                        {'action': 'MoveAhead', 'params': {'amount': 1}},
                        {'action': 'MoveAhead', 'params': {'amount': 1}},
                        {'action': 'MoveAhead', 'params': {'amount': round((.9 * math.sqrt(2) - 1) / MAX_MOVE_DISTANCE, geometry.POSITION_DIGITS)}}]  # noqa: E501
    all_objs = [goal_obj, obstacle_obj]
    actions, performer, heading = get_navigation_actions(
        start, goal_obj, all_objs)
    assert actions == expected_actions
    """


@pytest.mark.skip(reason="TODO MCS-381")
def test_trim_actions_to_reach():
    pass
    """
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
    actions, new_heading, performer = parse_path_section(
        path_section, 0, (0, 0), goal_boundary)
    target = {
        'shows': [{
            'position': {
                'x': 1,
                'y': 0,
                'z': 0
            }
        }]
    }
    actions, performer = trim_actions_to_reach(
        actions, performer, new_heading, target)
    assert actions == expected_actions
    """


def test_choose_definition():
    goal = TraversalGoal()
    definition = goal.choose_definition()
    assert definition


def test_choose_location():
    goal = TraversalGoal()
    definition = goal.choose_definition()
    old_bounds_list = []
    location, new_bounds_list = goal.choose_location(definition,
                                                     geometry.ORIGIN_LOCATION,
                                                     old_bounds_list)
    assert location
    assert len(old_bounds_list) == 0
    assert len(new_bounds_list) == 1


def test_RetrievalGoal_choose_target_definition():
    goal = RetrievalGoal()
    definition = goal.choose_target_definition(0)
    assert definition
    assert 'pickupable' in definition['attributes']


def test_RetrievalGoal_get_target_count():
    goal = RetrievalGoal()
    assert goal.get_target_count() == 1


def test_RetrievalGoal_update_goal_config():
    target = {
        'id': str(uuid.uuid4()),
        'info': ['blue', 'rubber', 'ball'],
        'goalString': 'blue rubber ball',
        'pickupable': True,
        'type': 'sphere'
    }

    goal = RetrievalGoal()
    config = goal.update_goal_config({}, [target])

    assert config['description'] == 'Find and pick up the blue rubber ball.'
    assert config['metadata']['target']['id'] == target['id']
    assert config['metadata']['target']['info'] == ['blue', 'rubber', 'ball']


def test_RetrievalGoal_validate_target_location():
    goal = RetrievalGoal()
    assert goal.validate_target_location(0, {}, [], geometry.ORIGIN_LOCATION)


def test_TransferralGoal_choose_target_definition_0():
    goal = TransferralGoal()
    definition = goal.choose_target_definition(0)
    assert definition
    assert 'pickupable' in definition['attributes']


def test_TransferralGoal_choose_target_definition_1():
    goal = TransferralGoal()
    definition = goal.choose_target_definition(1)
    assert definition
    assert 'stackTarget' in definition['attributes']


def test_TransferralGoal_get_target_count():
    goal = TransferralGoal()
    assert goal.get_target_count() == 2


def test_TransferralGoal_update_goal_config():
    target_1 = {
        'id': str(uuid.uuid4()),
        'info': ['blue', 'rubber', 'ball'],
        'goalString': 'blue rubber ball',
        'pickupable': True,
        'type': 'sphere'
    }
    target_2 = {
        'id': str(uuid.uuid4()),
        'info': ['grey', 'fabric', 'sofa'],
        'goalString': 'grey fabric sofa',
        'attributes': [],
        'type': 'sofa',
        'stackTarget': True
    }

    goal = TransferralGoal()
    config = goal.update_goal_config({}, [target_1, target_2])

    relationship = config['metadata']['relationship']
    relationship_type = relationship[1]
    assert relationship_type in [
        item.value for item in TransferralGoal.RelationshipType
    ]

    assert config['description'] == 'Find and pick up the blue rubber ' + \
        'ball and move it ' + relationship_type + ' the grey fabric sofa.'
    assert config['metadata']['target_1']['id'] == target_1['id']
    assert config['metadata']['target_1']['info'] == ['blue', 'rubber', 'ball']
    assert config['metadata']['target_2']['id'] == target_2['id']
    assert config['metadata']['target_2']['info'] == ['grey', 'fabric', 'sofa']


def test_TransferralGoal_validate_target_location_0():
    goal = TransferralGoal()
    assert goal.validate_target_location(0, {}, [], geometry.ORIGIN_LOCATION)


def test_TransferralGoal_validate_target_location_1_true():
    target_1 = {
        'shows': [{
            'position': {
                'x': 1,
                'y': 0,
                'z': 1
            }
        }]
    }

    goal = TransferralGoal()
    assert goal.validate_target_location(
        1,
        {'position': {'x': 3, 'y': 0, 'z': 1}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )
    assert goal.validate_target_location(
        1,
        {'position': {'x': 1, 'y': 0, 'z': 3}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )
    assert goal.validate_target_location(
        1,
        {'position': {'x': -2, 'y': 0, 'z': 1}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )
    assert goal.validate_target_location(
        1,
        {'position': {'x': 1, 'y': 0, 'z': -2}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )


def test_TransferralGoal_validate_target_location_1_false():
    target_1 = {
        'shows': [{
            'position': {
                'x': 1,
                'y': 0,
                'z': 1
            }
        }]
    }

    goal = TransferralGoal()
    assert not goal.validate_target_location(
        1,
        {'position': {'x': 2.9, 'y': 0, 'z': 1}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )
    assert not goal.validate_target_location(
        1,
        {'position': {'x': 1, 'y': 0, 'z': 2.9}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )
    assert not goal.validate_target_location(
        1,
        {'position': {'x': -0.9, 'y': 0, 'z': 1}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )
    assert not goal.validate_target_location(
        1,
        {'position': {'x': 1, 'y': 0, 'z': -0.9}},
        [target_1],
        geometry.ORIGIN_LOCATION
    )


def test_TraversalGoal_choose_target_definition():
    goal = TraversalGoal()
    definition = goal.choose_target_definition(0)
    assert definition


def test_TraversalGoal_get_target_count():
    goal = TraversalGoal()
    assert goal.get_target_count() == 1


def test_TraversalGoal_update_goal_config():
    target = {
        'id': str(uuid.uuid4()),
        'info': ['blue', 'rubber', 'ball'],
        'goalString': 'blue rubber ball',
        'pickupable': True,
        'type': 'sphere'
    }

    goal = TraversalGoal()
    config = goal.update_goal_config({}, [target])

    assert config['description'] == 'Find the blue rubber ball and move ' + \
        'near it.'
    assert config['metadata']['target']['id'] == target['id']
    assert config['metadata']['target']['info'] == ['blue', 'rubber', 'ball']


def test_TraversalGoal_validate_target_location_true():
    goal = TraversalGoal()
    assert goal.validate_target_location(
        0,
        {'position': {'x': 2, 'y': 0, 'z': 0}},
        [],
        geometry.ORIGIN_LOCATION
    )
    assert goal.validate_target_location(
        0,
        {'position': {'x': 0, 'y': 0, 'z': -2}},
        [],
        geometry.ORIGIN_LOCATION
    )
    assert goal.validate_target_location(
        0,
        {'position': {'x': -2, 'y': 0, 'z': 0}},
        [],
        geometry.ORIGIN_LOCATION
    )
    assert goal.validate_target_location(
        0,
        {'position': {'x': 0, 'y': 0, 'z': -2}},
        [],
        geometry.ORIGIN_LOCATION
    )


def test_TraversalGoal_validate_target_location_false():
    goal = TraversalGoal()
    assert not goal.validate_target_location(
        0,
        {'position': {'x': 1.9, 'y': 0, 'z': 0}},
        [],
        geometry.ORIGIN_LOCATION
    )
    assert not goal.validate_target_location(
        0,
        {'position': {'x': 0, 'y': 0, 'z': -1.9}},
        [],
        geometry.ORIGIN_LOCATION
    )
    assert not goal.validate_target_location(
        0,
        {'position': {'x': -1.9, 'y': 0, 'z': 0}},
        [],
        geometry.ORIGIN_LOCATION
    )
    assert not goal.validate_target_location(
        0,
        {'position': {'x': 0, 'y': 0, 'z': -1.9}},
        [],
        geometry.ORIGIN_LOCATION
    )


@pytest.mark.skip(reason="TODO MCS-381")
def test_TransferralGoal_ensure_pickup_action():
    """For MCS-270"""
    pass
    """
    for _ in range(util.MAX_TRIES):
        goal_obj = TransferralGoal()
        body: Dict[str, Any] = OUTPUT_TEMPLATE
        try:
            goal_obj.update_body(body, True)
        except PathfindingException:
            pass
        if 'actions' in body['answer']:
            break

    # should have a PickupObject action
    assert any(
        (
            action['action'] == 'PickupObject'
            for action in body['answer']['actions']
        )
    )
    # last action one should be PutObject
    assert body['answer']['actions'][-1]['action'] == 'PutObject'
    """


@pytest.mark.skip(reason="TODO MCS-381")
def test_TransferralGoal_navigate_near_objects():
    """For MCS-271"""
    pass
    """
    for _ in range(util.MAX_TRIES):
        goal_obj = TransferralGoal()
        body: Dict[str, Any] = OUTPUT_TEMPLATE
        try:
            goal_obj.update_body(body, True)
        except PathfindingException:
            pass
        if 'actions' in body['answer']:
            break

    pickupable_id = body['goal']['metadata']['target_1']['id']
    container_id = body['goal']['metadata']['target_2']['id']
    pickupable_obj = next(
        (obj for obj in body['objects'] if obj['id'] == pickupable_id))
    container_obj = next(
        (obj for obj in body['objects'] if obj['id'] == container_id))
    if 'locationParent' in pickupable_obj:
        parent = next(
            (
                obj
                for obj in body['objects']
                if obj['id'] == pickupable_obj['locationParent']
            )
        )
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
            # TODO I think this needs to account for the dimensions of the
            # pickupable object too?
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
    """


@pytest.mark.skip(reason="TODO MCS-381")
def test_add_RotateLook_to_action_list_before_Pickup_or_Put_Object():
    """For MCS-161"""
    pass
    """
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
                'boundingBox': [
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
    """
