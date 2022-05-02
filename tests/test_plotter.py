import os
import unittest

import ai2thor
from PIL import Image, ImageChops, ImageStat

from machine_common_sense.config_manager import (FloorPartitionConfig,
                                                 SceneConfiguration,
                                                 Vector2dInt, Vector3d)
from machine_common_sense.plotter import (Ramp, SceneAsset, SceneBounds,
                                          SceneCoord, TopDownPlotter,
                                          XZHeading)

test_path = os.path.dirname(__file__)
resources_path = os.path.join(test_path, 'resources')


class TestSceneCoord(unittest.TestCase):

    def test_add(self):
        sc1 = SceneCoord(x=-1.0, y=0, z=2.5)
        sc2 = SceneCoord(x=1.0, y=0, z=-2.5)
        sc_add = sc1 + sc2
        self.assertAlmostEqual(sc_add.x, 0)
        self.assertAlmostEqual(sc_add.z, 0)

    def test_subtract(self):
        sc1 = SceneCoord(x=-1.0, y=0, z=2.5)
        sc2 = SceneCoord(x=1.0, y=0, z=-2.5)

        sc_sub = sc1 - sc2
        self.assertAlmostEqual(sc_sub.x, -2.0)
        self.assertAlmostEqual(sc_sub.z, 5.0)

        # order matters
        sc_sub = sc2 - sc1
        self.assertAlmostEqual(sc_sub.x, 2.0)
        self.assertAlmostEqual(sc_sub.z, -5.0)

    def test_midpoint(self):
        '''Gets the midpoint between the two points'''
        sc1 = SceneCoord(x=-1.0, y=0, z=2.5)
        sc2 = SceneCoord(x=1.0, y=0, z=-2.5)

        sc_sub = sc1 | sc2
        self.assertAlmostEqual(sc_sub.x, 0.0)
        self.assertAlmostEqual(sc_sub.z, 0.0)

        # order shouldn't matter
        sc_sub = sc2 | sc1
        self.assertAlmostEqual(sc_sub.x, 0.0)
        self.assertAlmostEqual(sc_sub.z, 0.0)


class TestRamp(unittest.TestCase):

    bounds = [SceneCoord(**pt) for pt in [
        {'x': 1.5, 'y': 0, 'z': 2},
        {'x': 2.5, 'y': 0, 'z': 2},
        {'x': 2.5, 'y': 0, 'z': -2},
        {'x': 1.5, 'y': 0, 'z': -2},
        {'x': 1.5, 'y': 2, 'z': 2},
        {'x': 2.5, 'y': 2, 'z': 2},
        {'x': 2.5, 'y': 2, 'z': -2},
        {'x': 1.5, 'y': 2, 'z': -2}
    ]]

    def test_ramp_arrow(self):
        ramp = Ramp(
            held=False,
            visible=True,
            uuid="ramp-test",
            color="blue",
            bounds=SceneBounds(self.bounds))
        arrow = ramp.arrow
        self.assertTrue(len(arrow.floor), 2)
        self.assertIsInstance(arrow.floor, list)
        self.assertIsInstance(arrow.floor[0], SceneCoord)

        self.assertAlmostEqual(arrow.floor[0].x, self.bounds[3].x)
        self.assertAlmostEqual(arrow.floor[0].z, self.bounds[3].z)

        self.assertAlmostEqual(arrow.floor[1].x, self.bounds[2].x)
        self.assertAlmostEqual(arrow.floor[1].z, self.bounds[2].z)

        self.assertIsInstance(arrow.peak, SceneCoord)
        self.assertAlmostEqual(arrow.peak.x, 2.0)
        self.assertAlmostEqual(arrow.peak.z, 2.0)


class TestTopDownPlotter(unittest.TestCase):

    def setUp(self):
        scene_config = SceneConfiguration(
            name="test", room_dimensions=Vector3d(
                x=10, y=4, z=10))
        self.plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config
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
        self.assertIsInstance(img, Image.Image)

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
        self.assertIsInstance(img1, Image.Image)
        self.assertIsInstance(img2, Image.Image)

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
        self.assertAlmostEqual(robot.z, 3.14)
        self.assertAlmostEqual(robot.rotation_y, 282)

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
        self.assertAlmostEqual(robot.z, 0.0)
        self.assertAlmostEqual(robot.rotation_y, 282)

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
        self.assertAlmostEqual(robot.z, 3.14)
        self.assertAlmostEqual(robot.rotation_y, 360)

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
        obj = self.plotter._create_asset(object_metadata)

        self.assertTrue(obj.held)
        self.assertTrue(obj.visible)
        self.assertEqual(obj.uuid, 'test-uuid')
        self.assertIsInstance(obj.bounds, SceneBounds)
        self.assertEqual(len(obj.bounds.points), 8)
        self.assertEqual(obj.color, "orange")

    def test_create_object_empty(self):
        object_metadata = {}
        obj = self.plotter._create_asset(object_metadata)

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
                {'objectId': 'test-uuid1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'test-uuid2',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'test-uuid3',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
            ],
            'structuralObjects': [
                {'objectId': 'occluder1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'occluder2',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'wall1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
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
                {'objectId': 'test-uuid1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'test-uuid2',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'test-uuid3',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
            ],
            'structuralObjects': [
                {'objectId': 'occluder1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'occluder2',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'wall1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'future-object',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'floor-gets-filtered',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'ceiling-gets-filtered',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
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

    def test_find_plottable_objects_sorted(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [
                {'objectId': 'test-uuid1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 5}]}},
                {'objectId': 'test-uuid2',
                 'objectBounds': {'objectBoundsCorners': [{'y': 6}]}},
                {'objectId': 'test-uuid3',
                 'objectBounds': {'objectBoundsCorners': [{'y': 7}]}},
            ],
            'structuralObjects': [
                {'objectId': 'occluder1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 1}]}},
                {'objectId': 'occluder2',
                 'objectBounds': {'objectBoundsCorners': [{'y': 2}]}},
                {'objectId': 'wall1',
                 'objectBounds': {'objectBoundsCorners': [{'y': 3}]}},
                {'objectId': 'future-object',
                 'objectBounds': {'objectBoundsCorners': [{'y': 4}]}},
                {'objectId': 'floor-gets-filtered',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
                {'objectId': 'ceiling-gets-filtered',
                 'objectBounds': {'objectBoundsCorners': [{'y': 0}]}},
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
        self.assertEqual(self.plotter._scene_name, "test")

    def test_scene_name_prefix(self):
        scene_config = SceneConfiguration(
            name="prefix/test", room_dimensions=Vector3d(
                x=10, y=4, z=10))
        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config
        )

        self.assertEqual(plotter._scene_name, "test")

    def test_draw_holes_even_room_dimensions(self):
        holes = [
            Vector2dInt(**{"x": 0, "z": 0}),
            Vector2dInt(**{"x": -3, "z": 0}),
            Vector2dInt(**{"x": 3, "z": 0}),
            Vector2dInt(**{"x": 0, "z": 4}),
            Vector2dInt(**{"x": 0, "z": -4}),
            Vector2dInt(**{"x": 2, "z": 0}),
            Vector2dInt(**{"x": -2, "z": 0}),
            Vector2dInt(**{"x": 2, "z": 3}),
            Vector2dInt(**{"x": -2, "z": -3}),
            Vector2dInt(**{"x": 2, "z": -3}),
            Vector2dInt(**{"x": -2, "z": 3}),
            Vector2dInt(**{"x": -3, "z": -4}),
            Vector2dInt(**{"x": 3, "z": 4}),
            Vector2dInt(**{"x": -3, "z": 4}),
            Vector2dInt(**{"x": 3, "z": -4}),
        ]
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            holes=holes,
            room_dimensions=Vector3d(
                x=6,
                y=3,
                z=8),
            floor_textures=[]
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        holes_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        """
        holes_img.save(
            os.path.join(
                resources_path,
                'plotter_holes_even_dimensions.png'))
        """

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_holes_even_dimensions.png'))
        # calculate image difference
        diff = ImageChops.difference(holes_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_holes_odd_room_dimensions(self):
        holes = [
            Vector2dInt(**{"x": 0, "z": 0}),
            Vector2dInt(**{"x": 2, "z": 3}),
            Vector2dInt(**{"x": 2, "z": -3}),
            Vector2dInt(**{"x": -2, "z": -3}),
            Vector2dInt(**{"x": -2, "z": 3}),
            Vector2dInt(**{"x": 2, "z": 1}),
            Vector2dInt(**{"x": -2, "z": 1}),
            Vector2dInt(**{"x": -2, "z": -1}),
            Vector2dInt(**{"x": 2, "z": -1}),
            Vector2dInt(**{"x": 0, "z": 3}),
            Vector2dInt(**{"x": 0, "z": -3}),
            Vector2dInt(
                **{"x": -3, "z": 3}),  # out of bounds - don't draw
            Vector2dInt(
                **{"x": 3, "z": -3}),  # out of bounds - don't draw
        ]
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            holes=holes,
            room_dimensions=Vector3d(
                x=5,
                y=3,
                z=7),
            floor_textures=[]
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        holes_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        """
        holes_img.save(
            os.path.join(
                resources_path,
                'plotter_holes_odd_dimensions.png'))
        """

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_holes_odd_dimensions.png'))
        # calculate image difference
        diff = ImageChops.difference(holes_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_holes_even_odd_room_dimensions(self):
        holes = [
            Vector2dInt(**{"x": 0, "z": 0}),
            Vector2dInt(**{"x": 5, "z": 4}),
            Vector2dInt(**{"x": -5, "z": 4}),
            Vector2dInt(**{"x": 5, "z": -4}),
            Vector2dInt(**{"x": -5, "z": -4}),
            Vector2dInt(**{"x": 4, "z": -4}),
            Vector2dInt(**{"x": 4, "z": -3}),
            Vector2dInt(**{"x": 5, "z": -3}),
            Vector2dInt(**{"x": -5, "z": -3}),
            Vector2dInt(**{"x": -4, "z": -3}),
            Vector2dInt(**{"x": -4, "z": -4}),
            Vector2dInt(**{"x": 0, "z": -4}),
            Vector2dInt(**{"x": 0, "z": 4}),
            Vector2dInt(**{"x": 4, "z": 0}),
            Vector2dInt(**{"x": -4, "z": 0}),
            Vector2dInt(**{"x": 5, "z": 3}),
            Vector2dInt(**{"x": -5, "z": 3}),
            Vector2dInt(**{"x": -4, "z": 3}),
            Vector2dInt(**{"x": 4, "z": 3}),
            Vector2dInt(**{"x": 4, "z": 4}),
            Vector2dInt(**{"x": -4, "z": 4}),
            Vector2dInt(**{"x": -5, "z": 0}),
            Vector2dInt(**{"x": 5, "z": 0}),
            Vector2dInt(
                **{"x": 6, "z": 0}),  # out of bounds - dont draw
            Vector2dInt(
                **{"x": -5, "z": -5})  # out of bounds - dont draw

        ]
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            holes=holes,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=9),
            lava=[]
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        holes_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        """
        holes_img.save(
            os.path.join(
                resources_path,
                'plotter_holes_even_odd_dimensions.png'))
        """

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_holes_even_odd_dimensions.png'))
        # calculate image difference
        diff = ImageChops.difference(holes_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_lava(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=6,
                y=3,
                z=10),
            lava=[
                Vector2dInt(**{"x": 0, "z": 0}),
                Vector2dInt(**{"x": -3, "z": 0}),
                Vector2dInt(**{"x": 3, "z": 0}),
                Vector2dInt(**{"x": 0, "z": 5}),
                Vector2dInt(**{"x": 0, "z": -5}),
                Vector2dInt(**{"x": 2, "z": 0}),
                Vector2dInt(**{"x": -2, "z": 0}),
                Vector2dInt(**{"x": 2, "z": 4}),
                Vector2dInt(**{"x": -2, "z": -4}),
                Vector2dInt(**{"x": 2, "z": -4}),
                Vector2dInt(**{"x": -2, "z": 4}),
                Vector2dInt(**{"x": -3, "z": -4}),
                Vector2dInt(**{"x": 3, "z": 4}),
                Vector2dInt(**{"x": -3, "z": 4}),
                Vector2dInt(**{"x": 3, "z": -4}),
                Vector2dInt(**{"x": 3, "z": -5}),
                Vector2dInt(**{"x": 3, "z": 5}),
                Vector2dInt(**{"x": -3, "z": 5}),
                Vector2dInt(**{"x": -3, "z": -5}),
                Vector2dInt(**{"x": 2, "z": -5}),
                Vector2dInt(**{"x": 2, "z": 5}),
                Vector2dInt(**{"x": -2, "z": 5}),
                Vector2dInt(**{"x": -2, "z": -5}),
                Vector2dInt(
                    **{"x": -4, "z": -6}),  # out of bounds - lava don't draw
                Vector2dInt(
                    **{"x": 4, "z": 6})  # out of bounds bad - lava don't draw
            ]
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()

        lava_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # lava_img.save(os.path.join(resources_path, 'plotter_lava.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_lava.png'))
        # calculate image difference
        diff = ImageChops.difference(lava_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_lava_from_partition_floor(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(x=10, y=3, z=10),
            partition_floor=FloorPartitionConfig(left_half=0.2, right_half=0.8)
        )

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()

        lava_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # lava_img.save(os.path.join(resources_path, 'plotter_lava_2.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_lava_2.png')
        )
        # calculate image difference
        diff = ImageChops.difference(lava_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_room(self):
        '''Floor grid plus walls'''
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=10),
            lava=[]
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        base_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # base_img.save(os.path.join(resources_path, 'plotter_base.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_base.png'))
        # calculate image difference
        diff = ImageChops.difference(base_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_nonsquare_room(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=20),
            lava=[]
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        base_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # base_img.save(os.path.join(
        #     resources_path,
        #     'plotter_nonsquare_base.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_nonsquare_base.png'))
        # calculate image difference
        diff = ImageChops.difference(base_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_agent_facing_angled(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        robot_metadata = {
            'position': {'x': 1, 'y': 0, 'z': 2},
            'rotation': {'x': 0, 'y': 135, 'z': 0}
        }

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_robot(img, robot_metadata=robot_metadata)
        agent_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # agent_img.save(
        #     os.path.join(resources_path, 'plotter_agent_angle.png')
        # )

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_agent_angle.png')
        )
        # calculate image difference
        diff = ImageChops.difference(agent_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_agent_facing_front(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        robot_metadata = {
            'position': {'x': 1, 'y': 0, 'z': 2},
            'rotation': {'x': 0, 'y': 0, 'z': 0}
        }

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_robot(img, robot_metadata=robot_metadata)
        agent_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # agent_img.save(
        #     os.path.join(resources_path, 'plotter_agent_front.png')
        # )

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_agent_front.png')
        )
        # calculate image difference
        diff = ImageChops.difference(agent_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_agent_facing_left(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        robot_metadata = {
            'position': {'x': 1, 'y': 0, 'z': 2},
            'rotation': {'x': 0, 'y': -90, 'z': 0}
        }

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_robot(img, robot_metadata=robot_metadata)
        agent_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # agent_img.save(
        #     os.path.join(resources_path, 'plotter_agent_left.png')
        # )

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_agent_left.png')
        )
        # calculate image difference
        diff = ImageChops.difference(agent_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_goal_object(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=True,
            uuid='1',
            color='green',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': 1, 'y': 0, 'z': 1},
                {'x': 2, 'y': 0, 'z': 1},
                {'x': 2, 'y': 0, 'z': 2},
                {'x': 1, 'y': 0, 'z': 2},
                {'x': 1, 'y': 0.22, 'z': 1},
                {'x': 2, 'y': 0.22, 'z': 1},
                {'x': 2, 'y': 0.22, 'z': 2},
                {'x': 1, 'y': 0.22, 'z': 2}
            ]]))

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_goal(img, obj)
        goal_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # goal_img.save(os.path.join(resources_path, 'plotter_goal.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_goal.png'))
        # calculate image difference
        diff = ImageChops.difference(goal_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_goal_object_greyscale(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=True,
            uuid='1',
            color='white',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': -1, 'y': 0, 'z': -1},
                {'x': -1.5, 'y': 0, 'z': -1},
                {'x': -1.5, 'y': 0, 'z': -1.5},
                {'x': -1, 'y': 0, 'z': -1.5},
                {'x': -1, 'y': 0.22, 'z': -1},
                {'x': -1.5, 'y': 0.22, 'z': -1},
                {'x': -1.5, 'y': 0.22, 'z': -1.5},
                {'x': -1, 'y': 0.22, 'z': -1.5}
            ]]))

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_goal(img, obj)
        goal_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # goal_img.save(os.path.join(resources_path, 'plotter_goal_white.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_goal_white.png')
        )
        # calculate image difference
        diff = ImageChops.difference(goal_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_goal_object_angled(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=True,
            uuid='1',
            color='blue',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': 0.5, 'y': 0, 'z': 0},
                {'x': 0, 'y': 0, 'z': -0.5},
                {'x': -0.5, 'y': 0, 'z': 0},
                {'x': 0, 'y': 0, 'z': 0.5},
                {'x': 0.5, 'y': 0.22, 'z': 0},
                {'x': 0, 'y': 0.22, 'z': -0.5},
                {'x': -0.5, 'y': 0.22, 'z': 0},
                {'x': 0, 'y': 0.22, 'z': 0.5}
            ]]))

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_goal(img, obj)
        goal_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # goal_img.save(os.path.join(resources_path, 'plotter_goal_angle.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_goal_angle.png')
        )
        # calculate image difference
        diff = ImageChops.difference(goal_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_goal_object_hidden(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=False,
            uuid='1',
            color='blue',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': 0.5, 'y': 0, 'z': 0},
                {'x': 0, 'y': 0, 'z': -0.5},
                {'x': -0.5, 'y': 0, 'z': 0},
                {'x': 0, 'y': 0, 'z': 0.5},
                {'x': 0.5, 'y': 0.22, 'z': 0},
                {'x': 0, 'y': 0.22, 'z': -0.5},
                {'x': -0.5, 'y': 0.22, 'z': 0},
                {'x': 0, 'y': 0.22, 'z': 0.5}
            ]]))

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_goal(img, obj)
        goal_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # goal_img.save(
        #     os.path.join(resources_path, 'plotter_goal_hidden.png')
        # )

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_goal_hidden.png')
        )
        # calculate image difference
        diff = ImageChops.difference(goal_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_visible_object(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=True,
            uuid='1',
            color='blue',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': 1, 'y': 0, 'z': 1},
                {'x': 2, 'y': 0, 'z': 1},
                {'x': 2, 'y': 0, 'z': 2},
                {'x': 1, 'y': 0, 'z': 2},
                {'x': 1, 'y': 0.22, 'z': 1},
                {'x': 2, 'y': 0.22, 'z': 1},
                {'x': 2, 'y': 0.22, 'z': 2},
                {'x': 1, 'y': 0.22, 'z': 2}
            ]]))

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_object(img, obj)
        visible_object_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # visible_object_img.save(os.path.join(
        #     resources_path,
        #     'plotter_visible_object.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_visible_object.png'))
        # calculate image difference
        diff = ImageChops.difference(visible_object_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_visible_object_angled(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=True,
            uuid='1',
            color='brown',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': 2, 'y': 0, 'z': 1},
                {'x': -1, 'y': 0, 'z': -2},
                {'x': -2, 'y': 0, 'z': -1},
                {'x': 1, 'y': 0, 'z': 2},
                {'x': 2, 'y': 0.22, 'z': 1},
                {'x': -1, 'y': 0.22, 'z': -2},
                {'x': -2, 'y': 0.22, 'z': -1},
                {'x': 1, 'y': 0.22, 'z': 2}
            ]]))

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_object(img, obj)
        visible_object_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # visible_object_img.save(
        #     os.path.join(resources_path, 'plotter_visible_object_angle.png')
        # )

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_visible_object_angle.png')
        )
        # calculate image difference
        diff = ImageChops.difference(visible_object_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_hidden_object(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=False,
            uuid='1',
            color='yellow',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': 1, 'y': 0, 'z': 1},
                {'x': 2, 'y': 0, 'z': 1},
                {'x': 2, 'y': 0, 'z': 2},
                {'x': 1, 'y': 0, 'z': 2},
                {'x': 1, 'y': 0.22, 'z': 1},
                {'x': 2, 'y': 0.22, 'z': 1},
                {'x': 2, 'y': 0.22, 'z': 2},
                {'x': 1, 'y': 0.22, 'z': 2}
            ]]))

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_object(img, obj)
        hidden_object_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # hidden_object_img.save(os.path.join(
        #     resources_path,
        #     'plotter_hidden_object.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_hidden_object.png'))
        # calculate image difference
        diff = ImageChops.difference(hidden_object_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_hidden_object_angled(self):
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal={},
            room_dimensions=Vector3d(x=10, y=3, z=10),
            lava=[]
        )
        obj = SceneAsset(
            held=False,
            visible=False,
            uuid='1',
            color='brown',
            bounds=SceneBounds([SceneCoord(**pt) for pt in [
                {'x': 2, 'y': 0, 'z': 1},
                {'x': -1, 'y': 0, 'z': -2},
                {'x': -2, 'y': 0, 'z': -1},
                {'x': 1, 'y': 0, 'z': 2},
                {'x': 2, 'y': 0.22, 'z': 1},
                {'x': -1, 'y': 0.22, 'z': -2},
                {'x': -2, 'y': 0.22, 'z': -1},
                {'x': 1, 'y': 0.22, 'z': 2}
            ]]))

        plotter = TopDownPlotter(team="test", scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_object(img, obj)
        hidden_object_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # hidden_object_img.save(
        #     os.path.join(resources_path, 'plotter_hidden_object_angle.png')
        # )

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(resources_path, 'plotter_hidden_object_angle.png')
        )
        # calculate image difference
        diff = ImageChops.difference(hidden_object_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_ramp_arrow(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=10),
            lava=[]
        )
        bounds = SceneBounds([SceneCoord(**pt) for pt in [
            {'x': 1.5, 'y': 0, 'z': 2},
            {'x': 2.5, 'y': 0, 'z': 2},
            {'x': 2.5, 'y': 0, 'z': -2},
            {'x': 1.5, 'y': 0, 'z': -2},
            {'x': 1.5, 'y': 2, 'z': 2},
            {'x': 2.5, 'y': 2, 'z': 2},
            {'x': 2.5, 'y': 2, 'z': -2},
            {'x': 1.5, 'y': 2, 'z': -2}
        ]])

        ramp = SceneAsset(
            held=False,
            visible=True,
            uuid='ramp-1',
            color='yellow',
            bounds=bounds
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_object(img, ramp)
        ramp_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # ramp_img.save(os.path.join(
        #     resources_path,
        #     'plotter_ramp.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_ramp.png'))
        # calculate image difference
        diff = ImageChops.difference(ramp_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_draw_hidden_ramp_arrow(self):
        goal = {'metadata': {
            'target': {'image': [0]},
            'target_1': {'image': [1]},
            'target_2': {'image': [2]}
        }}
        scene_config = SceneConfiguration(
            name="testscene",
            version=1,
            goal=goal,
            room_dimensions=Vector3d(
                x=10,
                y=3,
                z=10),
            lava=[]
        )
        bounds = SceneBounds([SceneCoord(**pt) for pt in [
            {'x': 1.5, 'y': 0, 'z': 2},
            {'x': 2.5, 'y': 0, 'z': 2},
            {'x': 2.5, 'y': 0, 'z': -2},
            {'x': 1.5, 'y': 0, 'z': -2},
            {'x': 1.5, 'y': 2, 'z': 2},
            {'x': 2.5, 'y': 2, 'z': 2},
            {'x': 2.5, 'y': 2, 'z': -2},
            {'x': 1.5, 'y': 2, 'z': -2}
        ]])

        ramp = SceneAsset(
            held=False,
            visible=False,
            uuid='ramp-1',
            color='yellow',
            bounds=bounds
        )

        plotter = TopDownPlotter(
            team="test",
            scene_config=scene_config)
        img = plotter.base_room_img.copy()
        img = plotter._draw_object(img, ramp)
        ramp_img = plotter._export_plot(img)
        # save image to resources folder in the event of plotter changes
        # ramp_img.save(os.path.join(
        #     resources_path,
        #     'plotter_ramp_hidden.png'))

        # read image from resources folder
        truth_img = Image.open(
            os.path.join(
                resources_path,
                'plotter_ramp_hidden.png'))
        # calculate image difference
        diff = ImageChops.difference(ramp_img, truth_img)
        stat = ImageStat.Stat(diff)
        self.assertListEqual(stat.sum, [0.0, 0.0, 0.0])

    def test_find_opposite_color(self):
        color = self.plotter._find_opposite_color((0, 128, 255))
        self.assertTupleEqual(color, (255, 127, 0))


if __name__ == '__main__':
    unittest.main()
