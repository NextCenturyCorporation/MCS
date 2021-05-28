import os
import unittest
from unittest.mock import patch

from machine_common_sense.config_manager import (ConfigManager, GoalSchema,
                                                 SceneConfiguration)


class TestConfigManager(unittest.TestCase):

    def mock_env(**env_vars):
        return patch.dict(os.environ, env_vars, clear=True)

    @classmethod
    @mock_env()
    def setUpClass(cls):
        cls.config_mngr = ConfigManager(None)
        cls.config_mngr._config[
            cls.config_mngr.CONFIG_DEFAULT_SECTION
        ] = {}

    @classmethod
    def tearDownClass(cls):
        pass

    def test_init(self):
        self.assertEqual(
            self.config_mngr._config_file,
            self.config_mngr.DEFAULT_CONFIG_FILE)

    @mock_env()
    def test_init_with_arg(self):
        file_path = './arg-test.ini'
        config_mngr = ConfigManager(file_path)

        self.assertEqual(config_mngr._config_file, file_path)

    @mock_env(MCS_CONFIG_FILE_PATH='~/somefolder/env-var-test.ini')
    def test_init_with_env_variable(self):
        config_mngr = ConfigManager()

        self.assertEqual(
            config_mngr._config_file,
            '~/somefolder/env-var-test.ini')

    def test_validate_screen_size(self):
        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_SIZE
        ] = '450'
        self.config_mngr._validate_screen_size()

        self.assertEqual(self.config_mngr.get_size(), 450)

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_SIZE
        ] = '449'
        self.config_mngr._validate_screen_size()

        self.assertEqual(self.config_mngr.get_size(),
                         self.config_mngr.SCREEN_WIDTH_DEFAULT)

    def test_get_aws_access_key_id(self):
        self.assertIsNone(self.config_mngr.get_aws_access_key_id())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_AWS_ACCESS_KEY_ID
        ] = 'some_key_id'

        self.assertEqual(
            self.config_mngr.get_aws_access_key_id(),
            'some_key_id')

    def test_get_aws_secret_access_key(self):
        self.assertIsNone(self.config_mngr.get_aws_secret_access_key())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_AWS_SECRET_ACCESS_KEY
        ] = 'some_secret'

        self.assertEqual(
            self.config_mngr.get_aws_secret_access_key(),
            'some_secret')

    def test_get_evaluation_name(self):
        self.assertEqual(self.config_mngr.get_evaluation_name(), '')

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_EVALUATION_NAME
        ] = 'test_eval'

        self.assertEqual(
            self.config_mngr.get_evaluation_name(),
            'test_eval')

    @mock_env()
    def test_get_metadata_tier(self):
        self.assertEqual(self.config_mngr.get_metadata_tier(), 'default')

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_METADATA_TIER
        ] = 'oracle'

        self.assertEqual(
            self.config_mngr.get_metadata_tier(),
            'oracle')

    @mock_env(MCS_METADATA_LEVEL='level2')
    def test_get_metadata_tier_with_env_variable(self):
        self.assertEqual(self.config_mngr.get_metadata_tier(), 'level2')

    def test_get_s3_bucket(self):
        self.assertIsNone(self.config_mngr.get_s3_bucket())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_S3_BUCKET
        ] = 'some_s3_bucket'

        self.assertEqual(
            self.config_mngr.get_s3_bucket(),
            'some_s3_bucket')

    def test_get_s3_folder(self):
        self.assertIsNone(self.config_mngr.get_s3_folder())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_S3_FOLDER
        ] = 'eval-test-folder'

        self.assertEqual(
            self.config_mngr.get_s3_folder(),
            'eval-test-folder')

    def test_get_seed(self):
        self.assertEqual(self.config_mngr.get_seed(), None)

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_SEED
        ] = '1'

        self.assertEqual(self.config_mngr.get_seed(), 1)

    def test_get_size(self):
        self.assertEqual(self.config_mngr.get_size(), 600)

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_SIZE
        ] = '800'

        self.assertEqual(self.config_mngr.get_size(), 800)

    def test_get_team(self):
        self.assertEqual(self.config_mngr.get_team(), '')

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_TEAM
        ] = 'team-name'

        self.assertEqual(
            self.config_mngr.get_team(),
            'team-name')

    def test_is_evaluation(self):
        self.assertFalse(self.config_mngr.is_evaluation())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_EVALUATION
        ] = 'true'

        self.assertTrue(self.config_mngr.is_evaluation())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_EVALUATION
        ] = 'false'

        self.assertFalse(self.config_mngr.is_evaluation())

    def test_is_history_enabled(self):
        self.assertTrue(self.config_mngr.is_history_enabled())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_HISTORY_ENABLED
        ] = 'false'

        self.assertFalse(self.config_mngr.is_evaluation())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_HISTORY_ENABLED
        ] = 'true'

        self.assertTrue(self.config_mngr.is_history_enabled())

    def test_is_noise_enabled(self):
        self.assertFalse(self.config_mngr.is_noise_enabled())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_NOISE_ENABLED
        ] = 'true'

        self.assertTrue(self.config_mngr.is_noise_enabled())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_NOISE_ENABLED
        ] = 'false'

        self.assertFalse(self.config_mngr.is_noise_enabled())

    def test_is_video_enabled(self):
        self.assertFalse(self.config_mngr.is_video_enabled())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_VIDEO_ENABLED
        ] = 'true'

        self.assertTrue(self.config_mngr.is_video_enabled())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_VIDEO_ENABLED
        ] = 'false'

        self.assertFalse(self.config_mngr.is_noise_enabled())


class TestSceneConfig(unittest.TestCase):
    def test_retrieve_goal_with_config_metadata(self):
        # self.controller.set_metadata_tier('oracle')
        goal = {
            'metadata': {
                'target': {'image': [0]},
                'target_1': {'image': [1]},
                'target_2': {'image': [2]}
            }
        }

        goal = GoalSchema().load(goal)
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        actual = scene_config.retrieve_goal()
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_retrieve_goal(self):
        goal = GoalSchema().load({})
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        goal_1 = scene_config.retrieve_goal()
        self.assertEqual(goal_1.action_list, None)
        self.assertEqual(goal_1.category, '')
        self.assertEqual(goal_1.description, '')
        self.assertEqual(goal_1.habituation_total, 0)
        self.assertEqual(goal_1.last_step, None)
        self.assertEqual(goal_1.metadata, {})

        goal = {
            "goal": {
            }
        }
        goal = GoalSchema().load({})
        scene_config = SceneConfiguration(
            name="test", version=1, goal=goal)
        goal_2 = scene_config.retrieve_goal()
        self.assertEqual(goal_2.action_list, None)
        self.assertEqual(goal_2.category, '')
        self.assertEqual(goal_2.description, '')
        self.assertEqual(goal_2.habituation_total, 0)
        self.assertEqual(goal_2.last_step, None)
        self.assertEqual(goal_2.metadata, {})

        goal = {
            "action_list": [
                [("MoveAhead", {"amount": 0.1})],
                [],
                [("Pass", {}), ("RotateLeft", {}), ("RotateRight", {})]
            ],
            "category": "test category",
            "description": "test description",
            "habituation_total": 5,
            "last_step": 10,
            "metadata": {
                "key": "value"
            }
        }
        goal = GoalSchema().load(goal)
        scene_config = SceneConfiguration(
            name="test", version=1, goal=goal)
        goal_3 = scene_config.retrieve_goal()

        self.assertEqual(goal_3.action_list, [
            [("MoveAhead", {"amount": 0.1})],
            [],
            [("Pass", {}), ("RotateLeft", {}), ("RotateRight", {})]
        ])
        self.assertEqual(goal_3.category, "test category")
        self.assertEqual(goal_3.description, "test description")
        self.assertEqual(goal_3.habituation_total, 5)
        self.assertEqual(goal_3.last_step, 10)
        self.assertEqual(goal_3.metadata, {
            "category": "test category",
            "key": "value"
        })

    def test_update_goal_target_image(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }
        }
        goal = GoalSchema().load(goal)
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        actual = scene_config.update_goal_target_image(scene_config.goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_img_as_str(self):
        goal = {'metadata': {
            'target': {'image': "[0]"},
            'target_1': {'image': "[1]"},
            'target_2': {'image': "[2]"}
        }
        }
        goal = GoalSchema().load(goal)
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        actual = scene_config.update_goal_target_image(scene_config.goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_oracle(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        goal = GoalSchema().load(goal)
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        actual = scene_config.update_goal_target_image(scene_config.goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_update_goal_target_image_oracle_img_as_str(self):
        goal = {'metadata': {
            'target': {'image': "[0]"},
            'target_1': {'image': "[1]"},
            'target_2': {'image': "[2]"}
        }}
        goal = GoalSchema().load(goal)
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        actual = scene_config.update_goal_target_image(scene_config.goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })


if __name__ == '__main__':
    unittest.main()
