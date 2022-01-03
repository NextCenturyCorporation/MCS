import os
import unittest
from unittest.mock import DEFAULT, patch

from machine_common_sense.config_manager import (ChangeMaterialConfig,
                                                 ConfigManager, ForceConfig,
                                                 GoalSchema, MetadataTier,
                                                 MoveConfig, OpenCloseConfig,
                                                 PhysicsConfig,
                                                 SceneConfiguration,
                                                 SceneConfigurationSchema,
                                                 SceneObjectSchema, ShowConfig,
                                                 SingleStepConfig, SizeConfig,
                                                 StepBeginEndConfig,
                                                 TeleportConfig,
                                                 TransformConfig, Vector3d)


class TestConfigManager(unittest.TestCase):

    def mock_env(**env_vars):
        return patch.dict(os.environ, env_vars, clear=True)

    @classmethod
    @mock_env()
    def setUpClass(cls):
        cls.config_mngr = ConfigManager(config_file_or_dict={})
        cls.config_mngr._config[
            cls.config_mngr.CONFIG_DEFAULT_SECTION
        ] = {}

    @ classmethod
    def tearDownClass(cls):
        pass

    def test_init(self):
        self.assertIsNotNone(self.config_mngr._config)

    @ mock_env()
    @ patch.multiple(ConfigManager, _read_in_config_dict=DEFAULT,
                     _read_in_config_file=DEFAULT)
    def test_init_with_arg(self, _read_in_config_dict, _read_in_config_file):
        file_path = './arg-test.ini'
        _ = ConfigManager(file_path)

        _read_in_config_file.assert_called_once_with(file_path)
        _read_in_config_dict.assert_not_called()

    @ mock_env(MCS_CONFIG_FILE_PATH='~/somefolder/env-var-test.ini')
    @ patch.multiple(ConfigManager, _read_in_config_dict=DEFAULT,
                     _read_in_config_file=DEFAULT)
    def test_init_with_env_variable(
            self, _read_in_config_dict, _read_in_config_file):
        _ = ConfigManager()

        _read_in_config_dict.assert_not_called()
        _read_in_config_file.assert_called_once_with(
            os.environ.get('MCS_CONFIG_FILE_PATH'))

    @mock_env(MCS_CONFIG_FILE_PATH='~/somefolder/env-var-test.ini')
    @patch.multiple(ConfigManager, _read_in_config_dict=DEFAULT,
                    _read_in_config_file=DEFAULT)
    def test_init_with_arg_and_env_variable(
            self, _read_in_config_dict, _read_in_config_file):
        '''Ensures environment variable overrides provided file path'''
        file_path = './arg-test.ini'
        _ = ConfigManager(file_path)

        _read_in_config_dict.assert_not_called()
        _read_in_config_file.assert_called_once_with(
            os.environ.get('MCS_CONFIG_FILE_PATH')
        )

    @mock_env(MCS_CONFIG_FILE_PATH='~/somefolder/env-var-test.ini')
    def test_nonexistent_file_from_env_variable(self):
        '''Missing config files should raise an exception'''
        self.assertRaises(RuntimeError, ConfigManager)

    @mock_env(MCS_CONFIG_FILE_PATH=('machine_common_sense/scripts/'
                                    'config_level2_debug.ini'))
    def test_init_no_override_with_env_var_and_dict(self):
        config_options = {
            'metadata': 'oracle'
        }
        config_mngr = ConfigManager(config_options)
        self.assertEqual(config_mngr.get_metadata_tier(),
                         MetadataTier.LEVEL_2)

    @mock_env(MCS_CONFIG_FILE_PATH=('machine_common_sense/scripts/'
                                    'config_level2_debug.ini'))
    @patch.multiple(ConfigManager, _read_in_config_dict=DEFAULT,
                    _read_in_config_file=DEFAULT)
    def test_init_env_var_and_dict_function_calls(
            self, _read_in_config_dict, _read_in_config_file):
        config_options = {
            'metadata': 'oracle'
        }
        _ = ConfigManager(config_options)
        _read_in_config_dict.assert_not_called()
        _read_in_config_file.assert_called_once_with(
            os.environ.get('MCS_CONFIG_FILE_PATH'))

    def test_init_with_filepath(self):
        config_file = 'machine_common_sense/scripts/config_level2_debug.ini'
        config_mngr = ConfigManager(config_file_or_dict=config_file)
        self.assertEqual(config_mngr.get_metadata_tier(),
                         MetadataTier.LEVEL_2)

    def test_init_with_filepath_missing(self):
        '''Provided config file path must exist or an exception occurs'''
        missing_config_file = '~/somefolder/env-var-test.ini'
        self.assertRaises(RuntimeError, ConfigManager, missing_config_file)

    def test_init_with_no_config(self):
        '''No dictionary, no file, and no env should raise an exception'''
        self.assertRaises(RuntimeError, ConfigManager)

    def test_init_with_dict(self):
        config_options = {
            'metadata': 'oracle',
            'video_enabled': 'false',
            'save_debug_images': True
        }

        config_mngr = ConfigManager(config_options)

        self.assertIsNotNone(config_mngr._config)
        self.assertEqual(config_mngr.get_metadata_tier(),
                         MetadataTier.ORACLE)
        self.assertFalse(config_mngr.is_video_enabled())
        self.assertTrue(config_mngr.is_save_debug_images())

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

    def test_get_metadata_tier(self):
        self.assertEqual(
            self.config_mngr.get_metadata_tier(),
            MetadataTier.DEFAULT)
        self.assertEqual(self.config_mngr.get_metadata_tier().value, 'default')

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_METADATA_TIER
        ] = 'oracle'

        self.assertEqual(
            self.config_mngr.get_metadata_tier(),
            MetadataTier.ORACLE)
        self.assertEqual(
            self.config_mngr.get_metadata_tier().value,
            'oracle')

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

    def test_is_history_enabled(self):
        self.assertTrue(self.config_mngr.is_history_enabled())

        self.config_mngr._config[
            self.config_mngr.CONFIG_DEFAULT_SECTION
        ][
            self.config_mngr.CONFIG_HISTORY_ENABLED
        ] = 'false'

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
    def test_objects(self):
        object_config_list = [{
            'id': 'id_1',
            'type': 'type_1'
        }, {
            'id': 'id_2',
            'type': 'type_2',
            'centerOfMass': {
                'x': 0.01,
                'y': 0.02,
                'z': 0.03
            },
            'changeMaterials': [{
                'stepBegin': 10,
                'materials': ['material_3', 'material_4']
            }],
            'debug': {
                'key': 'value'
            },
            'forces': [{
                'relative': True,
                'stepBegin': 11,
                'stepEnd': 12,
                'vector': {
                    'x': 0.04,
                    'y': 0.05,
                    'z': 0.06
                }
            }],
            'ghosts': [{
                'stepBegin': 13,
                'stepEnd': 14
            }],
            'hides': [{
                'stepBegin': 15
            }],
            'kinematic': True,
            'locationParent': 'parent_id',
            'mass': 12.34,
            'materials': ['material_1', 'material_2'],
            'moveable': True,
            'moves': [{
                'stepBegin': 16,
                'stepEnd': 17,
                'vector': {
                    'x': 0.07,
                    'y': 0.08,
                    'z': 0.09
                }
            }],
            'nullParent': {
                'position': {
                    'x': 0.11,
                    'y': 0.12,
                    'z': 0.13
                },
                'rotation': {
                    'x': 0.14,
                    'y': 0.15,
                    'z': 0.16
                },
                'scale': {
                    'x': 0.17,
                    'y': 0.18,
                    'z': 0.19
                }
            },
            'openable': True,
            'opened': True,
            'openClose': [{
                'step': 18,
                'open': True
            }],
            'physics': True,
            'physicsProperties': {
                'enable': True,
                'angularDrag': 1,
                'bounciness': 2,
                'drag': 3,
                'dynamicFriction': 4,
                'staticFriction': 5
            },
            'pickupable': True,
            'receptacle': True,
            'resetCenterOfMass': True,
            'resizes': [{
                'stepBegin': 19,
                'stepEnd': 20,
                'size': {
                    'x': 0.21,
                    'y': 0.22,
                    'z': 0.23
                }
            }],
            'rotates': [{
                'stepBegin': 21,
                'stepEnd': 22,
                'vector': {
                    'x': 0.24,
                    'y': 0.25,
                    'z': 0.26
                }
            }],
            'salientMaterials': ['salient_1', 'salient_2'],
            'shows': [{
                'stepBegin': 23,
                'position': {
                    'x': 0.31,
                    'y': 0.32,
                    'z': 0.33
                },
                'rotation': {
                    'x': 0.34,
                    'y': 0.35,
                    'z': 0.36
                },
                'scale': {
                    'x': 0.37,
                    'y': 0.38,
                    'z': 0.39
                }
            }],
            'shrouds': [{
                'stepBegin': 24,
                'stepEnd': 25
            }],
            'states': [['state_1'], [], ['state_2'], ['state_1', 'state_3']],
            'structure': True,
            'teleports': [{
                'stepBegin': 26,
                'position': {
                    'x': 0.41,
                    'y': 0.42,
                    'z': 0.43
                }
            }],
            'togglePhysics': [{
                'stepBegin': 27
            }],
            'torques': [{
                'stepBegin': 28,
                'stepEnd': 29,
                'vector': {
                    'x': 0.44,
                    'y': 0.45,
                    'z': 0.46
                }
            }]
        }]
        object_list = [
            SceneObjectSchema().load(object_config)
            for object_config in object_config_list
        ]
        scene_config = SceneConfiguration(objects=object_list)
        assert len(scene_config.objects) == 2
        object_1 = scene_config.objects[0]
        object_2 = scene_config.objects[1]

        assert object_1.id == 'id_1'
        assert object_1.type == 'type_1'
        assert object_1.center_of_mass is None
        assert object_1.change_materials is None
        assert object_1.debug is None
        assert object_1.forces is None
        assert object_1.ghosts is None
        assert object_1.hides is None
        assert object_1.kinematic is None
        assert object_1.location_parent is None
        assert object_1.mass is None
        assert object_1.materials is None
        assert object_1.moveable is None
        assert object_1.moves is None
        assert object_1.null_parent is None
        assert object_1.openable is None
        assert object_1.opened is None
        assert object_1.open_close is None
        assert object_1.physics is None
        assert object_1.physics_properties is None
        assert object_1.pickupable is None
        assert object_1.receptacle is None
        assert object_1.reset_center_of_mass is None
        assert object_1.resizes is None
        assert object_1.rotates is None
        assert object_1.salient_materials is None
        assert object_1.shows is None
        assert object_1.shrouds is None
        assert object_1.states is None
        assert object_1.structure is None
        assert object_1.teleports is None
        assert object_1.toggle_physics is None
        assert object_1.torques is None

        assert object_2.id == 'id_2'
        assert object_2.type == 'type_2'
        assert object_2.center_of_mass == Vector3d(x=0.01, y=0.02, z=0.03)
        assert object_2.change_materials == [ChangeMaterialConfig(
            step_begin=10,
            materials=['material_3', 'material_4']
        )]
        assert object_2.debug == {'key': 'value'}
        assert object_2.forces == [ForceConfig(
            relative=True,
            step_begin=11,
            step_end=12,
            vector=Vector3d(x=0.04, y=0.05, z=0.06)
        )]
        assert object_2.ghosts == [StepBeginEndConfig(
            step_begin=13,
            step_end=14
        )]
        assert object_2.hides == [SingleStepConfig(step_begin=15)]
        assert object_2.kinematic is True
        assert object_2.location_parent == 'parent_id'
        assert object_2.mass == 12.34
        assert object_2.materials == ['material_1', 'material_2']
        assert object_2.moveable is True
        assert object_2.moves == [MoveConfig(
            step_begin=16,
            step_end=17,
            vector=Vector3d(x=0.07, y=0.08, z=0.09)
        )]
        assert object_2.null_parent == TransformConfig(
            position=Vector3d(x=0.11, y=0.12, z=0.13),
            rotation=Vector3d(x=0.14, y=0.15, z=0.16),
            scale=Vector3d(x=0.17, y=0.18, z=0.19)
        )
        assert object_2.openable is True
        assert object_2.opened is True
        assert object_2.open_close == [OpenCloseConfig(open=True, step=18)]
        assert object_2.physics is True
        assert object_2.physics_properties == PhysicsConfig(
            enable=True,
            angular_drag=1,
            bounciness=2,
            drag=3,
            dynamic_friction=4,
            static_friction=5
        )
        assert object_2.pickupable is True
        assert object_2.receptacle is True
        assert object_2.reset_center_of_mass is True
        assert object_2.resizes == [SizeConfig(
            step_begin=19,
            step_end=20,
            size=Vector3d(x=0.21, y=0.22, z=0.23)
        )]
        assert object_2.rotates == [MoveConfig(
            step_begin=21,
            step_end=22,
            vector=Vector3d(x=0.24, y=0.25, z=0.26)
        )]
        assert object_2.salient_materials == ['salient_1', 'salient_2']
        assert object_2.shows == [ShowConfig(
            step_begin=23,
            position=Vector3d(x=0.31, y=0.32, z=0.33),
            rotation=Vector3d(x=0.34, y=0.35, z=0.36),
            scale=Vector3d(x=0.37, y=0.38, z=0.39)
        )]
        assert object_2.shrouds == [StepBeginEndConfig(
            step_begin=24,
            step_end=25
        )]
        assert object_2.states == [
            ['state_1'], [], ['state_2'], ['state_1', 'state_3']
        ]
        assert object_2.structure is True
        assert object_2.teleports == [TeleportConfig(
            step_begin=26,
            position=Vector3d(x=0.41, y=0.42, z=0.43)
        )]
        assert object_2.toggle_physics == [SingleStepConfig(step_begin=27)]
        assert object_2.torques == [MoveConfig(
            step_begin=28,
            step_end=29,
            vector=Vector3d(x=0.44, y=0.45, z=0.46)
        )]

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
        }}
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


class TestSchemeConfigurationSchema(unittest.TestCase):

    def setUp(self):
        self.scheme_config = SceneConfigurationSchema()

    def test_remove_none(self):
        actual = self.scheme_config.remove_none({})
        self.assertEqual({}, actual)

        actual = self.scheme_config.remove_none({"test": None})
        self.assertEqual({}, actual)

        actual = self.scheme_config.remove_none({"test": 1})
        self.assertEqual({"test": 1}, actual)

        actual = self.scheme_config.remove_none({"test": 1, "none": None})
        self.assertEqual({"test": 1}, actual)

        actual = self.scheme_config.remove_none({"test1": {"test2": 1}})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.scheme_config.remove_none(
            {"test1": {"test2": 1, "none": None}})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.scheme_config.remove_none(
            {"test1": {"test2": 1}, "none": None})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.scheme_config.remove_none(
            {"test1": {"test2": 1, "none": None}, "none": None})
        self.assertEqual({"test1": {"test2": 1}}, actual)

        actual = self.scheme_config.remove_none({"test1": [{"test2": None}]})
        self.assertEqual({"test1": [{}]}, actual)

        actual = self.scheme_config.remove_none(
            {"test1": [{"test2": None, "test3": "test"}]})
        self.assertEqual({"test1": [{"test3": "test"}]}, actual)

        actual = self.scheme_config.remove_none(
            {"test1": [{"test2": None}], "test3": False})
        self.assertEqual({"test1": [{}], "test3": False}, actual)


if __name__ == '__main__':
    unittest.main()
