from machine_common_sense.config_manager import ConfigManager
import unittest

import machine_common_sense as mcs
from .mock_controller import MockController


class TestMCS(unittest.TestCase):

    def test_create_controller(self):
        # TODO How do we test this without starting the whole app?
        pass

    def test_add_subscribers(self):
        ctrl = MockController()
        cfg = ConfigManager()
        ctrl._subscribers.clear()

        def return_true():
            return True

        def return_false():
            return False

        cfg.is_history_enabled = return_false
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_false
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 2)
        classes = (mcs.ControllerLogger, mcs.HistoryEventHandler)
        self.assertIsInstance(ctrl._subscribers[0], classes)
        self.assertIsInstance(ctrl._subscribers[1], classes)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_false
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 4)
        self.assertIsInstance(ctrl._subscribers[0], mcs.DepthImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[1], mcs.SceneImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[2], mcs.ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[3], mcs.HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_true
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 5)
        self.assertIsInstance(ctrl._subscribers[0], mcs.ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            mcs.TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            mcs.HeatmapVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[3], mcs.ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[4], mcs.HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 6)
        self.assertIsInstance(ctrl._subscribers[0], mcs.ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            mcs.TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            mcs.HeatmapVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[3],
            mcs.SegmentationVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[4], mcs.ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[5], mcs.HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_false
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 4)
        self.assertIsInstance(ctrl._subscribers[0], mcs.DepthImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[1], mcs.SceneImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[2], mcs.ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[3], mcs.HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_false
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 5)
        self.assertIsInstance(ctrl._subscribers[0], mcs.DepthImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[1], mcs.SceneImageEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            mcs.ObjectMaskImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[3], mcs.ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[4], mcs.HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 7)
        self.assertIsInstance(ctrl._subscribers[0], mcs.ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            mcs.TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            mcs.HeatmapVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[3],
            mcs.DepthVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[4],
            mcs.SegmentationVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[5], mcs.ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[6], mcs.HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        mcs._add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 10)
        self.assertIsInstance(ctrl._subscribers[0], mcs.DepthImageEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            mcs.SceneImageEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            mcs.ObjectMaskImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[3], mcs.ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[4],
            mcs.TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[5],
            mcs.HeatmapVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[6],
            mcs.DepthVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[7],
            mcs.SegmentationVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[8], mcs.ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[9], mcs.HistoryEventHandler)

    def test_load_scene_file_json(self):
        actual, status = mcs.load_scene_json_file("tests/test_scene.json")
        expected = {
            "ceilingMaterial": "Walls/WallDrywallWhite",
            "floorMaterial": "Fabrics/RUG4",
            "wallMaterial": "Walls/YellowDrywall",
            "objects": [{
                "id": "testBall",
                "type": "sphere",
                "materialFile": "Plastics/BlueRubber",
                "physics": True,
                "shows": [{
                    "stepBegin": 0,
                    "position": {
                        "x": 0,
                        "y": 0.5,
                        "z": 3
                    },
                    "scale": {
                        "x": 0.25,
                        "y": 0.25,
                        "z": 0.25
                    }
                }],
                "forces": [{
                    "stepBegin": 1,
                    "stepEnd": 1,
                    "vector": {
                        "x": 50,
                        "y": 0,
                        "z": 0
                    }
                }]
            }]
        }
        self.assertEqual(actual, expected)
        self.assertEqual(status, None)

    def test_load_scene_file_json_is_invalid(self):
        actual, status = mcs.load_scene_json_file(
            "tests/test_scene_invalid.json")
        self.assertEqual(actual, {})
        self.assertEqual(
            status,
            "The given file 'tests/test_scene_invalid.json' does not " +
            "contain valid JSON."
        )

    def test_load_scene_file_json_is_missing(self):
        actual, status = mcs.load_scene_json_file(
            "tests/test_scene_missing.json")
        self.assertEqual(actual, {})
        self.assertEqual(
            status,
            "The given file 'tests/test_scene_missing.json' cannot be found.")


if __name__ == '__main__':
    unittest.main()
