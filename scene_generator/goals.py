#
# Goal generation
#

import copy
from enum import Enum, auto
import random


class GoalType(Enum):
    IDENTIFICATION = auto()
    TRANSPORTATION = auto()


class RelationshipType(Enum):
    NEXT_TO = 'next to'
    ON_TOP_OF = 'on top of'


ID_GOAL_TEMPLATE = {
    'type_list': ['interaction', 'identification', 'objects', 'places'],
    'task_list': ['navigation', 'identification']
}

TRANSPORTATION_GOAL_TEMPLATE = {
    'type_list': ['interaction', 'identification', 'objects', 'places'],
    'task_list': ['navigation', 'identification', 'transportation']
}


def _generate_id_goal(objects):
    target = random.choice(objects)

    goal = copy.deepcopy(ID_GOAL_TEMPLATE)
    goal['info_list'] = target['info']
    goal['metadata'] = {
        'target': {
            'id': target['id'],
            'info': target['info']
        }
    }
    return goal


def _generate_transportation_goal(objects):
    if len(objects) < 2:
        raise ValueError(f'need at least 2 for this goal, was only given {len(objects)}')
    pickupables = [x for x in objects if 'pickupable' in x['attributes']]
    if len(pickupables) == 0:
        raise ValueError('at least one object must be "pickupable"')
    target1 = random.choice(pickupables)
    other_objects = [x for x in objects if x != target1]
    target2 = random.choice(other_objects)
    relationship = random.choice(list(RelationshipType))

    goal = copy.deepcopy(TRANSPORTATION_GOAL_TEMPLATE)
    both_info = set(target1['info'] + target2['info'])
    goal['info_list'] = list(both_info)
    goal['metadata'] = {
        'target_1': {
            'id': target1['id'],
            'info': target1['info']
        },
        'target_2': {
            'id': target2['id'],
            'info': target2['info']
        },
        'relationship': [relationship.value, 'target_1', 'target_2']
    }
    return goal


def generate_goal(objects):
    """Return a 'goal' object of a random type with target(s) chosen randomly from the objects in the scene."""
    if len(objects) == 1:
        goal_type = GoalType.IDENTIFICATION
    else:
        goal_type = random.choice(list(GoalType))

    if goal_type == GoalType.IDENTIFICATION:
        return _generate_id_goal(objects)
    elif goal_type == GoalType.TRANSPORTATION:
        return _generate_transportation_goal(objects)
