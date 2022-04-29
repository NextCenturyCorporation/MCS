import glob
import os
import shutil
import unittest
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock

import numpy as np

import machine_common_sense as mcs
from machine_common_sense.config_manager import (ConfigManager, MetadataTier,
                                                 SceneConfiguration, Vector3d)
from machine_common_sense.controller_events import EndScenePayload, EventType
from machine_common_sense.goal_metadata import GoalMetadata
from machine_common_sense.parameter import Parameter

from .mock_controller import MOCK_VARIABLES, MockControllerAI2THOR

SCENE_HIST_DIR = "./SCENE_HISTORY/"
TEST_FILE_NAME = "test controller"


class TestController(unittest.TestCase):

    def setUp(self):
        self.controller = MockControllerAI2THOR()
        self.controller._publish_event = MagicMock()
        self.controller.set_metadata_tier('default')
        self.maxDiff = None

    @classmethod
    def tearDownClass(cls) -> None:
        # remove all TEST_FILE_NAME in SCENE_HIST_DIR
        test_files = glob.glob(f'{SCENE_HIST_DIR}/{TEST_FILE_NAME}*')
        for test_file in test_files:
            os.unlink(test_file)
        # if SCENE_HIST_DIR is empty, destroy it
        if os.path.isdir(SCENE_HIST_DIR) and not os.listdir(SCENE_HIST_DIR):
            shutil.rmtree(SCENE_HIST_DIR)

    def create_mock_scene_event(self, mock_scene_event_data):
        # Wrap the dict in a SimpleNamespace object to permit property access
        # with dotted notation since the actual variable is a class, not a
        # dict.
        return SimpleNamespace(**mock_scene_event_data)

    def create_step_data(self, **kwargs):
        data = dict(
            consistentColors=False,
            continuous=True,
            gridSize=Parameter.GRID_SIZE,
            horizon=0.0,
            logs=True,
            moveMagnitude=mcs.controller.DEFAULT_MOVE,
            objectId=None,
            objectImageCoords={
                'x': 0,
                'y': 0
            },
            receptacleObjectId=None,
            receptacleObjectImageCoords={
                'x': 0,
                'y': 0
            },
            renderDepthImage=False,
            renderObjectImage=False,
            rotation={'y': 0.0},
            snapToGrid=False,
            teleportPosition=None,
            teleportRotation=None,
            clockwise=True,
            lateral=0,
            straight=1
        )

        for key, value in kwargs.items():
            data[key] = value

        return data

    def create_wrap_output_scene_event(self):
        image_data = np.array([[0]], dtype=np.uint8)
        depth_data = np.array([[[128, 0, 0]]], dtype=np.uint8)
        object_mask_data = np.array([[192]], dtype=np.uint8)

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

    def test_end_scene(self):
        test_payload = self.controller._create_event_payload_kwargs()

        test_payload["rating"] = 1.0
        test_payload["score"] = 0.5
        test_payload["report"] = {
            1: {
                "rating": 1.0,
                "score": .75,
                "violations_xy_list": [
                    {
                        "x": 1,
                        "y": 1
                    }
                ]}
        }

        self.controller.end_scene(1.0, 0.5, {
            1: {
                "rating": 1.0,
                "score": .75,
                "violations_xy_list": [
                    {
                        "x": 1,
                        "y": 1
                    }
                ]}
        })

        self.controller._publish_event.assert_called_with(
            EventType.ON_END_SCENE,
            EndScenePayload(**test_payload)
        )

    def test_end_scene_with_numpy_float(self):
        test_payload = self.controller._create_event_payload_kwargs()

        test_payload["rating"] = 1.0
        test_payload["score"] = np.float64(0.5)
        test_payload["report"] = {
            1: {
                "rating": 1.0,
                "score": np.float64(.75),
                "violations_xy_list": [
                    {
                        "x": 1,
                        "y": 1
                    }
                ]}
        }

        self.controller.end_scene(1.0, np.float64(0.5), {
            1: {
                "rating": 1.0,
                "score": np.float64(.75),
                "violations_xy_list": [
                    {
                        "x": np.int32(1),
                        "y": np.int32(1)
                    }
                ]}
        })

        self.controller._publish_event.assert_called_with(
            EventType.ON_END_SCENE,
            EndScenePayload(**test_payload)
        )

    def test_end_scene_with_rating_string(self):
        test_payload = self.controller._create_event_payload_kwargs()

        test_payload["rating"] = 1.0
        test_payload["score"] = np.float64(0.5)
        test_payload["report"] = {
            1: {
                "rating": 1.0,
                "score": np.float64(.75),
                "violations_xy_list": [
                    {
                        "x": 1,
                        "y": 1
                    }
                ]}
        }

        with self.assertRaises(TypeError):
            self.controller.end_scene("1.0", np.float64(0.5), {
                1: {
                    "rating": 1.0,
                    "score": np.float64(.75),
                    "violations_xy_list": [
                        {
                            "x": np.int32(1),
                            "y": np.int32(1)
                        }
                    ]}
            })

    def test_end_scene_twice(self):
        test_payload = self.controller._create_event_payload_kwargs()

        test_payload["rating"] = 1.0
        test_payload["score"] = 0.5
        test_payload["report"] = {
            1: {
                "rating": 1.0,
                "score": .75,
                "violations_xy_list": [
                    {
                        "x": 1,
                        "y": 1
                    }
                ]}
        }

        self.controller.end_scene(1.0, 0.5, {
            1: {
                "rating": 1.0,
                "score": .75,
                "violations_xy_list": [
                    {
                        "x": 1,
                        "y": 1
                    }
                ]}
        })

        # calling end_scene a second time raises an exception
        with self.assertRaises(RuntimeError):
            self.controller.end_scene(
                1.0,
                0.5,
                {1: {
                    "rating": 1.0,
                    "score": .75,
                    "violations_xy_list": [
                        {
                            "x": 1,
                            "y": 1
                        }
                    ]}
                 })

    def test_start_scene(self):
        self.controller.set_metadata_tier(
            MetadataTier.ORACLE.value)
        output = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.assertIsNotNone(output)
        self.controller._publish_event.assert_called_with(
            EventType.ON_START_SCENE,
            ANY
        )
        self.assertEqual(
            output.action_list,
            GoalMetadata.DEFAULT_ACTIONS)
        self.assertEqual(output.return_status,
                         MOCK_VARIABLES['metadata']['lastActionStatus'])
        self.assertEqual(output.reward, 0)
        self.assertEqual(output.step_number, 0)
        self.assertEqual(str(output.goal), str(mcs.GoalMetadata()))
        self.assertEqual(len(output.image_list), MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.depth_map_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_mask_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_list),
                         len(MOCK_VARIABLES['metadata']['objects']))
        self.assertEqual(len(output.structural_object_list),
                         len(MOCK_VARIABLES['metadata']['structuralObjects']))

        output = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            GoalMetadata.DEFAULT_ACTIONS)
        self.assertEqual(output.return_status,
                         MOCK_VARIABLES['metadata']['lastActionStatus'])
        self.assertEqual(output.reward, 0)
        self.assertEqual(output.step_number, 0)
        self.assertEqual(str(output.goal), str(mcs.GoalMetadata()))
        self.assertEqual(len(output.image_list), MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.depth_map_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_mask_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_list),
                         len(MOCK_VARIABLES['metadata']['objects']))
        self.assertEqual(len(output.structural_object_list),
                         len(MOCK_VARIABLES['metadata']['structuralObjects']))

    def test_start_scene_preview_phase(self):
        self.controller.set_metadata_tier(
            MetadataTier.ORACLE.value)
        last_preview_phase_step = 5
        output = self.controller.start_scene({'name': TEST_FILE_NAME, 'goal': {
            'last_preview_phase_step': last_preview_phase_step}
        })
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            GoalMetadata.DEFAULT_ACTIONS)
        self.assertEqual(output.return_status,
                         MOCK_VARIABLES['metadata']['lastActionStatus'])
        self.assertEqual(output.reward, -0.005)
        self.assertEqual(output.step_number, 5)
        self.assertEqual(str(output.goal), str(
            mcs.GoalMetadata(last_preview_phase_step=5)))
        self.assertEqual(
            len(output.image_list),
            MOCK_VARIABLES['event_count'] * (last_preview_phase_step + 1),
        )
        self.assertEqual(
            len(output.depth_map_list),
            MOCK_VARIABLES['event_count'] * (last_preview_phase_step + 1),
        )
        self.assertEqual(
            len(output.object_mask_list),
            MOCK_VARIABLES['event_count'] * (last_preview_phase_step + 1),
        )
        self.assertEqual(len(output.object_list),
                         len(MOCK_VARIABLES['metadata']['objects']))
        self.assertEqual(len(output.structural_object_list),
                         len(MOCK_VARIABLES['metadata']['structuralObjects']))

    def test_step(self):
        self.controller.set_metadata_tier(
            MetadataTier.ORACLE.value)
        output = self.controller.start_scene({'name': TEST_FILE_NAME})
        output = self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            GoalMetadata.DEFAULT_ACTIONS)
        self.assertEqual(output.return_status,
                         MOCK_VARIABLES['metadata']['lastActionStatus'])
        self.assertEqual(output.reward, -0.001)
        self.assertEqual(output.step_number, 1)
        self.assertEqual(str(output.goal), str(mcs.GoalMetadata()))
        self.assertEqual(len(output.image_list), MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.depth_map_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_mask_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_list),
                         len(MOCK_VARIABLES['metadata']['objects']))
        self.assertEqual(len(output.structural_object_list),
                         len(MOCK_VARIABLES['metadata']['structuralObjects']))

        output = self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            GoalMetadata.DEFAULT_ACTIONS)
        self.assertEqual(output.return_status,
                         MOCK_VARIABLES['metadata']['lastActionStatus'])
        self.assertEqual(output.reward, -0.002)
        self.assertEqual(output.step_number, 2)
        self.assertEqual(str(output.goal), str(mcs.GoalMetadata()))
        self.assertEqual(len(output.image_list), MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.depth_map_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_mask_list),
                         MOCK_VARIABLES['event_count'])
        self.assertEqual(len(output.object_list),
                         len(MOCK_VARIABLES['metadata']['objects']))
        self.assertEqual(len(output.structural_object_list),
                         len(MOCK_VARIABLES['metadata']['structuralObjects']))

    def test_step_events(self):
        self.controller.set_metadata_tier(
            MetadataTier.ORACLE.value)
        output = self.controller.start_scene({'name': TEST_FILE_NAME})
        output = self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.controller._publish_event.assert_any_call(
            EventType.ON_BEFORE_STEP,
            ANY
        )
        self.controller._publish_event.assert_any_call(
            EventType.ON_AFTER_STEP,
            ANY
        )
        self.assertIsNotNone(output)

    def test_step_last_step(self):
        output = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.set_goal(mcs.GoalMetadata(last_step=0))
        output = self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertIsNone(output)

        self.controller.set_goal(mcs.GoalMetadata(last_step=1))
        output = self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertIsNotNone(output)
        output = self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertIsNone(output)

    def test_retrieve_action_list_at_step(self):
        test_action_list = [
            (mcs.Action.PASS.value, {}),
            (mcs.Action.LOOK_UP.value, {'amount': 10}),
            (mcs.Action.MOVE_AHEAD.value, {'amount': 0.1}),
            (mcs.Action.PICKUP_OBJECT.value, {'objectId': 'ball'}),
            (mcs.Action.PICKUP_OBJECT.value, {'objectId': 'duck'})
        ]

        # With no action list
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(),
                0
            ),
            GoalMetadata.DEFAULT_ACTIONS
        )
        # With empty action list
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[]),
                0
            ),
            GoalMetadata.DEFAULT_ACTIONS
        )
        # With empty nested action list
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[[]]),
                0
            ),
            GoalMetadata.DEFAULT_ACTIONS
        )
        # With test action list
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[test_action_list]),
                0
            ),
            test_action_list
        )
        # With index greater than action list length
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[test_action_list]),
                1
            ),
            GoalMetadata.DEFAULT_ACTIONS
        )
        # With incorrect index
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[test_action_list, []]),
                1
            ),
            GoalMetadata.DEFAULT_ACTIONS
        )
        # With incorrect index
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[[], test_action_list]),
                0
            ),
            GoalMetadata.DEFAULT_ACTIONS
        )
        # With correct index
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[[], test_action_list]),
                1
            ),
            test_action_list
        )
        # Before last step
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[test_action_list], last_step=1),
                0
            ),
            test_action_list
        )
        # On last step
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[test_action_list], last_step=0),
                0
            ),
            []
        )

    def test_get_metadata_level(self):
        self.assertEqual('default', self.controller.get_metadata_level())

        self.controller.set_metadata_tier('oracle')
        self.assertEqual('oracle', self.controller.get_metadata_level())

        self.controller.set_metadata_tier('none')
        self.assertEqual('none', self.controller.get_metadata_level())

    def test_scene_configuration_deserialization(self):
        config = SceneConfiguration()
        actual = self.controller._convert_scene_config(config)
        # should be same instance
        self.assertEqual(config, actual)

        config = {}
        actual = self.controller._convert_scene_config(config)
        # should be same instance
        self.assertEqual(None, actual.name)
        self.assertEqual(None, actual.floor_material)
        self.assertEqual([], actual.objects)
        self.assertEqual(
            ConfigManager.DEFAULT_ROOM_DIMENSIONS,
            actual.room_dimensions)
        self.assertEqual(None, actual.goal)

        config = {"name": "name1", "roomDimensions": {"x": 1, "y": 2, "z": 3}}
        actual = self.controller._convert_scene_config(config)
        self.assertIsInstance(actual, SceneConfiguration)
        self.assertEqual("name1", actual.name)
        self.assertEqual(None, actual.floor_material)
        self.assertEqual([], actual.objects)
        self.assertIsNotNone(actual.room_dimensions)
        self.assertIsInstance(actual.room_dimensions, Vector3d)
        self.assertEqual(1, actual.room_dimensions.x)
        self.assertEqual(2, actual.room_dimensions.y)
        self.assertEqual(3, actual.room_dimensions.z)
        self.assertEqual(None, actual.goal)

    def test_set_config(self):
        first_config = self.controller._config
        new_config = ConfigManager(config_file_or_dict={})
        previous_noise = first_config.is_noise_enabled()

        def flip():
            return ~previous_noise
        new_config.is_noise_enabled = flip
        self.controller._set_config(new_config)
        self.assertIs(new_config, self.controller._config)
        self.assertIsNot(first_config, new_config)
        self.assertNotEqual(previous_noise,
                            self.controller._config.is_noise_enabled())

    def test_retrieve_object_states(self):
        config = ConfigManager(config_file_or_dict={})
        self.controller._set_config(config)
        scene_config = self.controller._convert_scene_config(
            SceneConfiguration())
        self.controller._scene_config = scene_config
        states = self.controller.retrieve_object_states('')
        self.assertIsInstance(states, list)
        self.assertEqual(len(states), 0)

    def test_step_open_action_magnitude(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step(
            mcs.Action.OPEN_OBJECT.value,
            amount=1,
            objectId='test_id_1',
            receptacleObjectId='test_id_2')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MCSOpenObject',
                moveMagnitude=1.0,
                objectId='test_id_1',
                receptacleObjectId='test_id_2'))

        self.controller.step(
            mcs.Action.OPEN_OBJECT.value,
            amount=0.1,
            objectId='test_id_1',
            receptacleObjectId='test_id_2')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MCSOpenObject',
                moveMagnitude=0.1,
                objectId='test_id_1',
                receptacleObjectId='test_id_2'))

        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.OPEN_OBJECT.value,
                amount=1.5,
                objectId='test_id_1',
                receptacleObjectID='test_id_2')

        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.OPEN_OBJECT.value,
                amount=-1,
                objectId='test_id_1',
                receptacleObjectId='test_id_2')

        self.controller.step(
            mcs.Action.OPEN_OBJECT.value,
            amount=1,
            objectImageCoordsX=1,
            objectImageCoordsY=2)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MCSOpenObject', moveMagnitude=1.0,
                objectImageCoords={
                    'x': 1, 'y': MOCK_VARIABLES['metadata']['screenHeight'] - 3
                }
            )
        )

    def test_step_validate_action(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        with self.assertRaises(ValueError):
            self.controller.step('Foobar')

        self.controller.set_goal(mcs.GoalMetadata(action_list=[
            [(mcs.Action.PASS.value, {})]
        ]))
        with self.assertRaises(ValueError):
            self.controller.step(mcs.Action.MOVE_AHEAD.value)

        self.controller.set_goal(mcs.GoalMetadata(action_list=[
            [(mcs.Action.MOVE_AHEAD.value, {})],
            [(mcs.Action.MOVE_BACK.value, {})]]
        ))
        output = self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertIsNotNone(output)
        with self.assertRaises(ValueError):
            self.controller.step(mcs.Action.MOVE_AHEAD.value)

    def test_step_validate_parameters_move(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.MOVE_AHEAD.value,
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

        self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.MOVE_AHEAD.value,
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

        self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.MOVE_AHEAD.value,
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

        self.controller.step(mcs.Action.MOVE_AHEAD.value)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.MOVE_AHEAD.value,
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

    def test_step_validate_parameters_rotate(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step(mcs.Action.ROTATE_LEFT.value)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(action=mcs.Action.ROTATE_LEFT.value))

        self.controller.step(mcs.Action.ROTATE_LEFT.value)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.ROTATE_LEFT.value))

    def test_step_validate_parameters_force_object(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step(
            mcs.Action.PUSH_OBJECT.value,
            force=1,
            objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.PUSH_OBJECT.value,
                moveMagnitude=1.0,
                objectId='test_id_1'))

        self.controller.step(
            mcs.Action.PUSH_OBJECT.value,
            force=0.1,
            objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.PUSH_OBJECT.value,
                moveMagnitude=0.1,
                objectId='test_id_1'))

        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.PUSH_OBJECT.value,
                force=1.5,
                objectId='test_id_1')
        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.PUSH_OBJECT.value,
                force=-1,
                objectId='test_id_1')
        with self.assertRaises(Exception):
            self.controller.step(
                mcs.Action.PUSH_OBJECT.value,
                moveMagnitude=0.1)

        self.controller.step(
            mcs.Action.PUSH_OBJECT.value,
            force=1,
            objectImageCoordsX=1,
            objectImageCoordsY=2)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.PUSH_OBJECT.value,
                moveMagnitude=1.0,
                objectImageCoords={'x': 1, 'y': 397}))

        self.controller.step(
            mcs.Action.PUSH_OBJECT.value,
            objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.PUSH_OBJECT.value,
                moveMagnitude=0.5,
                objectId='test_id_1'))

    def test_step_validate_parameters_torque_object(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step(
            mcs.Action.TORQUE_OBJECT.value,
            force=1,
            objectImageCoordsX=1,
            objectImageCoordsY=2)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.TORQUE_OBJECT.value,
                moveMagnitude=1.0,
                objectImageCoords={'x': 1, 'y': 397}))

        self.controller.step(
            mcs.Action.TORQUE_OBJECT.value,
            force=-1,
            objectImageCoordsX=1,
            objectImageCoordsY=2)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.TORQUE_OBJECT.value,
                moveMagnitude=-1.0,
                objectImageCoords={'x': 1, 'y': 397}))

        self.controller.step(
            mcs.Action.TORQUE_OBJECT.value,
            objectImageCoordsX=1,
            objectImageCoordsY=2)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.TORQUE_OBJECT.value,
                moveMagnitude=0.5,
                objectImageCoords={'x': 1, 'y': 397}))

        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.TORQUE_OBJECT.value,
                force=1.1,
                objectId='test_id_1')

        with self.assertRaises(Exception):
            self.controller.step(
                mcs.Action.TORQUE_OBJECT.value,
                moveMagnitude=0.1)

        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.TORQUE_OBJECT.value,
                force=-1.1,
                objectId='test_id_1')

    def test_step_validate_parameters_rotate_object(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step(
            mcs.Action.ROTATE_OBJECT.value,
            objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.ROTATE_OBJECT.value,
                objectId='test_id_1',
                clockwise=True))

        self.controller.step(
            mcs.Action.ROTATE_OBJECT.value,
            objectId='test_id_1',
            clockwise='false')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.ROTATE_OBJECT.value,
                objectId='test_id_1',
                clockwise=False))

        self.controller.step(
            mcs.Action.ROTATE_OBJECT.value,
            objectId='test_id_1',
            clockwise='False')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.ROTATE_OBJECT.value,
                objectId='test_id_1',
                clockwise=False))

        self.controller.step(
            mcs.Action.ROTATE_OBJECT.value,
            objectId='test_id_1',
            clockwise=True)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.ROTATE_OBJECT.value,
                objectId='test_id_1',
                clockwise=True))

        self.controller.step(
            mcs.Action.ROTATE_OBJECT.value,
            objectId='test_id_1',
            clockwise=False)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action=mcs.Action.ROTATE_OBJECT.value,
                objectId='test_id_1',
                clockwise=False))

        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.ROTATE_OBJECT.value,
                clockwise=1.0,
                objectId='test_id_1')

        with self.assertRaises(Exception):
            self.controller.step(
                mcs.Action.ROTATE_OBJECT.value,
                clockwise=False)

        with self.assertRaises(ValueError):
            self.controller.step(
                mcs.Action.ROTATE_OBJECT.value,
                clockwise='string',
                objectId='test_id_1')

    def test_step_validate_parameters_move_object(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step('MoveObject', objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveObject',
                objectId='test_id_1',
                lateral=0,
                straight=1))
        self.controller.step(
            'MoveObject',
            objectId='test_id_1',
            lateral=1)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveObject',
                objectId='test_id_1',
                lateral=1,
                straight=0))
        self.controller.step(
            'MoveObject',
            objectId='test_id_1',
            lateral=1,
            straight=-1)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveObject',
                objectId='test_id_1',
                lateral=1,
                straight=-1))

        with self.assertRaises(ValueError):
            self.controller.step(
                'MoveObject',
                lateral='string',
                objectId='test_id_1')
        with self.assertRaises(ValueError):
            self.controller.step(
                'MoveObject',
                straight='string',
                objectId='test_id_1')
        with self.assertRaises(ValueError):
            self.controller.step(
                'MoveObject',
                lateral=1,
                straight=0.1,
                objectId='test_id_1')
        with self.assertRaises(ValueError):
            self.controller.step(
                'MoveObject',
                lateral=0.1,
                straight=1,
                objectId='test_id_1')
        with self.assertRaises(ValueError):
            self.controller.step(
                'MoveObject',
                lateral=True,
                straight=False,
                objectId='test_id_1')


if __name__ == '__main__':
    unittest.main()
