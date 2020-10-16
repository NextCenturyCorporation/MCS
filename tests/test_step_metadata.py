import unittest
import textwrap

import machine_common_sense as mcs


class Test_StepMetadata(unittest.TestCase):

    str_output = '''    {
        "action_list": [],
        "camera_aspect_ratio": [
            0.0,
            0.0
        ],
        "camera_clipping_planes": [
            0.0,
            0.0
        ],
        "camera_field_of_view": 0.0,
        "camera_height": 0.0,
        "depth_data_list": [],
        "goal": {
            "action_list": null,
            "category": "",
            "description": "",
            "habituation_total": 0,
            "last_preview_phase_step": 0,
            "last_step": null,
            "metadata": {}
        },
        "habituation_trial": null,
        "head_tilt": 0.0,
        "image_list": [],
        "object_list": [],
        "object_mask_list": [],
        "pose": "UNDEFINED",
        "position": {},
        "return_status": "UNDEFINED",
        "reward": 0,
        "rotation": 0.0,
        "step_number": 0,
        "structural_object_list": []
    }'''

    @classmethod
    def setUpClass(cls):
        cls.step_metadata = mcs.StepMetadata()

    @classmethod
    def tearDownClass(cls):
        # nothing to do here
        pass

    def test_action_list(self):
        self.assertFalse(self.step_metadata.action_list)
        self.assertIsInstance(self.step_metadata.action_list, list)

    def test_camera_aspect_ratio(self):
        self.assertIsInstance(self.step_metadata.camera_aspect_ratio, tuple)

    def test_camera_clipping_planes(self):
        self.assertIsInstance(
            self.step_metadata.camera_clipping_planes, tuple)

    def test_camera_field_of_view(self):
        self.assertIsInstance(self.step_metadata.camera_field_of_view, float)

    def test_camera_height(self):
        self.assertIsInstance(self.step_metadata.camera_height, float)

    def test_depth_data_list(self):
        self.assertFalse(self.step_metadata.depth_data_list)
        self.assertIsInstance(self.step_metadata.depth_data_list, list)

    def test_goal(self):
        self.assertIsInstance(self.step_metadata.goal, mcs.GoalMetadata)

    def test_habituation_trial(self):
        self.assertEqual(self.step_metadata.habituation_trial, None)

    def test_head_tilt(self):
        self.assertAlmostEqual(self.step_metadata.head_tilt, 0.0)
        self.assertIsInstance(self.step_metadata.head_tilt, float)

    def test_image_list(self):
        self.assertFalse(self.step_metadata.image_list)
        self.assertIsInstance(self.step_metadata.image_list, list)

    def test_object_list(self):
        self.assertFalse(self.step_metadata.object_list)
        self.assertIsInstance(self.step_metadata.object_list, list)

    def test_object_mask_list(self):
        self.assertFalse(self.step_metadata.object_mask_list)
        self.assertIsInstance(self.step_metadata.object_mask_list, list)

    def test_pose(self):
        self.assertEqual(self.step_metadata.pose, mcs.Pose.UNDEFINED.value)
        self.assertIsInstance(self.step_metadata.pose, str)

    def test_position(self):
        self.assertIsInstance(self.step_metadata.position, dict)

    def test_return_status(self):
        self.assertEqual(
            self.step_metadata.return_status,
            mcs.ReturnStatus.UNDEFINED.value)
        self.assertIsInstance(self.step_metadata.return_status, str)

    def test_reward(self):
        self.assertEqual(self.step_metadata.reward, 0)
        self.assertIsInstance(self.step_metadata.reward, int)

    def test_rotation(self):
        self.assertAlmostEqual(self.step_metadata.rotation, 0.0)
        self.assertIsInstance(self.step_metadata.rotation, float)

    def test_step_number(self):
        self.assertEqual(self.step_metadata.step_number, 0)
        self.assertIsInstance(self.step_metadata.step_number, int)

    def test_structural_object_list(self):
        self.assertFalse(self.step_metadata.structural_object_list)
        self.assertIsInstance(
            self.step_metadata.structural_object_list, list)

    def test_str(self):
        self.assertEqual(str(self.step_metadata),
                         textwrap.dedent(self.str_output))
