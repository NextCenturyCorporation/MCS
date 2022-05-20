from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import ai2thor.server
import colour
import cv2
import numpy as np
import PIL.Image
import skimage.draw
from shapely import affinity, geometry

from machine_common_sense.config_manager import SceneConfiguration, Vector3d


@dataclass
class SceneCoord():
    '''Unity scenes have floor dimensions of x and z'''
    x: float
    y: float
    z: float

    def __sub__(self, coord: SceneCoord):
        return SceneCoord(self.x - coord.x, self.y - coord.y, self.z - coord.z)

    def __add__(self, coord: SceneCoord):
        return SceneCoord(self.x + coord.x, self.y + coord.y, self.z + coord.z)

    def __or__(self, coord: SceneCoord):
        '''Midpoint between two SceneCoords'''
        return SceneCoord(
            (self.x + coord.x) / 2,
            (self.y + coord.y) / 2,
            (self.z + coord.z) / 2
        )


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
    '''AI robot/performer location and rotation in Unity'''
    x: float
    y: float
    z: float
    rotation_y: float


@dataclass
class Arrow():
    floor: List[SceneCoord]
    peak: SceneCoord


@dataclass
class SceneBounds():
    points: List[SceneCoord]
    rotation: Dict = None

    def __post_init__(self):
        # TODO If this object has any X/Z rotation, rotate the corners too.
        # Safe to assume the bounds will always be in a consistent order.
        # See BaseFPSAgentController.WorldCoordinatesOfBoundingBox (Unity)
        assert len(self.points) == 8

    def bottom_front_right_corner(self) -> SceneCoord:
        return self.points[0]

    def bottom_front_left_corner(self) -> SceneCoord:
        return self.points[1]

    def bottom_back_left_corner(self) -> SceneCoord:
        return self.points[2]

    def bottom_back_right_corner(self) -> SceneCoord:
        return self.points[3]

    def top_front_right_corner(self) -> SceneCoord:
        return self.points[4]

    def top_front_left_corner(self) -> SceneCoord:
        return self.points[5]

    def top_back_left_corner(self) -> SceneCoord:
        return self.points[6]

    def top_back_right_corner(self) -> SceneCoord:
        return self.points[7]


@dataclass
class SceneAsset():
    held: bool
    visible: bool
    uuid: str
    color: str
    bounds: SceneBounds


@dataclass
class Ramp(SceneAsset):

    @property
    def arrow(self) -> Arrow:
        peak_mid = self._peak_midpoint()
        floor_pts = self._floor_points()
        return Arrow(floor=floor_pts, peak=peak_mid)

    def _peak_midpoint(self) -> SceneCoord:
        '''The midpoint of the highest ramp side'''
        # Assumes ramps are always wedges (triangles).
        peak_pts = [
            self.bounds.top_front_right_corner(),
            self.bounds.top_front_left_corner()
        ]
        peak_scene_pts = [
            SceneCoord(x=pt.x, y=pt.y, z=pt.z) for pt in peak_pts
        ]
        return peak_scene_pts[0] | peak_scene_pts[1]

    def _floor_points(self) -> List[SceneCoord]:
        '''The points of the ramp side nearest the floor'''
        # Assumes ramps are always wedges (triangles).
        floor_points = [
            self.bounds.bottom_back_right_corner(),
            self.bounds.bottom_back_left_corner()
        ]
        return [SceneCoord(pt.x, pt.y, pt.z) for pt in floor_points]


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
    ROBOT_COLOR = colour.COLOR_NAME_TO_RGB['blue']
    DEFAULT_GOAL_COLOR = colour.COLOR_NAME_TO_RGB['lime']

    OBJECT_INSIDE_PERCENTAGE = 0.5
    HEADING_LENGTH = 0.6
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
            Vector3d(x=14, y=10, z=10) if scene_config.intuitive_physics
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
            y=self._room_size.y,
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
            img,
            scene_config.holes,
            scene_config.room_dimensions)
        img = self._draw_lava(
            img,
            scene_config.retrieve_lava(),
            scene_config.room_dimensions)

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

    def _convert_points(self, points: list) -> tuple:
        # convert list of tuples to list of rows and list of columns
        cs, rs = map(list, zip(*points))
        # convert room coordinates to image coordinates
        rs = list(map(lambda r: self.image_center.y - r * self.scale.y, rs))
        cs = list(map(lambda c: self.image_center.x + c * self.scale.x, cs))
        return cs, rs

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

    def _out_of_bounds(
            self, pos: SceneCoord, room_dim: Vector3d) -> bool:
        x_odd_reducer = 0 if room_dim.x % 2 == 0 else 1
        z_odd_reducer = 0 if room_dim.z % 2 == 0 else 1
        return (abs(pos.x) > (room_dim.x - x_odd_reducer) /
                2 or abs(pos.z) > (room_dim.z - z_odd_reducer) / 2)

    def _even_room_dim_edge_size_reducer(
            self,
            pos: SceneCoord,
            room_dim: Vector3d = Vector3d(x=10, y=0, z=10)
    ) -> Tuple(SceneCoord):

        size_reducer_left = SceneCoord(0, 0, 0)
        size_reducer_right = SceneCoord(0, 0, 0)
        if pos.x == -(room_dim.x / 2):
            size_reducer_left.x = 0.5
        if pos.z == -(room_dim.z / 2):
            size_reducer_left.z = 0.5
        if pos.x == (room_dim.x / 2):
            size_reducer_right.x = -0.5
        if pos.z == (room_dim.z / 2):
            size_reducer_right.z = -0.5

        return size_reducer_left, size_reducer_right

    def _even_x_odd_z_room_dim_edge_size_reducer(
            self,
            pos: SceneCoord,
            room_dim: Vector3d = Vector3d(x=10, y=0, z=10)
    ) -> Tuple(SceneCoord):

        size_reducer_left = SceneCoord(0, 0, 0)
        size_reducer_right = SceneCoord(0, 0, 0)
        if pos.x == -(room_dim.x / 2):
            size_reducer_left.x = 0.5
        if pos.x == (room_dim.x / 2):
            size_reducer_right.x = -0.5

        return size_reducer_left, size_reducer_right

    def _odd_x_even_z_room_dim_edge_size_reducer(
            self,
            pos: SceneCoord,
            room_dim: Vector3d = Vector3d(x=10, y=0, z=10)
    ) -> Tuple(SceneCoord):

        size_reducer_left = SceneCoord(0, 0, 0)
        size_reducer_right = SceneCoord(0, 0, 0)
        if pos.z == -(room_dim.z / 2):
            size_reducer_left.z = 0.5
        if pos.z == (room_dim.z / 2):
            size_reducer_right.z = -0.5

        return size_reducer_left, size_reducer_right

    def _plotter_hole_texture_size_reducer(
            self,
            pos: SceneCoord,
            room_dim: Vector3d = Vector3d(x=10, y=0, z=10)
    ) -> Tuple(SceneCoord):

        x_is_even = room_dim.x % 2 == 0
        z_is_even = room_dim.z % 2 == 0

        if self._out_of_bounds(pos, room_dim):
            return None, None
        if x_is_even and z_is_even:
            return (self._even_room_dim_edge_size_reducer(pos, room_dim))
        if x_is_even and not z_is_even:
            return self._even_x_odd_z_room_dim_edge_size_reducer(pos, room_dim)
        return self._odd_x_even_z_room_dim_edge_size_reducer(pos, room_dim)

    def _draw_lava(self, img: np.ndarray, lava: List,
                   room_dim: Vector3d = Vector3d(x=10, y=0, z=10)
                   ) -> np.ndarray:
        if lava is None:
            return img

        for area in lava:
            area_pos_ul = SceneCoord(x=area[0], y=0, z=area[1])
            area_pos_lr = SceneCoord(x=area[2], y=0, z=area[3])
            midpoint = area_pos_ul | area_pos_lr
            size_reducer_left, size_reducer_right = (
                self._plotter_hole_texture_size_reducer(midpoint, room_dim)
            )
            if size_reducer_left is None:
                continue
            area_pos_ul = area_pos_ul + size_reducer_left
            area_pos_lr = area_pos_lr + size_reducer_right
            area_img_pos_ul = self._convert_to_image_coords(area_pos_ul)
            area_img_pos_lr = self._convert_to_image_coords(area_pos_lr)

            img = self._draw_lava_area(
                img=img,
                upper_left=area_img_pos_ul,
                lower_right=area_img_pos_lr,
                texture_color=colour.COLOR_NAME_TO_RGB['red'])
            img = self._draw_perimeter(
                img,
                area_img_pos_ul,
                area_img_pos_lr,
                self.BACKGROUND_COLOR)
            img = self._draw_x(
                img,
                area_img_pos_ul,
                area_img_pos_lr,
                self.BACKGROUND_COLOR)
        return img

    def _draw_lava_area(
        self,
        img: np.ndarray,
        upper_left: ImageCoord,
        lower_right: ImageCoord,
        texture_color: colour.C_RGB
    ) -> np.ndarray:
        rr, cc = skimage.draw.rectangle(
            start=(upper_left.y, upper_left.x),
            end=(lower_right.y, lower_right.x),
            shape=img.shape[:2])
        img[rr, cc] = texture_color
        return img

    def _draw_holes(self, img: np.ndarray, holes: List,
                    room_dim: Vector3d = Vector3d(x=10, y=0, z=10
                                                  )) -> np.ndarray:
        '''Draw a box with an X to illustrate a floor hole'''
        if holes is None:
            return img

        for hole in holes:
            hole_center = SceneCoord(x=hole.x, y=0, z=hole.z)

            size_reducer_left, size_reducer_right = (
                self._plotter_hole_texture_size_reducer(
                    hole, room_dim))
            if size_reducer_left is None:
                continue
            half_cell_pos = SceneCoord(
                self.UNIT_CELL_WIDTH / 2, 0, self.UNIT_CELL_WIDTH / 2)
            # calculate scene corners
            hole_upper_left: SceneCoord = hole_center - half_cell_pos + \
                size_reducer_left
            hole_lower_right: SceneCoord = hole_center + half_cell_pos + \
                size_reducer_right

            # convert scene corners to image coordinates
            hole_img_upper_left: ImageCoord = self._convert_to_image_coords(
                hole_upper_left)
            hole_img_lower_right: ImageCoord = self._convert_to_image_coords(
                hole_lower_right)

            img = self._draw_perimeter(
                img,
                hole_img_upper_left,
                hole_img_lower_right,
                self.DEFAULT_COLOR)
            img = self._draw_x(
                img,
                hole_img_upper_left,
                hole_img_lower_right,
                self.DEFAULT_COLOR)
        return img

    def _draw_perimeter(
            self,
            img: np.ndarray,
            upper_left: ImageCoord,
            lower_right: ImageCoord,
            color: Tuple) -> np.ndarray:
        '''Outline the floor hole'''
        rr, cc = skimage.draw.rectangle_perimeter(
            start=(upper_left.y - 1, upper_left.x + 1),
            end=(lower_right.y + 1, lower_right.x - 1),
            shape=img.shape[:2],
            clip=True)
        img[rr, cc] = color
        return img

    def _draw_x(
            self,
            img: np.ndarray,
            upper_left: ImageCoord,
            lower_right: ImageCoord,
            color: Tuple) -> np.ndarray:
        rr, cc = skimage.draw.line(
            r0=upper_left.y,
            c0=upper_left.x,
            r1=lower_right.y,
            c1=lower_right.x)
        img[rr, cc] = color

        rr, cc = skimage.draw.line(
            r0=lower_right.y,
            c0=upper_left.x,
            r1=upper_left.y,
            c1=lower_right.x)
        img[rr, cc] = color
        return img

    def _export_plot(self, img: np.ndarray) -> PIL.Image.Image:
        '''Export the plot to a PIL Image'''
        return PIL.Image.fromarray(img, "RGB")

    def _draw_robot(self, img: np.ndarray, robot_metadata: Dict) -> np.ndarray:
        '''Plot the robot triangle'''
        if robot_metadata is None:
            return img
        robot = self._create_robot(robot_metadata)
        img = self._draw_robot_position(img, robot)
        return img

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
        return Robot(x, y, z, 360 - rotation_y)

    def _calculate_heading(self, rotation_angle: float,
                           heading_length: float) -> XZHeading:
        '''Calculate XZ heading vector from the rotation angle'''
        s = math.sin(math.radians(rotation_angle))
        c = math.cos(math.radians(rotation_angle))
        vec_x = heading_length * s * -1
        vec_z = heading_length * c
        return XZHeading(vec_x, vec_z)

    def _draw_robot_position(self, img: np.ndarray,
                             robot: Robot) -> np.ndarray:
        '''Draw the robot's scene XZ position as a triangle in the plot'''
        opposite_color = self._find_opposite_color(self.ROBOT_COLOR)
        half_length = self.HEADING_LENGTH / 2.0
        # Create the triangle points.
        front = self._calculate_heading(robot.rotation_y, self.HEADING_LENGTH)
        right = self._calculate_heading(120 + robot.rotation_y, half_length)
        left = self._calculate_heading(240 + robot.rotation_y, half_length)
        triangle = [(front.x, front.z), (right.x, right.z), (left.x, left.z)]
        # Create the triangle polygon.
        outer = geometry.MultiPoint(triangle).convex_hull
        # Move the triangle from the origin to the correct position.
        outer = affinity.translate(outer, robot.x, robot.z)
        # Draw the robot as two triangles: first a large outer triangle of the
        # opposite color as a border; and a small inner triangle as the center.
        percent = self.OBJECT_INSIDE_PERCENTAGE
        inner = affinity.scale(outer, xfact=percent, yfact=percent)
        for polygon, color in [
            (outer, opposite_color),
            (inner, self.ROBOT_COLOR)
        ]:
            points = list(polygon.exterior.coords)
            cs, rs = self._convert_points(points)
            rr, cc = skimage.draw.polygon(rs, cs, shape=img.shape[:2])
            img[rr, cc] = color
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
        combined_objects = filtered_structural_objects + objects
        # the combined list needs to be sorted by y height
        # so that the lowest objects are drawn first
        combined_objects = sorted(
            combined_objects,
            key=lambda obj: obj['objectBounds']['objectBoundsCorners'][0]['y'])
        return combined_objects

    def _draw_objects(self, img: np.ndarray, objects: Dict,
                      goal_id: str = None) -> np.ndarray:
        '''Plot the object bounds for each object in the scene'''
        for o in objects:
            obj = self._create_asset(o)
            if obj.bounds is not None:
                if goal_id is not None and o['objectId'] == goal_id:
                    img = self._draw_goal(img, obj)
                else:
                    img = self._draw_object(img, obj)
        return img

    def _create_asset(self, object_metadata: Dict) -> SceneAsset:
        '''Create the scene object from its metadata'''
        colors = object_metadata.get('colorsFromMaterials', [])
        if len(colors):
            color = self._convert_color(colors[0])
        else:
            color = self._convert_color('')

        obj_bounds = object_metadata.get('objectBounds')
        corners = None if obj_bounds is None else obj_bounds.get(
            'objectBoundsCorners')
        bounds = None if corners is None else [SceneCoord(
            x=corner['x'], y=corner['y'], z=corner['z']) for corner in corners]

        return SceneAsset(
            held=object_metadata.get('isPickedUp'),
            visible=object_metadata.get('visibleInCamera'),
            uuid=object_metadata.get('objectId'),
            color=color,
            bounds=(
                SceneBounds(bounds, object_metadata.get('rotation'))
                if bounds else None
            )
        )

    def _convert_color(self, color: str) -> str:
        '''Convert color string to string'''
        if not color:
            color = 'ivory'
        # Don't use the same color as the background (black).
        if color == 'black':
            color = 'ivory'
        # Rose is apparently not a valid web color.
        if color == 'rose':
            color = 'deeppink'
        # Azure as a web color is very different from the normal azure.
        if color == 'azure':
            color = 'deepskyblue'
        return color

    def _draw_object(self, img: np.ndarray,
                     obj: SceneAsset, is_goal: bool = False) -> np.ndarray:
        '''Draw the scene object'''

        obj_pts = [(pt.x, pt.z) for pt in obj.bounds.points]
        polygon = geometry.MultiPoint(obj_pts).convex_hull
        # Shrink the polygon for the goal object, since it will be drawn on top
        # of the correctly-sized polygon from _draw_goal.
        if is_goal:
            percent = self.OBJECT_INSIDE_PERCENTAGE
            polygon = affinity.scale(polygon, xfact=percent, yfact=percent)
        pts = polygon.exterior.coords

        cs, rs = self._convert_points(pts)

        # use dictionary get method for color retrieval
        # if no match for that color string, then resort to the default color
        clr = colour.COLOR_NAME_TO_RGB.get(
            obj.color.lower(), self.DEFAULT_COLOR)

        # draw filled polygon if visible to the robot
        if is_goal or obj.visible:
            rr, cc = skimage.draw.polygon(
                rs,
                cs,
                shape=img.shape[:2])
            # Draw a small black polygon for a hidden goal object, since it
            # already has a border around it.
            if not obj.visible:
                clr = self.BACKGROUND_COLOR
        else:
            rr, cc = skimage.draw.polygon_perimeter(
                rs,
                cs,
                shape=img.shape[:2])
        img[rr, cc] = clr

        # using ramp string prefix assumpation to make ramp determination
        # might be better to have an attribute to leverage
        if(obj.uuid.startswith('ramp')):
            self._draw_ramp_arrow(img, obj, clr)

        return img

    def _draw_ramp_arrow(self, img: np.ndarray, obj: SceneAsset,
                         ramp_color: Tuple) -> np.ndarray:
        # convert scene object to a ramp
        ramp = obj
        ramp.__class__ = Ramp
        return self._draw_arrow(img, ramp, ramp_color)

    def _draw_arrow(self, img: np.ndarray, ramp: Ramp,
                    ramp_color: Tuple) -> np.ndarray:
        '''draw lines from the arrow floor points to the peak
        to illustrate the ramp
        '''
        peak_pt = self._convert_to_image_coords(ramp.arrow.peak)
        for floor_pt in ramp.arrow.floor:
            img_pt = self._convert_to_image_coords(floor_pt)
            rr, cc = skimage.draw.line(
                r0=peak_pt.y,
                c0=peak_pt.x,
                r1=img_pt.y,
                c1=img_pt.x)
            arrow_color = (
                self.BACKGROUND_COLOR if ramp_color != self.BACKGROUND_COLOR
                else self.DEFAULT_COLOR
            )
            img[rr, cc] = arrow_color if ramp.visible else ramp_color
        return img

    def _draw_goal(self, img: np.ndarray,
                   obj: SceneAsset) -> np.ndarray:
        '''Draw the goal object of the scene'''
        obj_pts = [(pt.x, pt.z) for pt in obj.bounds.points]
        polygon = geometry.MultiPoint(
            obj_pts).convex_hull
        pts = polygon.exterior.coords

        color = colour.COLOR_NAME_TO_RGB.get(
            obj.color.lower(),
            self.DEFAULT_COLOR
        )
        opposite_color = self._find_opposite_color(color)
        # If the object's color is greyscale, use a default instead.
        if color[0] == color[1] == color[2]:
            opposite_color = self.DEFAULT_GOAL_COLOR

        cs, rs = self._convert_points(pts)

        # Draw a correctly-sized polygon with the opposite of the goal's color.
        # This will create a thick border around the 2nd polygon (see below).
        rr, cc = skimage.draw.polygon(rs, cs, shape=img.shape[:2])
        img[rr, cc] = opposite_color

        # Then draw a smaller polygon on top of the 1st polygon in its middle.
        return self._draw_object(img, obj, is_goal=True)

    def _find_opposite_color(self, color: tuple) -> tuple:
        '''Return the exact opposite of the given color.'''
        return (255 - color[0], 255 - color[1], 255 - color[2])


if __name__ == '__main__':
    import sys

    import machine_common_sense as mcs
    controller = mcs.create_controller(
        unity_cache_version='dev',
        config_file_or_dict={'metadata': 'level1',
                             'video_enabled': True})

    scene_data, _ = mcs.load_scene_json_file(sys.argv[1])
    controller.start_scene(scene_data)
    controller.end_scene()
