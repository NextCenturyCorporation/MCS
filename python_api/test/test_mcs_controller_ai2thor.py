import numpy
from PIL import Image
from types import SimpleNamespace
import unittest

from machine_common_sense.mcs_action import MCS_Action
from machine_common_sense.mcs_goal import MCS_Goal
from machine_common_sense.mcs_object import MCS_Object
from machine_common_sense.mcs_pose import MCS_Pose
from machine_common_sense.mcs_return_status import MCS_Return_Status
from machine_common_sense.mcs_step_output import MCS_Step_Output
from .mock_mcs_controller_ai2thor import Mock_MCS_Controller_AI2THOR

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

    def test_retrieve_action_list(self):
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(), 0), self.controller.ACTION_LIST)
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(action_list=[]), 0), \
                self.controller.ACTION_LIST)
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(action_list=[[]]), 0), \
                self.controller.ACTION_LIST)
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(action_list=[['MoveAhead',\
                'RotateLook,rotation=180']]), 0), ['MoveAhead', 'RotateLook,rotation=180'])
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(action_list=[['MoveAhead',\
                'RotateLook,rotation=180']]), 1), self.controller.ACTION_LIST)
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(action_list=[['MoveAhead',\
                'RotateLook,rotation=180'], []]), 1), self.controller.ACTION_LIST)
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(action_list=[[],['MoveAhead',\
                'RotateLook,rotation=180']]), 0), self.controller.ACTION_LIST)
        self.assertEqual(self.controller.retrieve_action_list(MCS_Goal(action_list=[[],['MoveAhead',\
                'RotateLook,rotation=180']]), 1), ['MoveAhead', 'RotateLook,rotation=180'])

    def test_retrieve_goal(self):
        goal_1 = self.controller.retrieve_goal({})
        self.assertEqual(goal_1.action_list, None)
        self.assertEqual(goal_1.info_list, [])
        self.assertEqual(goal_1.last_step, None)
        self.assertEqual(goal_1.task_list, [])
        self.assertEqual(goal_1.type_list, [])
        self.assertEqual(goal_1.metadata, {})

        goal_2 = self.controller.retrieve_goal({
            "goal": {
            }
        })
        self.assertEqual(goal_2.action_list, None)
        self.assertEqual(goal_2.info_list, [])
        self.assertEqual(goal_2.last_step, None)
        self.assertEqual(goal_2.task_list, [])
        self.assertEqual(goal_2.type_list, [])
        self.assertEqual(goal_2.metadata, {})

        goal_3 = self.controller.retrieve_goal({
            "goal": {
                "action_list": [["action1"], [], ["action2", "action3", "action4"]],
                "info_list": ["info1", "info2", 12.34],
                "last_step": 10,
                "task_list": ["task1", "task2"],
                "type_list": ["type1", "type2"],
                "metadata": {
                    "key": "value"
                }
            }
        })
        self.assertEqual(goal_3.action_list, [["action1"], [], ["action2", "action3", "action4"]])
        self.assertEqual(goal_3.info_list, ["info1", "info2", 12.34])
        self.assertEqual(goal_3.last_step, 10)
        self.assertEqual(goal_3.task_list, ["task1", "task2"])
        self.assertEqual(goal_3.type_list, ["type1", "type2"])
        self.assertEqual(goal_3.metadata, {
            "key": "value"
        })

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
            "events": [self.create_mock_scene_event({
                "object_id_to_color": {
                    "testId1": (12, 34, 56),
                    "testId2": (98, 76, 54)
                }
            })],
            "metadata": {
                "objects": [{
                    "direction": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                    },
                    "distance": 0,
                    "distanceXZ": 0,
                    "isPickedUp": True,
                    "mass": 1,
                    "objectId": "testId1",
                    "position": {
                        "x": 1,
                        "y": 1,
                        "z": 2
                    },
                    "rotation": {
                        "x": 1.0,
                        "y": 2.0,
                        "z": 3.0
                    },
                    "salientMaterials": [],
                    "visibleInCamera": True
                }, {
                    "direction": {
                        "x": 90,
                        "y": -30,
                        "z": 0
                    },
                    "distance": 1.5,
                    "distanceXZ": 1.1,
                    "isPickedUp": False,
                    "mass": 12.34,
                    "objectBounds": {
                        "objectBoundsCorners": ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
                    },
                    "objectId": "testId2",
                    "position": {
                        "x": 1,
                        "y": 2,
                        "z": 3
                    },
                    "rotation": {
                        "x": 1.0,
                        "y": 2.0,
                        "z": 3.0
                    },
                    "salientMaterials": ["Foobar", "Metal", "Plastic"],
                    "visibleInCamera": True
                }]
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
        self.assertEqual(actual[0].dimensions, {})
        self.assertEqual(actual[0].direction, {
            "x": 0,
            "y": 0,
            "z": 0
        })
        self.assertEqual(actual[0].distance, 0)
        self.assertEqual(actual[0].distance_in_steps, 0)
        self.assertEqual(actual[0].distance_in_world, 0)
        self.assertEqual(actual[0].held, True)
        self.assertEqual(actual[0].mass, 1)
        self.assertEqual(actual[0].material_list, [])
        self.assertEqual(actual[0].visible, True)

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].color, {
            "r": 98,
            "g": 76,
            "b": 54
        })
        self.assertEqual(actual[1].dimensions, ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
        self.assertEqual(actual[1].direction, {
            "x": 90,
            "y": -30,
            "z": 0
        })
        self.assertEqual(actual[1].distance, 2.2)
        self.assertEqual(actual[1].distance_in_steps, 2.2)
        self.assertEqual(actual[1].distance_in_world, 1.5)
        self.assertEqual(actual[1].held, False)
        self.assertEqual(actual[1].mass, 12.34)
        self.assertEqual(actual[1].material_list, ["METAL", "PLASTIC"])
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
        depth_mask_data = numpy.array([[128]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_mask_data,
                "frame": image_data,
                "instance_segmentation_frame": object_mask_data
            })]
        }

        image_list, depth_mask_list, object_mask_list = self.controller.save_images(self.create_mock_scene_event(
            mock_scene_event_data))

        self.assertEqual(len(image_list), 1)
        self.assertEqual(len(depth_mask_list), 1)
        self.assertEqual(len(object_mask_list), 1)

        self.assertEqual(numpy.array(image_list[0]), image_data)
        self.assertEqual(numpy.array(depth_mask_list[0]), numpy.round(depth_mask_data / 30))
        self.assertEqual(numpy.array(object_mask_list[0]), object_mask_data)

    def test_save_images_with_multiple_images(self):
        image_data_1 = numpy.array([[64]], dtype=numpy.uint8)
        depth_mask_data_1 = numpy.array([[128]], dtype=numpy.uint8)
        object_mask_data_1 = numpy.array([[192]], dtype=numpy.uint8)

        image_data_2 = numpy.array([[32]], dtype=numpy.uint8)
        depth_mask_data_2 = numpy.array([[96]], dtype=numpy.uint8)
        object_mask_data_2 = numpy.array([[160]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_mask_data_1,
                "frame": image_data_1,
                "instance_segmentation_frame": object_mask_data_1
            }), self.create_mock_scene_event({
                "depth_frame": depth_mask_data_2,
                "frame": image_data_2,
                "instance_segmentation_frame": object_mask_data_2
            })]
        }

        image_list, depth_mask_list, object_mask_list = self.controller.save_images(self.create_mock_scene_event(
            mock_scene_event_data))

        self.assertEqual(len(image_list), 2)
        self.assertEqual(len(depth_mask_list), 2)
        self.assertEqual(len(object_mask_list), 2)

        self.assertEqual(numpy.array(image_list[0]), image_data_1)
        self.assertEqual(numpy.array(depth_mask_list[0]), numpy.round(depth_mask_data_1 / 30))
        self.assertEqual(numpy.array(object_mask_list[0]), object_mask_data_1)

        self.assertEqual(numpy.array(image_list[1]), image_data_2)
        self.assertEqual(numpy.array(depth_mask_list[1]), numpy.round(depth_mask_data_2 / 30))
        self.assertEqual(numpy.array(object_mask_list[1]), object_mask_data_2)

    def test_validate_and_convert_params(self):
        # TODO MCS-15
        pass

    def test_wrap_output(self):
        image_data = numpy.array([[0]], dtype=numpy.uint8)
        depth_mask_data = numpy.array([[128]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_mask_data,
                "frame": image_data,
                "instance_segmentation_frame": object_mask_data,
                "object_id_to_color": {
                    "testId": (12, 34, 56)
                }
            })],
            "metadata": {
                "agent": {
                    "cameraHorizon": 12.34,
                    "position": {
                        "x": 0.12,
                        "y": -0.23,
                        "z": 4.5
                    },
                    "rotation": {
                        "x": 1.111,
                        "y": 2.222,
                        "z": 3.333
                    }
                },
                "lastActionStatus": "SUCCESSFUL",
                "lastActionSuccess": True,
                "objects": [{
                    "direction": {
                        "x": 90,
                        "y": -30,
                        "z": 0
                    },
                    "distance": 1.5,
                    "distanceXZ": 1.1,
                    "isPickedUp": False,
                    "mass": 12.34,
                    "objectBounds": {
                        "objectBoundsCorners": ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"]
                    },
                    "objectId": "testId",
                    "position": {
                        "x": 10,
                        "y": 11,
                        "z": 12
                    },
                    "rotation": {
                        "x": 1.0,
                        "y": 2.0,
                        "z": 3.0
                    },
                    "salientMaterials": ["Wood"],
                    "visibleInCamera": True
                }]
            }
        }

        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-15
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
        self.assertEqual(actual.object_list[0].dimensions, ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
        self.assertEqual(actual.object_list[0].direction, {
            "x": 90,
            "y": -30,
            "z": 0
        })
        self.assertEqual(actual.object_list[0].distance, 2.2)
        self.assertEqual(actual.object_list[0].distance_in_steps, 2.2)
        self.assertEqual(actual.object_list[0].distance_in_world, 1.5)
        self.assertEqual(actual.object_list[0].held, False)
        self.assertEqual(actual.object_list[0].mass, 12.34)
        self.assertEqual(actual.object_list[0].material_list, ["WOOD"])
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
            "numberProperty": 1234,
            "renderDepthImage": True,
            "renderObjectImage": True,
            "stringProperty": "test_property",
            "visibilityDistance": 1.0
        }
        self.assertEqual(actual, expected)

    def test_generate_noise(self):
        # Current noise range is -0.5 to 0.5
        minValue = -0.5
        maxValue = 0.5

        currentNoise = self.controller.generate_noise()
        self.assertTrue(minValue <= currentNoise <= maxValue)

        currentNoise = self.controller.generate_noise()
        self.assertTrue(minValue <= currentNoise <= maxValue)
