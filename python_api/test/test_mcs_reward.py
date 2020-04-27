import unittest
import math
import sympy

from machine_common_sense.mcs_reward import MCS_Reward
from machine_common_sense.mcs_goal import MCS_Goal
from machine_common_sense.mcs_object import MCS_Object
from machine_common_sense.mcs_util import MCS_Util


class Test_MCS_Reward(unittest.TestCase):

    def test_default_reward(self):
        goal = MCS_Goal()
        reward = MCS_Reward.calculate_reward(goal, objects={}, agent={})
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_none_goal(self):
        goal = None
        reward = MCS_Reward.calculate_reward(goal, objects={}, agent={})
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_target_in_empty_object_list(self):
        obj_list = []
        target_id = ''
        self.assertIsNone(MCS_Reward._MCS_Reward__get_object_from_list(obj_list, target_id))

    def test_target_in_object_list(self):
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i)}
            obj_list.append(obj)
        target_id = '7'
        results = MCS_Reward._MCS_Reward__get_object_from_list(obj_list, target_id)
        self.assertTrue(results)
        self.assertIsInstance(results, dict)
        self.assertEqual(results['objectId'], target_id)

    def test_target_not_in_object_list(self):
        obj_list = []
        for i in range(10):
            obj_list.append({"objectId":str(i)})
        target_id = '111' # not in list
        results = MCS_Reward._MCS_Reward__get_object_from_list(obj_list, target_id)
        self.assertIsNone(results)

    def test_duplicate_target_ids_in_list(self):
        obj_list = []
        for i in range(10):
            obj_list.append({"objectId":str(i)})
        # add duplicate object
        obj_list.append({"objectId":'7', "duplicate": True})
        target_id = '7'
        results = MCS_Reward._MCS_Reward__get_object_from_list(obj_list, target_id)
        self.assertTrue(results)
        self.assertIsInstance(results, dict)
        self.assertEqual(results['objectId'], target_id)
        # expect that method still returns the first instance and not the duplicate
        self.assertFalse('duplicate' in results)

    def test_convert_object_bounds_to_polygons(self):
        goal_object = {'objectBounds': {'objectBoundsCorners': []}}
        # create lower plane (y = 0)
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0, 'z': 1.0})
        # create upper plane (y = 1)
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0, 'z': 1.0})

        lower, upper = MCS_Reward._convert_bounds_to_polygons(goal_object)

        self.assertIsInstance(lower, sympy.Polygon)
        self.assertIsInstance(upper, sympy.Polygon)
        self.assertEqual(len(lower.vertices), 4)
        self.assertEqual(len(upper.vertices), 4)
        self.assertIsInstance(lower.vertices[0], sympy.Point2D)
        self.assertIsInstance(upper.vertices[0], sympy.Point2D)

    def test_distance_to_object_within_polygon(self):
        goal_object = {'objectBounds': {'objectBoundsCorners': []}}
        # create lower plane (y = 0)
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0, 'z': 1.0})
        # create upper plane (y = 1)
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0, 'z': 1.0})
        # goal object center position
        goal_object['position'] = {'x': 0.5, 'z': 0.5}

        dist = MCS_Reward._MCS_Reward__calc_distance_to_goal((0.5, 0.5), goal_object)
        self.assertIsInstance(dist, float)
        self.assertEqual(dist, 0.0)

    def test_distance_to_object_outside_polygon(self):
        goal_object = {'objectBounds': {'objectBoundsCorners': []}}
        # create lower plane (y = 0)
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0, 'z': 1.0})
        # create upper plane (y = 1)
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0, 'z': 1.0})
        # goal object center position
        goal_object['position'] = {'x': 0.5, 'z': 0.5}

        dist = MCS_Reward._MCS_Reward__calc_distance_to_goal((1.5, 1.5), goal_object)
        self.assertIsInstance(dist, float)
        self.assertTrue(dist)
        # distance to edge is 0.5 in both dimensions ~= 0.707
        self.assertAlmostEqual(dist, math.sqrt(0.5*0.5 + 0.5*0.5))

    def test_retrieval_reward(self):
        goal = MCS_Goal()
        goal.metadata['target'] = {'id': '0'}
        obj_list = []
        for i in range(10):
            obj = {"objectId": str(i), 'isPickedUp': not i}
            obj_list.append(obj)
        reward = MCS_Reward._calc_retrieval_reward(goal, obj_list, agent={})
        self.assertEqual(reward, 1)
        self.assertIsInstance(reward, int)

    def test_retrieval_reward_nothing_pickedup(self):
        goal = MCS_Goal()
        goal.metadata['target'] = {'id': '0'}
        obj_list = []
        for i in range(10):
            obj = {"objectId": str(i), 'isPickedUp': False}
            obj_list.append(obj)
        reward = MCS_Reward._calc_retrieval_reward(goal, obj_list, agent={})
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_traversal_reward(self):
        goal = MCS_Goal()
        goal.metadata['target'] = {'id': '0'}
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 1.0})
            # create upper plane (y = 1)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 1.0})
            obj['position'] = {'x': 0.5 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':0.0}}
        reward = MCS_Reward._calc_traversal_reward(goal, obj_list, agent)
        self.assertEqual(reward, 1)
        self.assertIsInstance(reward, int)

    def test_traversal_reward_outside_agent_reach(self):
        goal = MCS_Goal()
        goal.metadata['target'] = {'id': '0'}
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 1.0})
            # create upper plane (y = 1)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 1.0})
            obj['position'] = {'x': 0.5 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':-1.0}}
        reward = MCS_Reward._calc_traversal_reward(goal, obj_list, agent)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_traversal_reward_with_missing_target(self):
        goal = MCS_Goal()
        goal.metadata['target'] = {'id': '111'} # missing target
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 1.0})
            # create upper plane (y = 1)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 1.0})
            obj['position'] = {'x': 0.5 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':0.0}}
        reward = MCS_Reward._calc_traversal_reward(goal, obj_list, agent)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_transferral_reward_with_missing_relationship(self):
        goal = MCS_Goal()
        goal.metadata['target'] = {'id': '0'}
        goal.metadata['relationship'] = []
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 1.0})
            # create upper plane (y = 1)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 1.0})
            obj['position'] = {'x': 0.5 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':0.0}}
        reward = MCS_Reward._calc_transferral_reward(goal, obj_list, agent)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_transferral_reward_next_to(self):
        goal = MCS_Goal()
        goal.metadata['relationship'] = [{'id': '0'}, 'next_to', {'id': '1'}]
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 1.0})
            # create upper plane (y = 1)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 1.0})
            obj['position'] = {'x': 0.5 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':0.0}}
        reward = MCS_Reward._calc_transferral_reward(goal, obj_list, agent)
        self.assertEqual(reward, 1)
        self.assertIsInstance(reward, int)

    def test_transferral_reward_next_to_with_pickedup_object(self):
        goal = MCS_Goal()
        goal.metadata['relationship'] = [{'id': '0'}, 'next_to', {'id': '1'}]
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}, "isPickedUp": True}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 0.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 0.0, 'z': 1.0})
            # create upper plane (y = 1)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0 + i, 'y': 1.0, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0 + i, 'y': 1.0, 'z': 1.0})
            obj['position'] = {'x': 0.5 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':0.0}}
        reward = MCS_Reward._calc_transferral_reward(goal, obj_list, agent)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_transferral_reward_on_top_of(self):
        goal = MCS_Goal()
        goal.metadata['relationship'] = [{'id': '1'}, 'on_top_of', {'id': '0'}]
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0 + i, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0 + i, 'z': 1.0})
            # create upper plane (y = 1) + i
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0 + i, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0 + i, 'z': 1.0})
            obj['position'] = {'x': 0.5, 'y': 0.0 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':0.0}}
        reward = MCS_Reward._calc_transferral_reward(goal, obj_list, agent)
        self.assertEqual(reward, 1)
        self.assertIsInstance(reward, int)

    def test_transferral_reward_on_top_of_with_pickedup_object(self):
        goal = MCS_Goal()
        goal.metadata['relationship'] = [{'id': '1'}, 'on_top_of', {'id': '0'}]
        obj_list = []
        for i in range(10):
            obj = {"objectId":str(i), "objectBounds": {"objectBoundsCorners": []}, "isPickedUp": True}
            # create lower plane (y = 0)
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 0.0 + i, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 0.0 + i, 'z': 1.0})
            # create upper plane (y = 1) + i
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0 + i, 'z': 0.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':1.0, 'y': 1.0 + i, 'z': 1.0})
            obj['objectBounds']['objectBoundsCorners'].append({'x':0.0, 'y': 1.0 + i, 'z': 1.0})
            obj['position'] = {'x': 0.5, 'y': 0.0 + i, 'z': 0.5}
            obj_list.append(obj)
        agent = {'position': {'x':-0.9, 'y': 0.5, 'z':0.0}}
        reward = MCS_Reward._calc_transferral_reward(goal, obj_list, agent)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)