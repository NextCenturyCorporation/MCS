import textwrap
import unittest

import machine_common_sense as mcs


class TestGoalMetadata(unittest.TestCase):

    str_output = '''    {
        "action_list": null,
        "category": "",
        "description": "",
        "habituation_total": 0,
        "last_preview_phase_step": 0,
        "last_step": null,
        "metadata": {},
        "steps_allowed_in_lava": 0
    }'''

    @classmethod
    def setUpClass(cls):
        cls.goal_metadata = mcs.GoalMetadata()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_action_list(self):
        self.assertIsNone(self.goal_metadata.action_list)

    def test_category(self):
        self.assertEqual(self.goal_metadata.category, '')

    def test_description(self):
        self.assertEqual(self.goal_metadata.description, '')

    def test_habituation_total(self):
        self.assertEqual(self.goal_metadata.habituation_total, 0)
        self.assertIsInstance(self.goal_metadata.habituation_total, int)

    def test_last_preview_phase(self):
        self.assertEqual(self.goal_metadata.last_preview_phase_step, 0)
        self.assertIsInstance(self.goal_metadata.last_preview_phase_step, int)

    def test_last_step(self):
        self.assertIsNone(self.goal_metadata.last_step)

    def test_metadata(self):
        self.assertFalse(self.goal_metadata.metadata)
        self.assertIsInstance(self.goal_metadata.metadata, dict)

    def test_retrieve_action_list_with_preview_phase(self):
        goal_metadata = mcs.GoalMetadata(
            action_list=[],
            last_preview_phase_step=10,
            last_step=10)
        self.assertEqual(
            goal_metadata.retrieve_action_list_at_step(0), [(
                'Pass', {})])
        self.assertEqual(
            goal_metadata.retrieve_action_list_at_step(9), [(
                'Pass', {})])
        self.assertEqual(self.goal_metadata.retrieve_action_list_at_step(10), [
            ('CloseObject', {}),
            ('DropObject', {}),
            ('MoveAhead', {}),
            ('MoveBack', {}),
            ('MoveLeft', {}),
            ('MoveRight', {}),
            ('OpenObject', {}),
            ('PickupObject', {}),
            ('PullObject', {}),
            ('PushObject', {}),
            ('PutObject', {}),
            ('TorqueObject', {}),
            ('RotateObject', {}),
            ('MoveObject', {}),
            ('InteractWithAgent', {}),
            ('LookUp', {}),
            ('LookDown', {}),
            ('RotateLeft', {}),
            ('RotateRight', {}),
            ('EndScene', {}),
            ('Pass', {})
        ])

    def test_retrieve_action_list_after_preview_phase(self):
        goal_metadata = mcs.GoalMetadata(
            action_list=[['MoveBack']],
            last_preview_phase_step=10,
            last_step=11)
        self.assertEqual(
            goal_metadata.retrieve_action_list_at_step(0), [(
                'Pass', {})])
        self.assertEqual(
            goal_metadata.retrieve_action_list_at_step(9), [(
                'Pass', {})])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(10), [
            ('MoveBack', {})
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(11), [])

    def test_retrieve_action_list_at_final_step(self):
        goal_metadata = mcs.GoalMetadata(
            action_list=[],
            last_step=10)
        self.assertEqual(
            goal_metadata.retrieve_action_list_at_step(10), [])

    def test_retrieve_action_list_after_final_step(self):
        goal_metadata = mcs.GoalMetadata(
            action_list=[],
            last_step=10)
        self.assertEqual(
            goal_metadata.retrieve_action_list_at_step(15), [])

    def test_retrieve_action_too_many_steps_lava_default(self):
        goal_metadata = mcs.GoalMetadata(
            action_list=[],
            last_step=10)
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(11, 1), [
            ('EndScene', {})
        ])

    def test_retrieve_action_too_many_steps(self):
        goal_metadata = mcs.GoalMetadata(
            action_list=[],
            last_step=10,
            steps_allowed_in_lava=3)
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(11, 1), [])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(11, 4), [
            ('EndScene', {})
        ])

    def test_retrieve_action_list_at_step(self):
        self.assertEqual(self.goal_metadata.retrieve_action_list_at_step(0), [
            ('CloseObject', {}),
            ('DropObject', {}),
            ('MoveAhead', {}),
            ('MoveBack', {}),
            ('MoveLeft', {}),
            ('MoveRight', {}),
            ('OpenObject', {}),
            ('PickupObject', {}),
            ('PullObject', {}),
            ('PushObject', {}),
            ('PutObject', {}),
            ('TorqueObject', {}),
            ('RotateObject', {}),
            ('MoveObject', {}),
            ('InteractWithAgent', {}),
            ('LookUp', {}),
            ('LookDown', {}),
            ('RotateLeft', {}),
            ('RotateRight', {}),
            ('EndScene', {}),
            ('Pass', {})
        ])
        self.assertEqual(self.goal_metadata.retrieve_action_list_at_step(10), [
            ('CloseObject', {}),
            ('DropObject', {}),
            ('MoveAhead', {}),
            ('MoveBack', {}),
            ('MoveLeft', {}),
            ('MoveRight', {}),
            ('OpenObject', {}),
            ('PickupObject', {}),
            ('PullObject', {}),
            ('PushObject', {}),
            ('PutObject', {}),
            ('TorqueObject', {}),
            ('RotateObject', {}),
            ('MoveObject', {}),
            ('InteractWithAgent', {}),
            ('LookUp', {}),
            ('LookDown', {}),
            ('RotateLeft', {}),
            ('RotateRight', {}),
            ('EndScene', {}),
            ('Pass', {})
        ])

    def test_retrieve_action_list_hidden_endhabituation_params(self):
        goal_metadata = mcs.GoalMetadata(action_list=[
            ['EndHabituation,xPosition=0,zPosition=0,yRotation=90'],
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(0), [
            ('EndHabituation', {})
        ])

    def test_retrieve_action_list_at_step_with_custom_action_list(self):
        goal_metadata = mcs.GoalMetadata(action_list=[
            ['Pass'],
            ['LookDown', 'LookUp', 'RotateLeft', 'RotateRight', 'Pass'],
            [],
            ['EndHabituation,xPosition=0,zPosition=0,yRotation=90'],
            [('PickupObject', {'objectId': 'target'})]
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(0), [
            ('Pass', {})
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(1), [
            ('LookDown', {}),
            ('LookUp', {}),
            ('RotateLeft', {}),
            ('RotateRight', {}),
            ('Pass', {})
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(2), [
            ('CloseObject', {}),
            ('DropObject', {}),
            ('MoveAhead', {}),
            ('MoveBack', {}),
            ('MoveLeft', {}),
            ('MoveRight', {}),
            ('OpenObject', {}),
            ('PickupObject', {}),
            ('PullObject', {}),
            ('PushObject', {}),
            ('PutObject', {}),
            ('TorqueObject', {}),
            ('RotateObject', {}),
            ('MoveObject', {}),
            ('InteractWithAgent', {}),
            ('LookUp', {}),
            ('LookDown', {}),
            ('RotateLeft', {}),
            ('RotateRight', {}),
            ('EndScene', {}),
            ('Pass', {})
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(3), [
            ('EndHabituation', {})
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(4), [
            ('PickupObject', {'objectId': 'target'})
        ])
        self.assertEqual(goal_metadata.retrieve_action_list_at_step(10), [
            ('CloseObject', {}),
            ('DropObject', {}),
            ('MoveAhead', {}),
            ('MoveBack', {}),
            ('MoveLeft', {}),
            ('MoveRight', {}),
            ('OpenObject', {}),
            ('PickupObject', {}),
            ('PullObject', {}),
            ('PushObject', {}),
            ('PutObject', {}),
            ('TorqueObject', {}),
            ('RotateObject', {}),
            ('MoveObject', {}),
            ('InteractWithAgent', {}),
            ('LookUp', {}),
            ('LookDown', {}),
            ('RotateLeft', {}),
            ('RotateRight', {}),
            ('EndScene', {}),
            ('Pass', {})
        ])

    def test_str(self):
        self.assertEqual(str(self.goal_metadata),
                         textwrap.dedent(self.str_output))


if __name__ == '__main__':
    unittest.main()
