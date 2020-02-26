import numpy
from PIL import Image
from types import SimpleNamespace
import unittest

from mcs_action import MCS_Action
from mcs_goal import MCS_Goal
from mcs_pose import MCS_Pose
from mcs_return_status import MCS_Return_Status
from mcs_step_output import MCS_Step_Output
from mock_mcs_controller_ai2thor import Mock_MCS_Controller_AI2THOR

class Test_MCS_Controller_AI2THOR(unittest.TestCase):

    def setUp(self):
        self.controller = Mock_MCS_Controller_AI2THOR()

    def create_mock_scene_event(self, mock_scene_event_data):
        # Wrap the dict in a SimpleNamespace object to permit property access with dotted notation since the actual
        # variable is a class, not a dict.
        return SimpleNamespace(**mock_scene_event_data)

    def test_end_scene(self):
        # TODO When this function actually does anything
        pass

    def test_start_scene(self):
        # TODO MCS-15
        pass

    def test_step(self):
        # TODO MCS-15
        pass

    def test_retrieve_goal(self):
        # TODO MCS-53
        pass

    def test_retrieve_head_tilt(self):
        mock_scene_event_data = {
            "metadata": {
                "agent": {
                    "cameraHorizon": 12.34
                }
            }
        }
        actual = self.controller.retrieve_head_tilt(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, 12.34)

        mock_scene_event_data = {
            "metadata": {
                "agent": {
                    "cameraHorizon": -56.78
                }
            }
        }
        actual = self.controller.retrieve_head_tilt(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, -56.78)

    def test_retrieve_object_list(self):
        # TODO MCS-52
        pass

    def test_retrieve_pose(self):
        # TODO MCS-18
        pass

    def test_retrieve_return_status(self):
        # TODO MCS-47
        pass

    def test_save_images(self):
        image_data = numpy.array([[0]], dtype=numpy.uint8)
        class_mask_data = numpy.array([[64]], dtype=numpy.uint8)
        depth_mask_data = numpy.array([[128]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "class_segmentation_frame": class_mask_data,
            "depth_frame": depth_mask_data,
            "frame": image_data,
            "instance_segmentation_frame": object_mask_data
        }

        scene_image, depth_mask, object_mask = self.controller.save_images(self.create_mock_scene_event(
            mock_scene_event_data))

        self.assertEqual(numpy.array(depth_mask), numpy.round(depth_mask_data / 30))
        self.assertEqual(numpy.array(scene_image), image_data)
        self.assertEqual(numpy.array(object_mask), object_mask_data)

    def test_validate_and_convert_params(self):
        # TODO
        pass

    def test_wrap_output(self):
        image_data = numpy.array([[0]], dtype=numpy.uint8)
        class_mask_data = numpy.array([[64]], dtype=numpy.uint8)
        depth_mask_data = numpy.array([[128]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "class_segmentation_frame": class_mask_data,
            "depth_frame": depth_mask_data,
            "frame": image_data,
            "instance_segmentation_frame": object_mask_data,
            "metadata": {
                "agent": {
                    "cameraHorizon": 12.34
                },
                "lastActionSuccess": True
            }
        }

        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-53
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.object_list, []) # TODO MCS-52
        self.assertEqual(actual.pose, MCS_Pose.UNDEFINED.value) # TODO MCS-18
        self.assertEqual(actual.return_status, MCS_Return_Status.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        self.assertEqual(len(actual.depth_mask_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 1)
        self.assertEqual(numpy.array(actual.depth_mask_list[0]), numpy.round(depth_mask_data / 30))
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        self.assertEqual(numpy.array(actual.object_mask_list[0]), object_mask_data)

    def test_wrap_step(self):
        actual = self.controller.wrap_step(action="TestAction", numberProperty=1234, stringProperty="test_property")
        expected = {
            "action": "TestAction",
            "logs": True,
            "numberProperty": 1234,
            "renderClassImage": True,
            "renderDepthImage": True,
            "renderObjectImage": True,
            "stringProperty": "test_property"
        }
        self.assertEqual(actual, expected)

