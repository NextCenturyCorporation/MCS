import pathlib
import logging
import PIL
import numpy as np

from .controller_events import AbstractControllerSubscriber
from .plotter import TopDownPlotter
from .recorder import VideoRecorder
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ControllerVideoManager(AbstractControllerSubscriber):
    # TODO: We should separate these and only enable specific classes
    # instead of having constant checks

    def on_start_scene(self, payload, controller):
        # used to be def _create_video_recorders(self, timestamp):
        '''Create video recorders used to capture evaluation scenes for review
        '''
        if payload.config.is_evaluation() or payload.config.is_video_enabled():
            timestamp = payload.timestamp
            output_folder = pathlib.Path(payload.output_folder)
            eval_name = payload.config.get_evaluation_name()
            team = payload.config.get_team()
            scene_name = payload.scene_config.get(
                'name', '').replace('json', '')

            team = payload.config.get_team()
            scene = payload.scene_config.get(
                'name', '').replace('json', '')

            self.__plotter = TopDownPlotter(team, scene)

            # strip prefix in scene_name
            if '/' in scene_name:
                scene_name = scene_name.rsplit('/', 1)[1]

            basename_template = '_'.join(
                [eval_name, payload.config.get_metadata_tier(),
                 team,
                 scene_name,
                 controller.PLACEHOLDER, timestamp]) + '.mp4'

            visual_video_filename = basename_template.replace(
                controller.PLACEHOLDER, controller.VISUAL)
            self.__image_recorder = VideoRecorder(
                vid_path=output_folder / visual_video_filename,
                fps=payload.step_output.physics_frames_per_second)

            topdown_video_filename = basename_template.replace(
                controller.PLACEHOLDER, controller.TOPDOWN)
            self.__topdown_recorder = VideoRecorder(
                vid_path=output_folder / topdown_video_filename,
                fps=payload.step_output.physics_frames_per_second)

            heatmap_video_filename = basename_template.replace(
                controller.PLACEHOLDER, controller.HEATMAP)
            self.__heatmap_recorder = VideoRecorder(
                vid_path=output_folder / heatmap_video_filename,
                fps=payload.step_output.physics_frames_per_second)

            if payload.config.is_depth_maps_enabled():
                depth_video_filename = basename_template.replace(
                    controller.PLACEHOLDER, controller.DEPTH)
                self.__depth_recorder = VideoRecorder(
                    vid_path=output_folder / depth_video_filename,
                    fps=payload.step_output.physics_frames_per_second)

            if payload.config.is_object_masks_enabled():
                segmentation_video_filename = basename_template.replace(
                    controller.PLACEHOLDER, controller.SEGMENTATION)
                self.__segmentation_recorder = VideoRecorder(
                    vid_path=output_folder / segmentation_video_filename,
                    fps=payload.step_output.physics_frames_per_second)

        self._save_images_and_add_to_video(payload, controller)

    def on_prediction(self, payload, controller):
        if(
            payload.heatmap_img is not None and
            isinstance(payload.heatmap_img, PIL.Image.Image) and
            (payload.config.is_evaluation() or
             payload.config.is_video_enabled())
        ):
            self.__heatmap_recorder.add(payload.heatmap_img)

    def on_end_scene(self, payload, controller):
        config = payload.config
        if config.is_evaluation() or config.is_video_enabled():
            self.__topdown_recorder.finish()
            self.__image_recorder.finish()
            self.__heatmap_recorder.finish()

            if payload.config.is_depth_maps_enabled():
                self.__depth_recorder.finish()
            if payload.config.is_object_masks_enabled():
                self.__segmentation_recorder.finish()

        if (config.is_evaluation()):
            uploader = payload.uploader
            folder_prefix = config.uploader_folder_prefix

            topdown_filename = self._get_filename_without_timestamp(
                self.__topdown_recorder.path)
            uploader.upload_video(
                video_path=self.__topdown_recorder.path,
                s3_filename=folder_prefix + '/' + topdown_filename
            )

            video_filename = self._get_filename_without_timestamp(
                self.__image_recorder.path)
            uploader.upload_video(
                video_path=self.__image_recorder.path,
                s3_filename=folder_prefix + '/' + video_filename
            )

            video_filename = self._get_filename_without_timestamp(
                self.__heatmap_recorder.path)
            uploader.upload_video(
                video_path=self.__heatmap_recorder.path,
                s3_filename=folder_prefix + '/' + video_filename
            )

            if self._config.is_depth_maps_enabled():
                video_filename = self._get_filename_without_timestamp(
                    self.__depth_recorder.path)
                uploader.upload_video(
                    video_path=self.__depth_recorder.path,
                    s3_filename=folder_prefix + '/' + video_filename
                )

            if self._config.is_object_masks_enabled():
                video_filename = self._get_filename_without_timestamp(
                    self.__segmentation_recorder.path)
                uploader.upload_video(
                    video_path=self.__segmentation_recorder.path,
                    s3_filename=folder_prefix + '/' + video_filename
                )

    def on_after_step(self, payload, controller):
        self._save_images_and_add_to_video(payload, controller)

    def _save_images_and_add_to_video(self, payload, controller):
        # foreach image list
        config = payload.config
        for index, scene_image in enumerate(payload.step_output.image_list):
            if config.is_evaluation() or config.is_video_enabled():
                self.__image_recorder.add(scene_image)
            if (payload.output_folder and
                    payload.config.is_save_debug_images()):
                suffix = self._get_suffix(payload, index)
                scene_image.save(fp=payload.output_folder +
                                 'frame_image' + suffix)

        if config.is_evaluation() or config.is_video_enabled():
            for index, event in enumerate(payload.step_metadata.events):
                # The plotter used to be inside the for look the same as
                # image_recorder, but it seems like it would only plot one per
                # step.
                goal_id = None
                # Is there a better way to do this test?
                if (payload.goal is not None and
                        payload.goal.metadata is not None):
                    goal_id = payload.goal.metadata.get(
                        'target', {}).get('id', None)
                    self.__topdown_recorder.add(
                        self.__plotter.plot(payload.step_metadata,
                                            payload.step_number,
                                            goal_id))

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
                if config.is_evaluation() or config.is_video_enabled():
                    self.__depth_recorder.add(depth_map)
                if (payload.output_folder and
                        payload.config.is_save_debug_images()):
                    suffix = self._get_suffix(payload, index)
                    depth_map.save(fp=payload.output_folder +
                                   'depth_map' + suffix)

        for index, object_mask in enumerate(
                payload.step_output.object_mask_list):
            if payload.config.is_object_masks_enabled():
                if config.is_evaluation() or config.is_video_enabled():
                    self.__segmentation_recorder.add(object_mask)
                if (payload.output_folder and
                        payload.config.is_save_debug_images()):
                    suffix = self._get_suffix(payload, index)
                    object_mask.save(fp=payload.output_folder +
                                     'object_mask' + suffix)

# if payload.output_folder and payload.config.is_save_debug_images:
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

    def _get_filename_without_timestamp(self, filepath: pathlib.Path):
        return filepath.stem[:-16] + filepath.suffix
