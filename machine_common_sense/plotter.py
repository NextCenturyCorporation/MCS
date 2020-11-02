import io
import math
import PIL

import matplotlib.pyplot as plt
from typing import Dict
from shapely import geometry


class TopDownPlotter():

    HEADING_LENGTH = 0.4
    MINIMUM_ROOM_DIMENSION = -5
    MAXIMUM_ROOM_DIMENSION = 5
    BORDER = 0.05
    AGENT_COLOR = 'gray'

    def __init__(self, team: str, scene_name: str,
                 plot_width: int, plot_height: int):
        self._team = team
        self._scene_name = scene_name
        self._plot_width = plot_width
        self._plot_height = plot_height

    def plot(self, scene_event: Dict, step_number: int) -> PIL.Image.Image:

        self._draw_agent(scene_event.metadata['agent'])

        colors = scene_event.events[-1].object_id_to_color

        self._draw_object_bounds(scene_event.metadata['objects'], colors)

        # set scene extents
        plt.xlim(self.MINIMUM_ROOM_DIMENSION, self.MAXIMUM_ROOM_DIMENSION)
        plt.ylim(self.MINIMUM_ROOM_DIMENSION, self.MAXIMUM_ROOM_DIMENSION)
        plt.text(
            self.MAXIMUM_ROOM_DIMENSION + self.BORDER,
            self.MINIMUM_ROOM_DIMENSION + self.BORDER,
            step_number)
        plt.title(f"{self._team} {self._scene_name}")

        # convert figure to PIL Image
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = PIL.Image.open(buf)

        # resize image to match screen dimensions
        img = img.resize((self._plot_width, self._plot_height))
        plt.close()

        return img

    def _draw_agent(self, agent_metadata: Dict) -> None:
        '''Plot the agent position and heading'''
        agent_x = agent_metadata['position']['x']
        agent_z = agent_metadata['position']['z']
        rotation = agent_metadata['rotation']['y']

        # draw agent position
        circle = plt.Circle(
            (agent_x, agent_z),
            radius=0.2,
            color="xkcd:" + self.AGENT_COLOR,
            label='agent')
        plt.gca().add_patch(circle)

        # draw heading
        s = math.sin((360 - rotation) * math.pi / 180)
        c = math.cos((360 - rotation) * math.pi / 180)
        heading_x = 0 * c - self.HEADING_LENGTH * s + agent_x
        heading_y = 0 * s + self.HEADING_LENGTH * c + agent_z
        heading = plt.Line2D((agent_x, heading_x),
                             (agent_z, heading_y),
                             color="xkcd:" + self.AGENT_COLOR,
                             lw=1)
        plt.gca().add_line(heading)

    def _draw_object_bounds(self, objects: Dict, colors: Dict) -> None:
        '''Plot the object bounds for each object in the scene'''
        for obj in objects:
            held = obj['isPickedUp']
            visible = obj['visibleInCamera']
            uuid = obj['objectId']
            obj_clr = obj.get('colorsFromMaterials', [])
            obj_clr = obj_clr[0] if len(obj_clr) else 'black'
            bounds = obj.get('objectBounds', None)
            if bounds is not None:
                dimensions = bounds.get('objectBoundsCorners', None)

                # white color does not show up in plot but ivory does
                if obj_clr == 'white':
                    obj_clr = 'ivory'

                if dimensions is not None:
                    obj_pts = [(d['x'], d['z']) for d in dimensions[:4]]
                    polygon = geometry.MultiPoint(obj_pts).convex_hull
                    pts = polygon.exterior.coords
                    poly = plt.Polygon(pts,
                                       color="xkcd:" + obj_clr,
                                       fill="xkcd:" + obj_clr if visible or
                                            held else '',
                                       ec="xkcd:black",
                                       label=uuid)
                    plt.gca().add_patch(poly)
