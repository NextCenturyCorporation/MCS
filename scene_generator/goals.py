#
# Goal generation
#

import copy
import random
from enum import Enum


class AttributeConstraint:
    """True iff the object has attribute and predicate is true when applied to the attribute and the arguments."""
    def __init__(self, predicate, attribute, *arguments):
        self.predicate = predicate
        self.attribute = attribute
        self.arguments = arguments

    def is_true(self, obj):
        return self.attribute in obj and self.predicate(obj[self.attribute], *self.arguments)


class Goal:
    """An abstract Goal."""

    def get_object_constraint_lists(self):
        return []

    def get_goal(self, objects):
        return {}

    @staticmethod
    def find_valid_object(constraint_list, objects):
        """Find a member of objects that satisifies all constraints in constraint_list"""
        for obj in objects:
            obj_ok = True
            for constraint in constraint_list:
                if not constraint.is_true(obj):
                    obj_ok = False
                    break
            if obj_ok:
                return obj
        return None

    def find_valid_objects(self, objects):
        """Find objects that satisfy this goal's constraints. It does not do backtracking, so it can fail to find a
        solution if there are too many constraints and too few objects."""
        valid_objects = []
        for constraint_list in self.get_object_constraint_lists():
            obj = self.find_valid_object(constraint_list, objects)
            if obj is None:
                return None
            valid_objects.append(obj)
            objects.remove(obj)
        return valid_objects

    @staticmethod
    def find_all_valid_objects(constraint_list, objects):
        """Find all members of objects that satisfy all constraints in constraint_list"""
        valid_objects = []
        for obj in objects:
            obj_ok = True
            for constraint in constraint_list:
                if not constraint.is_true(obj):
                    obj_ok = False
                    break
            if obj_ok:
                valid_objects.append(obj)
        return valid_objects

    def find_all_valid_objects_all_constraints(self, objects):
        """For each constraint, find all valid members of objects."""
        valid_objects = []
        for constraint_list in self.get_object_constraint_lists():
            objects = self.find_all_valid_objects(constraint_list, objects)
            valid_objects.append(objects)
        return valid_objects


class IdGoal(Goal):
    TEMPLATE = {
        'type_list': ['interaction', 'identification', 'objects', 'places'],
        'task_list': ['navigation', 'identification']
    }

    def get_object_constraint_lists(self):
        return [[]]

    def get_goal(self, objects):
        target = objects[0]

        goal = copy.deepcopy(self.TEMPLATE)
        goal['info_list'] = target['info']
        goal['metadata'] = {
            'target': {
                'id': target['id'],
                'info': target['info']
            }
        }
        return goal


class TransportationGoal(Goal):
    class RelationshipType(Enum):
        NEXT_TO = 'next to'
        ON_TOP_OF = 'on top of'

    TEMPLATE = {
        'type_list': ['interaction', 'identification', 'objects', 'places'],
        'task_list': ['navigation', 'identification', 'transportation']
    }

    def get_object_constraint_lists(self):
        return [[AttributeConstraint(list.__contains__, 'attributes', 'pickupable')], []]

    def get_goal(self, objects):
        if len(objects) < 2:
            raise ValueError(f'need at least 2 objects for this goal, was given {len(objects)}')
        target1, target2 = objects
        if 'pickupable' not in target1['attributes']:
            raise ValueError('first object must be "pickupable"')
        relationship = random.choice(list(self.RelationshipType))

        goal = copy.deepcopy(self.TEMPLATE)
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


GOAL_TYPES = [IdGoal, TransportationGoal]


def generate_goal():
    """Return a 'goal' object of a random type"""
    return random.choice(GOAL_TYPES)()
