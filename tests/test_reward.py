import unittest
from typing import Tuple

from shapely import geometry

import machine_common_sense as mcs


class TestReward(unittest.TestCase):

    def test_default_reward(self):
        goal = mcs.GoalMetadata()
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=1,
            reach=1.0, steps_on_lava=0)
        self.assertEqual(reward, -mcs.reward.STEP_PENALTY)
        self.assertIsInstance(reward, float)

    def test_none_goal(self):
        goal = None
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=5,
            reach=1.0, steps_on_lava=0)
        self.assertEqual(reward, -(5 * mcs.reward.STEP_PENALTY))
        self.assertIsInstance(reward, float)

    def test_penalty_step_calcuation(self):
        goal = None
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=456,
            reach=1.0, steps_on_lava=0)
        penalty = 0 - (456 * mcs.reward.STEP_PENALTY)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_steps_with_config_step_penalty(self):
        goal = None
        config_step_penalty = 0.25
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=456,
            reach=1.0, steps_on_lava=0, step_penalty=config_step_penalty)
        penalty = 0 - (456 * config_step_penalty)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_penalty_on_lava(self):
        goal = None
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=1,
            reach=1.0, steps_on_lava=1)
        penalty = 0 - (1 * mcs.reward.STEP_PENALTY) - mcs.reward.LAVA_PENALTY
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_penalty_on_lava_multiple_steps(self):
        goal = None
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=456,
            reach=1.0, steps_on_lava=2)
        penalty = 0 - (456 * mcs.reward.STEP_PENALTY) - \
            (2 * mcs.reward.LAVA_PENALTY)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_penalty_on_lava_multiple_steps_with_config_lava_penalty(self):
        goal = None
        config_lava_penalty = 10.5
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=456,
            reach=1.0, steps_on_lava=2, lava_penalty=config_lava_penalty)
        penalty = 0 - (456 * mcs.reward.STEP_PENALTY) - \
            (2 * config_lava_penalty)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_steps_and_lava_config_penalty(self):
        goal = None
        config_lava_penalty = 10.5
        config_step_penalty = 0.25
        reward = mcs.Reward.calculate_reward(
            goal, objects=[{}], agent={}, number_steps=456,
            reach=1.0, steps_on_lava=2, lava_penalty=config_lava_penalty,
            step_penalty=config_step_penalty)
        penalty = 0 - (456 * config_step_penalty) - \
            (2 * config_lava_penalty)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_steps_and_lava_config_is_none(self):
        current_score = 0
        config_lava_penalty = None
        config_step_penalty = None
        steps_on_lava = None
        reward = mcs.Reward._adjust_score_penalty(
            current_score=current_score, number_steps=456,
            steps_on_lava=steps_on_lava,
            lava_penalty=config_lava_penalty, step_penalty=config_step_penalty)
        penalty = current_score - (456 * mcs.reward.STEP_PENALTY) - \
            (0 * mcs.reward.LAVA_PENALTY)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_steps_and_lava_config_penalty_score_is_not_one(self):
        current_score = 0
        config_lava_penalty = 10.5
        config_step_penalty = 0.25
        reward = mcs.Reward._adjust_score_penalty(
            current_score=current_score, number_steps=456, steps_on_lava=8,
            lava_penalty=config_lava_penalty, step_penalty=config_step_penalty)
        penalty = current_score - (456 * config_step_penalty) - \
            (8 * config_lava_penalty)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_steps_and_lava_config_penalty_score_is_one(self):
        current_score = 1
        config_lava_penalty = 10.5
        config_step_penalty = 0.25
        reward = mcs.Reward._adjust_score_penalty(
            current_score=current_score, number_steps=456, steps_on_lava=8,
            lava_penalty=config_lava_penalty, step_penalty=config_step_penalty)
        penalty = current_score - ((456 - 1) * config_step_penalty)
        self.assertEqual(reward, penalty)
        self.assertIsInstance(reward, float)

    def test_target_in_empty_object_list(self):
        obj_list = []
        target_id = ''
        self.assertIsNone(
            mcs.Reward._Reward__get_object_from_list(
                obj_list, target_id))

    def test_target_in_object_list(self):
        obj_list = []
        for i in range(10):
            obj = {"objectId": str(i)}
            obj_list.append(obj)
        target_id = '7'
        results = mcs.Reward._Reward__get_object_from_list(
            obj_list, target_id)
        self.assertTrue(results)
        self.assertIsInstance(results, dict)
        self.assertEqual(results['objectId'], target_id)

    def test_target_not_in_object_list(self):
        obj_list = [{"objectId": str(i)} for i in range(10)]
        target_id = '111'  # not in list
        results = mcs.Reward._Reward__get_object_from_list(
            obj_list, target_id)
        self.assertIsNone(results)

    def test_duplicate_target_ids_in_list(self):
        obj_list = [{"objectId": str(i)} for i in range(10)]
        # add duplicate object
        obj_list.append({"objectId": '7', "duplicate": True})
        target_id = '7'
        results = mcs.Reward._Reward__get_object_from_list(
            obj_list, target_id)
        self.assertTrue(results)
        self.assertIsInstance(results, dict)
        self.assertEqual(results['objectId'], target_id)
        # expect that method still returns the first instance and not the
        # duplicate
        self.assertFalse('duplicate' in results)

    def test_convert_object_to_planar_polygon(self):
        goal_object = {'objectBounds': {'objectBoundsCorners': []}}
        # create lower plane (y = 0)
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 0.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 0.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 0.0, 'y': 0.0, 'z': 1.0})
        # create upper plane (y = 1)
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 0.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 1.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 1.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 0.0, 'y': 1.0, 'z': 1.0})

        polygon = mcs.Reward._convert_object_to_planar_polygon(goal_object)

        self.assertIsInstance(polygon, geometry.Polygon)
        self.assertEqual(len(list(polygon.exterior.coords)), 5)
        self.assertIsInstance(list(polygon.exterior.coords)[0], Tuple)

    def test_convert_skewed_object_to_planar_polygon(self):
        goal_object = {'objectBounds': {'objectBoundsCorners': []}}

        # create lower plane (y = 0)
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 0.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 0.0, 'z': 0.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 0.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 0.0, 'y': 0.0, 'z': 1.0})
        # create upper plane (y = 1) but shifted over x and z by 1
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 1.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 2.0, 'y': 1.0, 'z': 1.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 2.0, 'y': 1.0, 'z': 2.0})
        goal_object['objectBounds']['objectBoundsCorners'].append(
            {'x': 1.0, 'y': 1.0, 'z': 2.0})

        polygon = mcs.Reward._convert_object_to_planar_polygon(goal_object)

        self.assertIsInstance(polygon, geometry.Polygon)
        self.assertEqual(len(list(polygon.exterior.coords)), 7)
        self.assertIsInstance(list(polygon.exterior.coords)[0], Tuple)

    def test_retrieval_reward(self):
        goal = mcs.GoalMetadata()
        goal.metadata['target'] = {'id': '0'}
        obj_list = []
        for i in range(10):
            obj = {"objectId": str(i), 'wasPickedUp': not i}
            obj_list.append(obj)
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, agent={},
                                                   performer_reach=1.0)
        self.assertEqual(reward, 1)
        self.assertIsInstance(reward, int)

    def test_retrieval_reward_nothing_pickedup(self):
        goal = mcs.GoalMetadata()
        goal.metadata['target'] = {'id': '0'}
        obj_list = []
        for i in range(10):
            obj = {"objectId": str(i), 'wasPickedUp': False}
            obj_list.append(obj)
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, agent={},
                                                   performer_reach=1.0)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_retrieval_reward_multi_target(self):
        goal = mcs.GoalMetadata()
        goal.metadata['targets'] = [{'id': '0'}, {'id': '1'}, {'id': '2'}]
        obj_list = []
        for i in range(10):
            obj_list.append({'objectId': str(i), 'wasPickedUp': True})
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, agent={},
                                                   performer_reach=1.0)
        self.assertEqual(reward, 1)
        self.assertIsInstance(reward, int)

    def test_retrieval_reward_multi_target_nothing_pickedup(self):
        goal = mcs.GoalMetadata()
        goal.metadata['targets'] = [{'id': '0'}, {'id': '1'}, {'id': '2'}]
        obj_list = []
        for i in range(10):
            obj_list.append({'objectId': str(i), 'wasPickedUp': False})
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, agent={},
                                                   performer_reach=1.0)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_retrieval_reward_multi_target_some_pickedup(self):
        goal = mcs.GoalMetadata()
        goal.metadata['targets'] = [{'id': '0'}, {'id': '1'}, {'id': '2'}]
        obj_list = []
        for i in range(10):
            obj_list.append({'objectId': str(i), 'wasPickedUp': (i == 0)})
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, agent={},
                                                   performer_reach=1.0)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_retrieval_reward_multi_target_more_pickedup(self):
        goal = mcs.GoalMetadata()
        goal.metadata['targets'] = [{'id': '0'}, {'id': '1'}, {'id': '2'}]
        obj_list = []
        for i in range(10):
            obj_list.append({'objectId': str(i), 'wasPickedUp': (i != 0)})
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, agent={},
                                                   performer_reach=1.0)
        self.assertEqual(reward, 0)
        self.assertIsInstance(reward, int)

    def test_retrieval_reward_multi_target_pickup_one_of_two(self):
        goal = mcs.GoalMetadata()
        goal.metadata['targets'] = [{'id': '0'}, {'id': '1'}]
        goal.metadata['pickup_number'] = 1

        # Test: Picking up no targets should return a reward of 0
        obj_list = [
            {'objectId': '0', 'wasPickedUp': False},
            {'objectId': '1', 'wasPickedUp': False}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 0)

        # Test: Picking up only the 1st target should return a reward of 1
        obj_list = [
            {'objectId': '0', 'wasPickedUp': True},
            {'objectId': '1', 'wasPickedUp': False}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 1)

        # Test: Picking up only the 2nd target should return a reward of 1
        obj_list = [
            {'objectId': '0', 'wasPickedUp': False},
            {'objectId': '1', 'wasPickedUp': True}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 1)

        # Test: Picking up all targets should return a reward of 1
        obj_list = [
            {'objectId': '0', 'wasPickedUp': True},
            {'objectId': '1', 'wasPickedUp': True}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 1)

    def test_retrieval_reward_multi_target_pickup_two_of_three(self):
        goal = mcs.GoalMetadata()
        goal.metadata['targets'] = [{'id': '0'}, {'id': '1'}, {'id': '2'}]
        goal.metadata['pickup_number'] = 2

        # Test: Picking up no targets should return a reward of 0
        obj_list = [
            {'objectId': '0', 'wasPickedUp': False},
            {'objectId': '1', 'wasPickedUp': False},
            {'objectId': '2', 'wasPickedUp': False}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 0)

        # Test: Picking up only the 1st target should return a reward of 0
        obj_list = [
            {'objectId': '0', 'wasPickedUp': True},
            {'objectId': '1', 'wasPickedUp': False},
            {'objectId': '2', 'wasPickedUp': False}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 0)

        # Test: Picking up only the 2nd target should return a reward of 0
        obj_list = [
            {'objectId': '0', 'wasPickedUp': False},
            {'objectId': '1', 'wasPickedUp': True},
            {'objectId': '2', 'wasPickedUp': False}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 0)

        # Test: Picking up only the 3rd target should return a reward of 0
        obj_list = [
            {'objectId': '0', 'wasPickedUp': False},
            {'objectId': '1', 'wasPickedUp': False},
            {'objectId': '2', 'wasPickedUp': True}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 0)

        # Test: Picking up the 1st and 2nd targets should return a reward of 1
        obj_list = [
            {'objectId': '0', 'wasPickedUp': True},
            {'objectId': '1', 'wasPickedUp': True},
            {'objectId': '2', 'wasPickedUp': False}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 1)

        # Test: Picking up the 1st and 3rd targets should return a reward of 1
        obj_list = [
            {'objectId': '0', 'wasPickedUp': True},
            {'objectId': '1', 'wasPickedUp': False},
            {'objectId': '2', 'wasPickedUp': True}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 1)

        # Test: Picking up the 2nd and 3rd targets should return a reward of 1
        obj_list = [
            {'objectId': '0', 'wasPickedUp': False},
            {'objectId': '1', 'wasPickedUp': True},
            {'objectId': '2', 'wasPickedUp': True}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 1)

        # Test: Picking up all targets should return a reward of 1
        obj_list = [
            {'objectId': '0', 'wasPickedUp': True},
            {'objectId': '1', 'wasPickedUp': True},
            {'objectId': '2', 'wasPickedUp': True}
        ]
        reward = mcs.Reward._calc_retrieval_reward(goal, obj_list, {}, 1.0)
        self.assertEqual(reward, 1)


if __name__ == '__main__':
    unittest.main()
