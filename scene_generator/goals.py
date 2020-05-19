#
# Goal generation
#

import random
from typing import List

from goal import Goal, EmptyGoal
from interaction_goals import RetrievalGoal, TransferralGoal, TraversalGoal
from intphys_goals import GravityGoal, ObjectPermanenceGoal, ShapeConstancyGoal, SpatioTemporalContinuityGoal

# Note: the names of all goal classes in GOAL_TYPES must end in "Goal" or choose_goal will not work
GOAL_TYPES = {
    'interaction': [RetrievalGoal, TransferralGoal, TraversalGoal],
    'intphys': [GravityGoal, ObjectPermanenceGoal, ShapeConstancyGoal, SpatioTemporalContinuityGoal]
}


def choose_goal(goal_type: str) -> Goal:
    """Return a random class of 'goal' object from within the specified
overall type, or EmptyGoal if goal_type is None"""
    if goal_type is None:
        return EmptyGoal()
    else:
        if goal_type in GOAL_TYPES:
            return random.choice(GOAL_TYPES[goal_type])()
        else:
            class_name = goal_type + 'Goal'
            klass = globals()[class_name]
            return klass()


def get_goal_types() -> List[str]:
    generic_types = GOAL_TYPES.keys()
    specific_types = [klass.__name__.replace('Goal', '') for classes in GOAL_TYPES.values() for klass in classes]
    return list(generic_types) + specific_types
