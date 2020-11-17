import unittest

from machine_common_sense.config_manager import ConfigManager
from unittest.mock import patch
import os


class Test_Config_Manager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config_mngr = ConfigManager(None)
        cls.config_mngr._config[
            cls.config_mngr.CONFIG_DEFAULT_SECTION
        ] = {}

    @classmethod
    def tearDownClass(cls):
        pass

    def mock_env(**env_vars):
        return patch.dict(os.environ, env_vars, clear=True)

    def test_init(self):
        self.assertEquals(
            self.config_mngr._config_file,
            self.config_mngr.DEFAULT_CONFIG_FILE)

    def test_init_with_arg(self):
        file_path = './arg-test.ini'
        config_mngr = ConfigManager(file_path)

        self.assertEquals(config_mngr._config_file, file_path)

    @mock_env(MCS_CONFIG_FILE_PATH='~/somefolder/env-var-test.ini')
    def test_init_with_env_variable(self):
        config_mngr = ConfigManager()

        self.assertEquals(
            config_mngr._config_file,
            '~/somefolder/env-var-test.ini')

    def test_get_aws_access_key_id(self):
        self.assertIsNone(self.config_mngr.get_aws_access_key_id())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_AWS_ACCESS_KEY_ID
        ] = 'some_key_id'

        self.assertEquals(
            self.config_mngr.get_aws_access_key_id(),
            'some_key_id')

    def test_get_aws_secret_access_key(self):
        self.assertIsNone(self.config_mngr.get_aws_secret_access_key())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_AWS_SECRET_ACCESS_KEY
        ] = 'some_secret'

        self.assertEquals(
            self.config_mngr.get_aws_secret_access_key(),
            'some_secret')

    def test_get_evaluation_name(self):
        self.assertEquals(self.config_mngr.get_evaluation_name(), '')

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_EVALUATION_NAME
        ] = 'test_eval'

        self.assertEquals(
            self.config_mngr.get_evaluation_name(),
            'test_eval')

    def test_get_metadata_tier(self):
        self.assertEquals(self.config_mngr.get_metadata_tier(), '')

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_METADATA_TIER
        ] = 'oracle'

        self.assertEquals(
            self.config_mngr.get_metadata_tier(),
            'oracle')

    @mock_env(MCS_METADATA_LEVEL='level2')
    def test_get_metadata_tier_with_env_variable(self):
        self.assertEquals(self.config_mngr.get_metadata_tier(), 'level2')

    def test_get_s3_bucket(self):
        self.assertIsNone(self.config_mngr.get_s3_bucket())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_S3_BUCKET
        ] = 'some_s3_bucket'

        self.assertEquals(
            self.config_mngr.get_s3_bucket(),
            'some_s3_bucket')

    def test_get_s3_folder(self):
        self.assertIsNone(self.config_mngr.get_s3_folder())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_S3_FOLDER
        ] = 'eval-test-folder'

        self.assertEquals(
            self.config_mngr.get_s3_folder(),
            'eval-test-folder')

    def test_get_team(self):
        self.assertEquals(self.config_mngr.get_team(), '')

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_TEAM
        ] = 'team-name'

        self.assertEquals(
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
