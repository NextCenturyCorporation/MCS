from .config_manager import ConfigManager
from .controller import Controller
from .controller_logger import ControllerAi2thorFileGenerator
from .controller_logger import ControllerDebugFileGenerator
from .controller_logger import ControllerLogger
from .controller_media import (
    DepthVideoEventHandler,
    DepthImageEventHandler,
    HeatmapVideoEventHandler,
    ImageVideoEventHandler,
    ObjectMaskImageEventHandler,
    SceneImageEventHandler,
    TopdownVideoEventHandler,
    SegmentationVideoEventHandler)
from .history_writer import HistoryEventHandler


class Setup():
    @staticmethod
    def add_subscribers(controller: Controller, config: ConfigManager):
        if controller:
            if config.is_save_debug_json():
                controller.subscribe(
                    ControllerDebugFileGenerator())
                controller.subscribe(ControllerAi2thorFileGenerator())
            if (config.is_evaluation() or config.is_save_debug_images()):
                controller.subscribe(DepthImageEventHandler())
                controller.subscribe(SceneImageEventHandler())
                if (config.is_object_masks_enabled()):
                    controller.subscribe(ObjectMaskImageEventHandler())
            if (config.is_evaluation() or config.is_video_enabled()):
                controller.subscribe(ImageVideoEventHandler())
                controller.subscribe(TopdownVideoEventHandler())
                controller.subscribe(HeatmapVideoEventHandler())
                if (config.is_depth_maps_enabled()):
                    controller.subscribe(DepthVideoEventHandler())
                if (config.is_object_masks_enabled()):
                    controller.subscribe(SegmentationVideoEventHandler())
            controller.subscribe(ControllerLogger())
            # TODO once we remove evaulation code, we can better handle when,
            # this handler subscribes
            controller.subscribe(HistoryEventHandler())
