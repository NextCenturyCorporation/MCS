import unittest
from unittest.mock import patch
import os

from .mock_controller import (
    MockControllerAI2THOR
)


class Test_Env_Variables(unittest.TestCase):

    def mock_env(**env_vars):
        return patch.dict(os.environ, env_vars, clear=True)

    @mock_env()
    def test_no_env_variables_set(self):
        controller = MockControllerAI2THOR()
        self.assertEqual(
            controller._config_file,
            './mcs_config.yaml')
        self.assertEqual(
            controller._config,
            {})
        self.assertEqual(
            controller._metadata_tier,
            '')

    @mock_env(MCS_CONFIG_FILE_PATH='test-metadata-lvl1.yaml')
    def test_config_file_env_set(self):
        controller = MockControllerAI2THOR()
        self.assertEqual(
            controller._config_file,
            'test-metadata-lvl1.yaml')
        self.assertEqual(
            controller._config,
            {'metadata': 'level1'})
        self.assertEqual(
            controller._metadata_tier,
            'level1')

    @mock_env(MCS_METADATA_LEVEL='level2')
    def test_metadata_env_set(self):
        controller = MockControllerAI2THOR()
        self.assertEqual(
            controller._config_file,
            './mcs_config.yaml')
        self.assertEqual(
            controller._config,
            {})
        self.assertEqual(
            controller._metadata_tier,
            'level2')

    @mock_env(
        MCS_CONFIG_FILE_PATH='test-metadata-lvl1.yaml',
        MCS_METADATA_LEVEL='level2'
    )
    def test_both_config_and_metadata_env_set(self):
        controller = MockControllerAI2THOR()
        self.assertEqual(
            controller._config_file,
            'test-metadata-lvl1.yaml')
        self.assertEqual(
            controller._config,
            {'metadata': 'level1'})
        self.assertEqual(
            controller._metadata_tier,
            'level2')
