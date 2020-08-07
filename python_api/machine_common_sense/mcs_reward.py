from typing import List, Dict

from shapely import geometry

#from .mcs_goal import MCS_Goal
from .mcs_goal_category import MCS_Goal_Category
from .mcs_controller_ai2thor import MAX_REACH_DISTANCE, MAX_MOVE_DISTANCE

import machine_common_sense as mcs

GOAL_ACHIEVED = 1
GOAL_NOT_ACHIEVED = 0


class MCS_Reward(object):
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
            goal: mcs.Goal,
            objects: Dict,
            agent: Dict) -> int:
        '''
        Calculate the reward for the retrieval goal.

        The goal object must be in the agent's hand.

        Args:
            goal: MCS_Goal
            objects: Dict
            agent: Dict

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata['target'].get('id', None)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)

        if goal_object and goal_object.get('isPickedUp', False):
            reward = GOAL_ACHIEVED
        return reward

    @staticmethod
    def _calc_traversal_reward(
            goal: mcs.Goal,
            objects: Dict,
            agent: Dict) -> int:
        '''
        Calculate the reward for the traversal goal.

        Agent must be within reach distance of an object edge to be
        considered near.

        Args:
            goal: MCS_Goal
            objects: Dict
            agent: Dict

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata['target'].get('id', None)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)

        agent_pos = agent['position']
        agent_xz = geometry.Point(agent_pos['x'], agent_pos['z'])

        if goal_object is not None:
            goal_polygon = MCS_Reward._convert_object_to_planar_polygon(
                goal_object)
            polygonal_distance = agent_xz.distance(goal_polygon)
            reward = int(polygonal_distance <= MAX_REACH_DISTANCE)

        return reward

    @staticmethod
    def _calc_transferral_reward(
            goal: mcs.Goal,
            objects: Dict,
            agent: Dict) -> int:
        '''
        Calculate the reward for the transferral goal.

        The action object must be next to or on top of the goal object. This
        depends on the relationship action verb.

        Args:
            goal: MCS_Goal
            objects: Dict
            agent: Dict

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
        action_object = MCS_Reward.__get_object_from_list(objects, action_id)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)

        if goal_object is None or goal_object.get('isPickedUp', False):
            return GOAL_NOT_ACHIEVED

        if action_object is None or action_object.get('isPickedUp', False):
            return GOAL_NOT_ACHIEVED

        goal_polygon = MCS_Reward._convert_object_to_planar_polygon(
            goal_object)
        action_polygon = MCS_Reward._convert_object_to_planar_polygon(
            action_object)

        # actions are next_to or on_top_of (ie; action obj next to goal obj)
        if action == 'next to':
            polygonal_distance = action_polygon.distance(goal_polygon)
            reward = int(polygonal_distance <= MAX_MOVE_DISTANCE)
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
    def _calculate_default_reward(
            goal: mcs.Goal,
            objects: Dict,
            agent: Dict) -> int:
        '''Returns the default reward of 0; not achieved.'''
        return GOAL_NOT_ACHIEVED

    @staticmethod
    def calculate_reward(goal: mcs.Goal, objects: Dict, agent: Dict) -> int:
        '''
        Determine if the agent achieved the objective/task/goal.

        Args:
            goal: MCS_Goal
            objects: Dict
            agent: Dict

        Returns:
            int: reward is 1 if goal achieved, 0 otherwise

        '''

        category = None
        if goal is not None and goal.metadata:
            category = goal.metadata.get('category', None)

        switch = {
            MCS_Goal_Category.RETRIEVAL.value: MCS_Reward._calc_retrieval_reward,  # noqa: E501
            MCS_Goal_Category.TRANSFERRAL.value: MCS_Reward._calc_transferral_reward,  # noqa: E501
            MCS_Goal_Category.TRAVERSAL.value: MCS_Reward._calc_traversal_reward,  # noqa: E501
        }

        return switch.get(category,
                          MCS_Reward._calculate_default_reward)(goal,
                                                                objects, agent)
