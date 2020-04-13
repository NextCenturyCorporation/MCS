import unittest
import textwrap

from machine_common_sense.mcs_step_output import MCS_Step_Output
from machine_common_sense.mcs_goal import MCS_Goal
from machine_common_sense.mcs_pose import MCS_Pose
from machine_common_sense.mcs_return_status import MCS_Return_Status


class Test_Default_MCS_Step_Output(unittest.TestCase):

    str_output = '''    {
        "action_list": [],
        "depth_mask_list": [],
        "goal": {
            "action_list": None,
            "info_list": [],
            "last_preview_phase_step": 0,
            "last_step": None,
            "task_list": [],
            "type_list": [],
            "metadata": {}
        },
        "head_tilt": 0.0,
        "image_list": [],
        "object_list": [],
        "object_mask_list": [],
        "pose": MCS_Pose.UNDEFINED,
        "position": {},
        "return_status": MCS_Return_Status.UNDEFINED,
        "rotation": 0.0,
        "step_number": 0
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
        self.assertEqual(self.mcs_step_output.pose, MCS_Pose.UNDEFINED)
        self.assertIsInstance(self.mcs_step_output.pose, MCS_Pose)

    def test_position(self):
        self.assertIsInstance(self.mcs_step_output.position, dict)

    def test_return_status(self):
        self.assertEqual(self.mcs_step_output.return_status, MCS_Return_Status.UNDEFINED)
        self.assertIsInstance(self.mcs_step_output.return_status, MCS_Return_Status)

    def test_rotation(self):
        self.assertAlmostEqual(self.mcs_step_output.rotation, 0.0)
        self.assertIsInstance(self.mcs_step_output.rotation, float)

    def test_step_number(self):
        self.assertEqual(self.mcs_step_output.step_number, 0)
        self.assertIsInstance(self.mcs_step_output.step_number, int)

    def test_str(self):
        self.assertEqual(str(self.mcs_step_output), textwrap.dedent(self.str_output))