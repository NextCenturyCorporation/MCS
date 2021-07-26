import io
import math

import ai2thor
import matplotlib
import PIL

from machine_common_sense.config_manager import Vector3d

matplotlib.use('Agg')
from typing import Dict, List, NamedTuple

import matplotlib.pyplot as plt
from shapely import geometry


class XZHeading(NamedTuple):
    x: float
    z: float


class Robot(NamedTuple):
    x: float
    y: float
    z: float
    rotation: float


class Object(NamedTuple):
    held: bool
    visible: bool
    uuid: str
    color: str
    bounds: list


class TopDownPlotter():

    ROBOT_PLOT_WIDTH = 0.2
    ROBOT_PLOT_LABEL = "robot"
    ROBOT_COLOR = 'xkcd:gray'
    DEFAULT_COLOR = "xkcd:black"
    HEADING_LENGTH = 0.4
    BORDER = 0.05

    def __init__(self, team: str, scene_name: str, room_size: Vector3d):
        self._team = team
        if '/' in scene_name:
            scene_name = scene_name.rsplit('/', 1)[1]
        self._scene_name = scene_name
        self._room_size = room_size

    def plot(self, scene_event: ai2thor.server.Event,
             step_number: int,
             goal_id: str = None
             ) -> PIL.Image.Image:

        plt = self._initialize_plot(step_number=step_number)
        self._draw_objects(self._find_plottable_objects(scene_event), goal_id)
        self._draw_robot(scene_event.metadata.get('agent'))
        img = self._export_plot(plt)
        plt.close()
        return img

    def _find_plottable_objects(
            self, scene_event: ai2thor.server.Event) -> List:
        '''Find plottable objects from the scene data.

        Plottable objects include normal scene objects as well as
        occluder and wall structural objects.
        '''
        structural_objects = scene_event.metadata.get('structuralObjects', [])
        filtered_structural_objects = [
            obj for obj in structural_objects
            if not obj.get('objectId', '').startswith('ceiling') and not
            obj.get('objectId', '').startswith('floor')
        ]
        objects = scene_event.metadata.get('objects', [])
        return filtered_structural_objects + objects

    def _initialize_plot(self, step_number: int) -> None:
        '''Create the plot'''
        # plot the xz topdown plane in xy plot coordinates
        x_half_size = self._room_size.x / 2.0
        z_half_size = self._room_size.z / 2.0
        plt.axis('scaled')
        plt.xlim(-x_half_size, x_half_size)
        plt.ylim(-z_half_size, z_half_size)
        plt.text(
            x_half_size + self.BORDER,
            -z_half_size + self.BORDER,
            step_number)
        plt.title(f"{self._team} {self._scene_name}")
        return plt

    def _export_plot(self, plt: matplotlib.pyplot) -> PIL.Image.Image:
        '''Export the plot to a PIL Image'''
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        return PIL.Image.open(buf)

    def _draw_robot(self, robot_metadata: Dict) -> None:
        '''Plot the robot position and heading'''
        if robot_metadata is None:
            return None
        robot = self._create_robot(robot_metadata)
        self._draw_robot_position(robot)
        self._draw_robot_heading(robot)

    def _draw_robot_position(self, robot: Robot) -> None:
        '''Draw the robot's scene XZ position in the plot'''
        circle = plt.Circle(
            (robot.x, robot.z),
            radius=self.ROBOT_PLOT_WIDTH,
            color=self.ROBOT_COLOR,
            label=self.ROBOT_PLOT_LABEL)
        plt.gca().add_patch(circle)

    def _draw_robot_heading(self, robot: Robot) -> None:
        '''Draw the heading vector starting from the robot XZ position'''
        heading = self._calculate_heading(
            rotation_angle=360.0 - robot.rotation,
            heading_length=self.HEADING_LENGTH
        )
        heading = plt.Line2D((robot.x, robot.x + heading.x),
                             (robot.z, robot.z + heading.z),
                             color=self.ROBOT_COLOR,
                             lw=1)
        plt.gca().add_line(heading)

    def _draw_objects(self, objects: Dict,
                      goal_id: str = None) -> None:
        '''Plot the object bounds for each object in the scene'''
        for o in objects:
            obj = self._create_object(o)
            if obj.bounds is not None:
                obj_pts = [(pt['x'], pt['z']) for pt in obj.bounds]
                polygon = geometry.MultiPoint(obj_pts).convex_hull
                pts = polygon.exterior.coords
                self._draw_object_bounds(obj, pts)
                if goal_id is not None and o['objectId'] == goal_id:
                    self._draw_goal(o['position'])

    def _draw_goal(self, position: Object) -> None:
        '''Draw the goal object of the scene'''
        plt.scatter(
            position['x'],
            position['z'],
            c=self._convert_color("gold"),
            s=300,
            marker="*",
            zorder=5,
            alpha=.7,
            edgecolors=self._convert_color("black"),
            linewidths=.5
        )

    def _draw_object_bounds(self, obj: Object, points: List) -> None:
        '''Draw the scene object'''
        poly = plt.Polygon(points,
                           color=obj.color,
                           fill=obj.color if obj.visible or
                           obj.held else '',
                           ec=self.DEFAULT_COLOR,
                           label=obj.uuid)
        plt.gca().add_patch(poly)

    def _calculate_heading(self, rotation_angle: float,
                           heading_length: float) -> XZHeading:
        '''Calculate XZ heading vector from the rotation angle'''
        s = math.sin(math.radians(rotation_angle))
        c = math.cos(math.radians(rotation_angle))
        vec_x = 0 * c - heading_length * s
        vec_z = 0 * s + heading_length * c
        return XZHeading(vec_x, vec_z)

    def _create_robot(self, robot_metadata: Dict) -> Robot:
        '''Extract robot position and rotation information from the metadata'''
        position = robot_metadata.get('position')
        if position is not None:
            x = position.get('x')
            y = position.get('y')
            z = position.get('z')
        else:
            x = 0.0
            y = 0.0
            z = 0.0

        rotation = robot_metadata.get('rotation')
        rotation_y = rotation.get('y') if rotation is not None else 0.0
        return Robot(x, y, z, rotation_y)

    def _create_object(self, object_metadata: Dict) -> Object:
        '''Create the scene object from its metadata'''

        held = object_metadata.get('isPickedUp')
        visible = object_metadata.get('visibleInCamera')
        uuid = object_metadata.get('objectId')

        colors = object_metadata.get('colorsFromMaterials', [])
        if len(colors):
            color = self._convert_color(colors[0])
        else:
            color = self._convert_color('')

        bounds = object_metadata.get('objectBounds')
        corners = None if bounds is None else bounds.get('objectBoundsCorners')
        return Object(
            held=held,
            visible=visible,
            uuid=uuid,
            color=color,
            bounds=corners
        )

    def _convert_color(self, color: str) -> str:
        '''Convert color string to xkcd string'''
        # use default of black if no color present
        if not color:
            color = 'black'
        # white color does not show up in plot but ivory does
        if color == 'white':
            color = 'ivory'
        # prefix with xkcd string
        return 'xkcd:' + color
