import unittest
import textwrap

from machine_common_sense.mcs_step_output import MCS_Step_Output
from machine_common_sense.mcs_goal import MCS_Goal
from machine_common_sense.mcs_pose import MCS_Pose
from machine_common_sense.mcs_return_status import MCS_Return_Status


class Test_Default_MCS_Step_Output(unittest.TestCase):

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
        "depth_mask_list": [],
        "goal": {
            "action_list": null,
            "category": "",
            "description": "",
            "domain_list": [],
            "info_list": [],
            "last_preview_phase_step": 0,
            "last_step": null,
            "type_list": [],
            "metadata": {}
        },
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
        cls.mcs_step_output = MCS_Step_Output()

    @classmethod
    def tearDownClass(cls):
        # nothing to do here
        pass

    def test_action_list(self):
        self.assertFalse(self.mcs_step_output.action_list)
        self.assertIsInstance(self.mcs_step_output.action_list, list)

    def test_camera_aspect_ratio(self):
        self.assertIsInstance(self.mcs_step_output.camera_aspect_ratio, tuple)

    def test_camera_clipping_planes(self):
        self.assertIsInstance(
            self.mcs_step_output.camera_clipping_planes, tuple)

    def test_camera_field_of_view(self):
        self.assertIsInstance(self.mcs_step_output.camera_field_of_view, float)

    def test_camera_height(self):
        self.assertIsInstance(self.mcs_step_output.camera_height, float)

    def test_depth_mask_list(self):
        self.assertFalse(self.mcs_step_output.depth_mask_list)
        self.assertIsInstance(self.mcs_step_output.depth_mask_list, list)

    def test_goal(self):
        self.assertIsInstance(self.mcs_step_output.goal, MCS_Goal)

    def test_head_tilt(self):
        self.assertAlmostEqual(self.mcs_step_output.head_tilt, 0.0)
        self.assertIsInstance(self.mcs_step_output.head_tilt, float)

    def test_image_list(self):
        self.assertFalse(self.mcs_step_output.image_list)
        self.assertIsInstance(self.mcs_step_output.image_list, list)

    def test_object_list(self):
        self.assertFalse(self.mcs_step_output.object_list)
        self.assertIsInstance(self.mcs_step_output.object_list, list)

    def test_object_mask_list(self):
        self.assertFalse(self.mcs_step_output.object_mask_list)
        self.assertIsInstance(self.mcs_step_output.object_mask_list, list)

    def test_pose(self):
        self.assertEqual(self.mcs_step_output.pose, MCS_Pose.UNDEFINED.value)
        self.assertIsInstance(self.mcs_step_output.pose, str)

    def test_position(self):
        self.assertIsInstance(self.mcs_step_output.position, dict)

    def test_return_status(self):
        self.assertEqual(
            self.mcs_step_output.return_status,
            MCS_Return_Status.UNDEFINED.value)
        self.assertIsInstance(self.mcs_step_output.return_status, str)

    def test_reward(self):
        self.assertEqual(self.mcs_step_output.reward, 0)
        self.assertIsInstance(self.mcs_step_output.reward, int)

    def test_rotation(self):
        self.assertAlmostEqual(self.mcs_step_output.rotation, 0.0)
        self.assertIsInstance(self.mcs_step_output.rotation, float)

    def test_step_number(self):
        self.assertEqual(self.mcs_step_output.step_number, 0)
        self.assertIsInstance(self.mcs_step_output.step_number, int)

    def test_structural_object_list(self):
        self.assertFalse(self.mcs_step_output.structural_object_list)
        self.assertIsInstance(
            self.mcs_step_output.structural_object_list, list)

    def test_str(self):
        self.assertEqual(str(self.mcs_step_output),
                         textwrap.dedent(self.str_output))
