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
        "metadata": {}
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

    def test_str(self):
        self.assertEqual(str(self.goal_metadata),
                         textwrap.dedent(self.str_output))


if __name__ == '__main__':
    unittest.main()
