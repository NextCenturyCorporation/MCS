import unittest

import ai2thor
import PIL

from machine_common_sense.config_manager import Vector3d
from machine_common_sense.plotter import TopDownPlotter, XZHeading


class TestTopDownPlotter(unittest.TestCase):

    def setUp(self):
        self.plotter = TopDownPlotter(
            team="test",
            scene_name="scene",
            room_size=Vector3d(x=10, y=4, z=10)
        )

    def test_convert_color_empty(self):
        color = self.plotter._convert_color('')
        self.assertEqual(color, "ivory")

    def test_convert_color_none(self):
        color = self.plotter._convert_color(None)
        self.assertEqual(color, "ivory")

    def test_convert_color_black(self):
        color = self.plotter._convert_color('black')
        self.assertEqual(color, "ivory")

    def test_convert_color(self):
        color = self.plotter._convert_color('red')
        self.assertEqual(color, "red")

    def test_plot_image_size(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [],
            'structuralObjects': [],
            'agent': {
                'position': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0
                },
                'rotation': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0
                }
            }}
        scene_event = ai2thor.server.Event(metadata=metadata)
        img = self.plotter.plot(scene_event=scene_event, step_number=1)
        self.assertIsInstance(img, PIL.Image.Image)

    def test_plot_twice(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [],
            'structuralObjects': [],
            'agent': {
                'position': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0
                },
                'rotation': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0
                }
            }}
        scene_event = ai2thor.server.Event(metadata=metadata)
        img1 = self.plotter.plot(scene_event=scene_event, step_number=1)
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [],
            'structuralObjects': [],
            'agent': {
                'position': {
                    'x': 2.0,
                    'y': 0.0,
                    'z': 2.0
                },
                'rotation': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0
                }
            }}
        scene_event = ai2thor.server.Event(metadata=metadata)
        img2 = self.plotter.plot(scene_event=scene_event, step_number=2)
        self.assertNotEqual(img1, img2)
        self.assertIsInstance(img1, PIL.Image.Image)
        self.assertIsInstance(img2, PIL.Image.Image)

    def test_calculate_heading_zero_degrees(self):
        heading = self.plotter._calculate_heading(
            0, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, 0.0)
        self.assertAlmostEqual(heading.z, TopDownPlotter.HEADING_LENGTH)
        self.assertIsInstance(heading, XZHeading)

    def test_calculate_heading_ninety_degrees(self):
        heading = self.plotter._calculate_heading(
            90, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, -TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.z, 0.0)
        self.assertIsInstance(heading, XZHeading)

    def test_calculate_heading_one_eighty_degrees(self):
        heading = self.plotter._calculate_heading(
            180, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, 0.0)
        self.assertAlmostEqual(heading.z, -TopDownPlotter.HEADING_LENGTH)
        self.assertIsInstance(heading, XZHeading)

    def test_calculate_heading_two_seventy_degrees(self):
        heading = self.plotter._calculate_heading(
            270, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.z, 0.0)
        self.assertIsInstance(heading, XZHeading)

    def test_calculate_heading_three_sixty_degrees(self):
        heading = self.plotter._calculate_heading(
            360, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, 0.0)
        self.assertAlmostEqual(heading.z, TopDownPlotter.HEADING_LENGTH)
        self.assertIsInstance(heading, XZHeading)

    def test_calculate_heading_seven_twenty_degrees(self):
        heading = self.plotter._calculate_heading(
            720, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, 0.0)
        self.assertAlmostEqual(heading.z, TopDownPlotter.HEADING_LENGTH)
        self.assertIsInstance(heading, XZHeading)

    def test_calculate_heading_negative_ninety_degrees(self):
        heading = self.plotter._calculate_heading(
            -90, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.z, 0.0)
        self.assertIsInstance(heading, XZHeading)

    def test_calculate_heading_negative_seven_twenty_degrees(self):
        heading = self.plotter._calculate_heading(
            -720, TopDownPlotter.HEADING_LENGTH)
        self.assertAlmostEqual(heading.x, 0.0)
        self.assertAlmostEqual(heading.z, TopDownPlotter.HEADING_LENGTH)
        self.assertIsInstance(heading, XZHeading)

    def test_create_robot(self):
        robot_metadata = {
            'position': {
                'x': 2.70,
                'y': 1.23,
                'z': 3.14
            },
            'rotation': {
                'x': 0.0,
                'y': 78.0,
                'z': 0.0
            }
        }
        robot = self.plotter._create_robot(robot_metadata)

        self.assertAlmostEqual(robot.x, 2.70)
        self.assertAlmostEqual(robot.y, 1.23)
        self.assertAlmostEqual(robot.z, 3.14)
        self.assertAlmostEqual(robot.rotation, 78.0)

    def test_create_robot_missing_position(self):
        robot_metadata = {
            'rotation': {
                'x': 0.0,
                'y': 78.0,
                'z': 0.0
            }
        }
        robot = self.plotter._create_robot(robot_metadata)

        self.assertAlmostEqual(robot.x, 0.0)
        self.assertAlmostEqual(robot.y, 0.0)
        self.assertAlmostEqual(robot.z, 0.0)
        self.assertAlmostEqual(robot.rotation, 78.0)

    def test_create_robot_missing_rotation(self):
        robot_metadata = {
            'position': {
                'x': 2.70,
                'y': 1.23,
                'z': 3.14
            }
        }
        robot = self.plotter._create_robot(robot_metadata)

        self.assertAlmostEqual(robot.x, 2.70)
        self.assertAlmostEqual(robot.y, 1.23)
        self.assertAlmostEqual(robot.z, 3.14)
        self.assertAlmostEqual(robot.rotation, 0.0)

    def test_create_object(self):
        object_metadata = {
            'isPickedUp': True,
            'visibleInCamera': True,
            'objectId': 'test-uuid',
            'colorsFromMaterials': [
                'orange'
            ],
            'objectBounds': {
                'objectBoundsCorners': [
                    {'x': 0, 'y': 0, 'z': 0},
                    {'x': 0, 'y': 0, 'z': 1},
                    {'x': 1, 'y': 0, 'z': 1},
                    {'x': 1, 'y': 0, 'z': 0},
                    {'x': 0, 'y': 1, 'z': 0},
                    {'x': 0, 'y': 1, 'z': 1},
                    {'x': 1, 'y': 1, 'z': 1},
                    {'x': 1, 'y': 1, 'z': 0}
                ]
            }
        }
        obj = self.plotter._create_object(object_metadata)

        self.assertTrue(obj.held)
        self.assertTrue(obj.visible)
        self.assertEqual(obj.uuid, 'test-uuid')
        self.assertIsInstance(obj.bounds, list)
        self.assertEqual(len(obj.bounds), 8)
        self.assertEqual(obj.color, "orange")

    def test_create_object_empty(self):
        object_metadata = {}
        obj = self.plotter._create_object(object_metadata)

        self.assertIsNone(obj.held)
        self.assertIsNone(obj.visible)
        self.assertIsNone(obj.uuid)
        self.assertIsNone(obj.bounds)
        self.assertEqual(obj.color, "ivory")

    def test_find_plottable_objects_empty(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [],
            'structuralObjects': [],
            'agent': {
                'position': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0
                },
                'rotation': {
                    'x': 0.0,
                    'y': 0.0,
                    'z': 0.0
                }
            }
        }
        scene_event = ai2thor.server.Event(metadata=metadata)
        filtered_objects = self.plotter._find_plottable_objects(scene_event)
        self.assertEqual(len(filtered_objects), 0)

    def test_find_plottable_objects_combined(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [
                {'objectId': 'test-uuid1'},
                {'objectId': 'test-uuid2'},
                {'objectId': 'test-uuid3'}
            ],
            'structuralObjects': [
                {'objectId': 'occluder1'},
                {'objectId': 'occluder2'},
                {'objectId': 'wall1'}
            ]
        }
        scene_event = ai2thor.server.Event(metadata=metadata)
        filtered_objects = self.plotter._find_plottable_objects(scene_event)
        self.assertEqual(len(filtered_objects), 6)
        self.assertEqual(len(
            [k for k in filtered_objects
             if k['objectId'].startswith('test-uuid')]), 3)
        self.assertEqual(len(
            [k for k in filtered_objects
             if k['objectId'].startswith('occluder')]), 2)
        self.assertEqual(len(
            [k for k in filtered_objects
             if k['objectId'].startswith('wall')]), 1)

    def test_find_plottable_objects_filtered(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [
                {'objectId': 'test-uuid1'},
                {'objectId': 'test-uuid2'},
                {'objectId': 'test-uuid3'}
            ],
            'structuralObjects': [
                {'objectId': 'occluder1'},
                {'objectId': 'occluder2'},
                {'objectId': 'wall1'},
                {'objectId': 'future-object'},
                {'objectId': 'floor-gets-filtered'},
                {'objectId': 'ceiling-gets-filtered'}
            ]
        }
        scene_event = ai2thor.server.Event(metadata=metadata)
        filtered_objects = self.plotter._find_plottable_objects(scene_event)
        self.assertEqual(len(filtered_objects), 7)
        self.assertEqual(filtered_objects[0]['objectId'], 'occluder1')
        self.assertEqual(filtered_objects[1]['objectId'], 'occluder2')
        self.assertEqual(filtered_objects[2]['objectId'], 'wall1')
        self.assertEqual(filtered_objects[3]['objectId'], 'future-object')
        self.assertEqual(filtered_objects[4]['objectId'], 'test-uuid1')
        self.assertEqual(filtered_objects[5]['objectId'], 'test-uuid2')
        self.assertEqual(filtered_objects[6]['objectId'], 'test-uuid3')

    def test_scene_name(self):
        self.assertEqual(self.plotter._scene_name, "scene")

    def test_scene_name_prefix(self):
        plotter = TopDownPlotter(
            team="test",
            scene_name="prefix/scene",
            room_size=Vector3d(x=10, y=3, z=10)
        )

        self.assertEqual(plotter._scene_name, "scene")


if __name__ == '__main__':
    unittest.main()
