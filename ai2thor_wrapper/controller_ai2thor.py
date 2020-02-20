import os
import ai2thor.controller
from PIL import Image
from controller_mcs import Controller_MCS
from step_output import StepOutput

class Controller_AI2THOR(Controller_MCS):

    __controller = None

    __default_scene = {
        "objects": []
    }

    # Save output image files to debug
    __output_folder = ''

    __step_number = 0

    MAX_ROTATION = 360
    MIN_ROTATION = -360
    MAX_HORIZON = 90
    MIN_HORIZON = -90

    ROTATION_KEY = 'rotation'
    HORIZON_KEY = 'horizon'

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

    # TODO: may need to reevaluate validation strategy/error handling in the future
    # Need a validation/conversion step for what ai2thor will accept as input
    # to keep parameters more simple for the user (in this case, wrapping
    # rotation degrees into an object)
    def validate_and_convert_params(self, **kwargs):
        rotation = kwargs.get(self.ROTATION_KEY, 0)
        horizon = kwargs.get(self.HORIZON_KEY, 0)

        if rotation > self.MAX_ROTATION or rotation < self.MIN_ROTATION:
            print('Value of rotation needs to be between ' + str(self.MIN_ROTATION) + \
                ' and ' + str(self.MAX_ROTATION) + '. Current value: ' + str(rotation) + \
                '. Will be reset to 0.')
            rotation = 0

        if horizon > self.MAX_HORIZON or horizon < self.MIN_HORIZON:
            print('Value of horizon needs to be between ' + str(self.MIN_HORIZON) + \
                ' and ' + str(self.MAX_HORIZON) + '. Current value: ' + str(horizon)+ \
                '. Will be reset to 0.')
            horizon = 0

        rotation_vector = {}
        rotation_vector['y'] = rotation

        return dict(
            rotation=rotation_vector,
            horizon=horizon
        )

    # Override
    def step(self, action, **kwargs):
        self.__step_number += 1

        params = self.validate_and_convert_params(**kwargs)

        return self.wrap_output(self.__controller.step(self.wrap_step(action=action, \
            rotation=params.get(self.ROTATION_KEY), horizon=params.get(self.HORIZON_KEY))))

    def retrieve_action_list(self, scene_event):
        # TODO Return the list of AI2-THOR actions based on the player's simulated age, position (lying, crawling, or standing), and nearby or held objects
        return []

    def retrieve_object_list(self, scene_event):
        # TODO Return the list of objects in the scene by non-descriptive UUID and their corresponding object metadata like the vector from the player to the object
        return []

    def retrieve_metadata(self, scene_event):
        # TODO Return any other metadata from the current scene that we want to pass to the TA1 performer modules
        return {}

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
            action_list=self.retrieve_action_list(scene_event),
            object_list=self.retrieve_object_list(scene_event),
            image=image,
            depth_mask=depth_mask,
            object_mask=object_mask,
            metadata=self.retrieve_metadata(scene_event)
        )

    def wrap_step(self, **kwargs):
        return dict(
            logs=True,
            renderClassImage=True,
            renderDepthImage=True,
            renderObjectImage=True,
            **kwargs
        )

