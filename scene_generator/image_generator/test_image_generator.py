import unittest
import mock
import numpy
from PIL import Image

import image_generator
from materials import *

def mock_get_global_material_list(material):
    return [(material + '_1', 'white'), (material + '_2', 'black')]

class Test_Image_Generator(unittest.TestCase):

    @mock.patch('image_generator.get_global_material_list', side_effect=mock_get_global_material_list)
    def test_generate_materials_lists_single_list_single_material(self, mock_function):
        materials_options = [
            ['plastic']
        ]
        actual = image_generator.generate_materials_lists(materials_options)
        expected = [['plastic_1'], ['plastic_2']]
        self.assertEqual(actual, expected)

    @mock.patch('image_generator.get_global_material_list', side_effect=mock_get_global_material_list)
    def test_generate_materials_lists_single_list_multiple_material(self, mock_function):
        materials_options = [
            ['plastic', 'metal']
        ]
        actual = image_generator.generate_materials_lists(materials_options)
        expected = [
            ['plastic_1', 'metal_1'],
            ['plastic_1', 'metal_2'],
            ['plastic_2', 'metal_1'],
            ['plastic_2', 'metal_2']
        ]
        self.assertEqual(actual, expected)

    @mock.patch('image_generator.get_global_material_list', side_effect=mock_get_global_material_list)
    def test_generate_materials_lists_multiple_list_single_material(self, mock_function):
        materials_options = [
            ['metal'],
            ['plastic']
        ]
        actual = image_generator.generate_materials_lists(materials_options)
        expected = [
            ['metal_1'],
            ['metal_2'],
            ['plastic_1'],
            ['plastic_2']
        ]
        self.assertEqual(actual, expected)

    @mock.patch('image_generator.get_global_material_list', side_effect=mock_get_global_material_list)
    def test_generate_materials_lists_multiple_list_multiple_material(self, mock_function):
        materials_options = [
            ['plastic', 'metal'],
            ['wood', 'wood']
        ]
        actual = image_generator.generate_materials_lists(materials_options)
        expected = [
            ['plastic_1', 'metal_1'],
            ['plastic_1', 'metal_2'],
            ['plastic_2', 'metal_1'],
            ['plastic_2', 'metal_2'],
            ['wood_1', 'wood_1'],
            ['wood_1', 'wood_2'],
            ['wood_2', 'wood_1'],
            ['wood_2', 'wood_2']
        ]
        self.assertEqual(actual, expected)

    def test_generate_scene_configuration(self):
        object_definition = {
            'type': 'sphere',
            'position': {
                'x': 0,
                'y': 0.5,
                'z': 2
            },
            'scale': {
                'x': 1,
                'y': 1,
                'z': 1
            }
        }
        actual = image_generator.generate_scene_configuration(object_definition, None)
        expected = {
            'screenshot': True,
            'objects': [{
                'id': 'test_sphere',
                'type': 'sphere',
                'shows': [{
                    'stepBegin': 0,
                    'position': {
                        'x': 0,
                        'y': 0.5,
                        'z': 2
                    },
                    'scale': {
                        'x': 1,
                        'y': 1,
                        'z': 1
                    }
                }]
            }]
        }
        self.assertEqual(actual, expected)

    def test_generate_scene_configuration_with_material_list(self):
        object_definition = {
            'type': 'sphere',
            'position': {
                'x': 0,
                'y': 0.5,
                'z': 2
            },
            'scale': {
                'x': 1,
                'y': 1,
                'z': 1
            }
        }
        actual = image_generator.generate_scene_configuration(object_definition, ['test_material'])
        expected = {
            'screenshot': True,
            'objects': [{
                'id': 'test_sphere',
                'type': 'sphere',
                'materials': ['test_material'],
                'shows': [{
                    'stepBegin': 0,
                    'position': {
                        'x': 0,
                        'y': 0.5,
                        'z': 2
                    },
                    'scale': {
                        'x': 1,
                        'y': 1,
                        'z': 1
                    }
                }]
            }]
        }
        self.assertEqual(actual, expected)

    @mock.patch('image_generator.get_global_material_list', side_effect=mock_get_global_material_list)
    def test_generate_scene_configuration_list(self, mock_function):
        self.maxDiff = None
        object_list = [{
            'type': 'sphere',
            'materials_options': [
                ['plastic'],
                ['metal']
            ],
            'position': {
                'x': 0,
                'y': 0.5,
                'z': 2
            },
            'scale': {
                'x': 1,
                'y': 1,
                'z': 1
            }
        }, {
            'type': 'sofa',
            'position': {
                'x': 0,
                'y': 0.5,
                'z': 3
            },
            'scale': {
                'x': 1,
                'y': 1,
                'z': 1
            }
        }]
        actual = image_generator.generate_scene_configuration_list(object_list)
        expected = [{
            'screenshot': True,
            'objects': [{
                'id': 'test_sphere',
                'type': 'sphere',
                'materials': ['plastic_1'],
                'shows': [{
                    'stepBegin': 0,
                    'position': {
                        'x': 0,
                        'y': 0.5,
                        'z': 2
                    },
                    'scale': {
                        'x': 1,
                        'y': 1,
                        'z': 1
                    }
                }]
            }]
        }, {
            'screenshot': True,
            'objects': [{
                'id': 'test_sphere',
                'type': 'sphere',
                'materials': ['plastic_2'],
                'shows': [{
                    'stepBegin': 0,
                    'position': {
                        'x': 0,
                        'y': 0.5,
                        'z': 2
                    },
                    'scale': {
                        'x': 1,
                        'y': 1,
                        'z': 1
                    }
                }]
            }]
        }, {
            'screenshot': True,
            'objects': [{
                'id': 'test_sphere',
                'type': 'sphere',
                'materials': ['metal_1'],
                'shows': [{
                    'stepBegin': 0,
                    'position': {
                        'x': 0,
                        'y': 0.5,
                        'z': 2
                    },
                    'scale': {
                        'x': 1,
                        'y': 1,
                        'z': 1
                    }
                }]
            }]
        }, {
            'screenshot': True,
            'objects': [{
                'id': 'test_sphere',
                'type': 'sphere',
                'materials': ['metal_2'],
                'shows': [{
                    'stepBegin': 0,
                    'position': {
                        'x': 0,
                        'y': 0.5,
                        'z': 2
                    },
                    'scale': {
                        'x': 1,
                        'y': 1,
                        'z': 1
                    }
                }]
            }]
        }, {
            'screenshot': True,
            'objects': [{
                'id': 'test_sofa',
                'type': 'sofa',
                'shows': [{
                    'stepBegin': 0,
                    'position': {
                        'x': 0,
                        'y': 0.5,
                        'z': 3
                    },
                    'scale': {
                        'x': 1,
                        'y': 1,
                        'z': 1
                    }
                }]
            }]
        }]
        self.assertEqual(actual, expected)

    def test_get_global_material_list(self):
        self.assertEqual(METAL_MATERIALS, image_generator.get_global_material_list('metal'))
        self.assertEqual(PLASTIC_MATERIALS, image_generator.get_global_material_list('plastic'))

    def test_stow_image_pixel_list(self):
        output_data = {}
        scene_configuration = {
            'objects': [{
                'type': 'sphere',
                'materials': ['test_material']
            }]
        }
        object_screenshot = Image.fromarray(numpy.array([[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]], \
            dtype=numpy.uint8))
        actual = image_generator.stow_image_pixel_list(output_data, scene_configuration, object_screenshot)
        expected = {
            'sphere': {
                'test_material': [[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]]
            }
        }
        self.assertEqual(actual, expected)

    def test_stow_image_pixel_list_existing_material(self):
        output_data = {
            'sphere': {
                'test_material_1': [[(21, 22, 23), (24, 25, 26)], [(27, 28, 29), (30, 31, 32)]]
            }
        }
        scene_configuration = {
            'objects': [{
                'type': 'sphere',
                'materials': ['test_material_2']
            }]
        }
        object_screenshot = Image.fromarray(numpy.array([[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]], \
            dtype=numpy.uint8))
        actual = image_generator.stow_image_pixel_list(output_data, scene_configuration, object_screenshot)
        expected = {
            'sphere': {
                'test_material_1': [[(21, 22, 23), (24, 25, 26)], [(27, 28, 29), (30, 31, 32)]],
                'test_material_2': [[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]]
            }
        }
        self.assertEqual(actual, expected)

    def test_stow_image_pixel_list_multiple_material(self):
        output_data = {}
        scene_configuration = {
            'objects': [{
                'type': 'sphere',
                'materials': ['test_material_1', 'test_material_2']
            }]
        }
        object_screenshot = Image.fromarray(numpy.array([[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]], \
            dtype=numpy.uint8))
        actual = image_generator.stow_image_pixel_list(output_data, scene_configuration, object_screenshot)
        expected = {
            'sphere': {
                'test_material_1': {
                    'test_material_2': [[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]]
                }
            }
        }
        self.assertEqual(actual, expected)

    def test_stow_image_pixel_list_no_material(self):
        output_data = {}
        scene_configuration = {
            'objects': [{
                'type': 'sphere'
            }]
        }
        object_screenshot = Image.fromarray(numpy.array([[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]], \
            dtype=numpy.uint8))
        actual = image_generator.stow_image_pixel_list(output_data, scene_configuration, object_screenshot)
        expected = {
            'sphere': [[(1, 2, 3), (4, 5, 6)], [(7, 8, 9), (10, 11, 12)]]
        }
        self.assertEqual(actual, expected)

