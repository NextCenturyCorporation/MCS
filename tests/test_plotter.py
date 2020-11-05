import unittest
import ai2thor
import PIL

from machine_common_sense.plotter import TopDownPlotter, XZHeading


class Test_TopDownPlotter(unittest.TestCase):

    PLOT_WIDTH = 600
    PLOT_HEIGHT = 400

    def setUp(self):
        self.plotter = TopDownPlotter(
            team="test",
            scene_name="scene",
            plot_width=self.PLOT_WIDTH,
            plot_height=self.PLOT_HEIGHT
        )

    def test_convert_color_empty(self):
        color = self.plotter._convert_color('')
        self.assertEqual(color, "xkcd:black")

    def test_convert_color_none(self):
        color = self.plotter._convert_color(None)
        self.assertEqual(color, "xkcd:black")

    def test_convert_color_white(self):
        color = self.plotter._convert_color('white')
        self.assertEqual(color, "xkcd:ivory")

    def test_convert_color(self):
        color = self.plotter._convert_color('red')
        self.assertEqual(color, "xkcd:red")

    def test_convert_color_xkcd_prefix(self):
        color = self.plotter._convert_color('red')
        self.assertTrue(color.startswith('xkcd:'))

    def test_plot_image_size(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [],
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
        self.assertEqual(img.width, self.PLOT_WIDTH)
        self.assertEqual(img.height, self.PLOT_HEIGHT)

    def test_plot_twice(self):
        metadata = {
            'screenWidth': 600,
            'screenHeight': 400,
            'objects': [],
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

    def test_create_agent(self):
        agent_metadata = {
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
        agent = self.plotter._create_agent(agent_metadata)

        self.assertAlmostEqual(agent.x, 2.70)
        self.assertAlmostEqual(agent.y, 1.23)
        self.assertAlmostEqual(agent.z, 3.14)
        self.assertAlmostEqual(agent.rotation, 78.0)

    def test_create_agent_missing_position(self):
        agent_metadata = {
            'rotation': {
                'x': 0.0,
                'y': 78.0,
                'z': 0.0
            }
        }
        agent = self.plotter._create_agent(agent_metadata)

        self.assertAlmostEqual(agent.x, 0.0)
        self.assertAlmostEqual(agent.y, 0.0)
        self.assertAlmostEqual(agent.z, 0.0)
        self.assertAlmostEqual(agent.rotation, 78.0)

    def test_create_agent_missing_rotation(self):
        agent_metadata = {
            'position': {
                'x': 2.70,
                'y': 1.23,
                'z': 3.14
            }
        }
        agent = self.plotter._create_agent(agent_metadata)

        self.assertAlmostEqual(agent.x, 2.70)
        self.assertAlmostEqual(agent.y, 1.23)
        self.assertAlmostEqual(agent.z, 3.14)
        self.assertAlmostEqual(agent.rotation, 0.0)

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
        self.assertEqual(obj.color, "xkcd:orange")

    def test_create_object_empty(self):
        object_metadata = {}
        obj = self.plotter._create_object(object_metadata)

        self.assertIsNone(obj.held)
        self.assertIsNone(obj.visible)
        self.assertIsNone(obj.uuid)
        self.assertIsNone(obj.bounds)
        self.assertEqual(obj.color, "xkcd:black")
