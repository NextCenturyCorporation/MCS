import math
from dataclasses import dataclass
from typing import Dict, List

import ai2thor.server
import colour
import cv2
import numpy as np
import PIL.Image
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

    DEFAULT_COLOR = colour.COLOR_NAME_TO_RGB['white']
    BACKGROUND_COLOR = colour.COLOR_NAME_TO_RGB['black']
    BORDER_COLOR = colour.COLOR_NAME_TO_RGB['white']
    CENTER_COLOR = colour.COLOR_NAME_TO_RGB['gray']
    GRID_COLOR = colour.COLOR_NAME_TO_RGB['darkslategray']
    ROBOT_COLOR = colour.COLOR_NAME_TO_RGB['red']
    GOAL_COLOR = colour.COLOR_NAME_TO_RGB['gold']

    ROBOT_PLOT_WIDTH = 0.2
    HEADING_LENGTH = 0.2
    ROBOT_NOSE_RADIUS = 0.08
    PLOT_IMAGE_SIZE = 512

    FONT = cv2.FONT_HERSHEY_COMPLEX
    FONT_SCALE = 0.4
    FONT_THICKNESS = 1
    WALL_BUFFER = 50

    def __init__(self, team: str, scene_name: str, room_size: Vector3d):
        self._team = team
        if '/' in scene_name:
            scene_name = scene_name.rsplit('/', 1)[1]
        self._scene_name = scene_name
        self._room_size = room_size
        # create the room once as it is computationally expensive
        self.grid_img = self._initialize_plot()

    def plot(self, scene_event: ai2thor.server.Event,
             step_number: int,
             goal_id: str = None
             ) -> PIL.Image.Image:
        '''Create a plot of the room, objects and robot'''
        plt_img = self.grid_img.copy()
        plt_objects = self._find_plottable_objects(scene_event)
        plt_img = self._draw_objects(plt_img,
                                     plt_objects,
                                     goal_id)
        agent_metadata = scene_event.metadata.get('agent', None)
        plt_img = self._draw_robot(
            plt_img,
            agent_metadata)
        plt_img = self._draw_step_number(plt_img, step_number)
        return self._export_plot(img=plt_img)

    def _initialize_plot(self) -> np.ndarray:
        '''Create the initial plot with grid lines'''
        img = np.zeros(
            (self.PLOT_IMAGE_SIZE, self.PLOT_IMAGE_SIZE, 3),
            dtype=np.int8)
        return self._draw_grid_lines(img)

    def _draw_step_number(self, img: np.ndarray,
                          step_number: int) -> np.ndarray:
        '''Write the step number on the plot image'''
        (label_width, label_height), baseline = cv2.getTextSize(
            str(step_number), self.FONT, self.FONT_SCALE, self.FONT_THICKNESS)
        text_draw_buffer = 5
        cv2.putText(
            img=img,
            text=str(step_number),
            org=(img.shape[0] - label_width - text_draw_buffer,
                 label_height + baseline),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=self.FONT_SCALE,
            color=self.BORDER_COLOR,
            lineType=self.FONT_THICKNESS)
        return img

    def _draw_grid_lines(self, img: np.ndarray) -> np.ndarray:
        '''Draw room coordinate grid aligned with Unity units'''
        room_x, room_z = self._room_size.x, self._room_size.z
        # treating y image dimension as z since this is an XZ planar plot
        x_dim, z_dim, _ = img.shape
        self.center_x = int(x_dim / 2) - 1  # ex: 512 /2 = 256 - 1 = 255
        self.center_z = int(z_dim / 2) - 1  # ex: 256 /2 = 128 - 1 = 127
        largest_dimension = max(room_x, room_z)

        # Add a buffer into the scale to properly show the room's walls.
        buffered_x_dim = x_dim - self.WALL_BUFFER
        buffered_z_dim = z_dim - self.WALL_BUFFER
        self.x_scale = (buffered_x_dim) / largest_dimension
        self.z_scale = (buffered_z_dim) / largest_dimension

        # outer buffer space to keep 1:1 aspect ratio
        buffer_x = (x_dim - (buffered_x_dim * room_x / largest_dimension)) / 2
        buffer_z = (z_dim - (buffered_z_dim * room_z / largest_dimension)) / 2

        img = self._draw_vertical_grid_lines(img, buffer_z)
        img = self._draw_horizontal_grid_lines(img, buffer_x)
        img = self._draw_room_border(img, buffer_x, buffer_z)

        return img

    def _draw_vertical_grid_lines(
            self, img: np.ndarray, buffer_z: int) -> np.ndarray:
        x_units = math.floor(self._room_size.x / 2)
        for x in range(x_units + 1):
            img_x = int(self.center_x + x * self.x_scale)
            rr, cc = skimage.draw.line(
                c0=img_x,
                r0=int(buffer_z),
                c1=img_x,
                r1=img.shape[0] - 1 - int(buffer_z))
            img[rr, cc] = self.CENTER_COLOR if x == 0 else self.GRID_COLOR

            img_x = int(self.center_x - x * self.x_scale)
            rr, cc = skimage.draw.line(
                c0=img_x,
                r0=int(buffer_z),
                c1=img_x,
                r1=img.shape[0] - 1 - int(buffer_z))
            img[rr, cc] = self.CENTER_COLOR if x == 0 else self.GRID_COLOR
        return img

    def _draw_horizontal_grid_lines(
            self, img: np.ndarray, buffer_x: int) -> np.ndarray:
        z_units = math.floor(self._room_size.z / 2)
        for z in range(z_units + 1):
            img_z = int(self.center_z + z * self.z_scale)
            rr, cc = skimage.draw.line(
                c0=int(buffer_x),
                r0=img_z,
                c1=img.shape[1] - 1 - int(buffer_x),
                r1=img_z)
            img[rr, cc] = self.CENTER_COLOR if z == 0 else self.GRID_COLOR

            img_z = int(self.center_z - z * self.z_scale)
            rr, cc = skimage.draw.line(
                c0=int(buffer_x),
                r0=img_z,
                c1=img.shape[1] - 1 - int(buffer_x),
                r1=img_z)
            img[rr, cc] = self.CENTER_COLOR if z == 0 else self.GRID_COLOR
        return img

    def _draw_room_border(self, img: np.ndarray,
                          buffer_x: int, buffer_z: int) -> np.ndarray:
        x_dim, z_dim, _ = img.shape
        rr, cc = skimage.draw.rectangle_perimeter(
            start=(buffer_z, buffer_x),
            end=(z_dim - buffer_z - 1, x_dim - buffer_x - 1),
            shape=img.shape[:2],
            clip=True)
        img[rr, cc] = self.BORDER_COLOR
        return img

    def _export_plot(self, img: np.ndarray) -> PIL.Image.Image:
        '''Export the plot to a PIL Image'''
        return PIL.Image.fromarray(img, "RGB")

    def _draw_robot(self, img: np.ndarray, robot_metadata: Dict) -> np.ndarray:
        '''Plot the robot position and heading'''
        if robot_metadata is None:
            return None
        robot = self._create_robot(robot_metadata)
        img = self._draw_robot_position(img, robot)
        img = self._draw_robot_heading(img, robot)
        return img

    def _draw_robot_position(self, img: np.ndarray,
                             robot: Robot) -> np.ndarray:
        '''Draw the robot's scene XZ position in the plot'''
        rr, cc = skimage.draw.disk(
            center=(
                self.center_z - robot.z * self.z_scale,
                self.center_x + robot.x * self.x_scale),
            radius=self.ROBOT_PLOT_WIDTH * self.x_scale,
            shape=img.shape[:2])
        img[rr, cc] = self.ROBOT_COLOR
        return img

    def _draw_robot_heading(self, img: np.ndarray, robot: Robot) -> np.ndarray:
        '''Draw the heading vector starting from the robot XZ position'''
        heading = self._calculate_heading(
            rotation_angle=360.0 - robot.rotation,
            heading_length=self.HEADING_LENGTH
        )
        z_point = int(self.center_z - robot.z * self.z_scale)
        x_point = int(self.center_x + robot.x * self.x_scale)
        rr, cc = skimage.draw.disk(
            center=(
                z_point - int(heading.z * self.x_scale),
                x_point + int(heading.x * self.x_scale)
            ),
            radius=self.ROBOT_NOSE_RADIUS * self.x_scale,
            shape=img.shape[:2]
        )
        img[rr, cc] = self.ROBOT_COLOR
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

    def _draw_objects(self, img: np.ndarray, objects: Dict,
                      goal_id: str = None) -> np.ndarray:
        '''Plot the object bounds for each object in the scene'''
        for o in objects:
            obj = self._create_object(o)
            if obj.bounds is not None:
                obj_pts = [(pt['x'], pt['z']) for pt in obj.bounds]
                polygon = geometry.MultiPoint(
                    obj_pts).convex_hull
                pts = polygon.exterior.coords
                img = self._draw_object_bounds(img, obj, pts)
                if goal_id is not None and o['objectId'] == goal_id:
                    img = self._draw_goal(img, pts)
        return img

    def _draw_goal(self, img: np.ndarray,
                   pts: List) -> np.ndarray:
        '''Draw the goal object of the scene'''
        cs, rs = map(list, zip(*pts))
        rr, cc = skimage.draw.polygon_perimeter(
            rs,
            cs,
            shape=img.shape[:2])
        img[rr, cc] = self.GOAL_COLOR
        return img

    def _draw_object_bounds(self, img: np.ndarray,
                            obj: Object, points: List) -> np.ndarray:
        '''Draw the scene object'''
        # convert list of tuples to list of rows and list of columns
        cs, rs = map(list, zip(*points))
        # convert room coordinates to image coordinates
        rs = list(map(lambda r: self.center_z - r * self.z_scale, rs))
        cs = list(map(lambda c: self.center_x + c * self.x_scale, cs))
        # use dictionary get method for color retrieval
        # if no match, then None will resort to default color
        clr = colour.COLOR_NAME_TO_RGB.get(obj.color.lower())

        # draw filled polygon if visible to the robot
        if(obj.visible):
            rr, cc = skimage.draw.polygon(
                rs,
                cs,
                shape=img.shape[:2])
        else:
            rr, cc = skimage.draw.polygon_perimeter(
                rs,
                cs,
                shape=img.shape[:2])
        img[rr, cc] = clr
        return img

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
        '''Convert color string to string'''
        if not color:
            color = 'ivory'

        if color == 'black':
            color = 'ivory'
        return color
