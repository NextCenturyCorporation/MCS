import numpy
from types import SimpleNamespace
import unittest

import machine_common_sense as mcs

from .mock_controller import (
    MockControllerAI2THOR,
    MOCK_VARIABLES
)


class Test_Controller(unittest.TestCase):

    def setUp(self):
        self.controller = MockControllerAI2THOR()
        self.controller.set_metadata_tier('')

    def create_mock_scene_event(self, mock_scene_event_data):
        # Wrap the dict in a SimpleNamespace object to permit property access
        # with dotted notation since the actual variable is a class, not a
        # dict.
        return SimpleNamespace(**mock_scene_event_data)

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
                    "visibleInCamera": True
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
                    "visibleInCamera": True
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
                    "visibleInCamera": False
                }]
            }
        }

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
                    "visibleInCamera": True
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
                    "visibleInCamera": False
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
                    "visibleInCamera": True
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
                    "visibleInCamera": False
                }]
            }
        }, image_data, depth_data, object_mask_data

    def create_step_data(self, **kwargs):
        data = dict(
            continuous=True,
            gridSize=mcs.Controller.GRID_SIZE,
            logs=True,
            renderDepthImage=False,
            renderObjectImage=False,
            snapToGrid=False,
            visibilityDistance=mcs.controller.MAX_REACH_DISTANCE,
            horizon=0,
            moveMagnitude=mcs.controller.MOVE_DISTANCE,
            objectImageCoords={
                'x': 0,
                'y': 0
            },
            objectId=None,
            receptacleObjectImageCoords={
                'x': 0,
                'y': 0
            },
            receptacleObjectId=None,
            rotation={'y': 0},
            consistentColors=False
        )

        for key, value in kwargs.items():
            data[key] = value

        return data

    def test_end_scene(self):
        # TODO When this function actually does anything
        pass

    def test_start_scene(self):
        self.controller.render_mask_images()
        output = self.controller.start_scene({'name': 'test name'})
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            mcs.Controller.ACTION_LIST)
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

        output = self.controller.start_scene({'name': 'test name'})
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            mcs.Controller.ACTION_LIST)
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
        self.controller.render_mask_images()
        last_preview_phase_step = 5
        output = self.controller.start_scene({'name': 'test name', 'goal': {
            'last_preview_phase_step': last_preview_phase_step}
        })
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            mcs.Controller.ACTION_LIST)
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
        self.controller.render_mask_images()
        output = self.controller.start_scene({'name': 'test name'})
        output = self.controller.step('MoveAhead')
        self.assertIsNotNone(output)
        self.assertEqual(
            output.action_list,
            mcs.Controller.ACTION_LIST)
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
            mcs.Controller.ACTION_LIST)
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

    def test_step_last_step(self):
        output = self.controller.start_scene({'name': 'test name'})
        self.controller.set_goal(mcs.GoalMetadata(last_step=0))
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

        self.controller.set_goal(mcs.GoalMetadata(last_step=1))
        output = self.controller.step('MoveAhead')
        self.assertIsNotNone(output)
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

    def test_step_validate_action(self):
        output = self.controller.step('Foobar')
        self.assertIsNone(output)

        self.controller.set_goal(mcs.GoalMetadata(action_list=[['Pass']]))
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

        output = self.controller.start_scene({'name': 'test name'})
        self.controller.set_goal(
            mcs.GoalMetadata(
                action_list=[
                    ['MoveAhead'],
                    ['MoveBack']]))
        output = self.controller.step('MoveAhead')
        self.assertIsNotNone(output)
        output = self.controller.step('MoveAhead')
        self.assertIsNone(output)

    def test_step_validate_parameters_move(self):
        _ = self.controller.start_scene({'name': 'test name'})
        self.controller.step('MoveAhead')
        self.assertEquals(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.MOVE_DISTANCE))

        self.controller.step('MoveAhead')
        self.assertEquals(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.MOVE_DISTANCE))

        self.controller.step('MoveAhead')
        self.assertEquals(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.MOVE_DISTANCE))

        self.controller.step('MoveAhead')
        self.assertEquals(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='MoveAhead',
                moveMagnitude=mcs.controller.MOVE_DISTANCE))

    def test_step_validate_parameters_rotate(self):
        _ = self.controller.start_scene({'name': 'test name'})
        self.controller.step('RotateLeft')
        self.assertEquals(
            self.controller.get_last_step_data(),
            self.create_step_data(action='RotateLeft'))

        self.controller.step('RotateLeft')
        self.assertEquals(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='RotateLeft'))

    def test_step_validate_parameters_force_object(self):
        _ = self.controller.start_scene({'name': 'test name'})
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
        self.assertEquals(
            self.controller.get_last_step_data(),
            self.create_step_data(
                action='PushObject',
                moveMagnitude=mcs.Controller.MAX_FORCE,
                objectImageCoords={'x': 1, 'y': 398}))

    def test_step_validate_parameters_open_close(self):
        _ = self.controller.start_scene({'name': 'test name'})
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
        self.assertEquals(
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

    def test_update_goal_target_image(self):
        goal = mcs.GoalMetadata(metadata={
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })
        actual = self.controller.update_goal_target_image(goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_img_as_str(self):
        goal = mcs.GoalMetadata(metadata={
            'target': {'image': "[0]"},
            'target_1': {'image': "[1]"},
            'target_2': {'image': "[2]"}
        })
        actual = self.controller.update_goal_target_image(goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_oracle(self):
        self.controller.set_metadata_tier('oracle')
        goal = mcs.GoalMetadata(metadata={
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })
        actual = self.controller.update_goal_target_image(goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_oracle_img_as_str(self):
        goal = mcs.GoalMetadata(metadata={
            'target': {'image': "[0]"},
            'target_1': {'image': "[1]"},
            'target_2': {'image': "[2]"}
        })
        actual = self.controller.update_goal_target_image(goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_level2(self):
        self.controller.set_metadata_tier('level2')
        goal = mcs.GoalMetadata(metadata={
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })
        actual = self.controller.update_goal_target_image(goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_level1(self):
        self.controller.set_metadata_tier('level1')
        goal = mcs.GoalMetadata(metadata={
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })
        actual = self.controller.update_goal_target_image(goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_none(self):
        self.controller.set_metadata_tier('none')
        goal = mcs.GoalMetadata(metadata={
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })
        actual = self.controller.update_goal_target_image(goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_restrict_step_output_metadata(self):
        step = mcs.StepMetadata(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_map_list=[7],
            object_mask_list=[8],
            position={'x': 4, 'y': 5, 'z': 6},
            rotation={'x': 7, 'y': 8, 'z': 9}
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_map_list, [7])
        self.assertEqual(actual.object_mask_list, [8])
        self.assertEqual(actual.position, {'x': 4, 'y': 5, 'z': 6})
        self.assertEqual(actual.rotation, {'x': 7, 'y': 8, 'z': 9})

    def test_restrict_step_output_metadata_oracle(self):
        self.controller.set_metadata_tier('oracle')
        step = mcs.StepMetadata(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_map_list=[7],
            object_mask_list=[8],
            position={'x': 4, 'y': 5, 'z': 6},
            rotation={'x': 7, 'y': 8, 'z': 9}
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_map_list, [7])
        self.assertEqual(actual.object_mask_list, [8])
        self.assertEqual(actual.position, {'x': 4, 'y': 5, 'z': 6})
        self.assertEqual(actual.rotation, {'x': 7, 'y': 8, 'z': 9})

    def test_restrict_step_output_metadata_level2(self):
        self.controller.set_metadata_tier('level2')
        step = mcs.StepMetadata(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_map_list=[7],
            object_mask_list=[8],
            position={'x': 4, 'y': 5, 'z': 6},
            rotation={'x': 7, 'y': 8, 'z': 9}
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_map_list, [7])
        self.assertEqual(actual.object_mask_list, [8])
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)

    def test_restrict_step_output_metadata_level1(self):
        self.controller.set_metadata_tier('level1')
        step = mcs.StepMetadata(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_map_list=[7],
            object_mask_list=[8],
            position={'x': 4, 'y': 5, 'z': 6},
            rotation={'x': 7, 'y': 8, 'z': 9}
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_map_list, [7])
        self.assertEqual(actual.object_mask_list, [])
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)

    def test_restrict_step_output_metadata_none(self):
        self.controller.set_metadata_tier('none')
        step = mcs.StepMetadata(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_map_list=[7],
            object_mask_list=[8],
            position={'x': 4, 'y': 5, 'z': 6},
            rotation={'x': 7, 'y': 8, 'z': 9}
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_map_list, [])
        self.assertEqual(actual.object_mask_list, [])
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)

    def test_retrieve_action_list(self):
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(), 0), self.controller.ACTION_LIST)
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(
                    action_list=[]),
                0),
            self.controller.ACTION_LIST)
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(
                    action_list=[[]]),
                0),
            self.controller.ACTION_LIST)
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(
                    action_list=[['MoveAhead', 'RotateLook,rotation=180']]
                ),
                0,
            ),
            ['MoveAhead', 'RotateLook,rotation=180']
        )
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(
                    action_list=[['MoveAhead', 'RotateLook,rotation=180']]
                ),
                1,
            ),
            self.controller.ACTION_LIST
        )
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(
                    action_list=[['MoveAhead', 'RotateLook,rotation=180'], []]
                ),
                1,
            ),
            self.controller.ACTION_LIST
        )
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(
                    action_list=[[], ['MoveAhead', 'RotateLook,rotation=180']]
                ),
                0,
            ),
            self.controller.ACTION_LIST
        )
        self.assertEqual(
            self.controller.retrieve_action_list(
                mcs.GoalMetadata(
                    action_list=[[], ['MoveAhead', 'RotateLook,rotation=180']]
                ),
                1,
            ),
            ['MoveAhead', 'RotateLook,rotation=180']
        )

    def test_retrieve_goal(self):
        goal_1 = self.controller.retrieve_goal({})
        self.assertEqual(goal_1.action_list, None)
        self.assertEqual(goal_1.category, '')
        self.assertEqual(goal_1.description, '')
        self.assertEqual(goal_1.habituation_total, 0)
        self.assertEqual(goal_1.last_step, None)
        self.assertEqual(goal_1.metadata, {})

        goal_2 = self.controller.retrieve_goal({
            "goal": {
            }
        })
        self.assertEqual(goal_2.action_list, None)
        self.assertEqual(goal_2.category, '')
        self.assertEqual(goal_2.description, '')
        self.assertEqual(goal_2.habituation_total, 0)
        self.assertEqual(goal_2.last_step, None)
        self.assertEqual(goal_2.metadata, {})

        goal_3 = self.controller.retrieve_goal({
            "goal": {
                "action_list": [
                    ["action1"],
                    [],
                    ["action2", "action3", "action4"]
                ],
                "category": "test category",
                "description": "test description",
                "habituation_total": 5,
                "last_step": 10,
                "metadata": {
                    "key": "value"
                }
            }
        })
        self.assertEqual(
            goal_3.action_list, [
                ["action1"], [], [
                    "action2", "action3", "action4"]])
        self.assertEqual(goal_3.category, "test category")
        self.assertEqual(goal_3.description, "test description")
        self.assertEqual(goal_3.habituation_total, 5)
        self.assertEqual(goal_3.last_step, 10)
        self.assertEqual(goal_3.metadata, {
            "category": "test category",
            "key": "value"
        })

    def test_retrieve_goal_with_config_metadata(self):
        self.controller.set_metadata_tier('oracle')
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': {'image': [0]},
                    'target_1': {'image': [1]},
                    'target_2': {'image': [2]}
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

        self.controller.set_metadata_tier('level2')
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': {'image': [0]},
                    'target_1': {'image': [1]},
                    'target_2': {'image': [2]}
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

        self.controller.set_metadata_tier('level1')
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': {'image': [0]},
                    'target_1': {'image': [1]},
                    'target_2': {'image': [2]}
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

        self.controller.set_metadata_tier('none')
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': {'image': [0]},
                    'target_1': {'image': [1]},
                    'target_2': {'image': [2]}
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_retrieve_head_tilt(self):
        mock_scene_event_data = {
            "metadata": {
                "agent": {
                    "cameraHorizon": 12.34
                }
            }
        }
        actual = self.controller.retrieve_head_tilt(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, 12.34)

        mock_scene_event_data = {
            "metadata": {
                "agent": {
                    "cameraHorizon": -56.78
                }
            }
        }
        actual = self.controller.retrieve_head_tilt(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, -56.78)

    def test_retrieve_object_list(self):
        self.controller.start_scene({'name': 'test name'})
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(
            self.create_mock_scene_event(mock_scene_event_data))
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
        self.controller.start_scene({
            'name': 'test name',
            'objects': [{
                'id': 'testId1',
                'states': [['a', 'b'], ['c', 'd']]
            }]
        })
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(
            self.create_mock_scene_event(mock_scene_event_data)
        )
        self.assertEqual(len(actual), 2)

        self.assertEqual(actual[0].uuid, "testId1")
        self.assertEqual(actual[0].state_list, ['a', 'b'])

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].state_list, [])

    def test_retrieve_object_list_with_config_metadata_oracle(self):
        self.controller.start_scene({'name': 'test name'})
        self.controller.set_metadata_tier('oracle')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(len(actual), 3)

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
        self.controller.start_scene({'name': 'test name'})
        self.controller.set_metadata_tier('level2')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(len(actual), 3)

    def test_retrieve_object_list_with_config_metadata_level1(self):
        self.controller.start_scene({'name': 'test name'})
        self.controller.set_metadata_tier('level1')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(len(actual), 3)

    def test_retrieve_object_list_with_config_metadata_none(self):
        self.controller.start_scene({'name': 'test name'})
        self.controller.set_metadata_tier('none')
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(len(actual), 3)

    def test_retrieve_pose(self):
        # Check function calls
        mock_scene_event_data = {
            "metadata": {
                "pose": mcs.Pose.STANDING.name
            }
        }
        ret_status = self.controller.retrieve_pose(
            self.create_mock_scene_event(mock_scene_event_data)
        )
        self.assertEqual(ret_status, mcs.Pose.STANDING.name)

        mock_scene_event_data = {
            "metadata": {
                "pose": mcs.Pose.CRAWLING.name
            }
        }
        ret_status = self.controller.retrieve_pose(
            self.create_mock_scene_event(mock_scene_event_data)
        )
        self.assertEqual(ret_status, mcs.Pose.CRAWLING.name)

        mock_scene_event_data = {
            "metadata": {
                "pose": mcs.Pose.LYING.name
            }
        }
        ret_status = self.controller.retrieve_pose(
            self.create_mock_scene_event(mock_scene_event_data)
        )
        self.assertEqual(ret_status, mcs.Pose.LYING.name)

        output = self.controller.start_scene({'name': 'test name'})

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

    def test_retrieve_return_status(self):
        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "SUCCESSFUL"
            }
        }

        actual = self.controller.retrieve_return_status(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, mcs.ReturnStatus.SUCCESSFUL.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "FAILED"
            }
        }

        actual = self.controller.retrieve_return_status(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, mcs.ReturnStatus.FAILED.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": "INVALID_STATUS"
            }
        }

        actual = self.controller.retrieve_return_status(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, mcs.ReturnStatus.UNDEFINED.name)

        mock_scene_event_data = {
            "metadata": {
                "lastActionStatus": None
            }
        }

        actual = self.controller.retrieve_return_status(
            self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(actual, mcs.ReturnStatus.UNDEFINED.name)

    def test_save_images(self):
        self.controller.render_mask_images()
        image_data = numpy.array([[0]], dtype=numpy.uint8)
        depth_data = numpy.array([[[0, 0, 0]]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        mock_scene_event_data = {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_data,
                "frame": image_data,
                "instance_segmentation_frame": object_mask_data
            })]
        }

        (
            image_list,
            depth_map_list,
            object_mask_list,
        ) = self.controller.save_images(
            self.create_mock_scene_event(mock_scene_event_data),
            15.0
        )

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
        self.controller.render_mask_images()
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
            })]
        }

        (
            image_list,
            depth_map_list,
            object_mask_list
        ) = self.controller.save_images(
            self.create_mock_scene_event(mock_scene_event_data),
            15.0
        )
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

    def test_wrap_output(self):
        self.controller.start_scene({'name': 'test name'})
        self.controller.render_mask_images()
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()
        actual = self.controller.wrap_output(
            self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
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
        self.controller.start_scene({'name': 'test name'})
        self.controller.render_mask_images()
        self.controller.set_metadata_tier('oracle')
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()
        pre_restrict = self.controller.wrap_output(
            self.create_mock_scene_event(mock_scene_event_data))

        pre_restrict.goal = self.controller.retrieve_goal({
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
            'target': {'image': [0], 'id': '1', 'image_name': "name_1"},
            'target_1': {'image': [1], 'id': '2', 'image_name': "name_2"},
            'target_2': {'image': [2], 'id': '3', 'image_name': "name_3"}
        })

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
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

    def test_wrap_output_with_config_metadata_level2(self):
        self.controller.start_scene({'name': 'test name'})
        self.controller.set_metadata_tier('level2')
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()
        pre_restrict = self.controller.wrap_output(
            self.create_mock_scene_event(mock_scene_event_data))

        pre_restrict.goal = self.controller.retrieve_goal({
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

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
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

        self.assertEqual(len(actual.depth_map_list), 0)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 0)
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
        self.controller.start_scene({'name': 'test name'})
        self.controller.set_metadata_tier('level1')
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()
        pre_restrict = self.controller.wrap_output(
            self.create_mock_scene_event(mock_scene_event_data))
        actual = self.controller.restrict_step_output_metadata(pre_restrict)

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
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

    def test_wrap_output_with_config_metadata_none(self):
        self.controller.start_scene({'name': 'test name'})
        self.controller.set_metadata_tier('none')
        (
            mock_scene_event_data,
            image_data,
            depth_data,
            object_mask_data
        ) = self.create_wrap_output_scene_event()
        pre_restrict = self.controller.wrap_output(
            self.create_mock_scene_event(mock_scene_event_data))
        actual = self.controller.restrict_step_output_metadata(pre_restrict)

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
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
            "visibilityDistance": 1.0,
            "consistentColors": False
        }
        self.assertEqual(actual, expected)

    def test_wrap_step_metadata_oracle(self):
        self.controller.set_metadata_tier('oracle')
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
            "visibilityDistance": 1.0,
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
