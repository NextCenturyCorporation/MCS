import unittest

from machine_common_sense.config_manager import ConfigManager
from machine_common_sense.parameter import Parameter


class TestParameter(unittest.TestCase):

    sc = {'screenshot': False,
          'version': 2,
          'floorTextures': [],
          'isometric': False,
          'performerStart': {'rotation': {'y': 0.0,
                                          'z': 0.0,
                                          'x': 0.0},
                             'position': {'y': 0.0,
                                          'z': 0.0,
                                          'x': 0.0}},
          'observation': False,
          'intuitivePhysics': False,
          'floorMaterial': 'AI2-THOR/Materials/Fabrics/CarpetWhite 3',
          'ceilingMaterial': 'AI2-THOR/Materials/Walls/Drywall',
          'holes': [],
          'objects': [{'shows': [{'position': {'y': 0.25,
                                               'z': 1.0,
                                               'x': 0.25},
                                  'boundingBox': [],
                                  'stepBegin': 0,
                                  'scale': {'y': 0.5,
                                            'z': 0.5,
                                            'x': 0.5},
                                  'rotation': {'y': 0.0,
                                               'z': 0.0,
                                               'x': 0.0}}],
                       'pickupable': False,
                       'mass': 1.0,
                       'materials': ['AI2-THOR/Materials/Plastics/BlueRubber'],
                       'salientMaterials': ['rubber'],
                       'moveable': False,
                       'type': 'ball',
                       'id': 'testBall1'},
                      {'shows': [{'position': {'y': 0.25,
                                               'z': 2.0,
                                               'x': -0.25},
                                  'boundingBox': [],
                                  'stepBegin': 0,
                                  'scale': {'y': 0.5,
                                            'z': 0.5,
                                            'x': 0.5},
                                  'rotation': {'y': 0.0,
                                               'z': 0.0,
                                               'x': 0.0}}],
                       'pickupable': False,
                       'mass': 1.0,
                       'materials': ['AI2-THOR/Materials/Plastics/BlueRubber'],
                       'salientMaterials': ['rubber'],
                       'moveable': False,
                       'type': 'ball',
                       'id': 'testBall2'}],
          'wallMaterial': 'AI2-THOR/Materials/Walls/Drywall',
          'name': 'depth and segmentation test',
          'roomDimensions': {'y': 3.0,
                             'z': 10.0,
                             'x': 10.0}}

    def setUp(self):
        config = ConfigManager(config_file_or_dict={})
        self.parameter_converter = Parameter(config)

    def test_build_aithor_step(self):
        foo, bar = self.parameter_converter.build_ai2thor_step(
            action='Initialize', sceneConfig=self.sc)

        self.assertIsNotNone(foo.get('sceneConfig'))
        print(foo)
        print(bar)

    """
    wrapped_step should be this with the depth integration test scene
    """
    {'continuous': True,
     'gridSize': 0.1,
     'logs': True,
     'renderDepthImage': True,
     'renderObjectImage': True,
     'snapToGrid': False,
     'consistentColors': True,
     'action': 'Initialize',
     'sceneConfig': {'isometric': False,
                     'objects': [{'type': 'ball',
                                  'moveable': False,
                                  'salientMaterials': ['rubber'],
                                  'pickupable': False,
                                  'id': 'testBall1',
                                  'shows': [{'scale': {'y': 0.5,
                                                       'z': 0.5,
                                                       'x': 0.5},
                                             'stepBegin': 0,
                                             'position': {'y': 0.25,
                                                          'z': 1.0,
                                                          'x': 0.25},
                                             'boundingBox': [],
                                             'rotation': {'y': 0.0,
                                                          'z': 0.0,
                                                          'x': 0.0}}],
                                  'mass': 1.0,
                                  'materials': ['AI2-THOR/Materials/Plastics/BlueRubber']},  # noqa: E501
                                 {'type': 'ball',
                                  'moveable': False,
                                  'salientMaterials': ['rubber'],
                                  'pickupable': False,
                                  'id': 'testBall2',
                                  'shows': [{'scale': {'y': 0.5,
                                                       'z': 0.5,
                                                       'x': 0.5},
                                             'stepBegin': 0,
                                             'position': {'y': 0.25,
                                                          'z': 2.0,
                                                          'x': -0.25},
                                             'boundingBox': [],
                                             'rotation': {'y': 0.0,
                                                          'z': 0.0,
                                                          'x': 0.0}}],
                                  'mass': 1.0,
                                  'materials': ['AI2-THOR/Materials/Plastics/BlueRubber']}],  # noqa: E501
                     'name': 'depth and segmentation test',
                     'intuitivePhysics': False,
                     'screenshot': False,
                     'floorMaterial': 'AI2-THOR/Materials/Fabrics/CarpetWhite 3',  # noqa: E501
                     'holes': [],
                     'performerStart': {'position': {'y': 0.0,
                                                     'z': 0.0,
                                                     'x': 0.0},
                                        'rotation': {'y': 0.0,
                                                     'z': 0.0,
                                                     'x': 0.0}},
                     'roomDimensions': {'y': 3.0,
                                        'z': 10.0,
                                        'x': 10.0},
                     'wallMaterial': 'AI2-THOR/Materials/Walls/Drywall',
                     'observation': False,
                     'version': 2,
                     'ceilingMaterial': 'AI2-THOR/Materials/Walls/Drywall',
                     'floorTextures': []}}
