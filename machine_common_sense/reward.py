from typing import Dict, List, Optional

import typeguard
from shapely import geometry

from .goal_metadata import GoalCategory, GoalMetadata

GOAL_ACHIEVED = 1
GOAL_NOT_ACHIEVED = 0
STEP_PENALTY = 0.001
LAVA_PENALTY = 100.0


class Reward(object):
    '''Reward utility class'''
    @staticmethod
    def __get_object_from_list(objects: List[Dict],
                               target_id: str) -> Dict:
        '''
        Finds an object in a list. Uses a generator to return the first item
        or defaults to None if the target isn't found.

        Args:
            objects: list of object dictionaries
            target_id: str objectId of the object to find

        Returns:
            target: object dictionary if found or None
        '''
        return next((o for o in objects if o['objectId'] == target_id), None)

    @staticmethod
    def _convert_object_to_planar_polygon(
            goal_object: Dict) -> geometry.Polygon:
        '''
        Project goal object bounds (x,y,z) to an XZ planar polygon.

        Args:
            goal_object: dict

        Returns:
            polygons: shapely.geometry.Polygon
        '''
        bbox3d = goal_object['objectBounds']['objectBoundsCorners']
        # project to XZ plane
        xz_pts = [(pt['x'], pt['z']) for pt in bbox3d]
        return geometry.MultiPoint(xz_pts).convex_hull

    @staticmethod
    def _calc_retrieval_reward(
            goal: GoalMetadata,
            objects: Dict,
            agent: Dict,
            performer_reach: float,
            goal_reward: float = GOAL_ACHIEVED) -> float:
        '''
        Calculate the reward for the retrieval goal.

        The goal object must be in the agent's hand.

        Args:
            goal: GoalMetadata
            objects: Dict
            agent: Dict
            performer_reach: float
            goal_reward: float

        Returns:
            float: 1 for goal achieved and no goal_reward arg is given,
            goal_reward value if goal_reward arg is given, 0 otherwise.

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata['target'].get('id', None)
        goal_object = Reward.__get_object_from_list(objects, goal_id)

        if goal_object and goal_object.get('isPickedUp', False):
            reward = goal_reward

        return reward

    @staticmethod
    def _adjust_score_penalty(
            current_score: int,
            number_steps: int,
            steps_on_lava: int,
            lava_penalty: float = LAVA_PENALTY,
            step_penalty: float = STEP_PENALTY) -> float:
        '''
        Calculate the score penalty based on the number of steps,
        if the current step results in a reward being achieved do
        not penalize them for the step that resulted in the goal
        being achieved.

        Args:
            current_score: 1 or 0 depending if reward achieved
            number_steps: the current step count
            steps_on_lava: the number of total steps on lava
            lava_penalty: the point deduction for each step on lava
            step_penalty: point deduction for each step

        Returns:
            float: new score based off of step penalty

        '''
        step_penalty = STEP_PENALTY if step_penalty is None else step_penalty
        lava_penalty = LAVA_PENALTY if lava_penalty is None else lava_penalty
        if current_score == 1:
            return current_score - ((number_steps - 1) * float(step_penalty))

        if steps_on_lava is None:
            steps_on_lava = 0
        return current_score - (number_steps * float(step_penalty)) - \
            (steps_on_lava * float(lava_penalty))

    @staticmethod
    def _calculate_default_reward(
            goal: GoalMetadata,
            objects: Dict,
            agent: Dict,
            reach: float,
            goal_reward: float = GOAL_ACHIEVED) -> float:
        '''Returns the default reward of 0; not achieved.'''
        return GOAL_NOT_ACHIEVED

    @staticmethod
    @typeguard.typechecked
    def calculate_reward(
            goal: Optional[GoalMetadata],
            objects: List[Dict],
            agent: Dict,
            number_steps: int,
            reach: Optional[float],
            steps_on_lava: Optional[int] = None,
            lava_penalty: Optional[float] = LAVA_PENALTY,
            step_penalty: Optional[float] = STEP_PENALTY,
            goal_reward: Optional[float] = GOAL_ACHIEVED) -> float:
        '''
        Determine if the agent achieved the goal.

        Args:
            goal: GoalMetadata
            objects: Dict
            agent: Dict
            reach: float
            steps_on_lava: int
            lava_penalty: float
            step_penalty: float
            goal_reward: float

        Returns:
            int: reward is 1 if goal achieved, 0 otherwise

        '''

        category = None
        if goal is not None and goal.metadata:
            category = goal.metadata.get('category', None)

        switch = {
            GoalCategory.RETRIEVAL.value: Reward._calc_retrieval_reward
        }

        current_score = switch.get(category, Reward._calculate_default_reward)(
            goal,
            objects,
            agent,
            reach,
            GOAL_ACHIEVED if goal_reward is None else goal_reward
        )

        return Reward._adjust_score_penalty(
            current_score, number_steps, steps_on_lava, lava_penalty,
            step_penalty
        )
