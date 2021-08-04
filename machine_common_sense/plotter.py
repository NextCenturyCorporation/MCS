import math
from dataclasses import dataclass
from typing import Dict, List

import ai2thor.server
import colour
import numpy as np
import PIL.Image
import skimage
import skimage.draw
from shapely import geometry

from machine_common_sense.config_manager import Vector3d


@dataclass
class XZHeading():
    x: float
    z: float


@dataclass
class Robot():
    x: float
    y: float
    z: float
    rotation: float


@dataclass
class Object():
    held: bool
    visible: bool
    uuid: str
    color: str
    bounds: list


class TopDownPlotter():

    BORDER_COLOR = colour.COLOR_NAME_TO_RGB['white']
    CENTER_COLOR = colour.COLOR_NAME_TO_RGB['gray']
    GRID_COLOR = colour.COLOR_NAME_TO_RGB['darkslategray']

    ROBOT_PLOT_WIDTH = 0.2
    ROBOT_COLOR = colour.COLOR_NAME_TO_RGB['red']
    DEFAULT_COLOR = colour.COLOR_NAME_TO_RGB['white']
    HEADING_LENGTH = 0.4

    def __init__(self, team: str, scene_name: str, room_size: Vector3d):
        self._team = team
        if '/' in scene_name:
            scene_name = scene_name.rsplit('/', 1)[1]
        self._scene_name = scene_name
        self._room_size = room_size
        # TODO should plot size come from config?

    def plot(self, scene_event: ai2thor.server.Event,
             step_number: int,
             goal_id: str = None
             ) -> PIL.Image.Image:
        self.plt_img = self._initialize_plot()
        self._draw_objects(self._find_plottable_objects(scene_event), goal_id)
        self._draw_robot(scene_event.metadata.get('agent', None))
        return self._export_plot(plt=self.plt_img)

    def _initialize_plot(self) -> np.ndarray:
        '''Create the plot'''
        # TODO image/video dimensions should be exposed via config
        img_size = 256
        img = np.zeros((img_size, img_size, 3), dtype=np.int8)
        self._draw_grid_lines(img)
        return img

    def _draw_grid_lines(self, plt_img: np.ndarray) -> None:
        room_x, room_z = self._room_size.x, self._room_size.z
        # treating y image dimension as z since this is an XZ planar plot
        x_dim, z_dim, _ = plt_img.shape
        self.center_x = int(x_dim / 2) - 1  # ex: 512 /2 = 256 - 1 = 255
        self.center_z = int(z_dim / 2) - 1  # ex: 256 /2 = 128 - 1 = 127
        largest_dimension = max(room_x, room_z)
        # TODO rename to x_scale and z_scale
        self.xs = (x_dim - 1) / largest_dimension
        self.zs = (z_dim - 1) / largest_dimension

        # outer buffer space to keep 1:1 aspect ratio
        buffer_x = (x_dim - (x_dim * room_x / largest_dimension)) / 2
        buffer_z = (z_dim - (z_dim * room_z / largest_dimension)) / 2

        # TODO break out to function
        x_units = math.floor(self._room_size.x / 2)
        for x in range(x_units + 1):
            img_x = int(self.center_x + x * self.xs)
            rr, cc = skimage.draw.line(
                c0=img_x,
                r0=int(buffer_z),
                c1=img_x,
                r1=plt_img.shape[0] - 1 - int(buffer_z))
            plt_img[rr, cc] = self.CENTER_COLOR if x == 0 else self.GRID_COLOR

            img_x = int(self.center_x - x * self.xs)
            rr, cc = skimage.draw.line(
                c0=img_x,
                r0=int(buffer_z),
                c1=img_x,
                r1=plt_img.shape[0] - 1 - int(buffer_z))
            plt_img[rr, cc] = self.CENTER_COLOR if x == 0 else self.GRID_COLOR

        # TODO break out to function
        z_units = math.floor(self._room_size.z / 2)
        for z in range(z_units + 1):
            img_z = int(self.center_z + z * self.zs)
            rr, cc = skimage.draw.line(
                c0=int(buffer_x),
                r0=img_z,
                c1=plt_img.shape[1] - 1 - int(buffer_x),
                r1=img_z)
            plt_img[rr, cc] = self.CENTER_COLOR if z == 0 else self.GRID_COLOR

            img_z = int(self.center_z - z * self.zs)
            rr, cc = skimage.draw.line(
                c0=int(buffer_x),
                r0=img_z,
                c1=plt_img.shape[1] - 1 - int(buffer_x),
                r1=img_z)
            plt_img[rr, cc] = self.CENTER_COLOR if z == 0 else self.GRID_COLOR

        # TODO break out to function
        # draw outside border
        rr, cc = skimage.draw.rectangle_perimeter(
            start=(buffer_z, buffer_x),
            end=(z_dim - buffer_z - 1, x_dim - buffer_x - 1),
            shape=plt_img.shape[:2],
            clip=True)
        plt_img[rr, cc] = self.BORDER_COLOR

    def _export_plot(self, plt: np.ndarray) -> PIL.Image.Image:
        '''Export the plot to a PIL Image'''
        # TODO rename plt which has matplotlib implications
        return PIL.Image.fromarray(plt, "RGB")

    def _draw_robot(self, robot_metadata: Dict) -> None:
        '''Plot the robot position and heading'''
        if robot_metadata is None:
            return None
        robot = self._create_robot(robot_metadata)
        self._draw_robot_position(robot)
        self._draw_robot_heading(robot)

    def _draw_robot_position(self, robot: Robot) -> None:
        '''Draw the robot's scene XZ position in the plot'''
        rr, cc = skimage.draw.disk(
            center=(
                self.center_z - robot.z * self.zs,
                self.center_x + robot.x * self.xs),
            radius=self.ROBOT_PLOT_WIDTH * self.xs,
            shape=self.plt_img.shape[:2])
        self.plt_img[rr, cc] = self.ROBOT_COLOR

    def _draw_robot_heading(self, robot: Robot) -> None:
        '''Draw the heading vector starting from the robot XZ position'''
        heading = self._calculate_heading(
            rotation_angle=360.0 - robot.rotation,
            heading_length=self.HEADING_LENGTH
        )
        rr, cc = skimage.draw.line(
            int(self.center_z - robot.z * self.zs),
            int(self.center_x + robot.x * self.xs),
            int(self.center_z - robot.z * self.zs - heading.z * self.xs),
            int(self.center_x + robot.x * self.xs + heading.x * self.xs))
        self.plt_img[rr, cc] = self.ROBOT_COLOR

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

    def _draw_objects(self, objects: Dict,
                      goal_id: str = None) -> None:
        '''Plot the object bounds for each object in the scene'''
        for o in objects:
            obj = self._create_object(o)
            if obj.bounds is not None:
                obj_pts = [(pt['x'], pt['z']) for pt in obj.bounds]
                polygon = geometry.MultiPoint(
                    obj_pts).convex_hull
                pts = polygon.exterior.coords
                self._draw_object_bounds(obj, pts)
                if goal_id is not None and o['objectId'] == goal_id:
                    self._draw_goal(o['position'])

    def _draw_goal(self, position: Object) -> None:
        '''Draw the goal object of the scene'''
        # plt.scatter(
        #     position['x'],
        #     position['z'],
        #     c=self._convert_color("gold"),
        #     s=300,
        #     marker="*",
        #     zorder=5,
        #     alpha=.7,
        #     edgecolors=self._convert_color("black"),
        #     linewidths=.5
        # )
        pass

    def _draw_object_bounds(self, obj: Object, points: List) -> None:
        '''Draw the scene object'''
        # convert list of tuples to list of rows and list of columns
        cs, rs = map(list, zip(*points))
        # convert room coordinates to image coordinates
        rs = list(map(lambda r: self.center_z - r * self.zs, rs))
        cs = list(map(lambda c: self.center_x + c * self.xs, cs))
        clr = colour.COLOR_NAME_TO_RGB[obj.color.lower()]

        if(obj.visible):
            rr, cc = skimage.draw.polygon(
                rs,
                cs,
                shape=self.plt_img.shape[:2])
            self.plt_img[rr, cc] = clr
            rr, cc = skimage.draw.polygon_perimeter(
                rs,
                cs,
                shape=self.plt_img.shape[:2])
            self.plt_img[rr, cc] = self.BORDER_COLOR
        else:
            rr, cc = skimage.draw.polygon_perimeter(
                rs,
                cs,
                shape=self.plt_img.shape[:2])
            self.plt_img[rr, cc] = clr

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

    # TODO is this function needed?
    def _convert_color(self, color: str) -> str:
        '''Convert color string to string'''
        # use default if no color present
        if not color:
            color = 'ivory'

        if color == 'black':
            color = 'ivory'
        return color
