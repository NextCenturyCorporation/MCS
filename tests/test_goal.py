import unittest
import textwrap

import machine_common_sense as mcs


class Test_GoalMetadata(unittest.TestCase):

    str_output = '''    {
        "action_list": null,
        "category": "",
        "description": "",
        "domain_list": [],
        "info_list": [],
        "last_preview_phase_step": 0,
        "last_step": null,
        "type_list": [],
        "metadata": {}
    }'''

    @classmethod
    def setUpClass(cls):
        cls.goal = mcs.GoalMetadata()

    @classmethod
    def tearDownClass(cls):
        pass

    def test_action_list(self):
        self.assertIsNone(self.goal.action_list)

    def test_category(self):
        self.assertEqual(self.goal.category, '')

    def test_description(self):
        self.assertEqual(self.goal.description, '')

    def test_domain_list(self):
        self.assertEqual(len(self.goal.domain_list), 0)
        self.assertIsInstance(self.goal.domain_list, list)

    def test_info_list(self):
        self.assertEqual(len(self.goal.info_list), 0)
        self.assertIsInstance(self.goal.info_list, list)

    def test_last_preview_phase(self):
        self.assertEqual(self.goal.last_preview_phase_step, 0)
        self.assertIsInstance(self.goal.last_preview_phase_step, int)

    def test_last_step(self):
        self.assertIsNone(self.goal.last_step)

    def test_type_list(self):
        self.assertEqual(len(self.goal.type_list), 0)
        self.assertIsInstance(self.goal.type_list, list)

    def test_metadata(self):
        self.assertFalse(self.goal.metadata)
        self.assertIsInstance(self.goal.metadata, dict)

    def test_str(self):
        self.assertEqual(str(self.goal), textwrap.dedent(self.str_output))
