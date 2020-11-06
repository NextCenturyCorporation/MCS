import io
import math
import PIL
import ai2thor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from typing import Dict, NamedTuple, List
from shapely import geometry


class XZHeading(NamedTuple):
    x: float
    z: float


class Agent(NamedTuple):
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

    AGENT_PLOT_WIDTH = 0.2
    AGENT_PLOT_LABEL = "agent"
    AGENT_COLOR = 'xkcd:gray'
    DEFAULT_COLOR = "xkcd:black"
    HEADING_LENGTH = 0.4
    MINIMUM_ROOM_DIMENSION = -5
    MAXIMUM_ROOM_DIMENSION = 5
    BORDER = 0.05

    def __init__(self, team: str, scene_name: str,
                 plot_width: int, plot_height: int):
        self._team = team
        self._scene_name = scene_name
        self._plot_width = plot_width
        self._plot_height = plot_height

    def plot(self, scene_event: ai2thor.server.Event,
             step_number: int) -> PIL.Image.Image:

        plt = self._initialize_plot(step_number=step_number)
        self._draw_objects(self._find_plottable_objects(scene_event))
        self._draw_agent(scene_event.metadata.get('agent', None))
        img = self._export_plot(plt)
        plt.close()
        return img

    def _find_plottable_objects(
            self, scene_event: ai2thor.server.Event) -> List:
        '''Find plottable objects from the scene data.

        Plottable objects include normal scene objects as well as
        occluder and wall structural objects.
        '''
        structural_objects = scene_event.metadata.get(
            'structuralObjects', [])
        filtered_structural_objects = [
            obj for obj in structural_objects
            if obj.get('objectId', '').startswith('occluder') or
            obj.get('objectId', '').startswith('wall')
        ]
        objects = scene_event.metadata.get('objects', [])
        return objects + filtered_structural_objects

    def _initialize_plot(self, step_number: int) -> None:
        '''Create the plot'''
        plt.xlim(self.MINIMUM_ROOM_DIMENSION, self.MAXIMUM_ROOM_DIMENSION)
        plt.ylim(self.MINIMUM_ROOM_DIMENSION, self.MAXIMUM_ROOM_DIMENSION)
        plt.text(
            self.MAXIMUM_ROOM_DIMENSION + self.BORDER,
            self.MINIMUM_ROOM_DIMENSION + self.BORDER,
            step_number)
        plt.title(f"{self._team} {self._scene_name}")
        return plt

    def _export_plot(self, plt: matplotlib.pyplot) -> PIL.Image.Image:
        '''Export the plot to a PIL Image'''
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = PIL.Image.open(buf)
        # resize image to match screen dimensions
        # current video recorders require it for now
        return img.resize((self._plot_width, self._plot_height))

    def _draw_agent(self, agent_metadata: Dict) -> None:
        '''Plot the agent position and heading'''
        if agent_metadata is None:
            return None
        agent = self._create_agent(agent_metadata)
        self._draw_agent_position(agent)
        self._draw_agent_heading(agent)

    def _draw_agent_position(self, agent: Agent) -> None:
        '''Draw the agent's scene XZ position in the plot'''
        circle = plt.Circle(
            (agent.x, agent.z),
            radius=self.AGENT_PLOT_WIDTH,
            color=self.AGENT_COLOR,
            label=self.AGENT_PLOT_LABEL)
        plt.gca().add_patch(circle)

    def _draw_agent_heading(self, agent: Agent) -> None:
        '''Draw the heading vector starting from the agent XZ position'''
        heading = self._calculate_heading(
            rotation_angle=360.0 - agent.rotation,
            heading_length=self.HEADING_LENGTH
        )
        heading = plt.Line2D((agent.x, agent.x + heading.x),
                             (agent.z, agent.z + heading.z),
                             color=self.AGENT_COLOR,
                             lw=1)
        plt.gca().add_line(heading)

    def _draw_objects(self, objects: Dict) -> None:
        '''Plot the object bounds for each object in the scene'''
        for o in objects:
            obj = self._create_object(o)
            if obj.bounds is not None:
                obj_pts = [(pt['x'], pt['z']) for pt in obj.bounds]
                polygon = geometry.MultiPoint(obj_pts).convex_hull
                pts = polygon.exterior.coords
                self._draw_object_bounds(obj, pts)

    def _draw_object_bounds(self, obj: Object, points: []) -> None:
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

    def _create_agent(self, agent_metadata: Dict) -> Agent:
        '''Extract agent position and rotation information from the metadata'''
        position = agent_metadata.get('position', None)
        if position is not None:
            x = position.get('x', None)
            y = position.get('y', None)
            z = position.get('z', None)
        else:
            x = 0.0
            y = 0.0
            z = 0.0

        rotation = agent_metadata.get('rotation', None)
        if rotation is not None:
            rotation_y = rotation.get('y', None)
        else:
            rotation_y = 0.0

        return Agent(x, y, z, rotation_y)

    def _create_object(self, object_metadata: Dict) -> Object:
        '''Create the scene object from its metadata'''

        held = object_metadata.get('isPickedUp', None)
        visible = object_metadata.get('visibleInCamera', None)
        uuid = object_metadata.get('objectId', None)

        colors = object_metadata.get('colorsFromMaterials', [])
        if len(colors):
            color = self._convert_color(colors[0])
        else:
            color = self._convert_color('')

        bounds = object_metadata.get('objectBounds', None)
        if bounds is not None:
            corners = bounds.get('objectBoundsCorners', None)
        else:
            corners = None

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
