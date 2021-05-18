import numpy
from types import SimpleNamespace
import unittest

import machine_common_sense as mcs
from machine_common_sense.controller_output_handler import StepOutput
from machine_common_sense.goal_metadata import GoalMetadata
from machine_common_sense.config_manager import ConfigManager


class TestControllerOutputHandler(unittest.TestCase):

    def setUp(self):
        self._config = ConfigManager()
        self._config._config[
            ConfigManager.CONFIG_DEFAULT_SECTION
        ] = {}

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def create_mock_scene_event(self, mock_scene_event_data):
        # Wrap the dict in a SimpleNamespace object to permit property access
        # with dotted notation since the actual variable is a class, not a
        # dict.
        ''''''
        return SimpleNamespace(**mock_scene_event_data)

    def create_wrap_output_scene_event(self):
        image_data = numpy.array([[0]], dtype=numpy.uint8)
        depth_data = numpy.array([[[128, 0, 0]]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        return {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_data,
                "frame": image_data,
                "instance_segmentation_frame": object_mask_data,
                "object_id_to_color": {
                    "testId": (12, 34, 56),
                    "testWallId": (101, 102, 103)
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
                "cameraPosition": {
                    "y": 0.1234
                },
                "clippingPlaneFar": 15,
                "clippingPlaneNear": 0,
                "fov": 42.5,
                "pose": mcs.Pose.STANDING.name,
                "lastActionStatus": "SUCCESSFUL",
                "lastActionSuccess": True,
                "objects": [{
                    "colorsFromMaterials": ["c1"],
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
                        "objectBoundsCorners": [
                            "p1",
                            "p2",
                            "p3",
                            "p4",
                            "p5",
                            "p6",
                            "p7",
                            "p8",
                        ]
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
                    "shape": "shape",
                    "visibleInCamera": True,
                    "isOpen": False,
                    "openable": False
                }, {
                    "colorsFromMaterials": [],
                    "direction": {
                        "x": -90,
                        "y": 180,
                        "z": 270
                    },
                    "distance": 2.5,
                    "distanceXZ": 2.0,
                    "isPickedUp": False,
                    "mass": 34.56,
                    "objectBounds": {
                        "objectBoundsCorners": [
                            "pA",
                            "pB",
                            "pC",
                            "pD",
                            "pE",
                            "pF",
                            "pG",
                            "pH",
                        ]
                    },
                    "objectId": "testIdHidden",
                    "position": {
                        "x": -3,
                        "y": -2,
                        "z": -1
                    },
                    "rotation": {
                        "x": 11.0,
                        "y": 12.0,
                        "z": 13.0
                    },
                    "salientMaterials": ["Wood"],
                    "shape": "shapeHidden",
                    "visibleInCamera": False,
                    "isOpen": False,
                    "openable": False
                }],
                "structuralObjects": [{
                    "colorsFromMaterials": ["c2"],
                    "direction": {
                        "x": 180,
                        "y": -60,
                        "z": 0
                    },
                    "distance": 2.5,
                    "distanceXZ": 2.2,
                    "isPickedUp": False,
                    "mass": 56.78,
                    "objectBounds": {
                        "objectBoundsCorners": [
                            "p11",
                            "p12",
                            "p13",
                            "p14",
                            "p15",
                            "p16",
                            "p17",
                            "p18",
                        ]
                    },
                    "objectId": "testWallId",
                    "position": {
                        "x": 20,
                        "y": 21,
                        "z": 22
                    },
                    "rotation": {
                        "x": 4.0,
                        "y": 5.0,
                        "z": 6.0
                    },
                    "salientMaterials": ["Ceramic"],
                    "shape": "structure",
                    "visibleInCamera": True,
                    "isOpen": False,
                    "openable": False
                }, {
                    "colorsFromMaterials": [],
                    "direction": {
                        "x": -180,
                        "y": 60,
                        "z": 90
                    },
                    "distance": 3.5,
                    "distanceXZ": 3.3,
                    "isPickedUp": False,
                    "mass": 78.90,
                    "objectBounds": {
                        "objectBoundsCorners": [
                            "pAA",
                            "pBB",
                            "pCC",
                            "pDD",
                            "pEE",
                            "pFF",
                            "pGG",
                            "pHH",
                        ]
                    },
                    "objectId": "testWallIdHidden",
                    "position": {
                        "x": 30,
                        "y": 31,
                        "z": 32
                    },
                    "rotation": {
                        "x": 14.0,
                        "y": 15.0,
                        "z": 16.0
                    },
                    "salientMaterials": ["Ceramic"],
                    "shape": "structureHidden",
                    "visibleInCamera": False,
                    "isOpen": False,
                    "openable": False
                }]
            }
        }, image_data, depth_data, object_mask_data

    def create_retrieve_object_list_scene_event(self):
        return {
            "events": [self.create_mock_scene_event({
                "object_id_to_color": {
                    "testId1": (12, 34, 56),
                    "testId2": (98, 76, 54),
                    "testId3": (101, 102, 103)
                }
            })],
            "metadata": {
                "objects": [{
                    "colorsFromMaterials": ["c1"],
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
                    "shape": "shape1",
                    "visibleInCamera": True,
                    "isOpen": False,
                    "openable": False
                }, {
                    "colorsFromMaterials": ["c2", "c3"],
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
                        "objectBoundsCorners": [
                            "p1",
                            "p2",
                            "p3",
                            "p4",
                            "p5",
                            "p6",
                            "p7",
                            "p8",
                        ]
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
                    "shape": "shape2",
                    "visibleInCamera": True,
                    "isOpen": False,
                    "openable": False
                }, {
                    "colorsFromMaterials": [],
                    "direction": {
                        "x": -90,
                        "y": 180,
                        "z": 270
                    },
                    "distance": 2.5,
                    "distanceXZ": 2,
                    "isPickedUp": False,
                    "mass": 34.56,
                    "objectBounds": {
                        "objectBoundsCorners": [
                            "pA",
                            "pB",
                            "pC",
                            "pD",
                            "pE",
                            "pF",
                            "pG",
                            "pH",
                        ]
                    },
                    "objectId": "testId3",
                    "position": {
                        "x": -3,
                        "y": -2,
                        "z": -1
                    },
                    "rotation": {
                        "x": 11.0,
                        "y": 12.0,
                        "z": 13.0
                    },
                    "salientMaterials": ["Wood"],
                    "shape": "shape3",
                    "visibleInCamera": False,
                    "isOpen": False,
                    "openable": False
                }]
            }
        }

    def test_retrieve_pose(self):
        # Check function calls
        mock_scene_event_data = {
            "metadata": {
                "pose": mcs.Pose.STANDING.name
            }
        }
        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        ret_status = stepOutput.retrieve_pose()
        self.assertEqual(ret_status, mcs.Pose.STANDING.name)

        mock_scene_event_data = {
            "metadata": {
                "pose": mcs.Pose.CRAWLING.name
            }
        }
        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        ret_status = stepOutput.retrieve_pose()
        self.assertEqual(ret_status, mcs.Pose.CRAWLING.name)

        mock_scene_event_data = {
            "metadata": {
                "pose": mcs.Pose.LYING.name
            }
        }
        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        ret_status = stepOutput.retrieve_pose()
        self.assertEqual(ret_status, mcs.Pose.LYING.name)

    def test_retrieve_return_status(self):
        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "SUCCESSFUL"
            }
        }

        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)

        actual = stepOutput.retrieve_return_status()
        self.assertEqual(actual, mcs.ReturnStatus.SUCCESSFUL.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "FAILED"
            }
        }

        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_return_status()
        self.assertEqual(actual, mcs.ReturnStatus.FAILED.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "INVALID_STATUS"
            }
        }

        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_return_status()
        self.assertEqual(actual, mcs.ReturnStatus.UNDEFINED.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": None
            }
        }

        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_return_status()
        self.assertEqual(actual, mcs.ReturnStatus.UNDEFINED.name)

    def test_retrieve_head_tilt(self):
        mock_scene_event_data = {
            "metadata": {
                "agent": {
                    "cameraHorizon": 12.34
                }
            },
            "events": []
        }

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)

        actual = stepOutput.retrieve_head_tilt()
        self.assertEqual(actual, 12.34)

        mock_scene_event_data = {
            "metadata": {
                "agent": {
                    "cameraHorizon": -56.78
                }
            },
            "events": []
        }

        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_head_tilt()
        self.assertEqual(actual, -56.78)

    def test_wrap_output(self):
        self._config.set_metadata_tier(
            ConfigManager.CONFIG_METADATA_TIER_DEFAULT)
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()
        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()
        actual = stepOutput.get_step_metadata(GoalMetadata(), 1, True)

        self.assertEqual(actual.action_list, ConfigManager.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 15))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        self.assertEqual(str(actual.goal), str(mcs.GoalMetadata()))
        self.assertEqual(actual.habituation_trial, None)
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, mcs.Pose.STANDING.value)
        self.assertEqual(actual.position, {'x': 0.12, 'y': -0.23, 'z': 4.5})
        self.assertEqual(actual.rotation, 2.222)
        self.assertEqual(
            actual.return_status,
            mcs.ReturnStatus.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        self.assertEqual(len(actual.object_list), 1)
        self.assertEqual(actual.object_list[0].uuid, "testId")
        self.assertEqual(actual.object_list[0].color, {
            "r": 12,
            "g": 34,
            "b": 56
        })
        self.assertEqual(
            actual.object_list[0].dimensions, [
                "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
        self.assertEqual(actual.object_list[0].direction, {
            "x": 90,
            "y": -30,
            "z": 0
        })
        self.assertEqual(actual.object_list[0].distance, 11.0)
        self.assertEqual(actual.object_list[0].distance_in_steps, 11.0)
        self.assertEqual(actual.object_list[0].distance_in_world, 1.5)
        self.assertEqual(actual.object_list[0].held, False)
        self.assertEqual(actual.object_list[0].mass, 12.34)
        self.assertEqual(actual.object_list[0].material_list, ["WOOD"])
        self.assertEqual(
            actual.object_list[0].position, {
                "x": 10, "y": 11, "z": 12})
        self.assertEqual(
            actual.object_list[0].rotation, {
                "x": 1, "y": 2, "z": 3})
        self.assertEqual(actual.object_list[0].shape, 'shape')
        self.assertEqual(actual.object_list[0].state_list, [])
        self.assertEqual(actual.object_list[0].texture_color_list, ['c1'])
        self.assertEqual(actual.object_list[0].visible, True)

        self.assertEqual(len(actual.structural_object_list), 1)
        self.assertEqual(actual.structural_object_list[0].uuid, "testWallId")
        self.assertEqual(actual.structural_object_list[0].color, {
            "r": 101,
            "g": 102,
            "b": 103
        })
        self.assertEqual(
            actual.structural_object_list[0].dimensions,
            ["p11", "p12", "p13", "p14", "p15", "p16", "p17", "p18"]
        )
        self.assertEqual(actual.structural_object_list[0].direction, {
            "x": 180,
            "y": -60,
            "z": 0
        })
        self.assertEqual(actual.structural_object_list[0].distance, 22.0)
        self.assertEqual(
            actual.structural_object_list[0].distance_in_steps, 22.0)
        self.assertEqual(
            actual.structural_object_list[0].distance_in_world, 2.5)
        self.assertEqual(actual.structural_object_list[0].held, False)
        self.assertEqual(actual.structural_object_list[0].mass, 56.78)
        self.assertEqual(
            actual.structural_object_list[0].material_list,
            ["CERAMIC"])
        self.assertEqual(
            actual.structural_object_list[0].position, {
                "x": 20, "y": 21, "z": 22})
        self.assertEqual(
            actual.structural_object_list[0].rotation, {
                "x": 4, "y": 5, "z": 6})
        self.assertEqual(actual.structural_object_list[0].shape, 'structure')
        self.assertEqual(actual.structural_object_list[0].state_list, [])
        self.assertEqual(
            actual.structural_object_list[0].texture_color_list,
            ['c2'])
        self.assertEqual(actual.structural_object_list[0].visible, True)

        # IF we are at default level, shouldn't depth maps, object masks be
        # restricted?
        self.assertEqual(len(actual.depth_map_list), 0)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 0)
        '''numpy.testing.assert_almost_equal(
            numpy.array(actual.depth_map_list[0]),
            numpy.array([[2.51]], dtype=numpy.float32),
            3
        )'''
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        '''self.assertEqual(
            numpy.array(
                actual.object_mask_list[0]),
            object_mask_data)
        '''

    def test_wrap_output_with_config_metadata_level2(self):
        self._config.set_metadata_tier('level2')
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()
        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()
        actual = stepOutput.get_step_metadata(GoalMetadata(), 1, True)

        '''pre_restrict.goal = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': {'image': [0], 'id': '1',
                               'image_name': "name_1"},
                    'target_1': {'image': [1], 'id': '2',
                                 'image_name': "name_2"},
                    'target_2': {'image': [2], 'id': '3',
                                 'image_name': "name_3"}
                }
            }
        })

        actual = self.controller.restrict_step_output_metadata(pre_restrict)

        self.assertEqual(pre_restrict.goal.metadata, {
            'target': {'image': None, 'id': None, 'image_name': None},
            'target_1': {'image': None, 'id': None, 'image_name': None},
            'target_2': {'image': None, 'id': None, 'image_name': None}
        })
        '''

        self.assertEqual(actual.action_list, ConfigManager.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 15))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        self.assertEqual(actual.habituation_trial, None)
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, mcs.Pose.STANDING.value)
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)
        self.assertEqual(
            actual.return_status,
            mcs.ReturnStatus.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 0)
        self.assertEqual(len(actual.structural_object_list), 0)

        # depth map list used to be 0, but should be 1 based on config level2
        self.assertEqual(len(actual.depth_map_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        # object mask list used to be 0, but should be 1 based on config level2
        self.assertEqual(len(actual.object_mask_list), 1)
        # self.assertEqual(
        #     numpy.array(
        #         actual.depth_map_list[0]),
        #     depth_data)
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        # self.assertEqual(
        #     numpy.array(
        #         actual.depth_map_list[0]),
        #     object_mask_data)

    def test_wrap_output_with_config_metadata_level1(self):
        self._config.set_metadata_tier(
            ConfigManager.CONFIG_METADATA_TIER_LEVEL_1)
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()
        actual = stepOutput.get_step_metadata(GoalMetadata(), 1, True)

        self.assertEqual(actual.action_list, ConfigManager.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 15))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        self.assertEqual(str(actual.goal), str(mcs.GoalMetadata()))
        self.assertEqual(actual.habituation_trial, None)
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, mcs.Pose.STANDING.value)
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)
        self.assertEqual(
            actual.return_status,
            mcs.ReturnStatus.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 0)
        self.assertEqual(len(actual.structural_object_list), 0)

        self.assertEqual(len(actual.depth_map_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 0)

    def test_wrap_output_with_config_metadata_none(self):
        self._config.set_metadata_tier('none')
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()
        actual = stepOutput.get_step_metadata(GoalMetadata(), 1, True)

        self.assertEqual(actual.action_list, ConfigManager.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 15))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        self.assertEqual(str(actual.goal), str(mcs.GoalMetadata()))
        self.assertEqual(actual.habituation_trial, None)
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, mcs.Pose.STANDING.value)
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)
        self.assertEqual(
            actual.return_status,
            mcs.ReturnStatus.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 0)
        self.assertEqual(len(actual.structural_object_list), 0)

        self.assertEqual(len(actual.depth_map_list), 0)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 0)

    def test_wrap_output_with_config_metadata_oracle_non_restrict(self):
        self._config.set_metadata_tier(
            ConfigManager.CONFIG_METADATA_TIER_ORACLE)
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()
        actual = stepOutput.get_step_metadata(GoalMetadata(), 1, False)

        self.assertEqual(actual.action_list, ConfigManager.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 15))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        self.assertEqual(actual.habituation_trial, None)
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, mcs.Pose.STANDING.value)
        self.assertEqual(actual.position, {'x': 0.12, 'y': -0.23, 'z': 4.5})
        self.assertEqual(actual.rotation, 2.222)
        self.assertEqual(
            actual.return_status,
            mcs.ReturnStatus.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 2)
        self.assertEqual(len(actual.structural_object_list), 2)

        self.assertEqual(len(actual.depth_map_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 1)
        numpy.testing.assert_almost_equal(
            numpy.array(actual.depth_map_list[0]),
            numpy.array([[2.51]], dtype=numpy.float32),
            3
        )
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        self.assertEqual(
            numpy.array(
                actual.object_mask_list[0]),
            object_mask_data)

    def test_wrap_output_with_config_metadata_oracle(self):
        self._config.set_metadata_tier(
            ConfigManager.CONFIG_METADATA_TIER_ORACLE)
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()
        actual = stepOutput.get_step_metadata(GoalMetadata(), 1, True)

        self.assertEqual(actual.action_list, ConfigManager.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 15))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        self.assertEqual(actual.habituation_trial, None)
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, mcs.Pose.STANDING.value)
        self.assertEqual(actual.position, {'x': 0.12, 'y': -0.23, 'z': 4.5})
        self.assertEqual(actual.rotation, 2.222)
        self.assertEqual(
            actual.return_status,
            mcs.ReturnStatus.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 2)
        self.assertEqual(len(actual.structural_object_list), 2)

        self.assertEqual(len(actual.depth_map_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 1)
        numpy.testing.assert_almost_equal(
            numpy.array(actual.depth_map_list[0]),
            numpy.array([[2.51]], dtype=numpy.float32),
            3
        )
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        self.assertEqual(
            numpy.array(
                actual.object_mask_list[0]),
            object_mask_data)

    def test_save_images(self):
        self._config.set_metadata_tier(
            ConfigManager.CONFIG_METADATA_TIER_ORACLE)
        image_data = numpy.array([[0]], dtype=numpy.uint8)
        depth_data = numpy.array([[[0, 0, 0]]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_data,
                "frame": image_data,
                "instance_segmentation_frame": object_mask_data
            })],
            "metadata": {"objects": []}
        }
        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()
        # actual = stepOutput.get_step_metadata(GoalMetadata(), 1, True)

        image_list = stepOutput._image_list
        depth_map_list = stepOutput._depth_map_list
        object_mask_list = stepOutput._object_mask_list

        self.assertEqual(len(image_list), 1)
        self.assertEqual(len(depth_map_list), 1)
        self.assertEqual(len(object_mask_list), 1)

        self.assertEqual(numpy.array(image_list[0]), image_data)
        numpy.testing.assert_almost_equal(
            numpy.array(depth_map_list[0]),
            numpy.array([[0.0]], dtype=numpy.float32),
            3
        )
        self.assertEqual(numpy.array(object_mask_list[0]), object_mask_data)

    def test_save_images_with_multiple_images(self):
        self._config.set_metadata_tier(
            ConfigManager.CONFIG_METADATA_TIER_ORACLE)
        image_data_1 = numpy.array([[64]], dtype=numpy.uint8)
        depth_data_1 = numpy.array([[[128, 64, 32]]], dtype=numpy.uint8)
        object_mask_data_1 = numpy.array([[192]], dtype=numpy.uint8)

        image_data_2 = numpy.array([[32]], dtype=numpy.uint8)
        depth_data_2 = numpy.array([[[96, 0, 0]]], dtype=numpy.uint8)
        object_mask_data_2 = numpy.array([[160]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_data_1,
                "frame": image_data_1,
                "instance_segmentation_frame": object_mask_data_1
            }), self.create_mock_scene_event({
                "depth_frame": depth_data_2,
                "frame": image_data_2,
                "instance_segmentation_frame": object_mask_data_2
            })],
            "metadata": {"objects": []}
        }

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        stepOutput.process_image_data()

        image_list = stepOutput._image_list
        depth_map_list = stepOutput._depth_map_list
        object_mask_list = stepOutput._object_mask_list

        self.assertEqual(len(image_list), 2)
        self.assertEqual(len(depth_map_list), 2)
        self.assertEqual(len(object_mask_list), 2)

        self.assertEqual(numpy.array(image_list[0]), image_data_1)
        numpy.testing.assert_almost_equal(
            numpy.array(depth_map_list[0]),
            numpy.array([[4.392]], dtype=numpy.float32),
            3
        )
        self.assertEqual(numpy.array(object_mask_list[0]), object_mask_data_1)

        self.assertEqual(numpy.array(image_list[1]), image_data_2)
        numpy.testing.assert_almost_equal(
            numpy.array(depth_map_list[1]),
            numpy.array([[1.882]], dtype=numpy.float32),
            3
        )
        self.assertEqual(numpy.array(object_mask_list[1]), object_mask_data_2)

    def test_retrieve_object_list(self):
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(
            self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_object_list()
        self.assertEqual(len(actual), 2)

        self.assertEqual(actual[0].uuid, "testId1")
        self.assertEqual(actual[0].color, {
            "r": 12,
            "g": 34,
            "b": 56
        })
        self.assertEqual(actual[0].dimensions, [])
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
        self.assertEqual(actual[0].position, {"x": 1, "y": 1, "z": 2})
        self.assertEqual(actual[0].rotation, {"x": 1, "y": 2, "z": 3})
        self.assertEqual(actual[0].shape, 'shape1')
        self.assertEqual(actual[0].state_list, [])
        self.assertEqual(actual[0].texture_color_list, ['c1'])
        self.assertEqual(actual[0].visible, True)

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].color, {
            "r": 98,
            "g": 76,
            "b": 54
        })
        self.assertEqual(
            actual[1].dimensions, [
                "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
        self.assertEqual(actual[1].direction, {
            "x": 90,
            "y": -30,
            "z": 0
        })
        self.assertEqual(actual[1].distance, 11.0)
        self.assertEqual(actual[1].distance_in_steps, 11.0)
        self.assertEqual(actual[1].distance_in_world, 1.5)
        self.assertEqual(actual[1].held, False)
        self.assertEqual(actual[1].mass, 12.34)
        self.assertEqual(actual[1].material_list, ["METAL", "PLASTIC"])
        self.assertEqual(actual[1].position, {"x": 1, "y": 2, "z": 3})
        self.assertEqual(actual[1].rotation, {"x": 1, "y": 2, "z": 3})
        self.assertEqual(actual[1].shape, 'shape2')
        self.assertEqual(actual[1].state_list, [])
        self.assertEqual(actual[1].texture_color_list, ['c2', 'c3'])
        self.assertEqual(actual[1].visible, True)

    def test_retrieve_object_list_with_states(self):
        scene_config = {
            'name': 'test name',
            'objects': [{
                'id': 'testId1',
                'states': [['a', 'b'], ['c', 'd']]
            }]
        }

        mock_scene_event_data = self.create_retrieve_object_list_scene_event()

        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(self._config, scene_config, mock_event, 0)
        actual = stepOutput.retrieve_object_list()

        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        mock_event = self.create_mock_scene_event(mock_scene_event_data)

        stepOutput = StepOutput(self._config, scene_config, mock_event, 0)

        actual = stepOutput.retrieve_object_list()
        self.assertEqual(len(actual), 2)

        self.assertEqual(actual[0].uuid, "testId1")
        self.assertEqual(actual[0].state_list, ['a', 'b'])

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].state_list, [])

    def test_retrieve_object_list_with_config_metadata_oracle(self):
        self._config.set_metadata_tier('oracle')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_object_list()
        self.assertEqual(len(actual), 3)

        self.assertEqual(actual[0].uuid, "testId1")
        self.assertEqual(actual[0].color, {
            "r": 12,
            "g": 34,
            "b": 56
        })
        self.assertEqual(actual[0].dimensions, [])
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
        self.assertEqual(actual[0].position, {"x": 1, "y": 1, "z": 2})
        self.assertEqual(actual[0].rotation, {"x": 1, "y": 2, "z": 3})
        self.assertEqual(actual[0].shape, 'shape1')
        self.assertEqual(actual[0].state_list, [])
        self.assertEqual(actual[0].texture_color_list, ['c1'])
        self.assertEqual(actual[0].visible, True)

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].color, {
            "r": 98,
            "g": 76,
            "b": 54
        })
        self.assertEqual(
            actual[1].dimensions, [
                "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"])
        self.assertEqual(actual[1].direction, {
            "x": 90,
            "y": -30,
            "z": 0
        })
        self.assertEqual(actual[1].distance, 11.0)
        self.assertEqual(actual[1].distance_in_steps, 11.0)
        self.assertEqual(actual[1].distance_in_world, 1.5)
        self.assertEqual(actual[1].held, False)
        self.assertEqual(actual[1].mass, 12.34)
        self.assertEqual(actual[1].material_list, ["METAL", "PLASTIC"])
        self.assertEqual(actual[1].position, {"x": 1, "y": 2, "z": 3})
        self.assertEqual(actual[1].rotation, {"x": 1, "y": 2, "z": 3})
        self.assertEqual(actual[1].shape, 'shape2')
        self.assertEqual(actual[1].state_list, [])
        self.assertEqual(actual[1].texture_color_list, ['c2', 'c3'])
        self.assertEqual(actual[1].visible, True)

        self.assertEqual(actual[2].uuid, "testId3")
        self.assertEqual(actual[2].color, {
            "r": 101,
            "g": 102,
            "b": 103
        })
        self.assertEqual(
            actual[2].dimensions, [
                "pA", "pB", "pC", "pD", "pE", "pF", "pG", "pH"])
        self.assertEqual(actual[2].direction, {
            "x": -90,
            "y": 180,
            "z": 270
        })
        self.assertEqual(actual[2].distance, 20.0)
        self.assertEqual(actual[2].distance_in_steps, 20.0)
        self.assertEqual(actual[2].distance_in_world, 2.5)
        self.assertEqual(actual[2].held, False)
        self.assertEqual(actual[2].mass, 34.56)
        self.assertEqual(actual[2].material_list, ["WOOD"])
        self.assertEqual(actual[2].position, {"x": -3, "y": -2, "z": -1})
        self.assertEqual(actual[2].rotation, {"x": 11, "y": 12, "z": 13})
        self.assertEqual(actual[2].shape, 'shape3')
        self.assertEqual(actual[2].state_list, [])
        self.assertEqual(actual[2].texture_color_list, [])
        self.assertEqual(actual[2].visible, False)

    def test_retrieve_object_list_with_config_metadata_level2(self):
        self._config.set_metadata_tier('level2')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_object_list()
        self.assertEqual(len(actual), 3)

    def test_retrieve_object_list_with_config_metadata_level1(self):
        self._config.set_metadata_tier('level1')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_object_list()
        self.assertEqual(len(actual), 3)

    def test_retrieve_object_list_with_config_metadata_none(self):
        self._config.set_metadata_tier('none')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        mock_event = self.create_mock_scene_event(mock_scene_event_data)
        stepOutput = StepOutput(self._config, {}, mock_event, 0)
        actual = stepOutput.retrieve_object_list()
        self.assertEqual(len(actual), 3)


if __name__ == '__main__':
    unittest.main()