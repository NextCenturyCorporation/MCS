import logging
import pathlib
from abc import abstractmethod

import numpy as np
import PIL

from .controller_events import (AbstractControllerSubscriber,
                                BasePostActionEventPayload,
                                ControllerEventPayload)
from .plotter import TopDownPlotter
from .recorder import VideoRecorder

logger = logging.getLogger(__name__)


DEPTH_HSV_BANDS = 400.0


def convert_depth_to_hsv(
    depth_float_array: np.array,
    clipping_plane_far: float
) -> np.array:
    # Split the depth data into multiple color bands. Each band corresponds to
    # the full hue spectrum, from red to purple, at a specific saturation and
    # value. Near bands have lower saturation (closer to white); far bands have
    # lower value (closer to black). Don't use saturation or value lower than
    # 30, or else the color will look too close to white or black.
    band_size = clipping_plane_far / DEPTH_HSV_BANDS
    mid_sat = band_size * int(DEPTH_HSV_BANDS / 2.0)
    mid_val = clipping_plane_far - (band_size * int(DEPTH_HSV_BANDS / 2.0))
    shape = depth_float_array.shape
    depth_hsv_array = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
    hue = (np.mod(depth_float_array, band_size) / band_size * 256)
    sat = np.where(
        depth_float_array < mid_sat,
        55 + np.floor(depth_float_array / band_size),
        255
    )
    val = np.where(
        depth_float_array >= mid_val,
        255 - np.floor((depth_float_array - mid_val) / band_size),
        255
    )
    # Note that PIL images use HSV ints between 0 and 255 inclusive.
    depth_hsv_array[:shape[0], :shape[1], 0] = hue
    depth_hsv_array[:shape[0], :shape[1], 1] = sat
    depth_hsv_array[:shape[0], :shape[1], 2] = val
    return depth_hsv_array


def convert_depth_to_image(
    depth_float_array: np.array,
    clipping_plane_far: float
) -> PIL.Image:
    '''Convert the given depth float array into a depth image, then return the
    image.'''
    # Convert the depth array from a 2D array of floats, ranging from 0 to the
    # camera's far clipping plane, to a 3D array of HSV tuples.
    depth_hsv_array = convert_depth_to_hsv(
        depth_float_array,
        clipping_plane_far
    )
    image = PIL.Image.fromarray(depth_hsv_array, mode='HSV')
    image = image.convert('RGB')
    return image


class AbstractImageEventHandler(AbstractControllerSubscriber):
    '''Abstract class for handling saving different images based on controller
    events.  This class assumes images should be saved on the start of the
    scene and on each step.  The implementation should create the image (PIL)
    and then call _do_save_image to save the file.
    '''

    def on_start_scene(self, payload: ControllerEventPayload):
        self._save_image(payload)

    def on_after_step(self, payload: ControllerEventPayload):
        self._save_image(payload)

    @abstractmethod
    def _save_image(self, payload):
        pass

    def _get_suffix(self, payload, index: int):
        if payload.step_number == 0:
            step_plus_substep_index = 0
        else:
            step_plus_substep_index = (
                ((payload.step_number - 1) *
                    len(payload.step_metadata.events)) +
                (index + 1)
            )
        return f"_{str(step_plus_substep_index)}.png"

    def _do_save_image(self, payload, index: int, data: PIL.Image, name: str):
        if (payload.output_folder):
            suffix = self._get_suffix(payload, index)
            data.save(fp=payload.output_folder +
                      name + suffix)


class AbstractVideoEventHandler(AbstractControllerSubscriber):

    '''Abstract class for handling saving different videos based on controller
        events.  This method provides some commonly used support methods, but
        leaves most of the work up to the implementation.  Typically, the
        implmentation should call create_video_recorder.  Images can be added
        to the video based on the implementations needs and at the end the
        recorder needs to be finished.
    '''

    PLACEHOLDER = 'placeholder'
    VISUAL = 'visual'
    DEPTH = 'depth'
    SEGMENTATION = 'segmentation'
    TOPDOWN = 'topdown'

    def get_basename(self, payload: ControllerEventPayload):
        timestamp = payload.timestamp
        scene_name = payload.scene_config.name.replace('json', '')
        return '_'.join(
            [payload.config.get_evaluation_name(),
             payload.config.get_metadata_tier().value,
             payload.config.get_team(),
             scene_name,
             AbstractVideoEventHandler.PLACEHOLDER, timestamp]) + '.mp4'

    def get_scene_name(self, payload: ControllerEventPayload):
        scene_name = payload.scene_config.name.replace('json', '')

        # strip prefix in scene_name
        if '/' in scene_name:
            scene_name = scene_name.rsplit('/', 1)[1]
        return scene_name

    def create_video_recorder(self, payload, file_tag):
        basename = self.get_basename(payload)
        video_filename = basename.replace(
            AbstractVideoEventHandler.PLACEHOLDER,
            file_tag
        )
        output_folder = pathlib.Path(payload.output_folder)
        vid_path = output_folder / video_filename
        fps = payload.step_output.physics_frames_per_second
        return VideoRecorder(vid_path, fps=fps)

    def _get_filename_without_timestamp(self, filepath: pathlib.Path):
        return filepath.stem[:-16] + filepath.suffix


class SceneImageEventHandler(AbstractImageEventHandler):
    '''
    Writes images for the visual output or scene output
    '''

    def _save_image(self, payload):
        for index, scene_image in enumerate(payload.step_output.image_list):
            self._do_save_image(payload, index, scene_image, 'frame_image')


class DepthImageEventHandler(AbstractImageEventHandler):
    '''
    writes images for depth map
    '''

    def _save_image(self, payload):
        for index, depth_float_array in enumerate(
                payload.step_output.depth_map_list):
            depth_image = convert_depth_to_image(
                depth_float_array,
                payload.step_output.camera_clipping_planes[1]
            )
            self._do_save_image(payload, index, depth_image, 'depth_map')


class ObjectMaskImageEventHandler(AbstractImageEventHandler):
    '''
    writes images for object mask
    '''

    def _save_image(self, payload):
        for index, object_mask in enumerate(
                payload.step_output.object_mask_list):
            self._do_save_image(payload, index, object_mask, 'object_mask')


class ImageVideoEventHandler(AbstractVideoEventHandler):
    '''
    writes videos for visual images
    '''

    def on_start_scene(self, payload: ControllerEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.VISUAL)
        self.save_video_for_step(payload)

    def on_after_step(self, payload: ControllerEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: ControllerEventPayload):
        for scene_image in payload.step_output.image_list:
            self.__recorder.add(scene_image)

    def on_end_scene(self, payload: ControllerEventPayload):
        self.__recorder.finish()


class TopdownVideoEventHandler(AbstractVideoEventHandler):
    '''
    writes top down video
    '''

    def on_start_scene(self, payload: BasePostActionEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.TOPDOWN)
        self.__plotter = TopDownPlotter(
            team=payload.config.get_team(),
            scene_config=payload.scene_config
        )
        self.save_video_for_step(payload)

    def on_after_step(self, payload: BasePostActionEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: BasePostActionEventPayload):
        for _ in payload.step_metadata.events:
            # The plotter used to be inside the for loop the same as
            # image_recorder, but it seems like it would only plot one per
            # step.
            goal_id = None
            # Is there a better way to do this test?
            if (payload.goal is not None and
                    payload.goal.metadata is not None):
                goal_id = payload.goal.metadata.get(
                    'target', {}).get('id', None)
            plot = self.__plotter.plot(payload.step_metadata,
                                       payload.step_number,
                                       goal_id)
            self.__recorder.add(plot)

    def on_end_scene(self, payload: BasePostActionEventPayload):
        self.__recorder.finish()


class DepthVideoEventHandler(AbstractVideoEventHandler):
    '''
    writes video of depth maps
    '''

    def on_start_scene(self, payload: BasePostActionEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.DEPTH)
        self.save_video_for_step(payload)

    def on_after_step(self, payload: BasePostActionEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: BasePostActionEventPayload):
        for depth_float_array in payload.step_output.depth_map_list:
            depth_image = convert_depth_to_image(
                depth_float_array,
                payload.step_output.camera_clipping_planes[1]
            )
            self.__recorder.add(depth_image)

    def on_end_scene(self, payload: BasePostActionEventPayload):
        self.__recorder.finish()


class SegmentationVideoEventHandler(AbstractVideoEventHandler):
    '''
    writes video for segmentation or object mask images
    '''

    def on_start_scene(self, payload: BasePostActionEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.SEGMENTATION)
        self.save_video_for_step(payload)

    def on_after_step(self, payload: BasePostActionEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: BasePostActionEventPayload):
        for object_mask in payload.step_output.object_mask_list:
            self.__recorder.add(object_mask)

    def on_end_scene(self, payload: BasePostActionEventPayload):
        self.__recorder.finish()
