from typing import List, Dict, Tuple

import sympy

from .mcs_goal import MCS_Goal
from .mcs_goal_category import MCS_Goal_Category
from .mcs_object import MCS_Object
from .mcs_controller_ai2thor import MAX_REACH_DISTANCE, MAX_MOVE_DISTANCE

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
    def _convert_bounds_to_polygons(goal_object: Dict) -> Tuple[sympy.Polygon, sympy.Polygon]:
        '''
        Converts goal object bounds to an upper and lower planar polygon.

        Args:
            goal_object: dict

        Returns:
            polygons: Tuple(sympy.Polygon, sympy.Polygon)
        '''
        # split 3d object bounds into upper and lower boxes
        bbox3d = goal_object['objectBounds']['objectBoundsCorners']
        lower_box, upper_box = bbox3d[:4], bbox3d[4:]

        # conver lower box plane to sympy Polygon
        lower_corners = [(pt['x'], pt['z']) for pt in lower_box]
        lower_polygon = sympy.Polygon(*lower_corners)

        # convert upper box plane to sympy Polygon
        upper_corners = [(pt['x'], pt['z']) for pt in upper_box]
        upper_polygon = sympy.Polygon(*upper_corners)

        return lower_polygon, upper_polygon

    @staticmethod
    def __calc_distance_to_goal(action_obj_xz_pos: Tuple[float, float], goal_obj: Dict) -> float:
        '''
        Object 2D (xz) distance center to the goal object nearest edge
        
        Args:
            action_obj_xz_pos: Tuple (x,z)
            goal_obj: dict

        Returns:
            distance_to_edge: float
        '''
        distance_to_edge = 0.0

        goal_object_xz_center = goal_obj['position']['x'], \
            goal_obj['position']['z']

        _, upper_polygon = MCS_Reward._convert_bounds_to_polygons(goal_obj)

        action_center_pt = sympy.Point(action_obj_xz_pos)
        if not upper_polygon.encloses_point(action_center_pt):
            distance_to_edge = upper_polygon.distance(action_center_pt).evalf()

        return float(distance_to_edge)

    @staticmethod
    def _calc_retrieval_reward(goal: MCS_Goal, objects: Dict, agent: Dict) -> int:
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
    def _calc_traversal_reward(goal: MCS_Goal, objects: Dict, agent: Dict) -> int:
        '''
        Calculate the reward for the traversal goal.

        Agent must be within reach distance of an object edge to be considered near.

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

        if goal_object is not None and agent is not None:
            agent_center_xz = agent['position']['x'], agent['position']['z']
            distance_to_goal = MCS_Reward.__calc_distance_to_goal(agent_center_xz, goal_object)
            reward = int(distance_to_goal < MAX_REACH_DISTANCE)

        return reward

    @staticmethod
    def _calc_transferral_reward(goal: MCS_Goal, objects: Dict, agent: Dict) -> int:
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
        action_target, action, goal_target = relationship
        action_id = action_target.get('id', None)
        goal_id = goal_target.get('id', None)
        action = action.lower()

        #objects = scene_metadata['objects']
        action_object = MCS_Reward.__get_object_from_list(objects, action_id)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)

        if goal_object is None or goal_object.get('isPickedUp', False):
            return GOAL_NOT_ACHIEVED
        
        if action_object is None or action_object.get('isPickedUp', False):
            return GOAL_NOT_ACHIEVED

        action_object_xz_center = action_object['position']['x'], \
            action_object['position']['z']

        # actions are next_to or on_top_of (ie; action obj next to goal obj)
        if action == 'next_to':
            distance_to_goal = MCS_Reward.__calc_distance_to_goal(action_object_xz_center, goal_object)
            reward = int(distance_to_goal <= MAX_MOVE_DISTANCE)
        elif action == 'on_top_of':
            # check that the target object center is within goal object bounds
            # and the y dimension of the target is above the goal
            _, upper_polygon = MCS_Reward._convert_bounds_to_polygons(goal_object)
            action_pt = sympy.Point(action_object_xz_center)
            action_obj_within_bounds = upper_polygon.encloses_point(action_pt)
            action_obj_above_goal = action_object['position']['y'] > goal_object['position']['y']
            if action_obj_within_bounds and action_obj_above_goal:
                reward = GOAL_ACHIEVED

        return reward

    @staticmethod
    def _calculate_default_reward(goal: MCS_Goal, objects: Dict, agent: Dict) -> int:
        '''Returns the default reward of 0; not achieved.'''
        return GOAL_NOT_ACHIEVED

    @staticmethod
    def calculate_reward(goal: MCS_Goal, objects: Dict, agent: Dict) -> int:
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
            MCS_Goal_Category.RETRIEVAL.value: MCS_Reward._calc_retrieval_reward,
            MCS_Goal_Category.TRANSFERRAL.value: MCS_Reward._calc_transferral_reward,
            MCS_Goal_Category.TRAVERSAL.value: MCS_Reward._calc_traversal_reward,
        }

        return switch.get(category,
                          MCS_Reward._calculate_default_reward)(goal,
                                                               objects, agent)
