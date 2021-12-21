from __future__ import annotations

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

from machine_common_sense.config_manager import (FloorTexturesConfig,
                                                 SceneConfiguration, Vector3d)


@dataclass
class SceneCoord():
    '''Unity scenes have floor dimensions of x and z'''
    x: int
    z: int

    def __sub__(self, coord: SceneCoord):
        return SceneCoord(self.x - coord.x, self.z - coord.z)

    def __add__(self, coord: SceneCoord):
        return SceneCoord(self.x + coord.x, self.z + coord.z)


@dataclass
class ImageCoord():
    '''Image xy coordinates where y corresponds to z in Unity'''
    x: int
    y: int


@dataclass
class XZHeading():
    '''Unity directional vector'''
    x: float
    z: float


@dataclass
class Robot():
    '''AI robot/performer location and heading in Unity'''
    x: float
    z: float
    heading: XZHeading


@dataclass
class Object():
    held: bool
    visible: bool
    uuid: str
    color: str
    bounds: list


@dataclass
class Texture():
    material: str
    positions: list


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
    UNIT_CELL_WIDTH = 1

    FONT = cv2.FONT_HERSHEY_COMPLEX
    FONT_SCALE = 0.4
    FONT_THICKNESS = 1
    WALL_BUFFER = 50

    def __init__(self, team: str, scene_config: SceneConfiguration) -> None:
        self._scene_name = scene_config.name.replace('json', '')
        if '/' in self._scene_name:
            self._scene_name = self._scene_name.rsplit('/', 1)[1]

        self._room_size = (
            # Room is automatically expanded in intuitive physics scenes.
            Vector3d(14, 10, 10) if scene_config.intuitive_physics
            else scene_config.room_dimensions
        )
        self._team = team
        # create the room once as it is computationally expensive
        self.base_room_img = self._initialize_plot(scene_config)

    def _initialize_plot(self, scene_config: SceneConfiguration) -> np.ndarray:
        '''Create the initial plot with grid lines'''
        img = np.zeros(
            (self.PLOT_IMAGE_SIZE, self.PLOT_IMAGE_SIZE, 3),
            dtype=np.int8)

        room = SceneCoord(
            x=self._room_size.x,
            z=self._room_size.z
        )
        largest_dimension = max(room.x, room.z)

        x_dim, y_dim, _ = img.shape
        self.image_center = ImageCoord(
            x=int(x_dim / 2) - 1,  # Ex. 512/2-1 = 255
            y=int(y_dim / 2) - 1
        )

        # determine the scale for each xy dimension
        self.scale = ImageCoord(
            x=(x_dim - self.WALL_BUFFER) / largest_dimension,
            y=(y_dim - self.WALL_BUFFER) / largest_dimension
        )

        # get the buffer for both x and y especially for non-square rooms
        buffer = ImageCoord(
            x=(x_dim - self.scale.x * room.x) / 2,
            y=(y_dim - self.scale.y * room.z) / 2
        )

        img = self._draw_grid_lines(img, buffer)
        img = self._draw_holes(
            img, scene_config.holes)
        img = self._draw_floor_textures(
            img,
            scene_config.floor_textures)

        return img

    def plot(self, scene_event: ai2thor.server.Event,
             step_number: int,
             goal_id: str = None
             ) -> PIL.Image.Image:
        '''Create a plot of the room, objects and robot'''
        plt_img = self.base_room_img.copy()

        plt_objects = self._find_plottable_objects(scene_event)
        plt_img = self._draw_objects(plt_img,
                                     plt_objects,
                                     goal_id)

        agent_metadata = scene_event.metadata.get('agent')
        plt_img = self._draw_robot(
            plt_img,
            agent_metadata)

        plt_img = self._draw_step_number(plt_img, step_number)
        return self._export_plot(img=plt_img)

    def _convert_to_image_coords(self, scene_pt: SceneCoord) -> ImageCoord:
        '''converts scene xz coordinate point to an xy image coordinate'''
        return ImageCoord(
            x=int(self.image_center.x + scene_pt.x * self.scale.x),
            y=int(self.image_center.y - scene_pt.z * self.scale.y)
        )

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

    def _draw_grid_lines(self, img: np.ndarray,
                         buffer: ImageCoord) -> np.ndarray:
        '''Draw room coordinate grid aligned with Unity units'''
        img = self._draw_vertical_grid_lines(img, buffer.y)
        img = self._draw_horizontal_grid_lines(img, buffer.x)
        return self._draw_room_border(img, buffer)

    def _draw_vertical_grid_lines(
            self, img: np.ndarray, buffer_y: int) -> np.ndarray:
        '''Draw vertical lines at each x-coordinate'''
        x_units = math.floor(self._room_size.x / 2)
        # draw vertical grid lines starting at the center and working out
        for x in range(x_units + 1):
            # positive x values
            img = self._draw_vertical_line(img, buffer_y, x)
            # negative x values
            img = self._draw_vertical_line(img, buffer_y, -x)
        return img

    def _draw_vertical_line(self, img: np.ndarray,
                            buffer_y: int, x_coord: int) -> np.ndarray:
        '''Draw a vertical grid line corresponding to the x-coordinate'''
        img_x = int(self.image_center.x + x_coord * self.scale.x)
        rr, cc = skimage.draw.line(
            c0=img_x,
            r0=int(buffer_y),
            c1=img_x,
            r1=img.shape[0] - 1 - int(buffer_y))
        img[rr, cc] = self.CENTER_COLOR if x_coord == 0 else self.GRID_COLOR
        return img

    def _draw_horizontal_grid_lines(
            self, img: np.ndarray, buffer_x: int) -> np.ndarray:
        '''Draw horizontal lines at each y-coordinate'''
        z_units = math.floor(self._room_size.z / 2)
        # draw horizontal grid lines starting at the center and working out
        for y in range(z_units + 1):
            img = self._draw_horizontal_line(img, buffer_x, y)
            img = self._draw_horizontal_line(img, buffer_x, -y)
        return img

    def _draw_horizontal_line(self, img: np.ndarray,
                              buffer_x: int, y_coord: int) -> np.ndarray:
        '''Draw a horizontal grid line corresponding to the y-coordinate'''
        img_y = int(self.image_center.y + y_coord * self.scale.y)
        rr, cc = skimage.draw.line(
            c0=int(buffer_x),
            r0=img_y,
            c1=img.shape[1] - 1 - int(buffer_x),
            r1=img_y)
        img[rr, cc] = self.CENTER_COLOR if y_coord == 0 else self.GRID_COLOR
        return img

    def _draw_room_border(self, img: np.ndarray,
                          buffer: ImageCoord) -> np.ndarray:
        '''Outline the room border'''
        x_dim, z_dim, _ = img.shape
        rr, cc = skimage.draw.rectangle_perimeter(
            start=(buffer.y, buffer.x),
            end=(z_dim - buffer.y - 1, x_dim - buffer.x - 1),
            shape=img.shape[:2],
            clip=True)
        img[rr, cc] = self.BORDER_COLOR
        return img

    def _draw_floor_textures(
        self,
        img: np.ndarray,
        floor_textures: List[FloorTexturesConfig]
    ) -> np.ndarray:
        if floor_textures is None:
            return img

        for floor_texture in floor_textures:
            # TODO MCS-1024 use floor_texture.material for color
            texture_color = colour.COLOR_NAME_TO_RGB['red']

            for position in floor_texture.positions:
                texture_pos = SceneCoord(x=position.x, z=position.z)
                half_cell_pos = SceneCoord(
                    self.UNIT_CELL_WIDTH / 2, self.UNIT_CELL_WIDTH / 2)
                tex_pos_ul = texture_pos - half_cell_pos
                tex_pos_lr = texture_pos + half_cell_pos
                tex_img_pos_ul = self._convert_to_image_coords(tex_pos_ul)
                tex_img_pos_lr = self._convert_to_image_coords(tex_pos_lr)
                img = self._draw_floor_texture(
                    img=img,
                    upper_left=tex_img_pos_ul,
                    lower_right=tex_img_pos_lr,
                    texture_color=texture_color)

        return img

    def _draw_floor_texture(self,
                            img: np.ndarray,
                            upper_left: ImageCoord,
                            lower_right: ImageCoord,
                            texture_color: colour.C_RGB) -> np.ndarray:
        rr, cc = skimage.draw.rectangle(
            start=(upper_left.y, upper_left.x),
            end=(lower_right.y, lower_right.x),
            shape=img.shape[:2])
        img[rr, cc] = texture_color
        return img

    def _draw_holes(self, img: np.ndarray, holes: List) -> np.ndarray:
        '''Draw a box with an X to illustrate a floor hole'''
        if holes is None:
            return img

        for hole in holes:
            hole_center = SceneCoord(x=hole.x, z=hole.z)
            half_cell_pos = SceneCoord(
                self.UNIT_CELL_WIDTH / 2,
                self.UNIT_CELL_WIDTH / 2)
            # calculate scene corners
            hole_upper_left: SceneCoord = hole_center - half_cell_pos
            hole_lower_right: SceneCoord = hole_center + half_cell_pos

            # convert scene corners to image coordinates
            hole_img_upper_left: ImageCoord = self._convert_to_image_coords(
                hole_upper_left)
            hole_img_lower_right: ImageCoord = self._convert_to_image_coords(
                hole_lower_right)

            img = self._draw_hole_perimeter(
                img, hole_img_upper_left, hole_img_lower_right)
            img = self._draw_hole_x(
                img, hole_img_upper_left, hole_img_lower_right)
        return img

    def _draw_hole_perimeter(
            self,
            img: np.ndarray,
            upper_left: ImageCoord,
            lower_right: ImageCoord) -> np.ndarray:
        '''Outline the floor hole'''
        rr, cc = skimage.draw.rectangle_perimeter(
            start=(upper_left.y, upper_left.x),
            end=(lower_right.y - 1, lower_right.x - 1),
            shape=img.shape[:2],
            clip=True)
        img[rr, cc] = self.DEFAULT_COLOR
        return img

    def _draw_hole_x(
            self,
            img: np.ndarray,
            upper_left: ImageCoord,
            lower_right: ImageCoord) -> np.ndarray:
        '''Draw an X through the hole cell'''
        rr, cc = skimage.draw.line(
            r0=upper_left.y,
            c0=upper_left.x,
            r1=lower_right.y,
            c1=lower_right.x)
        img[rr, cc] = self.DEFAULT_COLOR

        rr, cc = skimage.draw.line(
            r0=lower_right.y,
            c0=upper_left.x,
            r1=upper_left.y,
            c1=lower_right.x)
        img[rr, cc] = self.DEFAULT_COLOR
        return img

    def _export_plot(self, img: np.ndarray) -> PIL.Image.Image:
        '''Export the plot to a PIL Image'''
        return PIL.Image.fromarray(img, "RGB")

    def _draw_robot(self, img: np.ndarray, robot_metadata: Dict) -> np.ndarray:
        '''Plot the robot position and heading'''
        if robot_metadata is None:
            return img
        robot = self._create_robot(robot_metadata)
        img = self._draw_robot_position(img, robot)
        img = self._draw_robot_heading(img, robot)
        return img

    def _create_robot(self, robot_metadata: Dict) -> Robot:
        '''Extract robot position and rotation information from the metadata'''
        position = robot_metadata.get('position')
        if position is not None:
            x = position.get('x')
            z = position.get('z')
        else:
            x = 0.0
            z = 0.0
        rotation = robot_metadata.get('rotation')
        rotation_y = rotation.get('y') if rotation is not None else 0.0
        heading = self._calculate_heading(
            rotation_angle=360.0 - rotation_y,
            heading_length=self.HEADING_LENGTH
        )
        return Robot(x, z, heading)

    def _calculate_heading(self, rotation_angle: float,
                           heading_length: float) -> XZHeading:
        '''Calculate XZ heading vector from the rotation angle'''
        s = math.sin(math.radians(rotation_angle))
        c = math.cos(math.radians(rotation_angle))
        vec_x = 0 * c - heading_length * s
        vec_z = 0 * s + heading_length * c
        return XZHeading(vec_x, vec_z)

    def _draw_robot_position(self, img: np.ndarray,
                             robot: Robot) -> np.ndarray:
        '''Draw the robot's scene XZ position in the plot'''
        robot_position = self._convert_to_image_coords(
            scene_pt=SceneCoord(robot.x, robot.z)
        )
        rr, cc = skimage.draw.disk(
            center=(
                robot_position.y,
                robot_position.x
            ),
            radius=self.ROBOT_PLOT_WIDTH * self.scale.x,
            shape=img.shape[:2])
        img[rr, cc] = self.ROBOT_COLOR
        return img

    def _draw_robot_heading(self, img: np.ndarray, robot: Robot) -> np.ndarray:
        '''Draw the heading vector starting from the robot XZ position'''
        y_point = int(self.image_center.y - robot.z * self.scale.y)
        x_point = int(self.image_center.x + robot.x * self.scale.x)
        rr, cc = skimage.draw.disk(
            center=(
                y_point - int(robot.heading.z * self.scale.x),
                x_point + int(robot.heading.x * self.scale.x)
            ),
            radius=self.ROBOT_NOSE_RADIUS * self.scale.x,
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
                img = self._draw_object(img, obj, pts)
                if goal_id is not None and o['objectId'] == goal_id:
                    img = self._draw_goal(img, pts)
        return img

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
        if color == 'rose':
            color = 'deeppink'
        return color

    def _draw_object(self, img: np.ndarray,
                     obj: Object, points: List) -> np.ndarray:
        '''Draw the scene object'''
        # convert list of tuples to list of rows and list of columns
        cs, rs = map(list, zip(*points))
        # convert room coordinates to image coordinates
        rs = list(map(lambda r: self.image_center.y - r * self.scale.y, rs))
        cs = list(map(lambda c: self.image_center.x + c * self.scale.x, cs))

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
        # use dictionary get method for color retrieval
        # if no match for that color string, then resort to the default color
        clr = colour.COLOR_NAME_TO_RGB.get(
            obj.color.lower(), self.DEFAULT_COLOR)

        img[rr, cc] = clr
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
