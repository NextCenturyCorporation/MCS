import pathlib
import logging
import PIL
import numpy as np
from abc import abstractmethod

from .controller_events import AbstractControllerSubscriber
from .controller_events import ControllerEventPayload
from .plotter import TopDownPlotter
from .recorder import VideoRecorder
from .config_manager import ConfigManager


logger = logging.getLogger(__name__)


class AbstractImageEventHandler(AbstractControllerSubscriber):
    def on_start_scene(self, payload: ControllerEventPayload):
        self._save_image(payload)

    def on_after_step(self, payload: ControllerEventPayload):
        self._save_image(payload)

    @abstractmethod
    def _save_image(self, payload):
        pass

    def _get_suffix(self, payload, index):
        if payload.step_number == 0:
            step_plus_substep_index = 0
        else:
            step_plus_substep_index = (
                ((payload.step_number - 1) *
                    len(payload.step_metadata.events)) +
                (index + 1)
            )
        suffix = '_' + str(step_plus_substep_index) + '.png'
        return suffix

    def _do_save_image(self, payload, index, data, name):
        if (payload.output_folder):
            suffix = self._get_suffix(payload, index)
            data.save(fp=payload.output_folder +
                      name + suffix)


class AbstractVideoEventHandler(AbstractControllerSubscriber):
    PLACEHOLDER = 'placeholder'
    VISUAL = 'visual'
    DEPTH = 'depth'
    SEGMENTATION = 'segmentation'
    HEATMAP = 'heatmap'
    TOPDOWN = 'topdown'

    def get_basename(self, payload: ControllerEventPayload):
        eval_name = payload.config.get_evaluation_name()
        team = payload.config.get_team()
        timestamp = payload.timestamp
        scene_name = payload.scene_config.get(
            'name', '').replace('json', '')
        basename = '_'.join(
            [eval_name, payload.config.get_metadata_tier(),
             team,
             scene_name,
             AbstractVideoEventHandler.PLACEHOLDER, timestamp]) + '.mp4'
        return basename

    def get_scene_name(self, payload: ControllerEventPayload):
        scene_name = payload.scene_config.get(
            'name', '').replace('json', '')

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

    def _upload_video(self, payload):
        config = payload.config
        if (config.is_evaluation()):
            uploader = payload.uploader
            folder_prefix = config.uploader_folder_prefix

            filename = self._get_filename_without_timestamp(
                self.__recorder.path)
            uploader.upload_video(
                video_path=self.__recorder.path,
                s3_filename=folder_prefix + '/' + filename
            )

    def _get_filename_without_timestamp(self, filepath: pathlib.Path):
        return filepath.stem[:-16] + filepath.suffix


class SceneImageEventHandler(AbstractImageEventHandler):
    def _save_image(self, payload):
        for index, scene_image in enumerate(payload.step_output.image_list):
            self._do_save_image(payload, index, scene_image, 'frame_image')


class DepthImageEventHandler(AbstractImageEventHandler):
    def _save_image(self, payload):
        for index, depth_float_array in enumerate(
                payload.step_output.depth_map_list):
            max_depth = payload.step_metadata.metadata.get(
                'clippingPlaneFar',
                ConfigManager.DEFAULT_CLIPPING_PLANE_FAR
            )
            # Convert to pixel values for saving debug image.
            depth_pixel_array = depth_float_array * \
                255 / max_depth
            depth_map = PIL.Image.fromarray(
                depth_pixel_array.astype(np.uint8)
            )
            if payload.config.is_depth_maps_enabled():
                if (payload.config.is_save_debug_images()):
                    self._do_save_image(payload, index, depth_map, 'depth_map')


class ObjectMaskImageEventHandler(AbstractImageEventHandler):
    def _save_image(self, payload):
        for index, object_mask in enumerate(
                payload.step_output.object_mask_list):
            self._do_save_image(payload, index, object_mask, 'object_mask')


class ImageVideoEventHandler(AbstractVideoEventHandler):
    def on_start_scene(self, payload: ControllerEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.VISUAL)
        self.save_video_for_step(payload)

    def on_after_step(self, payload: ControllerEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: ControllerEventPayload):
        for index, scene_image in enumerate(
                payload.step_output.image_list):
            self.__recorder.add(scene_image)

    def on_end_scene(self, payload: ControllerEventPayload):
        self.__recorder.finish()
        self._upload_video(payload)


class TopdownVideoEventHandler(AbstractVideoEventHandler):
    def on_start_scene(self, payload: ControllerEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.TOPDOWN)
        team = payload.config.get_team()
        scene = payload.scene_config.get(
            'name', '').replace('json', '')
        self.__plotter = TopDownPlotter(team, scene)
        self.save_video_for_step(payload)

    def on_after_step(self, payload: ControllerEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: ControllerEventPayload):
        for index, event in enumerate(payload.step_metadata.events):
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

    def on_end_scene(self, payload: ControllerEventPayload):
        self.__recorder.finish()
        self._upload_video(payload)


class HeatmapVideoEventHandler(AbstractVideoEventHandler):
    def on_start_scene(self, payload: ControllerEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.HEATMAP)

    def on_prediction(self, payload: ControllerEventPayload):
        if(
            payload.heatmap_img is not None and
            isinstance(payload.heatmap_img, PIL.Image.Image)
        ):
            self.__recorder.add(payload.heatmap_img)

    def on_end_scene(self, payload: ControllerEventPayload):
        self.__recorder.finish()
        self._upload_video(payload)


class DepthVideoEventHandler(AbstractVideoEventHandler):
    def on_start_scene(self, payload: ControllerEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.DEPTH)
        self.save_video_for_step(payload)

    def on_after_step(self, payload: ControllerEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: ControllerEventPayload):
        for index, depth_float_array in enumerate(
                payload.step_output.depth_map_list):
            max_depth = payload.step_metadata.metadata.get(
                'clippingPlaneFar',
                ConfigManager.DEFAULT_CLIPPING_PLANE_FAR
            )
            # Convert to pixel values for saving debug image.
            depth_pixel_array = depth_float_array * \
                255 / max_depth
            depth_map = PIL.Image.fromarray(
                depth_pixel_array.astype(np.uint8)
            )
            self.__recorder.add(depth_map)

    def on_end_scene(self, payload: ControllerEventPayload):
        self.__recorder.finish()
        self._upload_video(payload)


class SegmentationVideoEventHandler(AbstractVideoEventHandler):
    def on_start_scene(self, payload: ControllerEventPayload):
        self.__recorder = self.create_video_recorder(
            payload, AbstractVideoEventHandler.SEGMENTATION)
        self.save_video_for_step(payload)

    def on_after_step(self, payload: ControllerEventPayload):
        self.save_video_for_step(payload)

    def save_video_for_step(self, payload: ControllerEventPayload):
        for index, object_mask in enumerate(
                payload.step_output.object_mask_list):
            self.__recorder.add(object_mask)

    def on_end_scene(self, payload: ControllerEventPayload):
        self.__recorder.finish()
        self._upload_video(payload)
