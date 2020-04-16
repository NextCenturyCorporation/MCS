from typing import List, Dict

import sympy

from .mcs_goal import MCS_Goal
from .mcs_goal_category import MCS_Goal_Category
from .mcs_object import MCS_Object

GOAL_ACHIEVED = 1
GOAL_NOT_ACHIEVED = 0
# duplicating these constants from the controller for now
MAX_REACH_DISTANCE = 1.0
MAX_MOVE_DISTANCE = 0.5


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
        objects = scene_metadata['objects']
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)
        if goal_object and goal_object['isPickedUp']:
            reward = GOAL_ACHIEVED
        return reward

    @staticmethod
    def calc_traversal_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''
        Calculate the reward for the traversal goal.

        Args:
            goal: MCS_Goal
            scene_metadata: Dict

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = GOAL_NOT_ACHIEVED
        goal_id = goal.metadata.get('target_id', None)

        objects = scene_metadata['objects']
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)
        goal_object_xz_center = goal_object['position']['x'], \
            goal_object['position']['z']

        bbox3d = goal_object['objectBounds']['objectBoundsCorners']
        lower_box = bbox3d[:4]
        upper_box = bbox3d[4:]

        corners = [(pt['x'], pt['z']) for pt in upper_box]
        a, b, c, d = corners
        upper_polygon = sympy.Polygon(a, b, c, d)

        # get agent center xz
        agent_center_xz = scene_metadata['agent']['position']['x'], \
            scene_metadata['agent']['position']['x']

        # calculate center_line from center of object to agent in the xz plane
        center_line = sympy.Segment(sympy.Point(goal_object_xz_center), \
                sympy.Point(agent_center_xz))

        # find the interesection of the center_line and the polygon
        intersections = [
            i.evalf() for i in upper_polygon.intersection(center_line)
        ]

        # check for 0, 1 or more intersections
        num_intersections = len(intersections)
        if num_intersections:
            # two intersections should only occur on a corner
            intersection = intersections[0]
            distance_to_object = sympy.Point(agent_center_xz).distance(
                intersection).evalf()
            if distance_to_object <= MAX_REACH_DISTANCE:
                reward = GOAL_ACHIEVED
        else:
            # 0 intersections means the agent is "inside" of upper box bounds
            reward = GOAL_ACHIEVED

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
            return reward

        objects = scene_event.metadata['objects']

        target_id, action, goal_id = relationship
        target_object = MCS_Reward.__get_object_from_list(objects, target_id)
        goal_object = MCS_Reward.__get_object_from_list(objects, goal_id)

        # if either object is None, then return default reward
        if goal_object is None or target_object is None:
            return reward

        # if either objects are held, the goal has not been achieved
        if goal_object['isPickedUp'] or target_object['isPickedUp']:
            return reward

        # ensure distance between objects are below some threshold
        MAX_MOVE_DISTANCE

        # actions are next_to or on_top_of
        # or the target is on top of the goal
        # going to use similar code to traversal goal

        return reward

    @staticmethod
    def calculate_default_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''Returns the default reward. Scene event is passed in but ignored.'''
        return GOAL_NOT_ACHIEVED

    @staticmethod
    def retrieve_reward(goal: MCS_Goal, scene_metadata: Dict) -> int:
        '''
        Determine if the agent achieved the objective/task/goal.

        Args:
            goal: MCS_Goal
            scene_metadata: Dict

        Returns:
            int: reward is 1 if goal achieved, 0 otherwise

        '''
        
        category = None
        if goal is not None:
            category = goal.metadata.get('category', None)

        switch = {
            MCS_Goal_Category.RETRIEVAL.name: MCS_Reward.calc_retrieval_reward,
            MCS_Goal_Category.TRANSFERRAL.name:
            MCS_Reward.calc_transferral_reward,
            MCS_Goal_Category.TRAVERSAL.name: MCS_Reward.calc_traversal_reward,
        }

        return switch.get(category,
                          MCS_Reward.calculate_default_reward)(goal,
                                                               scene_metadata)
