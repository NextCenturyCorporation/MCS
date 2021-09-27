import unittest

import machine_common_sense as mcs
from machine_common_sense.config_manager import ConfigManager
from machine_common_sense.controller_logger import ControllerLogger
from machine_common_sense.controller_media import (
    DepthImageEventHandler, DepthVideoEventHandler, ImageVideoEventHandler,
    ObjectMaskImageEventHandler, SceneImageEventHandler,
    SegmentationVideoEventHandler, TopdownVideoEventHandler)
from machine_common_sense.history_writer import HistoryEventHandler
from machine_common_sense.setup import add_subscribers

from .mock_controller import MockController


class TestMCS(unittest.TestCase):

    def test_create_controller(self):
        # TODO How do we test this without starting the whole app?
        pass

    def test_add_subscribers(self):
        ctrl = MockController()
        cfg = ConfigManager({})
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
        self.assertTrue(
            any([isinstance(subscriber, ControllerLogger)
                 for subscriber in ctrl._subscribers]))
        self.assertTrue(
            any([isinstance(subscriber, HistoryEventHandler)
                 for subscriber in ctrl._subscribers]))

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_false
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 4)
        # the order of event handlers in the list doesn't matter
        # These assertions check that any of the elements in the list
        # are the correct handler instances
        self.assertTrue(any([isinstance(subscriber, DepthImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, SceneImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ControllerLogger)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, HistoryEventHandler)
                             for subscriber in ctrl._subscribers]))

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 4)
        self.assertTrue(any([isinstance(subscriber, ImageVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, TopdownVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ControllerLogger)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, HistoryEventHandler)
                             for subscriber in ctrl._subscribers]))

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 5)
        self.assertTrue(any([isinstance(subscriber, ImageVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, TopdownVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber,
                                        SegmentationVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ControllerLogger)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, HistoryEventHandler)
                             for subscriber in ctrl._subscribers]))

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_false
        cfg.is_video_enabled = return_false
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 4)
        self.assertTrue(any([isinstance(subscriber, DepthImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, SceneImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ControllerLogger)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, HistoryEventHandler)
                             for subscriber in ctrl._subscribers]))

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_false
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_false
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 5)
        self.assertTrue(any([isinstance(subscriber, DepthImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, SceneImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber,
                                        ObjectMaskImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ControllerLogger)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, HistoryEventHandler)
                             for subscriber in ctrl._subscribers]))

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_false
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 6)
        self.assertTrue(any([isinstance(subscriber, ImageVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, TopdownVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, DepthVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber,
                                        SegmentationVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ControllerLogger)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, HistoryEventHandler)
                             for subscriber in ctrl._subscribers]))

        ctrl._subscribers.clear()
        cfg.is_save_debug_images = return_true
        cfg.is_depth_maps_enabled = return_true
        cfg.is_object_masks_enabled = return_true
        cfg.is_video_enabled = return_true
        add_subscribers(ctrl, cfg)
        self.assertEqual(len(ctrl._subscribers), 9)
        self.assertTrue(any([isinstance(subscriber, DepthImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, SceneImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber,
                                        ObjectMaskImageEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ImageVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, TopdownVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, DepthVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber,
                                        SegmentationVideoEventHandler)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, ControllerLogger)
                             for subscriber in ctrl._subscribers]))
        self.assertTrue(any([isinstance(subscriber, HistoryEventHandler)
                             for subscriber in ctrl._subscribers]))

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
