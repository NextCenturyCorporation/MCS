import os
import unittest
from unittest.mock import DEFAULT, patch

import machine_common_sense as mcs
from machine_common_sense.config_manager import (ActionConfig,
                                                 AgentMovementConfig,
                                                 AgentSettings,
                                                 ChangeMaterialConfig,
                                                 ConfigManager, ForceConfig,
                                                 Goal, MetadataTier,
                                                 MoveConfig, OpenCloseConfig,
                                                 PhysicsConfig,
                                                 SceneConfiguration,
                                                 SceneObject, SequenceConfig,
                                                 ShowConfig, SingleStepConfig,
                                                 SizeConfig,
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
        with self.assertRaises(RuntimeError):
            ConfigManager()

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
        with self.assertRaises(RuntimeError):
            ConfigManager(missing_config_file)

    def test_init_with_no_config(self):
        '''No dictionary, no file, and no env should raise an exception'''
        with self.assertRaises(RuntimeError):
            ConfigManager()

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
            'actions': [{
                'stepBegin': 1,
                'stepEnd': 5,
                'id': 'animation_a',
                'isLoopAnimation': True,
            }, {
                'stepBegin': 25,
                'id': 'animation_b'
            }],
            'agentMovement': {
                "repeat": True,
                "stepBegin": 4,
                "sequence": [{
                    "animation": "TPM_walk",
                    "endPoint":
                    {
                        "x": 1,
                        "z": 1
                    }
                }, {
                    "animation": "TPM_run",
                    "endPoint":
                    {
                        "x": -0.7,
                        "z": -1.3
                    }
                }, {
                    "animation": "TPF_walk",
                    "endPoint":
                    {
                        "x": 1.2,
                        "z": -1.5
                    }
                }, {
                    "animation": "TPF_run",
                    "endPoint":
                    {
                        "x": -0.6,
                        "z": 1.2
                    }
                }]
            },
            'agentSettings': {
                'chest': 1,
                'chestMaterial': 2,
                'eyes': 3,
                'feet': 4,
                'feetMaterial': 5,
                'glasses': 6,
                'hair': 7,
                'hairMaterial': 8,
                'hatMaterial': 9,
                'hideHair': True,
                'isElder': True,
                'jacket': 10,
                'jacketMaterial': 11,
                'legs': 12,
                'legsMaterial': 13,
                'showBeard': True,
                'showGlasses': True,
                'showJacket': True,
                'showTie': True,
                'skin': 14,
                'tie': 15,
                'tieMaterial': 16
            },
            'associatedWithAgent': "agent_male",
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
                'impulse': True,
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
            'maxAngularVelocity': 25,
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
            SceneObject(**object_config)
            for object_config in object_config_list
        ]
        scene_config = SceneConfiguration(objects=object_list)
        self.assertEqual(len(scene_config.objects), 2)
        object_1 = scene_config.objects[0]
        object_2 = scene_config.objects[1]

        self.assertEqual(object_1.id, 'id_1')
        self.assertEqual(object_1.type, 'type_1')
        self.assertIsNone(object_1.actions)
        self.assertIsNone(object_1.agent_movement)
        self.assertIsNone(object_1.agent_settings)
        self.assertIsNone(object_1.center_of_mass)
        self.assertIsNone(object_1.change_materials)
        self.assertIsNone(object_1.debug)
        self.assertIsNone(object_1.forces)
        self.assertIsNone(object_1.ghosts)
        self.assertIsNone(object_1.hides)
        self.assertIsNone(object_1.kinematic)
        self.assertIsNone(object_1.location_parent)
        self.assertIsNone(object_1.mass)
        self.assertIsNone(object_1.materials)
        self.assertIsNone(object_1.max_angular_velocity)
        self.assertIsNone(object_1.moveable)
        self.assertIsNone(object_1.moves)
        self.assertIsNone(object_1.null_parent)
        self.assertIsNone(object_1.openable)
        self.assertIsNone(object_1.opened)
        self.assertIsNone(object_1.open_close)
        self.assertIsNone(object_1.physics)
        self.assertIsNone(object_1.physics_properties)
        self.assertIsNone(object_1.pickupable)
        self.assertIsNone(object_1.receptacle)
        self.assertIsNone(object_1.reset_center_of_mass)
        self.assertIsNone(object_1.resizes)
        self.assertIsNone(object_1.rotates)
        self.assertIsNone(object_1.salient_materials)
        self.assertIsNone(object_1.shows)
        self.assertIsNone(object_1.shrouds)
        self.assertIsNone(object_1.states)
        self.assertIsNone(object_1.structure)
        self.assertIsNone(object_1.teleports)
        self.assertIsNone(object_1.toggle_physics)
        self.assertIsNone(object_1.torques)

        self.assertEqual(object_2.id, 'id_2')
        self.assertEqual(object_2.type, 'type_2')
        self.assertEqual(object_2.actions, [
            ActionConfig(
                step_begin=1,
                id='animation_a',
                step_end=5,
                is_loop_animation=True),
            ActionConfig(
                step_begin=25,
                id='animation_b',
                is_loop_animation=False)
        ])
        self.assertEqual(object_2.agent_movement, AgentMovementConfig(
            repeat=True,
            step_begin=4,
            sequence=[
                SequenceConfig(
                    animation="TPM_walk",
                    end_point=Vector3d(x=1, y=0, z=1)),
                SequenceConfig(
                    animation="TPM_run",
                    end_point=Vector3d(x=-0.7, y=0, z=-1.3)),
                SequenceConfig(
                    animation="TPF_walk",
                    end_point=Vector3d(x=1.2, y=0, z=-1.5)),
                SequenceConfig(
                    animation="TPF_run",
                    end_point=Vector3d(x=-0.6, y=0, z=1.2))
            ]
        ))
        self.assertEqual(object_2.agent_settings, AgentSettings(
            chest=1,
            chest_material=2,
            eyes=3,
            feet=4,
            feet_material=5,
            glasses=6,
            hair=7,
            hair_material=8,
            hat_material=9,
            hide_hair=True,
            is_elder=True,
            jacket=10,
            jacket_material=11,
            legs=12,
            legs_material=13,
            show_beard=True,
            show_glasses=True,
            show_jacket=True,
            show_tie=True,
            skin=14,
            tie=15,
            tie_material=16
        ))
        self.assertEqual(object_2.associated_with_agent, 'agent_male')
        self.assertEqual(
            object_2.center_of_mass, Vector3d(
                x=0.01, y=0.02, z=0.03))
        self.assertEqual(object_2.change_materials, [ChangeMaterialConfig(
            step_begin=10,
            materials=['material_3', 'material_4']
        )])
        self.assertEqual(object_2.debug, {'key': 'value'})
        self.assertEqual(object_2.forces, [ForceConfig(
            impulse=True,
            relative=True,
            step_begin=11,
            step_end=12,
            vector=Vector3d(x=0.04, y=0.05, z=0.06)
        )])
        self.assertEqual(object_2.ghosts, [StepBeginEndConfig(
            step_begin=13,
            step_end=14
        )])
        self.assertEqual(object_2.hides, [SingleStepConfig(step_begin=15)])
        self.assertTrue(object_2.kinematic)
        self.assertEqual(object_2.location_parent, 'parent_id')
        self.assertEqual(object_2.mass, 12.34)
        self.assertListEqual(object_2.materials, ['material_1', 'material_2'])
        self.assertEqual(object_2.max_angular_velocity, 25)
        self.assertTrue(object_2.moveable)
        self.assertEqual(object_2.moves, [MoveConfig(
            step_begin=16,
            step_end=17,
            vector=Vector3d(x=0.07, y=0.08, z=0.09)
        )])
        self.assertEqual(object_2.null_parent, TransformConfig(
            position=Vector3d(x=0.11, y=0.12, z=0.13),
            rotation=Vector3d(x=0.14, y=0.15, z=0.16),
            scale=Vector3d(x=0.17, y=0.18, z=0.19)
        ))
        self.assertTrue(object_2.openable)
        self.assertTrue(object_2.opened)
        self.assertEqual(
            object_2.open_close, [
                OpenCloseConfig(
                    open=True, step=18)])
        self.assertTrue(object_2.physics)
        self.assertEqual(object_2.physics_properties, PhysicsConfig(
            enable=True,
            angular_drag=1,
            bounciness=2,
            drag=3,
            dynamic_friction=4,
            static_friction=5
        ))
        self.assertTrue(object_2.pickupable)
        self.assertTrue(object_2.receptacle)
        self.assertTrue(object_2.reset_center_of_mass)
        self.assertEqual(object_2.resizes, [SizeConfig(
            step_begin=19,
            step_end=20,
            size=Vector3d(x=0.21, y=0.22, z=0.23)
        )])
        self.assertEqual(object_2.rotates, [MoveConfig(
            step_begin=21,
            step_end=22,
            vector=Vector3d(x=0.24, y=0.25, z=0.26)
        )])
        self.assertListEqual(
            object_2.salient_materials, [
                'salient_1', 'salient_2'])
        self.assertEqual(object_2.shows, [ShowConfig(
            step_begin=23,
            position=Vector3d(x=0.31, y=0.32, z=0.33),
            rotation=Vector3d(x=0.34, y=0.35, z=0.36),
            scale=Vector3d(x=0.37, y=0.38, z=0.39)
        )])
        self.assertEqual(object_2.shrouds, [StepBeginEndConfig(
            step_begin=24,
            step_end=25
        )])
        self.assertListEqual(object_2.states, [
            ['state_1'], [], ['state_2'], ['state_1', 'state_3']
        ])
        self.assertTrue(object_2.structure)
        self.assertEqual(object_2.teleports, [TeleportConfig(
            step_begin=26,
            position=Vector3d(x=0.41, y=0.42, z=0.43)
        )])
        self.assertEqual(
            object_2.toggle_physics, [
                SingleStepConfig(
                    step_begin=27)])
        self.assertEqual(object_2.torques, [ForceConfig(
            step_begin=28,
            step_end=29,
            vector=Vector3d(x=0.44, y=0.45, z=0.46)
        )])

    def test_retrieve_goal_with_config_metadata(self):
        # self.controller.set_metadata_tier('oracle')
        goal = {
            'metadata': {
                'target': {'image': [0]},
                'target_1': {'image': [1]},
                'target_2': {'image': [2]}
            }
        }

        goal = Goal(**goal)
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        actual = scene_config.retrieve_goal()
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })

    def test_retrieve_goal(self):
        goal = Goal(**{})
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
        goal = Goal(**{})
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
                [(mcs.Action.MOVE_AHEAD.value, {"amount": 0.1})],
                [],
                [(mcs.Action.PASS.value, {}),
                 (mcs.Action.ROTATE_LEFT.value, {}),
                 (mcs.Action.ROTATE_RIGHT.value, {})]
            ],
            "category": "test category",
            "description": "test description",
            "habituation_total": 5,
            "last_step": 10,
            "metadata": {
                "key": "value"
            }
        }
        goal = Goal(**goal)
        scene_config = SceneConfiguration(
            name="test", version=1, goal=goal)
        goal_3 = scene_config.retrieve_goal()

        self.assertEqual(goal_3.action_list, [
            [(mcs.Action.MOVE_AHEAD.value, {"amount": 0.1})],
            [],
            [(mcs.Action.PASS.value, {}), (mcs.Action.ROTATE_LEFT.value, {}),
             (mcs.Action.ROTATE_RIGHT.value, {})]
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
        goal = Goal(**goal)
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
        goal = Goal(**goal)
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
        goal = Goal(**goal)
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
        goal = Goal(**goal)
        scene_config = SceneConfiguration(name="test", version=1, goal=goal)
        actual = scene_config.update_goal_target_image(scene_config.goal)
        self.assertEqual(actual.metadata, {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        })


class TestSceneConfiguration(unittest.TestCase):

    def setUp(self):
        self.scheme_config = SceneConfiguration()

    @unittest.skip
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
