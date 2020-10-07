import unittest
import os

from machine_common_sense.history_writer import HistoryWriter
from machine_common_sense.scene_history import SceneHistory


class Test_HistoryWriter(unittest.TestCase):

    def test_init(self):
        config_data = {"name": "test_scene_file.json"}
        writer = HistoryWriter(config_data)

        self.assertEqual(writer.info_obj['name'], "test_scene_file")
        self.assertTrue(os.path.exists(writer.HISTORY_DIRECTORY))

    def test_add_step(self):
        config_data = {"name": "test_scene_file.json"}
        writer = HistoryWriter(config_data)

        history_item = SceneHistory(
            step=1,
            action="MoveAhead")
        writer.add_step(history_item)

        self.assertEqual(len(writer.current_steps), 1)
        self.assertEqual(writer.current_steps[0]["action"], "MoveAhead")

        history_item = SceneHistory(
            step=2,
            action="MoveLeft")
        writer.add_step(history_item)

        self.assertEqual(len(writer.current_steps), 2)
        self.assertEqual(writer.current_steps[1]["action"], "MoveLeft")

    def test_write_history_file(self):
        config_data = {"name": "test_scene_file.json"}
        writer = HistoryWriter(config_data)

        history_item = SceneHistory(
            step=1,
            action="MoveAhead")
        writer.add_step(history_item)

        history_item = SceneHistory(
            step=2,
            action="MoveLeft")
        writer.add_step(history_item)

        writer.write_history_file("Plausible", 0.75)

        self.assertEqual(writer.end_score["classification"], "Plausible")
        self.assertEqual(writer.end_score["confidence"], "0.75")

        self.assertEqual(writer.history_obj["info"]["name"], "test_scene_file")
        self.assertEqual(len(writer.history_obj["steps"]), 2)
        self.assertEqual(writer.history_obj["score"]["classification"], "Plausible")
        self.assertEqual(writer.history_obj["score"]["confidence"], "0.75")

        self.assertTrue(os.path.exists(writer.scene_history_file))
