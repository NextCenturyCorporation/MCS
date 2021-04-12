import unittest

from machine_common_sense.scene_history import SceneHistory


class TestSceneHistory(unittest.TestCase):

    def test_default_initialization(self):
        scene_history = SceneHistory()
        self.assertEqual(scene_history.step, -1)
        self.assertIsNone(scene_history.action)
        self.assertIsNone(scene_history.args)
        self.assertIsNone(scene_history.params)
        self.assertIsNone(scene_history.classification)
        self.assertIsNone(scene_history.confidence)
        self.assertIsNone(scene_history.violations_xy_list)
        self.assertIsNone(scene_history.internal_state)
        self.assertEqual(scene_history.delta_time_millis, 0)
        self.assertIsNone(scene_history.output)

    def test_str(self):
        scene_history = SceneHistory()
        print(scene_history)
        print(vars(scene_history))
        print(scene_history.__dict__)
