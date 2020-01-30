import os
import ai2thor.controller
from PIL import Image
from controller import Controller
from step_output import StepOutput

class Controller_AI2_THOR(Controller):

    controller = None

    default_scene = {
        "objects": []
    }

    # Save output image files to debug
    output_folder = ''

    step_number = 0

    def __init__(self, unity_app_path):
        super().__init__()
        self.controller = ai2thor.controller.Controller(
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
            sceneConfig=self.default_scene
        )

    # Override
    def reset_scene(self, config_name, config_data):
        os.makedirs('./' + config_name, exist_ok=True)
        self.output_folder = './' + config_name + '/'
        self.step_number = 0
        return self.wrap_output(self.controller.step(self.wrap_step(action='Initialize', sceneConfig=config_data)))

    # Override
    def step(self, action):
        self.step_number += 1
        return self.wrap_output(self.controller.step(self.wrap_step(action=action)))

    def save_images(self, scene_event):
        scene_image = Image.fromarray(scene_event.frame)
        scene_image.save(fp=self.output_folder + 'frame' + str(self.step_number) + '.png')
        scene_image = Image.fromarray(scene_event.depth_frame / 30)
        scene_image = scene_image.convert('L')
        scene_image.save(fp=self.output_folder + 'depth' + str(self.step_number) + '.png')
        scene_image = Image.fromarray(scene_event.class_segmentation_frame)
        scene_image.save(fp=self.output_folder + 'class' + str(self.step_number) + '.png')
        scene_image = Image.fromarray(scene_event.instance_segmentation_frame)
        scene_image.save(fp=self.output_folder + 'object' + str(self.step_number) + '.png')

    def wrap_output(self, scene_event):
        self.save_images(scene_event)
        return StepOutput(step_number=self.step_number, metadata=scene_event)

    def wrap_step(self, **kwargs):
        return dict(
            logs=True,
            renderClassImage=True,
            renderDepthImage=True,
            renderObjectImage=True,
            **kwargs
        )

