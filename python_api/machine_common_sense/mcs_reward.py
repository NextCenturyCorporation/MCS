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
    def __get_object_from_list(objects: List[MCS_Object],
                               target_id: str) -> MCS_Object:
        '''
        Finds an mcs_object in a list. Uses a generator to return the first item
        or defaults to None if the target isn't found.

        Args:
            objects: list of mcs_objects
            target_id: str ID of the mcs_object to find

        Returns:
            target: object if found or None
        '''
        return next((o for o in objects if o['objectId'] == target_id), None)

    @staticmethod
    def calc_distance_to_goal(action_obj_xz_pos: Tuple[float, float], goal_obj: MCS_Object) -> float:
        '''
        Object 2D (xz) distance center to the goal object nearest edge
        
        Args:
            action_obj_xz_pos: Tuple (x,z)
            goal_obj: MCS_Object

        Returns:
            distance_to_edge: float
        '''
        distance_to_edge = 0.0

        goal_object_xz_center = goal_obj['position']['x'], \
            goal_obj['position']['z']

        # split 3d object bounds into upper and lower boxes
        bbox3d = goal_object['objectBounds']['objectBoundsCorners']
        lower_box, upper_box = bbox3d[:4], bbox3d[4:]

        # convert upper box plane to sympy Polygon
        corners = [(pt['x'], pt['z']) for pt in upper_box]
        a, b, c, d = corners
        upper_polygon = sympy.Polygon(a, b, c, d)

        # calculate center_line from center of object to action object center
        center_line = sympy.Segment(sympy.Point(goal_object_xz_center), \
                sympy.Point(action_obj_xz_pos))

        # find the interesection of the center_line and the goal object bounds
        intersections = [
            i.evalf() for i in upper_polygon.intersection(center_line)
        ]
        num_intersections = len(intersections)
        # if there are 0 intersections then the action object is inside the goal
        # object bounds. We will return a distance of 0.0 in this case and consider
        # the goal reached as far as 'nearness' goes.
        if num_intersections:
            # most of the time, there should be only one intersection.
            # two intersections should only occur on a corner but
            # they will be identical points so just grab the first one
            intersection = intersections[0]
            # determine the distance from the center of the action object to the goal
            # object edge
            distance_to_edge = sympy.Point(action_obj_xz_pos).distance(
                intersection).evalf()
            
        return distance_to_edge

    @staticmethod
    def calc_retrieval_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''
        Calculate the reward for the retrieval goal.

        Args:
            goal: MCS_Goal
            scene_metadata: Dict

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata.get('target_id', None)
        objects = scene_metadata.get('objects', None)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)
        if goal_object and ('isPickedUp' in goal_object) and goal_object['isPickedUp']:
            reward = GOAL_ACHIEVED
        return reward

    @staticmethod
    def calc_traversal_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''
        Calculate the reward for the traversal goal.

        Agent must be within reach distance of an object edge to be considered near.

        Args:
            goal: MCS_Goal
            scene_metadata: Dict

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata.get('target_id', None)
        objects = scene_metadata.get('objects', None)
        agent = scene_metadata.get('agent', None)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)

        if goal_object is not None and agent is not None:
            agent_center_xz = agent['position']['x'], agent['position']['z']
            distance_to_goal = MCS_Reward.calc_distance_to_goal(agent_center_xz, goal_object)
            reward = int(distance_to_goal < MAX_REACH_DISTANCE)

        return reward

    @staticmethod
    def calc_transferral_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''
        Calculate the reward for the transferral goal.

        Args:
            goal: MCS_Goal
            scene_metadata: Dict

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED

        relationship = goal.metadata.get('relationship', None)
        if relationship is None or len(relationship) != 3:
            return GOAL_NOT_ACHIEVED

        # action object to goal object
        action_id, action, goal_id = relationship
        action = action.lower()

        objects = scene_metadata['objects']
        action_object = MCS_Reward.__get_object_from_list(objects, action_id)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)

        if goal_object is None or ('isPickedUp' in goal_object and goal_object['isPickedUp']):
            return GOAL_NOT_ACHIEVED
        
        if action_object is None or ('isPickedUp' in action_object and action_object['isPickedUp']):
            return GOAL_NOT_ACHIEVED

        action_object_xz_center = action_object['position']['x'], \
            action_object['position']['z']

        # actions are next_to or on_top_of (ie; action obj next to goal obj)
        if action == 'next_to':
            distance_to_goal = MCS_Reward.calc_distance_to_goal(action_object_xz_center, goal_object)
            reward = int(distance_to_goal <= MAX_MOVE_DISTANCE)
        elif action == 'on_top_of':

            # split 3d object bounds into upper and lower boxes
            bbox3d = goal_object['objectBounds']['objectBoundsCorners']
            lower_box, upper_box = bbox3d[:4], bbox3d[4:]
            # convert upper box plane to sympy Polygon
            corners = [(pt['x'], pt['z']) for pt in upper_box]
            a, b, c, d = corners
            upper_polygon = sympy.Polygon(a, b, c, d)

            action_pt = sympy.Point(action_object_center_xz)

            # check that the target object center is within goal object bounds
            # and the y dimension of the target is above the goal
            action_obj_within_bounds = upper_polygon.encloses_point(action_pt)
            action_obj_above_goal = action_object['position']['y'] > goal_object['position']['y']
            if action_obj_within_bounds and action_obj_above_goal:
                reward = GOAL_ACHIEVED

        return reward

    @staticmethod
    def calculate_default_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''Returns the default reward.'''
        return GOAL_NOT_ACHIEVED

    @staticmethod
    def calculate_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''
        Determine if the agent achieved the objective/task/goal.

        Args:
            goal: MCS_Goal
            scene_metadata: Dict

        Returns:
            int: reward is 1 if goal achieved, 0 otherwise

        '''
        
        category = None
        if goal is not None and goal.metadata:
            category = goal.metadata.get('category', None)

        switch = {
            MCS_Goal_Category.RETRIEVAL.name: MCS_Reward.calc_retrieval_reward,
            MCS_Goal_Category.TRANSFERRAL.name: MCS_Reward.calc_transferral_reward,
            MCS_Goal_Category.TRAVERSAL.name: MCS_Reward.calc_traversal_reward,
        }

        return switch.get(category,
                          MCS_Reward.calculate_default_reward)(goal,
                                                               scene_metadata)
