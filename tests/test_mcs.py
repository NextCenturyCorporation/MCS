from machine_common_sense.config_manager import ConfigManager

import unittest

import machine_common_sense as mcs
from .mock_controller import MockController

from machine_common_sense.controller_logger import ControllerLogger
from machine_common_sense.controller_media import (
    DepthVideoEventHandler,
    DepthImageEventHandler,
    HeatmapVideoEventHandler,
    ImageVideoEventHandler,
    ObjectMaskImageEventHandler,
    SceneImageEventHandler,
    TopdownVideoEventHandler,
    SegmentationVideoEventHandler)
from machine_common_sense.history_writer import HistoryEventHandler
from machine_common_sense.setup import add_subscribers


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
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 2)
        classes = (ControllerLogger, HistoryEventHandler)
        self.assertIsInstance(ctrl._subscribers[0], classes)
        self.assertIsInstance(ctrl._subscribers[1], classes)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_false
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 4)
        self.assertIsInstance(ctrl._subscribers[0], DepthImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[1], SceneImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[2], ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[3], HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 5)
        self.assertIsInstance(ctrl._subscribers[0], ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            HeatmapVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[3], ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[4], HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 6)
        self.assertIsInstance(ctrl._subscribers[0], ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            HeatmapVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[3],
            SegmentationVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[4], ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[5], HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_false
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 4)
        self.assertIsInstance(ctrl._subscribers[0], DepthImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[1], SceneImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[2], ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[3], HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_false
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 5)
        self.assertIsInstance(ctrl._subscribers[0], DepthImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[1], SceneImageEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            ObjectMaskImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[3], ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[4], HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 7)
        self.assertIsInstance(ctrl._subscribers[0], ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            HeatmapVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[3],
            DepthVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[4],
            SegmentationVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[5], ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[6], HistoryEventHandler)

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 10)
        self.assertIsInstance(ctrl._subscribers[0], DepthImageEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[1],
            SceneImageEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[2],
            ObjectMaskImageEventHandler)
        self.assertIsInstance(ctrl._subscribers[3], ImageVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[4],
            TopdownVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[5],
            HeatmapVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[6],
            DepthVideoEventHandler)
        self.assertIsInstance(
            ctrl._subscribers[7],
            SegmentationVideoEventHandler)
        self.assertIsInstance(ctrl._subscribers[8], ControllerLogger)
        self.assertIsInstance(ctrl._subscribers[9], HistoryEventHandler)

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
