import unittest
import os

import machine_common_sense as mcs


class Test_HistoryWriter(unittest.TestCase):

    def test_init(self):
        config_data = {"name": "test_scene_file.json"}
        writer = mcs.HistoryWriter(config_data)

        self.assertEqual(writer.info_obj.keys(), {'name', 'timestamp'})
        self.assertEqual(writer.info_obj['name'], "test_scene_file")
        self.assertTrue(os.path.exists(writer.HISTORY_DIRECTORY))

    def test_init_with_hist_info(self):
        config_data = {"name": "test_scene_file.json"}
        writer = mcs.HistoryWriter(config_data, {
            'team': 'team1',
            'metadata': 'level1'
        })

        self.assertEqual(writer.info_obj.keys(), {
            'team',
            'metadata',
            'name',
            'timestamp'
        })
        self.assertEqual(writer.info_obj['name'], "test_scene_file")
        self.assertEqual(writer.info_obj['team'], "team1")
        self.assertEqual(writer.info_obj['metadata'], "level1")
        self.assertTrue(os.path.exists(writer.HISTORY_DIRECTORY))

    def test_add_step(self):
        config_data = {"name": "test_scene_file.json"}
        writer = mcs.HistoryWriter(config_data)

        history_item = mcs.SceneHistory(
            step=1,
            action="MoveAhead")
        writer.add_step(history_item)

        self.assertEqual(len(writer.current_steps), 1)
        self.assertEqual(writer.current_steps[0]["action"], "MoveAhead")

        history_item = mcs.SceneHistory(
            step=2,
            action="MoveLeft")
        writer.add_step(history_item)

        self.assertEqual(len(writer.current_steps), 2)
        self.assertEqual(writer.current_steps[1]["action"], "MoveLeft")

    def test_write_history_file(self):
        config_data = {"name": "test_scene_file.json"}
        writer = mcs.HistoryWriter(config_data)

        history_item = mcs.SceneHistory(
            step=1,
            action="MoveAhead")
        writer.add_step(history_item)

        history_item = mcs.SceneHistory(
            step=2,
            action="MoveLeft")
        writer.add_step(history_item)

        writer.write_history_file("Plausible", 0.75)

        self.assertEqual(writer.end_score["classification"], "Plausible")
        self.assertEqual(writer.end_score["confidence"], "0.75")

        self.assertEqual(writer.history_obj["info"]["name"], "test_scene_file")
        self.assertEqual(len(writer.history_obj["steps"]), 2)
        self.assertEqual(
            writer.history_obj["score"]["classification"], "Plausible")
        self.assertEqual(writer.history_obj["score"]["confidence"], "0.75")

        self.assertTrue(os.path.exists(writer.scene_history_file))

    def test_write_history_file_with_slash(self):
        config_data = {"name": "prefix/test_scene_file.json"}
        writer = mcs.HistoryWriter(config_data)

        history_item = mcs.SceneHistory(
            step=1,
            action="MoveAhead")
        writer.add_step(history_item)

        history_item = mcs.SceneHistory(
            step=2,
            action="MoveLeft")
        writer.add_step(history_item)

        writer.write_history_file("Plausible", 0.75)

        self.assertEqual(writer.end_score["classification"], "Plausible")
        self.assertEqual(writer.end_score["confidence"], "0.75")

        self.assertEqual(
            writer.history_obj["info"]["name"],
            "prefix/test_scene_file")
        self.assertEqual(len(writer.history_obj["steps"]), 2)
        self.assertEqual(
            writer.history_obj["score"]["classification"], "Plausible")
        self.assertEqual(writer.history_obj["score"]["confidence"], "0.75")

        self.assertTrue(os.path.exists(writer.scene_history_file))

    def test_write_step_removes_some_output(self):
        config_data = {"name": "prefix/test_scene_file.json"}
        writer = mcs.HistoryWriter(config_data)

        output = mcs.StepMetadata(
            action_list=["CloseObject", "Crawl"],
            pose="STANDING",
            return_status="SUCCESSFUL",
            step_number=2,
            object_list={
                "object": "object"
            },
            structural_object_list={
                "structural_object": "structural_object"
            }
        )

        history_item = mcs.SceneHistory(
            step=1,
            action="MoveAhead",
            output=output
        )
        writer.add_step(history_item)

        self.assertEqual(len(writer.current_steps), 1)
        self.assertEqual(writer.current_steps[0]["action"], "MoveAhead")
        self.assertEqual(writer.current_steps[0]["output"]["pose"], "STANDING")
        self.assertIsNone(writer.current_steps[0]["output"]["action_list"])
        self.assertIsNone(writer.current_steps[0]["output"]["object_list"])
        self.assertIsNone(
            writer.current_steps[0]["output"]["structural_object_list"])

        history_item = mcs.SceneHistory(
            step=2,
            action="MoveLeft",
            output=output
        )
        writer.add_step(history_item)

        self.assertEqual(len(writer.current_steps), 2)
        self.assertEqual(writer.current_steps[1]["action"], "MoveLeft")
        self.assertEqual(writer.current_steps[1]["output"]["pose"], "STANDING")
        self.assertIsNone(writer.current_steps[1]["output"]["action_list"])
        self.assertIsNone(writer.current_steps[1]["output"]["object_list"])
        self.assertIsNone(
            writer.current_steps[1]["output"]["structural_object_list"])
