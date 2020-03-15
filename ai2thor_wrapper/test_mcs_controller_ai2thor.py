import numpy
from PIL import Image
from types import SimpleNamespace
import unittest

from mcs_action import MCS_Action
from mcs_goal import MCS_Goal
from mcs_object import MCS_Object
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
        mock_scene_event_data = {
            "metadata": {
                "objects": [{
                    "direction": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "distance": 0,
                    "isPickedUp": True,
                    "mass": 1,
                    "objectId": "testId1",
                    "points": [{
                        "x": 1,
                        "y": 2,
                        "z": 3
                    }, {
                        "x": 4,
                        "y": 5,
                        "z": 6
                    }, {
                        "x": 7,
                        "y": 8,
                        "z": 9
                    }],
                    "salientMaterials": [],
                    "visibleInCamera": False
                }, {
                    "direction": {
                        "x": 90,
                        "y": -30,
                        "z": 0
                    },
                    "distance": 1.1,
                    "isPickedUp": False,
                    "mass": 12.34,
                    "objectId": "testId2",
                    "points": [{
                        "x": 11,
                        "y": 12,
                        "z": 13
                    }, {
                        "x": 14,
                        "y": 15,
                        "z": 16
                    }, {
                        "x": 17,
                        "y": 18,
                        "z": 19
                    }],
                    "salientMaterials": ["Foobar", "Metal", "Plastic"],
                    "visibleInCamera": True
                }]
            },
            "object_id_to_color": {
                "testId1": (12, 34, 56),
                "testId2": (98, 76, 54)
            }
        }

        actual = self.controller.retrieve_object_list(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(len(actual), 2)

        self.assertEqual(actual[0].uuid, "testId1")
        self.assertEqual(actual[0].color, {
            "r": 12,
            "g": 34,
            "b": 56
        })
        self.assertEqual(actual[0].direction, {
            "x": 0,
            "y": 0,
            "z": 0
        })
        self.assertEqual(actual[0].distance, 0)
        self.assertEqual(actual[0].held, True)
        self.assertEqual(actual[0].mass, 1)
        self.assertEqual(actual[0].material_list, [])
        self.assertEqual(actual[0].point_list, [{
            "x": 1,
            "y": 2,
            "z": 3
        }, {
            "x": 4,
            "y": 5,
            "z": 6
        }, {
            "x": 7,
            "y": 8,
            "z": 9
        }])
        self.assertEqual(actual[0].visible, False)

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].color, {
            "r": 98,
            "g": 76,
            "b": 54
        })
        self.assertEqual(actual[1].direction, {
            "x": 90,
            "y": -30,
            "z": 0
        })
        self.assertEqual(actual[1].distance, 2.2)
        self.assertEqual(actual[1].held, False)
        self.assertEqual(actual[1].mass, 12.34)
        self.assertEqual(actual[1].material_list, ["METAL", "PLASTIC"])
        self.assertEqual(actual[1].point_list, [{
            "x": 11,
            "y": 12,
            "z": 13
        }, {
            "x": 14,
            "y": 15,
            "z": 16
        }, {
            "x": 17,
            "y": 18,
            "z": 19
        }])
        self.assertEqual(actual[1].visible, True)

    def test_retrieve_pose(self):
        # TODO MCS-18
        pass

    def test_retrieve_return_status(self):
        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "SUCCESSFUL"
            }
        }

        actual = self.controller.retrieve_return_status(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, MCS_Return_Status.SUCCESSFUL.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "FAILED"
            }
        }

        actual = self.controller.retrieve_return_status(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, MCS_Return_Status.FAILED.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "INVALID_STATUS"
            }
        }

        actual = self.controller.retrieve_return_status(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, MCS_Return_Status.UNDEFINED.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": None
            }
        }

        actual = self.controller.retrieve_return_status(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, MCS_Return_Status.UNDEFINED.name)

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
                "lastActionStatus": "SUCCESSFUL",
                "lastActionSuccess": True,
                "objects": [{
                    "direction": {
                        "x": 90,
                        "y": -30,
                        "z": 0
                    },
                    "distance": 1.1,
                    "isPickedUp": False,
                    "mass": 12.34,
                    "objectId": "testId",
                    "points": [{
                        "x": 1,
                        "y": 2,
                        "z": 3
                    }, {
                        "x": 4,
                        "y": 5,
                        "z": 6
                    }, {
                        "x": 7,
                        "y": 8,
                        "z": 9
                    }],
                    "salientMaterials": ["Wood"],
                    "visibleInCamera": True
                }]
            },
            "object_id_to_color": {
                "testId": (12, 34, 56)
            }
        }

        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-53
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, MCS_Pose.STAND.value) # TODO MCS-18
        self.assertEqual(actual.return_status, MCS_Return_Status.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        self.assertEqual(len(actual.object_list), 1)
        self.assertEqual(actual.object_list[0].uuid, "testId")
        self.assertEqual(actual.object_list[0].color, {
            "r": 12,
            "g": 34,
            "b": 56
        })
        self.assertEqual(actual.object_list[0].direction, {
            "x": 90,
            "y": -30,
            "z": 0
        })
        self.assertEqual(actual.object_list[0].distance, 2.2)
        self.assertEqual(actual.object_list[0].held, False)
        self.assertEqual(actual.object_list[0].mass, 12.34)
        self.assertEqual(actual.object_list[0].material_list, ["WOOD"])
        self.assertEqual(actual.object_list[0].point_list, [{
            "x": 1,
            "y": 2,
            "z": 3
        }, {
            "x": 4,
            "y": 5,
            "z": 6
        }, {
            "x": 7,
            "y": 8,
            "z": 9
        }])
        self.assertEqual(actual.object_list[0].visible, True)

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
            "continuous": True,
            "gridSize": 0.1,
            "logs": True,
            "moveMagnitude": 0.5,
            "numberProperty": 1234,
            # "renderClassImage": True,
            "renderDepthImage": True,
            "renderObjectImage": True,
            "stringProperty": "test_property",
            "visibilityDistance": 1.0
        }
        self.assertEqual(actual, expected)

