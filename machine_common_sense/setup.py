from .config_manager import ConfigManager
from .controller import Controller
from .controller_logger import (ControllerAi2thorFileGenerator,
                                ControllerDebugFileGenerator, ControllerLogger)
from .controller_media import (DepthImageEventHandler, DepthVideoEventHandler,
                               ImageVideoEventHandler,
                               ObjectMaskImageEventHandler,
                               SceneImageEventHandler,
                               SegmentationVideoEventHandler,
                               TopdownVideoEventHandler)
from .history_writer import HistoryEventHandler


def add_subscribers(controller: Controller, config: ConfigManager):
    if not controller:
        return

    if config.is_save_debug_json():
        controller.subscribe(
            ControllerDebugFileGenerator())
        controller.subscribe(ControllerAi2thorFileGenerator())
    if config.is_save_debug_images():
        controller.subscribe(DepthImageEventHandler())
        controller.subscribe(SceneImageEventHandler())
        if (config.is_object_masks_enabled()):
            controller.subscribe(ObjectMaskImageEventHandler())
    if config.is_video_enabled():
        controller.subscribe(ImageVideoEventHandler())
        controller.subscribe(TopdownVideoEventHandler())
        if (config.is_depth_maps_enabled()):
            controller.subscribe(DepthVideoEventHandler())
        if (config.is_object_masks_enabled()):
            controller.subscribe(SegmentationVideoEventHandler())
    controller.subscribe(ControllerLogger())
    # TODO once we remove evaulation code, we can better handle when,
    # this handler subscribes
    controller.subscribe(HistoryEventHandler())
