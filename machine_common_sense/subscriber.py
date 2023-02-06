from .config_manager import ConfigManager
from .controller import Controller
from .controller_logger import (ControllerAi2thorFileGenerator,
                                ControllerDebugFileGenerator, ControllerLogger)
from .controller_media import (DepthImageEventHandler, DepthVideoEventHandler,
                               ImageVideoEventHandler,
                               ObjectMaskImageEventHandler,
                               SceneImageEventHandler,
                               SegmentationVideoEventHandler,
                               TopdownVideoEventHandler,
                               UnityTopdownCameraCombinerEventHandler)
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
        if config.is_top_down_camera():
            controller.subscribe(UnityTopdownCameraCombinerEventHandler())
            # the two top down video generators use the same filename so we
            # shouldn't enable both at the same time
        elif config.is_top_down_plotter():
            controller.subscribe(TopdownVideoEventHandler())
        if (config.is_depth_maps_enabled()):
            controller.subscribe(DepthVideoEventHandler())
        if (config.is_object_masks_enabled()):
            controller.subscribe(SegmentationVideoEventHandler())
    # Add the logger unless the mode is falsey (False, None, etc.)
    if config.get_terminal_output_mode():
        controller.subscribe(ControllerLogger())
    # TODO once we remove evaulation code, we can better handle when,
    # this handler subscribes
    controller.subscribe(HistoryEventHandler())
