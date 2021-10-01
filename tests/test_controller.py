import glob
import os
import shutil
import unittest
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock

import numpy

import machine_common_sense as mcs
from machine_common_sense.config_manager import (ConfigManager, MetadataTier,
                                                 SceneConfiguration, Vector3d)
from machine_common_sense.controller_events import EndScenePayload, EventType
from machine_common_sense.goal_metadata import GoalMetadata

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

    def create_step_data(self, **kwargs):
        data = dict(
            consistentColors=False,
            continuous=True,
            gridSize=mcs.Controller.GRID_SIZE,
            horizon=0,
            logs=True,
            moveMagnitude=mcs.controller.DEFAULT_MOVE,
            objectId=None,
            objectImageCoords={
                'x': 0.0,
                'y': 0.0
            },
            receptacleObjectId=None,
            receptacleObjectImageCoords={
                'x': 0.0,
                'y': 0.0
            },
            renderDepthImage=False,
            renderObjectImage=False,
            rotation={'y': 0.0},
            snapToGrid=False,
            teleportPosition=None,
            teleportRotation=None
        )

        for key, value in kwargs.items():
            data[key] = value

        return data

    def test_end_scene(self):
        test_payload = self.controller._create_event_payload_kwargs()

        test_payload["rating"] = "plausible"
        test_payload["score"] = 0.5
        test_payload["report"] = {
            1: {
                "rating": "plausible",
                "score": .75,
                "violations_xy_list": [
                    {
                        "x": 1,
                        "y": 1
                    }
                ]}
        }

        self.controller.end_scene("plausible", 0.5, {
            1: {
                "rating": "plausible",
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
            GoalMetadata.ACTION_LIST)
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
            GoalMetadata.ACTION_LIST)
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
            GoalMetadata.ACTION_LIST)
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
        output = self.controller.step('MoveAhead')
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            GoalMetadata.ACTION_LIST)
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

        output = self.controller.step('MoveAhead')
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            GoalMetadata.ACTION_LIST)
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
        output = self.controller.step('MoveAhead')
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
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

        self.controller.set_goal(mcs.GoalMetadata(last_step=1))
        output = self.controller.step('MoveAhead')
        self.assertIsNotNone(output)
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

    def test_step_validate_action(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        output = self.controller.step('Foobar')
        self.assertIsNone(output)

        self.controller.set_goal(mcs.GoalMetadata(action_list=[
            [('Pass', {})]
        ]))
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

        self.controller.set_goal(mcs.GoalMetadata(action_list=[
            [('MoveAhead', {})],
            [('MoveBack', {})]]
        ))
        output = self.controller.step('MoveAhead')
        self.assertIsNotNone(output)
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

    def test_step_validate_parameters_move(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step('MoveAhead')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

        self.controller.step('MoveAhead')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

        self.controller.step('MoveAhead')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

        self.controller.step('MoveAhead')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.DEFAULT_MOVE))

    def test_step_validate_parameters_rotate(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step('RotateLeft')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(action='RotateLeft'))

        self.controller.step('RotateLeft')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='RotateLeft'))

    def test_step_validate_parameters_force_object(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step('PushObject', force=1, objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='PushObject',
                moveMagnitude=mcs.Controller.MAX_FORCE,
                objectId='test_id_1'))

        self.controller.step('PushObject', force=0.1, objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='PushObject',
                moveMagnitude=0.1 *
                mcs.Controller.MAX_FORCE,
                objectId='test_id_1'))

        self.controller.step('PushObject', force=1.5, objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='PushObject',
                moveMagnitude=mcs.Controller.DEFAULT_AMOUNT *
                mcs.Controller.MAX_FORCE,
                objectId='test_id_1'))

        self.controller.step('PushObject', force=-1, objectId='test_id_1')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='PushObject',
                moveMagnitude=mcs.Controller.DEFAULT_AMOUNT *
                mcs.Controller.MAX_FORCE,
                objectId='test_id_1'))

        self.controller.step(
            'PushObject',
            force=1,
            objectImageCoordsX=1,
            objectImageCoordsY=2)
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='PushObject',
                moveMagnitude=mcs.Controller.MAX_FORCE,
                objectImageCoords={'x': 1, 'y': 398}))

    def test_step_validate_parameters_open_close(self):
        _ = self.controller.start_scene({'name': TEST_FILE_NAME})
        self.controller.step(
            'OpenObject',
            amount=1,
            objectId='test_id_1',
            receptacleObjectId='test_id_2')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MCSOpenObject',
                moveMagnitude=1,
                objectId='test_id_1',
                receptacleObjectId='test_id_2'))

        self.controller.step(
            'OpenObject',
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

        self.controller.step(
            'OpenObject',
            amount=1.5,
            objectId='test_id_1',
            receptacleObjectId='test_id_2')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MCSOpenObject',
                moveMagnitude=mcs.Controller.DEFAULT_AMOUNT,
                objectId='test_id_1',
                receptacleObjectId='test_id_2'))

        self.controller.step(
            'OpenObject',
            amount=-1,
            objectId='test_id_1',
            receptacleObjectId='test_id_2')
        self.assertEqual(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MCSOpenObject',
                moveMagnitude=mcs.Controller.DEFAULT_AMOUNT,
                objectId='test_id_1',
                receptacleObjectId='test_id_2'))

        self.controller.step(
            'OpenObject',
            amount=1,
            objectImageCoordsX=1,
            objectImageCoordsY=2,
            receptacleObjectImageCoordsX=4,
            receptacleObjectImageCoordsY=5)
        self.assertEqual(
            self.controller.get_last_step_data(), self.create_step_data(
                action='MCSOpenObject', moveMagnitude=1,
                objectImageCoords={
                    'x': 1, 'y': MOCK_VARIABLES['metadata']['screenHeight'] - 2
                },
                receptacleObjectImageCoords={
                    'x': 4, 'y': MOCK_VARIABLES['metadata']['screenHeight'] - 5
                }
            )
        )

    def test_retrieve_action_list_at_step(self):
        test_action_list = [
            ('Pass', {}),
            ('LookUp', {'amount': 10}),
            ('MoveAhead', {'amount': 0.1}),
            ('PickupObject', {'objectId': 'ball'}),
            ('PickupObject', {'objectId': 'duck'})
        ]

        # With no action list
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(),
                0
            ),
            GoalMetadata.ACTION_LIST
        )
        # With empty action list
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[]),
                0
            ),
            GoalMetadata.ACTION_LIST
        )
        # With empty nested action list
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[[]]),
                0
            ),
            GoalMetadata.ACTION_LIST
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
            GoalMetadata.ACTION_LIST
        )
        # With incorrect index
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[test_action_list, []]),
                1
            ),
            GoalMetadata.ACTION_LIST
        )
        # With incorrect index
        self.assertEqual(
            self.controller.retrieve_action_list_at_step(
                mcs.GoalMetadata(action_list=[[], test_action_list]),
                0
            ),
            GoalMetadata.ACTION_LIST
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

    def test_retrieve_pose(self):
        output = self.controller.start_scene({'name': TEST_FILE_NAME})

        # Testing retrieving proper pose depending on action made
        # Check basics
        output = self.controller.step(action='Stand')
        self.assertEqual(output.pose, mcs.Pose.STANDING.name)

        output = self.controller.step(action='LieDown')
        self.assertEqual(output.pose, mcs.Pose.LYING.name)

        output = self.controller.step(action='Crawl')
        self.assertEqual(output.pose, mcs.Pose.CRAWLING.name)

        # Check movement within crawling pose
        output = self.controller.step(action='MoveAhead')
        self.assertEqual(output.pose, mcs.Pose.CRAWLING.name)
        self.controller.step(action='MoveBack')

        self.controller.step(action='Stand')
        output = self.controller.step(action='MoveBack')
        self.assertEqual(output.pose, mcs.Pose.STANDING.name)

        # Check stand->lying->crawl->stand
        output = self.controller.step(action='LieDown')
        self.assertEqual(output.pose, mcs.Pose.LYING.name)
        output = self.controller.step(action='Crawl')
        self.assertEqual(output.pose, mcs.Pose.CRAWLING.name)
        output = self.controller.step(action='Stand')
        self.assertEqual(output.pose, mcs.Pose.STANDING.name)

        # Check stand->crawl->Lying->crawl->lying->crawl->stand
        self.controller.step(action='Crawl')
        output = self.controller.step(action='LieDown')
        self.assertEqual(output.pose, mcs.Pose.LYING.name)
        self.controller.step(action='Crawl')
        output = self.controller.step(action='LieDown')
        self.assertEqual(output.pose, mcs.Pose.LYING.name)
        self.controller.step(action='Crawl')
        output = self.controller.step(action='Stand')
        self.assertEqual(output.pose, mcs.Pose.STANDING.name)

        # Check stand->Lying (!= ->) stand
        self.controller.step(action='LieDown')
        output = self.controller.step(action='Stand')
        self.assertNotEqual(output.pose, mcs.Pose.STANDING.name)

        self.controller.step(action='Crawl')
        output = self.controller.step(action='Stand')
        self.assertEqual(output.pose, mcs.Pose.STANDING.name)

    def test_wrap_step(self):
        actual = self.controller.wrap_step(
            action="TestAction",
            numberProperty=1234,
            stringProperty="test_property")
        expected = {
            "action": "TestAction",
            "continuous": True,
            "gridSize": 0.1,
            "logs": True,
            "numberProperty": 1234,
            "renderDepthImage": False,
            "renderObjectImage": False,
            "snapToGrid": False,
            "stringProperty": "test_property",
            "consistentColors": False
        }
        self.assertEqual(actual, expected)

    def test_wrap_step_metadata_oracle(self):
        self.controller.set_metadata_tier('oracle')
        actual = self.controller.wrap_step(
            action="TestAction",
            numberProperty=1234,
            stringProperty="test_property")
        # Changed depth and object because oracle should result in both being
        # true.
        expected = {
            "action": "TestAction",
            "continuous": True,
            "gridSize": 0.1,
            "logs": True,
            "numberProperty": 1234,
            "renderDepthImage": True,
            "renderObjectImage": True,
            "snapToGrid": False,
            "stringProperty": "test_property",
            "consistentColors": True
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
        self.assertEqual(None, actual.floorMaterial)
        self.assertEqual([], actual.objects)
        self.assertEqual(
            ConfigManager.DEFAULT_ROOM_DIMENSIONS,
            actual.roomDimensions)
        self.assertEqual(None, actual.goal)

        config = {"name": "name1", "roomDimensions": {"x": 1, "y": 2, "z": 3}}
        actual = self.controller._convert_scene_config(config)
        self.assertIsInstance(actual, SceneConfiguration)
        self.assertEqual("name1", actual.name)
        self.assertEqual(None, actual.floorMaterial)
        self.assertEqual([], actual.objects)
        self.assertIsNotNone(actual.roomDimensions)
        self.assertIsInstance(actual.roomDimensions, Vector3d)
        self.assertEqual(1, actual.roomDimensions.x)
        self.assertEqual(2, actual.roomDimensions.y)
        self.assertEqual(3, actual.roomDimensions.z)
        self.assertEqual(None, actual.goal)

    def test_remove_none(self):
        actual = self.controller._remove_none({})
        self.assertEqual({}, actual)

        actual = self.controller._remove_none({"test": None})
        self.assertEqual({}, actual)

        actual = self.controller._remove_none({"test": 1})
        self.assertEqual({"test": 1}, actual)

        actual = self.controller._remove_none({"test": 1, "none": None})
        self.assertEqual({"test": 1}, actual)

        actual = self.controller._remove_none({"test1": {"test2": 1}})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.controller._remove_none(
            {"test1": {"test2": 1, "none": None}})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.controller._remove_none(
            {"test1": {"test2": 1}, "none": None})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.controller._remove_none(
            {"test1": {"test2": 1, "none": None}, "none": None})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.controller._remove_none({"test1": [{"test2": None}]})
        self.assertEqual({"test1": [{}]}, actual)

        actual = self.controller._remove_none(
            {"test1": [{"test2": None, "test3": "test"}]})
        self.assertEqual({"test1": [{"test3": "test"}]}, actual)

        actual = self.controller._remove_none(
            {"test1": [{"test2": None}], "test3": False})
        self.assertEqual({"test1": [{}], "test3": False}, actual)

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


if __name__ == '__main__':
    unittest.main()
