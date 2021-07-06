import os
import unittest
from unittest.mock import patch

from machine_common_sense.config_manager import (ChangeMaterialConfig,
                                                 ConfigManager, ForceConfig,
                                                 GoalSchema, MoveConfig,
                                                 OpenCloseConfig,
                                                 PhysicsConfig,
                                                 SceneConfiguration,
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
        assert object_1.centerOfMass is None
        assert object_1.changeMaterials is None
        assert object_1.debug is None
        assert object_1.forces is None
        assert object_1.ghosts is None
        assert object_1.hides is None
        assert object_1.kinematic is None
        assert object_1.locationParent is None
        assert object_1.mass is None
        assert object_1.materials is None
        assert object_1.moveable is None
        assert object_1.moves is None
        assert object_1.nullParent is None
        assert object_1.openable is None
        assert object_1.opened is None
        assert object_1.openClose is None
        assert object_1.physics is None
        assert object_1.physicsProperties is None
        assert object_1.pickupable is None
        assert object_1.receptacle is None
        assert object_1.resetCenterOfMass is None
        assert object_1.resizes is None
        assert object_1.rotates is None
        assert object_1.salientMaterials is None
        assert object_1.shows is None
        assert object_1.shrouds is None
        assert object_1.states is None
        assert object_1.structure is None
        assert object_1.teleports is None
        assert object_1.togglePhysics is None
        assert object_1.torques is None

        assert object_2.id == 'id_2'
        assert object_2.type == 'type_2'
        assert object_2.centerOfMass == Vector3d(x=0.01, y=0.02, z=0.03)
        assert object_2.changeMaterials == [ChangeMaterialConfig(
            stepBegin=10,
            materials=['material_3', 'material_4']
        )]
        assert object_2.debug == {'key': 'value'}
        assert object_2.forces == [ForceConfig(
            relative=True,
            stepBegin=11,
            stepEnd=12,
            vector=Vector3d(x=0.04, y=0.05, z=0.06)
        )]
        assert object_2.ghosts == [StepBeginEndConfig(
            stepBegin=13,
            stepEnd=14
        )]
        assert object_2.hides == [SingleStepConfig(stepBegin=15)]
        assert object_2.kinematic is True
        assert object_2.locationParent == 'parent_id'
        assert object_2.mass == 12.34
        assert object_2.materials == ['material_1', 'material_2']
        assert object_2.moveable is True
        assert object_2.moves == [MoveConfig(
            stepBegin=16,
            stepEnd=17,
            vector=Vector3d(x=0.07, y=0.08, z=0.09)
        )]
        assert object_2.nullParent == TransformConfig(
            position=Vector3d(x=0.11, y=0.12, z=0.13),
            rotation=Vector3d(x=0.14, y=0.15, z=0.16),
            scale=Vector3d(x=0.17, y=0.18, z=0.19)
        )
        assert object_2.openable is True
        assert object_2.opened is True
        assert object_2.openClose == [OpenCloseConfig(open=True, step=18)]
        assert object_2.physics is True
        assert object_2.physicsProperties == PhysicsConfig(
            enable=True,
            angularDrag=1,
            bounciness=2,
            drag=3,
            dynamicFriction=4,
            staticFriction=5
        )
        assert object_2.pickupable is True
        assert object_2.receptacle is True
        assert object_2.resetCenterOfMass is True
        assert object_2.resizes == [SizeConfig(
            stepBegin=19,
            stepEnd=20,
            size=Vector3d(x=0.21, y=0.22, z=0.23)
        )]
        assert object_2.rotates == [MoveConfig(
            stepBegin=21,
            stepEnd=22,
            vector=Vector3d(x=0.24, y=0.25, z=0.26)
        )]
        assert object_2.salientMaterials == ['salient_1', 'salient_2']
        assert object_2.shows == [ShowConfig(
            stepBegin=23,
            position=Vector3d(x=0.31, y=0.32, z=0.33),
            rotation=Vector3d(x=0.34, y=0.35, z=0.36),
            scale=Vector3d(x=0.37, y=0.38, z=0.39)
        )]
        assert object_2.shrouds == [StepBeginEndConfig(
            stepBegin=24,
            stepEnd=25
        )]
        assert object_2.states == [
            ['state_1'], [], ['state_2'], ['state_1', 'state_3']
        ]
        assert object_2.structure is True
        assert object_2.teleports == [TeleportConfig(
            stepBegin=26,
            position=Vector3d(x=0.41, y=0.42, z=0.43)
        )]
        assert object_2.togglePhysics == [SingleStepConfig(stepBegin=27)]
        assert object_2.torques == [MoveConfig(
            stepBegin=28,
            stepEnd=29,
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
