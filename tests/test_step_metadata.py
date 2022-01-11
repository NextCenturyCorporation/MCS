import copy
import textwrap
import unittest

import machine_common_sense as mcs


class TestStepMetadata(unittest.TestCase):

    str_output = '''    {
        "action_list": [],
        "camera_aspect_ratio": [0.0,0.0],
        "camera_clipping_planes": [0.0,0.0],
        "camera_field_of_view": 0.0,
        "camera_height": 0.0,
        "depth_map_list": [],
        "goal": {
            "action_list": null,
            "category": "",
            "description": "",
            "habituation_total": 0,
            "last_preview_phase_step": 0,
            "last_step": null,
            "metadata": {}
        },
        "habituation_trial": null,
        "head_tilt": 0.0,
        "image_list": [],
        "object_list": [],
        "object_mask_list": [],
        "performer_radius": 0.0,
        "performer_reach": 0.0,
        "physics_frames_per_second": 0,
        "pose": "UNDEFINED",
        "position": {},
        "return_status": "UNDEFINED",
        "reward": 0,
        "rotation": 0.0,
        "step_number": 0,
        "structural_object_list": []
    }'''

    str_output_segment_map_ints = '''    {
        "action_list": [],
        "camera_aspect_ratio": [0.0,0.0],
        "camera_clipping_planes": [0.0,0.0],
        "camera_field_of_view": 0.0,
        "camera_height": 0.0,
        "depth_map_list": [],
        "goal": {
            "action_list": null,
            "category": "",
            "description": "",
            "habituation_total": 0,
            "last_preview_phase_step": 0,
            "last_step": null,
            "metadata": {}
        },
        "habituation_trial": null,
        "head_tilt": 0.0,
        "image_list": [],
        "object_list": [],
        "object_mask_list": [],
        "performer_radius": 0.0,
        "performer_reach": 0.0,
        "physics_frames_per_second": 0,
        "pose": "UNDEFINED",
        "position": {},
        "return_status": "UNDEFINED",
        "reward": 0,
        "rotation": 0.0,
        "step_number": 0,
        "structural_object_list": [],
        "segment_map": {
            "0": {
                "r": 218,
                "g": 65,
                "b": 21
            }
        }
    }'''

    @classmethod
    def setUpClass(cls):
        cls.step_metadata = mcs.StepMetadata()

    @classmethod
    def tearDownClass(cls):
        # nothing to do here
        pass

    def test_action_list(self):
        self.assertFalse(self.step_metadata.action_list)
        self.assertIsInstance(self.step_metadata.action_list, list)

    def test_camera_aspect_ratio(self):
        self.assertIsInstance(self.step_metadata.camera_aspect_ratio, tuple)

    def test_camera_clipping_planes(self):
        self.assertIsInstance(
            self.step_metadata.camera_clipping_planes, tuple)

    def test_camera_field_of_view(self):
        self.assertIsInstance(self.step_metadata.camera_field_of_view, float)

    def test_camera_height(self):
        self.assertIsInstance(self.step_metadata.camera_height, float)

    def test_depth_map_list(self):
        self.assertFalse(self.step_metadata.depth_map_list)
        self.assertIsInstance(self.step_metadata.depth_map_list, list)

    def test_goal(self):
        self.assertIsInstance(self.step_metadata.goal, mcs.GoalMetadata)

    def test_habituation_trial(self):
        self.assertEqual(self.step_metadata.habituation_trial, None)

    def test_head_tilt(self):
        self.assertAlmostEqual(self.step_metadata.head_tilt, 0.0)
        self.assertIsInstance(self.step_metadata.head_tilt, float)

    def test_image_list(self):
        self.assertFalse(self.step_metadata.image_list)
        self.assertIsInstance(self.step_metadata.image_list, list)

    def test_object_list(self):
        self.assertFalse(self.step_metadata.object_list)
        self.assertIsInstance(self.step_metadata.object_list, list)

    def test_object_mask_list(self):
        self.assertFalse(self.step_metadata.object_mask_list)
        self.assertIsInstance(self.step_metadata.object_mask_list, list)

    def test_performer_radius(self):
        self.assertEqual(self.step_metadata.performer_radius, 0.0)
        self.assertIsInstance(self.step_metadata.performer_radius, float)

    def test_performer_reach(self):
        self.assertEqual(self.step_metadata.performer_reach, 0.0)
        self.assertIsInstance(self.step_metadata.performer_reach, float)

    def test_pose(self):
        self.assertEqual(self.step_metadata.pose, mcs.Pose.UNDEFINED.value)
        self.assertIsInstance(self.step_metadata.pose, str)

    def test_position(self):
        self.assertIsInstance(self.step_metadata.position, dict)

    def test_return_status(self):
        self.assertEqual(
            self.step_metadata.return_status,
            mcs.ReturnStatus.UNDEFINED.value)
        self.assertIsInstance(self.step_metadata.return_status, str)

    def test_reward(self):
        self.assertEqual(self.step_metadata.reward, 0)
        self.assertIsInstance(self.step_metadata.reward, int)

    def test_rotation(self):
        self.assertAlmostEqual(self.step_metadata.rotation, 0.0)
        self.assertIsInstance(self.step_metadata.rotation, float)

    def test_step_number(self):
        self.assertEqual(self.step_metadata.step_number, 0)
        self.assertIsInstance(self.step_metadata.step_number, int)

    def test_structural_object_list(self):
        self.assertFalse(self.step_metadata.structural_object_list)
        self.assertIsInstance(
            self.step_metadata.structural_object_list, list)

    def test_str(self):
        self.assertEqual(str(self.step_metadata),
                         textwrap.dedent(self.str_output))

    def test_str_int_segment_map(self):
        metadata = copy.deepcopy(self.step_metadata)
        metadata.segment_map = {
            0: {
                'r': 218,
                'g': 65,
                'b': 21
            }
        }
        self.assertEqual(str(metadata),
                         textwrap.dedent(self.str_output_segment_map_ints))

    def test_copy_without_depth_or_images(self):
        data = mcs.StepMetadata(
            action_list=['action_1', 'action_2'],
            camera_aspect_ratio=[3, 2],
            camera_clipping_planes=[0, 10],
            camera_field_of_view=10,
            camera_height=2,
            depth_map_list=['depth_1', 'depth_2'],
            goal=mcs.GoalMetadata(metadata={'key': 'value'}),
            habituation_trial=1,
            head_tilt=15,
            image_list=['image_1', 'image_2'],
            object_list=[
                mcs.ObjectMetadata(uuid='object_1'),
                mcs.ObjectMetadata(uuid='object_2')
            ],
            object_mask_list=['segmentation_1', 'segmentation_2'],
            performer_radius=0.5,
            performer_reach=1,
            physics_frames_per_second=20,
            pose=mcs.Pose.CRAWLING.value,
            position={'x': 1, 'z': 2},
            return_status=mcs.ReturnStatus.SUCCESSFUL.value,
            reward=0,
            rotation=90,
            step_number=25,
            structural_object_list=[
                mcs.ObjectMetadata(uuid='structure_1'),
                mcs.ObjectMetadata(uuid='structure_2')
            ]
        )
        copy = data.copy_without_depth_or_images()
        # Assert are exactly equal
        self.assertEqual(data.action_list, copy.action_list)
        self.assertEqual(data.camera_aspect_ratio, copy.camera_aspect_ratio)
        self.assertEqual(
            data.camera_clipping_planes,
            copy.camera_clipping_planes
        )
        self.assertEqual(
            data.camera_field_of_view,
            copy.camera_field_of_view
        )
        self.assertEqual(data.camera_height, copy.camera_height)
        self.assertEqual(dict(data.goal), dict(copy.goal))
        self.assertEqual(data.habituation_trial, copy.habituation_trial)
        self.assertEqual(data.head_tilt, copy.head_tilt)
        self.assertEqual(
            [dict(object_data) for object_data in data.object_list],
            [dict(object_data) for object_data in copy.object_list]
        )
        self.assertEqual(data.performer_radius, copy.performer_radius)
        self.assertEqual(data.performer_reach, copy.performer_reach)
        self.assertEqual(
            data.physics_frames_per_second,
            copy.physics_frames_per_second
        )
        self.assertEqual(data.pose, copy.pose)
        self.assertEqual(data.position, copy.position)
        self.assertEqual(data.return_status, copy.return_status)
        self.assertEqual(data.reward, copy.reward)
        self.assertEqual(data.rotation, copy.rotation)
        self.assertEqual(data.step_number, copy.step_number)
        self.assertEqual(
            [dict(object_data) for object_data in data.structural_object_list],
            [dict(object_data) for object_data in copy.structural_object_list]
        )
        # Assert are empty lists
        self.assertEqual(copy.depth_map_list, [])
        self.assertEqual(copy.image_list, [])
        self.assertEqual(copy.object_mask_list, [])
        # Assert are not the same instances
        self.assertNotEqual(data.goal, copy.goal)
        self.assertNotEqual(data.object_list, copy.object_list)
        self.assertNotEqual(
            data.structural_object_list,
            copy.structural_object_list
        )


if __name__ == '__main__':
    unittest.main()
