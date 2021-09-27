import unittest
from unittest.mock import MagicMock

from machine_common_sense.config_manager import (ConfigManager,
                                                 SceneConfiguration)
from machine_common_sense.controller_events import (AfterStepPayload,
                                                    BeforeStepPayload,
                                                    EndScenePayload,
                                                    StartScenePayload)
from machine_common_sense.history_writer import (HistoryEventHandler,
                                                 HistoryWriter, SceneHistory)

TEST_FILE_NAME = "test_scene_file.json"


class TestHistoryEventHandler(unittest.TestCase):

    scene_config = SceneConfiguration(name=TEST_FILE_NAME)
    config_mngr = ConfigManager({})

    def setUp(self):
        self.config_mngr._config[
            ConfigManager.CONFIG_DEFAULT_SECTION
        ] = {
            ConfigManager.CONFIG_EVALUATION_NAME: "test-name",
            ConfigManager.CONFIG_HISTORY_ENABLED: True,
            ConfigManager.CONFIG_METADATA_TIER: "level1",
        }

        self.histEvents = HistoryEventHandler()

    def test_on_start_scene(self):
        test_payload = {
            "step_number": 1,
            "config": self.config_mngr,
            "scene_config": self.scene_config,
            "output_folder": None,
            "timestamp": "20210831-202203",
            "wrapped_step": {},
            "step_metadata": {},
            "step_output": {},
            "restricted_step_output": {},
            "goal": {}
        }

        self.assertIsNone(
            self.histEvents._HistoryEventHandler__history_writer)

        self.histEvents.on_start_scene(StartScenePayload(**test_payload))

        self.assertIsNotNone(
            self.histEvents._HistoryEventHandler__history_writer)
        self.assertIsNotNone(
            self.histEvents._HistoryEventHandler__history_writer)

    def test_on_start_scene_hist_not_enabled(self):
        self.config_mngr._config[
            ConfigManager.CONFIG_DEFAULT_SECTION
        ] = {
            ConfigManager.CONFIG_EVALUATION_NAME: "test-name",
            ConfigManager.CONFIG_HISTORY_ENABLED: False,
            ConfigManager.CONFIG_METADATA_TIER: "level1",
        }
        test_payload = {
            "step_number": 0,
            "config": self.config_mngr,
            "scene_config": self.scene_config,
            "output_folder": None,
            "timestamp": "20210831-202203",
            "wrapped_step": {},
            "step_metadata": {},
            "step_output": {},
            "restricted_step_output": {},
            "goal": {}
        }

        self.assertIsNone(
            self.histEvents._HistoryEventHandler__history_writer)

        self.histEvents.on_start_scene(StartScenePayload(**test_payload))

        self.assertIsNone(
            self.histEvents._HistoryEventHandler__history_writer)

    def test_on_before_step_zero(self):
        self.histEvents._HistoryEventHandler__history_writer = MagicMock()
        test_payload = {
            "step_number": 0,
            "config": self.config_mngr,
            "scene_config": self.scene_config,
            "action": "Initialize",
            "habituation_trial": None,
            "goal": {}
        }

        self.histEvents.on_before_step(BeforeStepPayload(**test_payload))

        hist_writer = self.histEvents._HistoryEventHandler__history_writer

        hist_writer.init_timer.assert_called()
        hist_writer.add_step.assert_not_called()

    def test_on_before_step_one(self):
        histItem = SceneHistory(
            step=1,
            action="MoveAhead",
            args=None,
            params=None,
            output=None,
            delta_time_millis=0)
        self.histEvents._HistoryEventHandler__history_item = histItem
        self.histEvents._HistoryEventHandler__history_writer = MagicMock()
        test_payload = {
            "step_number": 1,
            "config": self.config_mngr,
            "scene_config": self.scene_config,
            "action": "Initialize",
            "habituation_trial": None,
            "goal": {}
        }

        self.histEvents.on_before_step(BeforeStepPayload(**test_payload))

        hist_writer = self.histEvents._HistoryEventHandler__history_writer

        hist_writer.init_timer.assert_not_called()
        hist_writer.add_step.assert_called_with(histItem)

    def test_on_after_step(self):
        test_payload = {
            "step_number": 1,
            "ai2thor_action": "MoveAhead",
            "action_kwargs": {},
            "step_params": {},
            "config": self.config_mngr,
            "scene_config": self.scene_config,
            "goal": {},
            "output_folder": None,
            "timestamp": "20210831-202203",
            "wrapped_step": {},
            "step_metadata": {},
            "step_output": MagicMock(),
            "restricted_step_output": {}
        }

        after_step_payload = AfterStepPayload(**test_payload)

        self.histEvents.on_after_step(after_step_payload)

        histItem = self.histEvents._HistoryEventHandler__history_item

        after_step_payload.step_output.copy_without_depth_or_images.assert_called()  # noqa: E501
        self.assertEqual(histItem.step, 1)
        self.assertEqual(histItem.action, "MoveAhead")
        self.assertEqual(histItem.delta_time_millis, 0)

    def test_on_end_scene(self):
        self.histEvents._HistoryEventHandler__history_writer = HistoryWriter(
            self.scene_config, {}, "20210831-202203")
        self.histEvents._HistoryEventHandler__history_writer.write_history_file = MagicMock()  # noqa: E501
        histItem = SceneHistory(
            step=1,
            action="MoveAhead",
            args=None,
            params=None,
            output=None,
            delta_time_millis=0)
        self.histEvents._HistoryEventHandler__history_item = histItem
        test_payload = {}
        test_payload["step_number"] = 1
        test_payload["config"] = self.config_mngr
        test_payload["scene_config"] = self.scene_config
        test_payload["rating"] = "plausible"
        test_payload["score"] = .8
        test_payload["report"] = {1: {"rating": "plausible",
                                      "score": .75,
                                      "violations_xy_list": [
                                          {
                                              "x": 1,
                                              "y": 1
                                          }
                                      ],
                                      "internal_state": {
                                          "test": "some state"
                                      }}
                                  }

        self.histEvents.on_end_scene(EndScenePayload(**test_payload))

        hist_writer = self.histEvents._HistoryEventHandler__history_writer
        self.assertEqual(len(hist_writer.current_steps), 1)
        self.assertEqual(
            hist_writer.current_steps[0]["action"], "MoveAhead")
        self.assertEqual(
            hist_writer.current_steps[0]["classification"],
            "plausible")
        self.assertEqual(
            hist_writer.current_steps[0]["confidence"],
            0.75)
        self.assertEqual(
            hist_writer.current_steps[0]["violations_xy_list"],
            [
                {
                    "x": 1,
                    "y": 1
                }
            ])
        self.assertEqual(
            hist_writer.current_steps[0]["internal_state"],
            {
                "test": "some state"
            })
        self.assertEqual(
            hist_writer.current_steps[0]["internal_state"],
            {
                "test": "some state"
            })

        hist_writer.write_history_file.assert_called_with("plausible", .8)

    def test_on_end_scene_history_not_enabled(self):
        self.config_mngr._config[
            ConfigManager.CONFIG_DEFAULT_SECTION
        ] = {
            ConfigManager.CONFIG_EVALUATION_NAME: "test-name",
            ConfigManager.CONFIG_HISTORY_ENABLED: False,
            ConfigManager.CONFIG_METADATA_TIER: "level1",
        }
        self.histEvents._HistoryEventHandler__history_writer = MagicMock()  # noqa: E501

        test_payload = {}
        test_payload["step_number"] = 1
        test_payload["config"] = self.config_mngr
        test_payload["scene_config"] = self.scene_config
        test_payload["rating"] = "plausible"
        test_payload["score"] = .8
        test_payload["report"] = {1: {"rating": "plausible",
                                      "score": .75,
                                      "violations_xy_list": [
                                          {
                                              "x": 1,
                                              "y": 1
                                          }
                                      ],
                                      "internal_state": {
                                          "test": "some state"
                                      }}
                                  }

        self.histEvents.on_end_scene(EndScenePayload(**test_payload))

        hist_writer = self.histEvents._HistoryEventHandler__history_writer
        hist_writer.add_step.assert_not_called()
        hist_writer.write_history_file.assert_not_called()


if __name__ == '__main__':
    unittest.main()
