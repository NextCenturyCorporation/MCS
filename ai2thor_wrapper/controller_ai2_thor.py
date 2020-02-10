import os
import ai2thor.controller
from PIL import Image
from controller import Controller
from step_output import StepOutput

class Controller_AI2_THOR(Controller):

    __controller = None

    __default_scene = {
        "objects": []
    }

    # Save output image files to debug
    __output_folder = ''

    __step_number = 0

    def __init__(self, unity_app_path):
        super().__init__()
        self.__controller = ai2thor.controller.Controller(
            # The grid size is how far the player can move with a single step
            gridSize=0.1,
            quality='Medium',
            fullscreen=False,
            # The headless flag does not work for me
            headless=False,
            local_executable_path=unity_app_path,
            width=600,
            height=400,
            # Set the name of our Scene in our Unity app
            scene='MCS',
            logs=True,
            # This constructor always initializes a scene, so add a scene config to ensure it doesn't error
            sceneConfig=self.__default_scene
        )

    # Override
    def reset_scene(self, config_name, config_data):
        os.makedirs('./' + config_name, exist_ok=True)
        self.__output_folder = './' + config_name + '/'
        self.__step_number = 0
        return self.wrap_output(self.__controller.step(self.wrap_step(action='Initialize', sceneConfig=config_data)))

    # Override
    def step(self, action):
        self.__step_number += 1
        return self.wrap_output(self.__controller.step(self.wrap_step(action=action)))

    def save_images(self, scene_event):
        scene_image = Image.fromarray(scene_event.frame)
        scene_image.save(fp=self.__output_folder + 'frame' + str(self.__step_number) + '.png')
        # Divide the depth mask by 30 so it doesn't appear all white (some odd side effect of the depth grayscaling).
        depth_mask = Image.fromarray(scene_event.depth_frame / 30)
        depth_mask = depth_mask.convert('L')
        depth_mask.save(fp=self.__output_folder + 'depth' + str(self.__step_number) + '.png')
        class_mask = Image.fromarray(scene_event.class_segmentation_frame)
        class_mask.save(fp=self.__output_folder + 'class' + str(self.__step_number) + '.png')
        object_mask = Image.fromarray(scene_event.instance_segmentation_frame)
        object_mask.save(fp=self.__output_folder + 'object' + str(self.__step_number) + '.png')
        return scene_image, depth_mask, object_mask

    def wrap_output(self, scene_event):
        image, depth_mask, object_mask = self.save_images(scene_event)
        return StepOutput(
            step_number=self.__step_number,
            image=image,
            depth_mask=depth_mask,
            object_mask=object_mask,
            metadata=scene_event
        )

    def wrap_step(self, **kwargs):
        return dict(
            logs=True,
            renderClassImage=True,
            renderDepthImage=True,
            renderObjectImage=True,
            **kwargs
        )

