import unittest
import os
import glob
import shutil

import machine_common_sense as mcs


TEST_FILE_NAME = "test_scene_file.json"
PREFIX = 'prefix'


class Test_HistoryWriter(unittest.TestCase):

    config_data = {"name": TEST_FILE_NAME}
    prefix_config_data = {"name": f"{PREFIX}/{TEST_FILE_NAME}"}

    @classmethod
    def tearDownClass(cls):
        # remove all TEST_FILE_NAME in PREFIX
        test_file_base = os.path.splitext(TEST_FILE_NAME)[0]
        prefix_test_files = glob.glob(
            f'{mcs.HistoryWriter.HISTORY_DIRECTORY}/{PREFIX}/{test_file_base}*'
        )
        for prefix_test_file in prefix_test_files:
            os.unlink(prefix_test_file)
        # if PREFIX empty, destroy it
        if not os.listdir(f"{mcs.HistoryWriter.HISTORY_DIRECTORY}/{PREFIX}"):
            shutil.rmtree(f"{mcs.HistoryWriter.HISTORY_DIRECTORY}/{PREFIX}")

        # remove all TEST_FILE_NAME in SCENE_HIST_DIR
        test_files = glob.glob(
            f'{mcs.HistoryWriter.HISTORY_DIRECTORY}/{test_file_base}*')
        for test_file in test_files:
            os.unlink(test_file)
        # if SCENE_HIST_DIR is empty, destroy it
        if not os.listdir(mcs.HistoryWriter.HISTORY_DIRECTORY):
            shutil.rmtree(mcs.HistoryWriter.HISTORY_DIRECTORY)

    def test_init(self):
        writer = mcs.HistoryWriter(self.config_data)

        self.assertEqual(writer.info_obj.keys(), {'name', 'timestamp'})
        self.assertEqual(writer.info_obj['name'], "test_scene_file")
        self.assertEqual(writer.info_obj['timestamp'], "")
        self.assertTrue(os.path.exists(writer.HISTORY_DIRECTORY))

    def test_init_with_hist_info(self):
        config_data = {"name": TEST_FILE_NAME}
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
        self.assertEqual(writer.info_obj['timestamp'], "")
        self.assertTrue(os.path.exists(writer.HISTORY_DIRECTORY))

    def test_init_with_timestamp(self):
        writer = mcs.HistoryWriter(self.config_data, {}, "some-time-value")

        self.assertEqual(writer.info_obj.keys(), {'name', 'timestamp'})
        self.assertEqual(writer.info_obj['name'], "test_scene_file")
        self.assertEqual(writer.info_obj['timestamp'], "some-time-value")
        self.assertTrue(os.path.exists(writer.HISTORY_DIRECTORY))

    def test_add_step(self):
        writer = mcs.HistoryWriter(self.config_data)

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
        writer = mcs.HistoryWriter(self.config_data)

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
        writer = mcs.HistoryWriter(self.prefix_config_data)

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
        writer = mcs.HistoryWriter(self.prefix_config_data)

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
