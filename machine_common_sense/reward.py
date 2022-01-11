from typing import Dict, List

from shapely import geometry

from .controller import DEFAULT_MOVE
from .goal_metadata import GoalCategory, GoalMetadata

GOAL_ACHIEVED = 1
GOAL_NOT_ACHIEVED = 0
STEP_PENALTY = 0.001


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
        polygon = geometry.MultiPoint(xz_pts).convex_hull

        return polygon

    @staticmethod
    def _calc_retrieval_reward(
            goal: GoalMetadata,
            objects: Dict,
            agent: Dict,
            performer_reach: float) -> int:
        '''
        Calculate the reward for the retrieval goal.

        The goal object must be in the agent's hand.

        Args:
            goal: GoalMetadata
            objects: Dict
            agent: Dict
            performer_reach: float

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata['target'].get('id', None)
        goal_object = Reward.__get_object_from_list(objects, goal_id)

        if goal_object and goal_object.get('isPickedUp', False):
            reward = GOAL_ACHIEVED
        return reward

    @staticmethod
    def _calc_traversal_reward(
            goal: GoalMetadata,
            objects: Dict,
            agent: Dict,
            performer_reach: float) -> int:
        '''
        Calculate the reward for the traversal goal.

        Agent must be within reach distance of an object edge to be
        considered near.

        Args:
            goal: GoalMetadata
            objects: Dict
            agent: Dict
            performer_reach: float

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata['target'].get('id', None)
        goal_object = Reward.__get_object_from_list(objects, goal_id)

        agent_pos = agent['position']
        agent_xz = geometry.Point(agent_pos['x'], agent_pos['z'])

        if goal_object is not None:
            goal_polygon = Reward._convert_object_to_planar_polygon(
                goal_object)
            polygonal_distance = agent_xz.distance(goal_polygon)
            reward = int(polygonal_distance <= performer_reach)

        return reward

    @staticmethod
    def _calc_transferral_reward(
            goal: GoalMetadata,
            objects: Dict,
            agent: Dict,
            performer_reach: float) -> int:
        '''
        Calculate the reward for the transferral goal.

        The action object must be next to or on top of the goal object. This
        depends on the relationship action verb.

        Args:
            goal: GoalMetadata
            objects: Dict
            agent: Dict
            performer_reach: float

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED

        relationship = goal.metadata.get('relationship', None)
        if relationship is None or len(relationship) != 3:
            return GOAL_NOT_ACHIEVED

        # action object to goal object
        _, action, _ = relationship
        action_target = goal.metadata.get('target_1', None)
        action_id = action_target.get('id', None)
        goal_target = goal.metadata.get('target_2', None)
        goal_id = goal_target.get('id', None)
        action = action.lower()

        # objects = scene_metadata['objects']
        action_object = Reward.__get_object_from_list(objects, action_id)
        goal_object = Reward.__get_object_from_list(objects, goal_id)

        if goal_object is None or goal_object.get('isPickedUp', False):
            return GOAL_NOT_ACHIEVED

        if action_object is None or action_object.get('isPickedUp', False):
            return GOAL_NOT_ACHIEVED

        goal_polygon = Reward._convert_object_to_planar_polygon(
            goal_object)
        action_polygon = Reward._convert_object_to_planar_polygon(
            action_object)

        # actions are next_to or on_top_of (ie; action obj next to goal obj)
        if action == 'next to':
            polygonal_distance = action_polygon.distance(goal_polygon)
            reward = int(polygonal_distance <= DEFAULT_MOVE)
        elif action == 'on top of':
            # check that the action object center intersects the goal object
            # bounds and the y dimension of the target is above the goal
            action_obj_within_goal = action_polygon.intersects(goal_polygon)
            action_obj_above_goal = (action_object['position']['y'] >
                                     goal_object['position']['y'])
            if action_obj_within_goal and action_obj_above_goal:
                reward = GOAL_ACHIEVED

        return reward

    @staticmethod
    def _adjust_score_penalty(
            current_score: int,
            number_steps: int) -> float:
        '''
        Calculate the score penalty based on the number of steps,
        if the current step results in a reward being achieved do
        not penalize them for the step that resulted in the goal
        being achieved.

        Args:
            current_score: 1 or 0 depending if reward achieved
            number_steps: the current step count

        Returns:
            float: new score based off of step penalty

        '''
        if current_score == 1:
            return current_score - ((number_steps - 1) * STEP_PENALTY)
        else:
            return current_score - ((number_steps) * STEP_PENALTY)

    @staticmethod
    def _calculate_default_reward(
            goal: GoalMetadata,
            objects: Dict,
            agent: Dict,
            reach: float) -> int:
        '''Returns the default reward of 0; not achieved.'''
        return GOAL_NOT_ACHIEVED

    @staticmethod
    def calculate_reward(
            goal: GoalMetadata,
            objects: Dict,
            agent: Dict,
            number_steps: int,
            reach: float) -> float:
        '''
        Determine if the agent achieved the objective/task/goal.

        Args:
            goal: GoalMetadata
            objects: Dict
            agent: Dict
            reach: float

        Returns:
            int: reward is 1 if goal achieved, 0 otherwise

        '''

        category = None
        if goal is not None and goal.metadata:
            category = goal.metadata.get('category', None)

        switch = {
            GoalCategory.RETRIEVAL.value: Reward._calc_retrieval_reward,  # noqa: E501
            GoalCategory.TRANSFERRAL.value: Reward._calc_transferral_reward,  # noqa: E501
            GoalCategory.TRAVERSAL.value: Reward._calc_traversal_reward,  # noqa: E501
        }

        current_score = switch.get(category,
                                   Reward._calculate_default_reward)(goal,
                                                                     objects,
                                                                     agent,
                                                                     reach)
        return Reward._adjust_score_penalty(current_score, number_steps)
