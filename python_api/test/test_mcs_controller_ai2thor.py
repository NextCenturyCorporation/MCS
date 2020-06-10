import mock
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
        self.controller.set_config({ 'metadata': '' })

    def create_mock_scene_event(self, mock_scene_event_data):
        # Wrap the dict in a SimpleNamespace object to permit property access with dotted notation since the actual
        # variable is a class, not a dict.
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
                }, {
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
                        "objectBoundsCorners": ["pA", "pB", "pC", "pD", "pE", "pF", "pG", "pH"]
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
                    "visibleInCamera": False
                }]
            }
        }

    def create_wrap_output_scene_event(self):
        image_data = numpy.array([[0]], dtype=numpy.uint8)
        depth_mask_data = numpy.array([[128]], dtype=numpy.uint8)
        object_mask_data = numpy.array([[192]], dtype=numpy.uint8)

        return {
            "events": [self.create_mock_scene_event({
                "depth_frame": depth_mask_data,
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
                "clippingPlaneFar": 25,
                "clippingPlaneNear": 0,
                "fov": 42.5,
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
                }, {
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
                        "objectBoundsCorners": ["pA", "pB", "pC", "pD", "pE", "pF", "pG", "pH"]
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
                    "visibleInCamera": False
                }],
                "structuralObjects": [{
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
                        "objectBoundsCorners": ["p11", "p12", "p13", "p14", "p15", "p16", "p17", "p18"]
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
                    "visibleInCamera": True
                }, {
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
                        "objectBoundsCorners": ["pAA", "pBB", "pCC", "pDD", "pEE", "pFF", "pGG", "pHH"]
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
                    "visibleInCamera": False
                }]
            }
        }, image_data, depth_mask_data, object_mask_data

    def test_end_scene(self):
        # TODO When this function actually does anything
        pass

    def test_start_scene(self):
        # TODO MCS-15
        pass

    def test_step(self):
        # TODO MCS-15
        pass

    def test_restrict_goal_output_metadata(self):
        goal = MCS_Goal(metadata={
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })
        actual = self.controller.restrict_goal_output_metadata(goal)
        self.assertEqual(actual.metadata, {
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })

    def test_restrict_goal_output_metadata_full(self):
        self.controller.set_config({ 'metadata': 'full' })
        goal = MCS_Goal(metadata={
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })
        actual = self.controller.restrict_goal_output_metadata(goal)
        self.assertEqual(actual.metadata, {
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })

    def test_restrict_goal_output_metadata_no_navigation(self):
        self.controller.set_config({ 'metadata': 'no_navigation' })
        goal = MCS_Goal(metadata={
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })
        actual = self.controller.restrict_goal_output_metadata(goal)
        self.assertEqual(actual.metadata, {
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })

    def test_restrict_goal_output_metadata_no_vision(self):
        self.controller.set_config({ 'metadata': 'no_vision' })
        goal = MCS_Goal(metadata={
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })
        actual = self.controller.restrict_goal_output_metadata(goal)
        self.assertEqual(actual.metadata, {
            'target': { 'image': None },
            'target_1': { 'image': None },
            'target_2': { 'image': None }
        })

    def test_restrict_goal_output_metadata_none(self):
        self.controller.set_config({ 'metadata': 'none' })
        goal = MCS_Goal(metadata={
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })
        actual = self.controller.restrict_goal_output_metadata(goal)
        self.assertEqual(actual.metadata, {
            'target': { 'image': None },
            'target_1': { 'image': None },
            'target_2': { 'image': None }
        })

    def test_restrict_object_output_metadata(self):
        test_object = MCS_Object(
            color={ 'r': 1, 'g': 2, 'b': 3 },
            dimensions={ 'x': 1, 'y': 2, 'z': 3 },
            distance=12.34,
            distance_in_steps=34.56,
            distance_in_world=56.78,
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_object_output_metadata(test_object)
        self.assertEqual(actual.color, { 'r': 1, 'g': 2, 'b': 3 })
        self.assertEqual(actual.dimensions, { 'x': 1, 'y': 2, 'z': 3 })
        self.assertEqual(actual.distance, 12.34)
        self.assertEqual(actual.distance_in_steps, 34.56)
        self.assertEqual(actual.distance_in_world, 56.78)
        self.assertEqual(actual.position, { 'x': 4, 'y': 5, 'z': 6 })
        self.assertEqual(actual.rotation, { 'x': 7, 'y': 8, 'z': 9 })

    def test_restrict_object_output_metadata_full(self):
        self.controller.set_config({ 'metadata': 'full' })
        test_object = MCS_Object(
            color={ 'r': 1, 'g': 2, 'b': 3 },
            dimensions={ 'x': 1, 'y': 2, 'z': 3 },
            distance=12.34,
            distance_in_steps=34.56,
            distance_in_world=56.78,
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_object_output_metadata(test_object)
        self.assertEqual(actual.color, { 'r': 1, 'g': 2, 'b': 3 })
        self.assertEqual(actual.dimensions, { 'x': 1, 'y': 2, 'z': 3 })
        self.assertEqual(actual.distance, 12.34)
        self.assertEqual(actual.distance_in_steps, 34.56)
        self.assertEqual(actual.distance_in_world, 56.78)
        self.assertEqual(actual.position, { 'x': 4, 'y': 5, 'z': 6 })
        self.assertEqual(actual.rotation, { 'x': 7, 'y': 8, 'z': 9 })

    def test_restrict_object_output_metadata_no_navigation(self):
        self.controller.set_config({ 'metadata': 'no_navigation' })
        test_object = MCS_Object(
            color={ 'r': 1, 'g': 2, 'b': 3 },
            dimensions={ 'x': 1, 'y': 2, 'z': 3 },
            distance=12.34,
            distance_in_steps=34.56,
            distance_in_world=56.78,
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_object_output_metadata(test_object)
        self.assertEqual(actual.color, { 'r': 1, 'g': 2, 'b': 3 })
        self.assertEqual(actual.dimensions, { 'x': 1, 'y': 2, 'z': 3 })
        self.assertEqual(actual.distance, 12.34)
        self.assertEqual(actual.distance_in_steps, 34.56)
        self.assertEqual(actual.distance_in_world, 56.78)
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)

    def test_restrict_object_output_metadata_no_vision(self):
        self.controller.set_config({ 'metadata': 'no_vision' })
        test_object = MCS_Object(
            color={ 'r': 1, 'g': 2, 'b': 3 },
            dimensions={ 'x': 1, 'y': 2, 'z': 3 },
            distance=12.34,
            distance_in_steps=34.56,
            distance_in_world=56.78,
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_object_output_metadata(test_object)
        self.assertEqual(actual.color, None)
        self.assertEqual(actual.dimensions, None)
        self.assertEqual(actual.distance, None)
        self.assertEqual(actual.distance_in_steps, None)
        self.assertEqual(actual.distance_in_world, None)
        self.assertEqual(actual.position, { 'x': 4, 'y': 5, 'z': 6 })
        self.assertEqual(actual.rotation, { 'x': 7, 'y': 8, 'z': 9 })

    def test_restrict_object_output_metadata_none(self):
        self.controller.set_config({ 'metadata': 'none' })
        test_object = MCS_Object(
            color={ 'r': 1, 'g': 2, 'b': 3 },
            dimensions={ 'x': 1, 'y': 2, 'z': 3 },
            distance=12.34,
            distance_in_steps=34.56,
            distance_in_world=56.78,
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_object_output_metadata(test_object)
        self.assertEqual(actual.color, None)
        self.assertEqual(actual.dimensions, None)
        self.assertEqual(actual.distance, None)
        self.assertEqual(actual.distance_in_steps, None)
        self.assertEqual(actual.distance_in_world, None)
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)

    def test_restrict_step_output_metadata(self):
        step = MCS_Step_Output(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_mask_list=[7],
            object_mask_list=[8],
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_mask_list, [7])
        self.assertEqual(actual.object_mask_list, [8])
        self.assertEqual(actual.position, { 'x': 4, 'y': 5, 'z': 6 })
        self.assertEqual(actual.rotation, { 'x': 7, 'y': 8, 'z': 9 })

    def test_restrict_step_output_metadata_full(self):
        self.controller.set_config({ 'metadata': 'full' })
        step = MCS_Step_Output(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_mask_list=[7],
            object_mask_list=[8],
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_mask_list, [7])
        self.assertEqual(actual.object_mask_list, [8])
        self.assertEqual(actual.position, { 'x': 4, 'y': 5, 'z': 6 })
        self.assertEqual(actual.rotation, { 'x': 7, 'y': 8, 'z': 9 })

    def test_restrict_step_output_metadata_no_navigation(self):
        self.controller.set_config({ 'metadata': 'no_navigation' })
        step = MCS_Step_Output(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_mask_list=[7],
            object_mask_list=[8],
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, (1, 2))
        self.assertEqual(actual.camera_clipping_planes, (3, 4))
        self.assertEqual(actual.camera_field_of_view, 5)
        self.assertEqual(actual.camera_height, 6)
        self.assertEqual(actual.depth_mask_list, [7])
        self.assertEqual(actual.object_mask_list, [8])
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)

    def test_restrict_step_output_metadata_no_vision(self):
        self.controller.set_config({ 'metadata': 'no_vision' })
        step = MCS_Step_Output(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_mask_list=[7],
            object_mask_list=[8],
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, None)
        self.assertEqual(actual.camera_clipping_planes, None)
        self.assertEqual(actual.camera_field_of_view, None)
        self.assertEqual(actual.camera_height, None)
        self.assertEqual(actual.depth_mask_list, [])
        self.assertEqual(actual.object_mask_list, [])
        self.assertEqual(actual.position, { 'x': 4, 'y': 5, 'z': 6 })
        self.assertEqual(actual.rotation, { 'x': 7, 'y': 8, 'z': 9 })

    def test_restrict_step_output_metadata_none(self):
        self.controller.set_config({ 'metadata': 'none' })
        step = MCS_Step_Output(
            camera_aspect_ratio=(1, 2),
            camera_clipping_planes=(3, 4),
            camera_field_of_view=5,
            camera_height=6,
            depth_mask_list=[7],
            object_mask_list=[8],
            position={ 'x': 4, 'y': 5, 'z': 6 },
            rotation={ 'x': 7, 'y': 8, 'z': 9 }
        )
        actual = self.controller.restrict_step_output_metadata(step)
        self.assertEqual(actual.camera_aspect_ratio, None)
        self.assertEqual(actual.camera_clipping_planes, None)
        self.assertEqual(actual.camera_field_of_view, None)
        self.assertEqual(actual.camera_height, None)
        self.assertEqual(actual.depth_mask_list, [])
        self.assertEqual(actual.object_mask_list, [])
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)

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

    def test_retrieve_goal_with_config_metadata(self):
        self.controller.set_config({ 'metadata': 'full' })
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': { 'image': [0] },
                    'target_1': { 'image': [1] },
                    'target_2': { 'image': [2] }
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })

        self.controller.set_config({ 'metadata': 'no_navigation' })
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': { 'image': [0] },
                    'target_1': { 'image': [1] },
                    'target_2': { 'image': [2] }
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': { 'image': [0] },
            'target_1': { 'image': [1] },
            'target_2': { 'image': [2] }
        })

        self.controller.set_config({ 'metadata': 'no_vision' })
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': { 'image': [0] },
                    'target_1': { 'image': [1] },
                    'target_2': { 'image': [2] }
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': { 'image': None },
            'target_1': { 'image': None },
            'target_2': { 'image': None }
        })

        self.controller.set_config({ 'metadata': 'none' })
        actual = self.controller.retrieve_goal({
            'goal': {
                'metadata': {
                    'target': { 'image': [0] },
                    'target_1': { 'image': [1] },
                    'target_2': { 'image': [2] }
                }
            }
        })
        self.assertEqual(actual.metadata, {
            'target': { 'image': None },
            'target_1': { 'image': None },
            'target_2': { 'image': None }
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
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
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
        self.assertEqual(actual[0].position, { "x": 1, "y": 1, "z": 2 })
        self.assertEqual(actual[0].rotation, 2.0)
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
        self.assertEqual(actual[1].position, { "x": 1, "y": 2, "z": 3 })
        self.assertEqual(actual[1].rotation, 2)
        self.assertEqual(actual[1].visible, True)

    def test_retrieve_object_list_with_config_metadata_full(self):
        self.controller.set_config({ 'metadata': 'full' })
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(self.create_mock_scene_event(mock_scene_event_data))
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
        self.assertEqual(actual[0].position, { "x": 1, "y": 1, "z": 2 })
        self.assertEqual(actual[0].rotation, 2.0)
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
        self.assertEqual(actual[1].position, { "x": 1, "y": 2, "z": 3 })
        self.assertEqual(actual[1].rotation, 2)
        self.assertEqual(actual[1].visible, True)

        self.assertEqual(actual[2].uuid, "testId3")
        self.assertEqual(actual[2].color, {
            "r": 101,
            "g": 102,
            "b": 103
        })
        self.assertEqual(actual[2].dimensions, ["pA", "pB", "pC", "pD", "pE", "pF", "pG", "pH"])
        self.assertEqual(actual[2].direction, {
            "x": -90,
            "y": 180,
            "z": 270
        })
        self.assertEqual(actual[2].distance, 4)
        self.assertEqual(actual[2].distance_in_steps, 4)
        self.assertEqual(actual[2].distance_in_world, 2.5)
        self.assertEqual(actual[2].held, False)
        self.assertEqual(actual[2].mass, 34.56)
        self.assertEqual(actual[2].material_list, ["WOOD"])
        self.assertEqual(actual[2].position, { "x": -3, "y": -2, "z": -1 })
        self.assertEqual(actual[2].rotation, 12)
        self.assertEqual(actual[2].visible, False)

    def test_retrieve_object_list_with_config_metadata_no_navigation(self):
        self.controller.set_config({ 'metadata': 'no_navigation' })
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
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
        self.assertEqual(actual[0].position, None)
        self.assertEqual(actual[0].rotation, None)
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
        self.assertEqual(actual[1].position, None)
        self.assertEqual(actual[1].rotation, None)
        self.assertEqual(actual[1].visible, True)

    def test_retrieve_object_list_with_config_metadata_no_vision(self):
        self.controller.set_config({ 'metadata': 'no_vision' })
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(len(actual), 2)

        self.assertEqual(actual[0].uuid, "testId1")
        self.assertEqual(actual[0].color, None)
        self.assertEqual(actual[0].dimensions, None)
        self.assertEqual(actual[0].direction, None)
        self.assertEqual(actual[0].distance, None)
        self.assertEqual(actual[0].distance_in_steps, None)
        self.assertEqual(actual[0].distance_in_world, None)
        self.assertEqual(actual[0].held, True)
        self.assertEqual(actual[0].mass, 1)
        self.assertEqual(actual[0].material_list, [])
        self.assertEqual(actual[0].position, { "x": 1, "y": 1, "z": 2 })
        self.assertEqual(actual[0].rotation, 2.0)
        self.assertEqual(actual[0].visible, True)

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].color, None)
        self.assertEqual(actual[1].dimensions, None)
        self.assertEqual(actual[1].direction, None)
        self.assertEqual(actual[1].distance, None)
        self.assertEqual(actual[1].distance_in_steps, None)
        self.assertEqual(actual[1].distance_in_world, None)
        self.assertEqual(actual[1].held, False)
        self.assertEqual(actual[1].mass, 12.34)
        self.assertEqual(actual[1].material_list, ["METAL", "PLASTIC"])
        self.assertEqual(actual[1].position, { "x": 1, "y": 2, "z": 3 })
        self.assertEqual(actual[1].rotation, 2)
        self.assertEqual(actual[1].visible, True)

    def test_retrieve_object_list_with_config_metadata_none(self):
        self.controller.set_config({ 'metadata': 'none' })
        mock_scene_event_data = self.create_retrieve_object_list_scene_event()
        actual = self.controller.retrieve_object_list(self.create_mock_scene_event(mock_scene_event_data))
        self.assertEqual(len(actual), 2)

        self.assertEqual(actual[0].uuid, "testId1")
        self.assertEqual(actual[0].color, None)
        self.assertEqual(actual[0].dimensions, None)
        self.assertEqual(actual[0].direction, None)
        self.assertEqual(actual[0].distance, None)
        self.assertEqual(actual[0].distance_in_steps, None)
        self.assertEqual(actual[0].distance_in_world, None)
        self.assertEqual(actual[0].held, True)
        self.assertEqual(actual[0].mass, 1)
        self.assertEqual(actual[0].material_list, [])
        self.assertEqual(actual[0].position, None)
        self.assertEqual(actual[0].rotation, None)
        self.assertEqual(actual[0].visible, True)

        self.assertEqual(actual[1].uuid, "testId2")
        self.assertEqual(actual[1].color, None)
        self.assertEqual(actual[1].dimensions, None)
        self.assertEqual(actual[1].direction, None)
        self.assertEqual(actual[1].distance, None)
        self.assertEqual(actual[1].distance_in_steps, None)
        self.assertEqual(actual[1].distance_in_world, None)
        self.assertEqual(actual[1].held, False)
        self.assertEqual(actual[1].mass, 12.34)
        self.assertEqual(actual[1].material_list, ["METAL", "PLASTIC"])
        self.assertEqual(actual[1].position, None)
        self.assertEqual(actual[1].rotation, None)
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
        self.assertEqual(numpy.array(depth_mask_list[0]), depth_mask_data)
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
        self.assertEqual(numpy.array(depth_mask_list[0]), depth_mask_data_1)
        self.assertEqual(numpy.array(object_mask_list[0]), object_mask_data_1)

        self.assertEqual(numpy.array(image_list[1]), image_data_2)
        self.assertEqual(numpy.array(depth_mask_list[1]), depth_mask_data_2)
        self.assertEqual(numpy.array(object_mask_list[1]), object_mask_data_2)

    def test_validate_and_convert_params(self):
        # TODO MCS-15
        pass

    def test_wrap_output(self):
        mock_scene_event_data, image_data, depth_mask_data, object_mask_data = self.create_wrap_output_scene_event()
        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 25))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-15
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, MCS_Pose.STAND.value) # TODO MCS-18
        self.assertEqual(actual.position, { 'x': 0.12, 'y': -0.23, 'z': 4.5 })
        self.assertEqual(actual.rotation, 2.222)
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

        self.assertEqual(len(actual.structural_object_list), 1)
        self.assertEqual(actual.structural_object_list[0].uuid, "testWallId")
        self.assertEqual(actual.structural_object_list[0].color, {
            "r": 101,
            "g": 102,
            "b": 103
        })
        self.assertEqual(actual.structural_object_list[0].dimensions, ["p11", "p12", "p13", "p14", "p15", "p16", "p17", "p18"])
        self.assertEqual(actual.structural_object_list[0].direction, {
            "x": 180,
            "y": -60,
            "z": 0
        })
        self.assertEqual(actual.structural_object_list[0].distance, 4.4)
        self.assertEqual(actual.structural_object_list[0].distance_in_steps, 4.4)
        self.assertEqual(actual.structural_object_list[0].distance_in_world, 2.5)
        self.assertEqual(actual.structural_object_list[0].held, False)
        self.assertEqual(actual.structural_object_list[0].mass, 56.78)
        self.assertEqual(actual.structural_object_list[0].material_list, ["CERAMIC"])
        self.assertEqual(actual.structural_object_list[0].visible, True)

        self.assertEqual(len(actual.depth_mask_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 1)
        self.assertEqual(numpy.array(actual.depth_mask_list[0]), depth_mask_data)
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        self.assertEqual(numpy.array(actual.object_mask_list[0]), object_mask_data)

    def test_wrap_output_with_config_metadata_full(self):
        self.controller.set_config({ 'metadata': 'full' })
        mock_scene_event_data, image_data, depth_mask_data, object_mask_data = self.create_wrap_output_scene_event()
        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 25))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-15
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, MCS_Pose.STAND.value) # TODO MCS-18
        self.assertEqual(actual.position, { 'x': 0.12, 'y': -0.23, 'z': 4.5 })
        self.assertEqual(actual.rotation, 2.222)
        self.assertEqual(actual.return_status, MCS_Return_Status.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 2)
        self.assertEqual(len(actual.structural_object_list), 2)

        self.assertEqual(len(actual.depth_mask_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 1)
        self.assertEqual(numpy.array(actual.depth_mask_list[0]), depth_mask_data)
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        self.assertEqual(numpy.array(actual.object_mask_list[0]), object_mask_data)

    def test_wrap_output_with_config_metadata_no_navigation(self):
        self.controller.set_config({ 'metadata': 'no_navigation' })
        mock_scene_event_data, image_data, depth_mask_data, object_mask_data = self.create_wrap_output_scene_event()
        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, (600, 400))
        self.assertEqual(actual.camera_clipping_planes, (0, 25))
        self.assertEqual(actual.camera_field_of_view, 42.5)
        self.assertEqual(actual.camera_height, 0.1234)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-15
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, MCS_Pose.STAND.value) # TODO MCS-18
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)
        self.assertEqual(actual.return_status, MCS_Return_Status.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 1)
        self.assertEqual(len(actual.structural_object_list), 1)

        self.assertEqual(len(actual.depth_mask_list), 1)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 1)
        self.assertEqual(numpy.array(actual.depth_mask_list[0]), depth_mask_data)
        self.assertEqual(numpy.array(actual.image_list[0]), image_data)
        self.assertEqual(numpy.array(actual.object_mask_list[0]), object_mask_data)

    def test_wrap_output_with_config_metadata_no_vision(self):
        self.controller.set_config({ 'metadata': 'no_vision' })
        mock_scene_event_data, image_data, depth_mask_data, object_mask_data = self.create_wrap_output_scene_event()
        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, None)
        self.assertEqual(actual.camera_clipping_planes, None)
        self.assertEqual(actual.camera_field_of_view, None)
        self.assertEqual(actual.camera_height, None)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-15
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, MCS_Pose.STAND.value) # TODO MCS-18
        self.assertEqual(actual.position, { 'x': 0.12, 'y': -0.23, 'z': 4.5 })
        self.assertEqual(actual.rotation, 2.222)
        self.assertEqual(actual.return_status, MCS_Return_Status.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 1)
        self.assertEqual(len(actual.structural_object_list), 1)

        self.assertEqual(len(actual.depth_mask_list), 0)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 0)

    def test_wrap_output_with_config_metadata_none(self):
        self.controller.set_config({ 'metadata': 'none' })
        mock_scene_event_data, image_data, depth_mask_data, object_mask_data = self.create_wrap_output_scene_event()
        actual = self.controller.wrap_output(self.create_mock_scene_event(mock_scene_event_data))

        self.assertEqual(actual.action_list, self.controller.ACTION_LIST)
        self.assertEqual(actual.camera_aspect_ratio, None)
        self.assertEqual(actual.camera_clipping_planes, None)
        self.assertEqual(actual.camera_field_of_view, None)
        self.assertEqual(actual.camera_height, None)
        # self.assertEqual(actual.goal, MCS_Goal()) # TODO MCS-15
        self.assertEqual(actual.head_tilt, 12.34)
        self.assertEqual(actual.pose, MCS_Pose.STAND.value) # TODO MCS-18
        self.assertEqual(actual.position, None)
        self.assertEqual(actual.rotation, None)
        self.assertEqual(actual.return_status, MCS_Return_Status.SUCCESSFUL.value)
        self.assertEqual(actual.step_number, 0)

        # Correct object metadata properties tested elsewhere
        self.assertEqual(len(actual.object_list), 1)
        self.assertEqual(len(actual.structural_object_list), 1)

        self.assertEqual(len(actual.depth_mask_list), 0)
        self.assertEqual(len(actual.image_list), 1)
        self.assertEqual(len(actual.object_mask_list), 0)

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

