import glob
import json
import os
import math
import sympy
from PIL import Image

import ai2thor.controller

from machine_common_sense.mcs_action import MCS_Action
from machine_common_sense.mcs_controller import MCS_Controller
from machine_common_sense.mcs_goal import MCS_Goal
from machine_common_sense.mcs_goal_category import MCS_Goal_Category
from machine_common_sense.mcs_object import MCS_Object
from machine_common_sense.mcs_pose import MCS_Pose
from machine_common_sense.mcs_return_status import MCS_Return_Status
from machine_common_sense.mcs_step_output import MCS_Step_Output
from machine_common_sense.mcs_util import MCS_Util

class MCS_Controller_AI2THOR(MCS_Controller):
    """
    MCS Controller class implementation for the AI2-THOR library.

    https://ai2thor.allenai.org/ithor/documentation/
    """

    ACTION_LIST = [item.value for item in MCS_Action]

    # AI2-THOR creates a square grid across the scene that is uses for "snap-to-grid" movement.
    # (This value may not really matter because we set continuous to True in the step input.)
    GRID_SIZE = 0.1

    # How far the player can move with a single step.
    MAX_MOVE_DISTANCE = 0.5

    # The amount of force to offset force values, that seems appropriate for a baby
    # TODO Check with psych team about this about what we should use for a baby, defaulting to 50 now
    MAX_BABY_FORCE = 50.0

    # How far the player can reach.  I think this value needs to be bigger than the MAX_MOVE_DISTANCE or else the
    # player may not be able to move into a position to reach some objects (it may be mathematically impossible).
    # TODO Reduce this number once the player can crouch down to reach and pickup small objects on the floor.
    MAX_REACH_DISTANCE = 1.0

    DEFAULT_HORIZON= 0
    DEFAULT_ROTATION = 0
    DEFAULT_FORCE = 0.5
    DEFAULT_AMOUNT = 0.5
    DEFAULT_DIRECTION = 0
    DEFAULT_OBJECT_MOVE_AMOUNT = 1
    DEFAULT_REWARD = 0

    MAX_ROTATION = 360
    MIN_ROTATION = -360
    MAX_HORIZON = 180
    MIN_HORIZON = -180

    MAX_FORCE = 1
    MIN_FORCE = 0
    MAX_AMOUNT = 1
    MIN_AMOUNT = 0

    ROTATION_KEY = 'rotation'
    HORIZON_KEY = 'horizon'
    FORCE_KEY = 'force'
    AMOUNT_KEY = 'amount'
    OBJECT_DIRECTION_X_KEY = 'objectDirectionX'
    OBJECT_DIRECTION_Y_KEY = 'objectDirectionY'
    OBJECT_DIRECTION_Z_KEY = 'objectDirectionZ'
    RECEPTACLE_DIRECTION_X = 'receptacleObjectDirectionX'
    RECEPTACLE_DIRECTION_Y = 'receptacleObjectDirectionY'
    RECEPTACLE_DIRECTION_Z = 'receptacleObjectDirectionZ'

    # Hard coding actions that effect MoveMagnitude so the appropriate value is set based off of the action
    # TODO: Move this to an enum or some place, so that you can determine special move interactions that way
    FORCE_ACTIONS = ["ThrowObject", "PushObject", "PullObject"]
    OBJECT_MOVE_ACTIONS = ["CloseObject", "OpenObject"]
    MOVE_ACTIONS = ["MoveAhead", "MoveLeft", "MoveRight", "MoveBack"]

    def __init__(self, unity_app_file_path, debug=False, enable_noise=False):
        super().__init__()

        self.__controller = ai2thor.controller.Controller(
            quality='Medium',
            fullscreen=False,
            # The headless flag does not work for me
            headless=False,
            local_executable_path=unity_app_file_path,
            width=600,
            height=400,
            # Set the name of our Scene in our Unity app
            scene='MCS',
            logs=True,
            # This constructor always initializes a scene, so add a scene config to ensure it doesn't error
            sceneConfig={
                "objects": []
            }
        )

        self.on_init(debug, enable_noise)

    def on_init(self, debug=False, enable_noise=False):
        self.__debug_to_file = True if (debug is True or debug is 'file') else False
        self.__debug_to_terminal = True if (debug is True or debug is 'terminal') else False

        self.__enable_noise = enable_noise

        self.__scene_configuration = None
        self.__head_tilt = 0
        self.__output_folder = None # Save output image files to debug
        self.__step_number = 0
        self.__goal = None

    # Override
    def end_scene(self, classification, confidence):
        super().end_scene(classification, confidence)
        # TODO MCS-54 Save classification, confidence, and list of actions (steps) taken in this scene for scoring (maybe save to file?)
        pass

    # Override
    def start_scene(self, config_data):
        super().start_scene(config_data)

        self.__scene_configuration = config_data
        self.__step_number = 0
        self.__goal = self.retrieve_goal(self.__scene_configuration)
        skip_preview_phase = True if 'goal' in config_data and 'skip_preview_phase' in config_data['goal'] else False

        if self.__debug_to_file and config_data['name'] is not None:
            os.makedirs('./' + config_data['name'], exist_ok=True)
            self.__output_folder = './' + config_data['name'] + '/'
            file_list = glob.glob(self.__output_folder + '*')
            for file_path in file_list:
                os.remove(file_path)

        output = self.wrap_output(self.__controller.step(self.wrap_step(action='Initialize', sceneConfig=config_data)))

        if not skip_preview_phase:
            if self.__goal is not None and self.__goal.last_preview_phase_step > 0:
                image_list = output.image_list
                depth_mask_list = output.depth_mask_list
                object_mask_list = output.object_mask_list

                if self.__debug_to_terminal:
                    print('STARTING PREVIEW PHASE...')

                for i in range(0, self.__goal.last_preview_phase_step):
                    output = self.step('Pass')
                    image_list = image_list + output.image_list
                    depth_mask_list = depth_mask_list + output.depth_mask_list
                    object_mask_list = object_mask_list + output.object_mask_list

                if self.__debug_to_terminal:
                    print('ENDING PREVIEW PHASE')

                output.image_list = image_list
                output.depth_mask_list = depth_mask_list
                output.object_mask_list = object_mask_list
            elif self.__debug_to_terminal:
                print('NO PREVIEW PHASE')

        return output

    # TODO: may need to reevaluate validation strategy/error handling in the future
    """
    Need a validation/conversion step for what ai2thor will accept as input
    to keep parameters more simple for the user (in this case, wrapping
    rotation degrees into an object)
    """
    def validate_and_convert_params(self, action, **kwargs):
        moveMagnitude = self.MAX_MOVE_DISTANCE
        rotation = kwargs.get(self.ROTATION_KEY, self.DEFAULT_ROTATION)
        horizon = kwargs.get(self.HORIZON_KEY, self.DEFAULT_HORIZON)
        amount = kwargs.get(self.AMOUNT_KEY, self.DEFAULT_AMOUNT)
        force = kwargs.get(self.FORCE_KEY, self.DEFAULT_FORCE)

        objectDirectionX = kwargs.get(self.OBJECT_DIRECTION_X_KEY, self.DEFAULT_DIRECTION)
        objectDirectionY = kwargs.get(self.OBJECT_DIRECTION_Y_KEY, self.DEFAULT_DIRECTION)
        objectDirectionZ = kwargs.get(self.OBJECT_DIRECTION_Z_KEY, self.DEFAULT_DIRECTION)
        receptacleObjectDirectionX = kwargs.get(self.RECEPTACLE_DIRECTION_X, self.DEFAULT_DIRECTION)
        receptacleObjectDirectionY = kwargs.get(self.RECEPTACLE_DIRECTION_Y, self.DEFAULT_DIRECTION)
        receptacleObjectDirectionZ = kwargs.get(self.RECEPTACLE_DIRECTION_Z, self.DEFAULT_DIRECTION)

        # Check params that should be numbers
        if not MCS_Util.is_number(rotation, self.ROTATION_KEY):
            rotation = self.DEFAULT_ROTATION

        if not MCS_Util.is_number(horizon, self.HORIZON_KEY):
            horizon = self.DEFAULT_HORIZON

        if not MCS_Util.is_number(amount, self.AMOUNT_KEY):
            # The default for open/close is 1, the default for "Move" actions is 0.5
            if action in self.OBJECT_MOVE_ACTIONS:
                amount = self.DEFAULT_OBJECT_MOVE_AMOUNT
            else:
                amount = self.DEFAULT_AMOUNT

        if not MCS_Util.is_number(force, self.FORCE_KEY):
            force = self.DEFAULT_FORCE

        # Check object directions are numbers
        if not MCS_Util.is_number(objectDirectionX, self.OBJECT_DIRECTION_X_KEY):
            objectDirectionX = self.DEFAULT_DIRECTION

        if not MCS_Util.is_number(objectDirectionY, self.OBJECT_DIRECTION_Y_KEY):
            objectDirectionY = self.DEFAULT_DIRECTION

        if not MCS_Util.is_number(objectDirectionZ, self.OBJECT_DIRECTION_Z_KEY):
            objectDirectionZ = self.DEFAULT_DIRECTION

        # Check receptacle directions are numbers
        if not MCS_Util.is_number(receptacleObjectDirectionX, self.RECEPTACLE_DIRECTION_X):
            receptacleObjectDirectionX = self.DEFAULT_DIRECTION

        if not MCS_Util.is_number(receptacleObjectDirectionY, self.RECEPTACLE_DIRECTION_Y):
            receptacleObjectDirectionY = self.DEFAULT_DIRECTION

        if not MCS_Util.is_number(receptacleObjectDirectionZ, self.RECEPTACLE_DIRECTION_Z):
            receptacleObjectDirectionZ = self.DEFAULT_DIRECTION

        # Check that params that should fall in a range are in that range
        horizon = MCS_Util.is_in_range(horizon, self.MIN_HORIZON, self.MAX_HORIZON, self.DEFAULT_HORIZON, \
                self.HORIZON_KEY)
        amount = MCS_Util.is_in_range(amount, self.MIN_AMOUNT, self.MAX_AMOUNT, self.DEFAULT_AMOUNT, self.AMOUNT_KEY)
        force = MCS_Util.is_in_range(force, self.MIN_FORCE, self.MAX_FORCE, self.DEFAULT_FORCE, self.FORCE_KEY)

        # TODO Consider the current "head tilt" value while validating the input "horizon" value.

        # Set the Move Magnitude to the appropriate amount based on the action
        if action in self.FORCE_ACTIONS:
            moveMagnitude = force * self.MAX_BABY_FORCE

        if action in self.OBJECT_MOVE_ACTIONS:
            moveMagnitude = amount

        if action in self.MOVE_ACTIONS:
            moveMagnitude = amount * self.MAX_MOVE_DISTANCE

        # Add in noise if noise is enable
        if self.__enable_noise:
            rotation = rotation * (1 + self.generate_noise())
            horizon = horizon * (1 + self.generate_noise())
            moveMagnitude = moveMagnitude * (1 + self.generate_noise())

        rotation_vector = {}
        rotation_vector['y'] = rotation

        object_vector = {}
        object_vector['x'] = objectDirectionX
        object_vector['y'] = objectDirectionY
        object_vector['z'] = objectDirectionZ

        receptacle_vector = {}
        receptacle_vector['x'] = receptacleObjectDirectionX
        receptacle_vector['y'] = receptacleObjectDirectionY
        receptacle_vector['z'] = receptacleObjectDirectionZ

        return dict(
            objectId=kwargs.get("objectId", None),
            receptacleObjectId=kwargs.get("receptacleObjectId", None),
            rotation=rotation_vector,
            horizon=horizon,
            moveMagnitude=moveMagnitude,
            objectDirection=object_vector,
            receptacleObjectDirection=receptacle_vector
        )

    # Override
    def step(self, action, **kwargs):
        super().step(action, **kwargs)

        if self.__goal.last_step is not None and self.__goal.last_step == self.__step_number:
            print("MCS Warning: You have passed the last step for this scene. Skipping your action. " + \
                    "Please call controller.end_scene() now.")
            return None

        if ',' in action:
            action, kwargs = MCS_Util.input_to_action_and_params(action)

        if not action in self.ACTION_LIST:
            print("MCS Warning: The given action '" + action + "' is not valid. Exchanging it with the 'Pass' action.")
            action = "Pass"

        self.__step_number += 1

        if self.__debug_to_terminal:
            print("===============================================================================")
            print("STEP: " + str(self.__step_number))
            print("ACTION: " + action)

        params = self.validate_and_convert_params(action, **kwargs)

        # Only call mcs_action_to_ai2thor_action AFTER calling validate_and_convert_params
        action = self.mcs_action_to_ai2thor_action(action)

        if self.__goal.last_step is not None and self.__goal.last_step == self.__step_number:
            print("MCS Warning: This is your last step for this scene. All your future actions will be skipped. " + \
                    "Please call controller.end_scene() now.")

        return self.wrap_output(self.__controller.step(self.wrap_step(action=action, **params)))

    def mcs_action_to_ai2thor_action(self, action):
        if action == MCS_Action.CLOSE_OBJECT.value:
            # The AI2-THOR Python library has buggy error checking specifically for the CloseObject action,
            # so just use our own custom action here.
            return "MCSCloseObject"

        if action == MCS_Action.DROP_OBJECT.value:
            return "DropHandObject"

        if action == MCS_Action.OPEN_OBJECT.value:
            # The AI2-THOR Python library has buggy error checking specifically for the OpenObject action,
            # so just use our own custom action here.
            return "MCSOpenObject"

        # if action == MCS_Action.ROTATE_OBJECT_IN_HAND.value:
        #     return "RotateHand"

        return action

    def retrieve_action_list(self, goal, step_number):
        if goal is not None and goal.action_list is not None:
            if step_number < goal.last_preview_phase_step:
                return ['Pass']
            adjusted_step = step_number - goal.last_preview_phase_step
            if len(goal.action_list) > adjusted_step:
                if len(goal.action_list[adjusted_step]) > 0:
                    return goal.action_list[adjusted_step]

        return self.ACTION_LIST

    def retrieve_goal(self, scene_configuration):
        goal_config = scene_configuration['goal'] if 'goal' in scene_configuration else {}

        return MCS_Goal(
            action_list=(goal_config['action_list'] if 'action_list' in goal_config else None),
            info_list=(goal_config['info_list'] if 'type_list' in goal_config else []),
            last_preview_phase_step=(goal_config['last_preview_phase_step'] if 'last_preview_phase_step' \
                    in goal_config else 0),
            last_step=(goal_config['last_step'] if 'last_step' in goal_config else None),
            task_list=(goal_config['task_list'] if 'type_list' in goal_config else []),
            type_list=(goal_config['type_list'] if 'type_list' in goal_config else []),
            metadata=(goal_config['metadata'] if 'metadata' in goal_config else {})
        )

    def retrieve_head_tilt(self, scene_event):
        return scene_event.metadata['agent']['cameraHorizon']

    def retrieve_rotation(self, scene_event):
        return scene_event.metadata['agent']['rotation']['y']

    def retrieve_object_colors(self, scene_event):
        # Use the color map for the final event (though they should all be the same anyway).
        return scene_event.events[len(scene_event.events) - 1].object_id_to_color

    def retrieve_object_list(self, scene_event):
        return sorted([self.retrieve_object_output(object_metadata, self.retrieve_object_colors(scene_event)) for \
                object_metadata in scene_event.metadata['objects'] if object_metadata['visibleInCamera']], key=lambda x: x.uuid)

    def retrieve_object_output(self, object_metadata, object_id_to_color):
        material_list = list(filter(MCS_Util.verify_material_enum_string, [material.upper() for material in \
                object_metadata['salientMaterials']])) if object_metadata['salientMaterials'] is not None else []

        rgb = object_id_to_color[object_metadata['objectId']] if object_metadata['objectId'] in object_id_to_color \
                else [None, None, None]

        if object_metadata['objectBounds'] is None:
            print(f"No bounds for {object_metadata['objectId']}")

        return MCS_Object(
            uuid=object_metadata['objectId'],
            color={
                'r': rgb[0],
                'g': rgb[1],
                'b': rgb[2]
            },
            direction=object_metadata['direction'],
            distance=(object_metadata['distanceXZ'] / self.MAX_MOVE_DISTANCE),
            held=object_metadata['isPickedUp'],
            mass=object_metadata['mass'],
            material_list=material_list,
            position=object_metadata['position'],
            rotation=object_metadata['rotation']['y'],
            visible=(object_metadata['visibleInCamera'] or object_metadata['isPickedUp'])
        )

    def retrieve_pose(self, scene_event):
        # TODO MCS-18 Return pose from Unity in step output object
        return MCS_Pose.STAND.name

    def retrieve_position(self, scene_event) -> dict:
        return scene_event.metadata['agent']['position']

    def retrieve_return_status(self, scene_event):
        # TODO MCS-47 Need to implement all proper step statuses on the Unity side
        return_status = MCS_Return_Status.UNDEFINED.name

        try:
            if scene_event.metadata['lastActionStatus']:
                return_status = MCS_Return_Status[scene_event.metadata['lastActionStatus']].name
        except KeyError:
            print("Return status " + scene_event.metadata['lastActionStatus'] + " is not currently supported.")
        finally:
            return return_status

    def __get_object_from_list(self, objects, target_id):
        '''
        Finds an mcs_object in a list. Uses a generator to return the first item
        or defaults to None if the target isn't found.

        Args:
            objects: list of mcs_objects
            target_id: ID of mcs_object to find

        Returns:
            target: object if found or None
        '''
        return next((o for o in objects if o['objectId'] == target_id), None)

    def _calc_retrieval_reward(self, scene_event):
        '''
        Calculate the reward for the retrieval goal.

        Args:
            scene_event: 

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = self.DEFAULT_REWARD
        goal_id = self.__goal.metadata.get('target_id', None)
        objects = scene_event.metadata['objects']
        goal_object = self.__get_object_from_list(objects, goal_id)
        if goal_object and goal_object['isPickedUp']:
            reward = 1
        return reward

    def _calc_goto_reward(self, scene_event):
        '''
        Calculate the reward for the go to goal.

        Args:
            scene_event:

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward = self.DEFAULT_REWARD
        objects = scene_event.metadata['objects']
        #goal_id = self.__goal.metadata.get('target_id', None)
        goal_id = self.__goal.metadata.get('target_id', 'block_blank_a') # testing
        goal_object = self.__get_object_from_list(objects, goal_id)
        goal_object_xz_center = goal_object['position']['x'], \
            goal_object['position']['z']
        print(goal_object_xz_center)
        bbox3d = goal_object['objectBounds']['objectBoundsCorners']
        print(bbox3d)
        lower_box = bbox3d[:4]
        upper_box = bbox3d[4:]
        # get the corner positions. unique in x and z, ignores y.
        # bounds corners are not always upright/square
        # or is this a precision thing?
        corners = [(pt['x'], pt['z']) for pt in upper_box]
        print(corners)

        a, b, c, d = corners
        poly = sympy.Polygon(a,b,c,d)

        # get agent center xz
        agent_center_xz = scene_event.metadata['agent']['position']['x'], \
            scene_event.metadata['agent']['position']['x']
        print(agent_center_xz)

        # calculate center_line from center of object to agent in the xz plane
        center_line = sympy.Segment(sympy.Point(goal_object_xz_center), \
                sympy.Point(agent_center_xz))

        # does the center_line intersect the polygon?
        intersections = [ i.evalf() for i in poly.intersection(center_line)]

        # check for 0, 1 or more intersections
        # 0 intersections means agent is "inside" of objects. near
        # 1 intersection needs to be evaluated for intersection point
        # more than 1 intersection is a problem unless at a corner
        # two intersections should be identical in that case
        if len(intersections):
            intersection = intersections[0]

            # intersection distance is less than center distance
            distance_to_object = sympy.Point(agent_center_xz).distance(intersection).evalf()
            print(distance_to_object)
            if distance_to_object <= self.MAX_REACH_DISTANCE + 0.5:
                reward = 1
        else:
            reward = 1

        print(f'reward is {reward}')
        return reward

    def _calc_transferral_reward(self, scene_event):
        '''
        Calculate the reward for the transferral goal.

        Args:
            scene_event:

        Returns:
            int: 1 for goal achieved, 0 otherwise

        '''
        reward=self.DEFAULT_REWARD
        relationship = self.__goal.metadata.get('relationship', None)
        if relationship is None or len(relationship) != 3:
            return reward
        
        objects = scene_event.metadata['objects']

        target_id, action, goal_id = relationship
        target_object = self.__get_object_from_list(objects, target_id)
        goal_object = self.__get_object_from_list(objects, goal_id)

        # if either object is None, then return default reward
        if goal_object is None or target_object is None:
            return reward

        # if either objects are held, the goal has not been achieved
        if goal_object['isPickedUp'] or target_object['isPickedUp']:
            return reward

        # ensure distance between objects are below some threshold
        self.MAX_MOVE_DISTANCE

        # actions are next_to or on_top_of
        # or the target is on top of the goal
        
        return reward
    
    def _calculate_default_reward(self, scene_event):
        '''Returns the default reward. Scene event is passed in but ignored.'''
        return self.DEFAULT_REWARD

    def retrieve_reward(self, scene_event):
        '''
        Determine if the agent achieved the objective/task/goal.

        Args:
            scene_event:

        Returns:
            int: reward is 1 if goal achieved, 0 otherwise

        '''
        # TODO maybe this becomes mcs_reward
        # then I can write proper unit tests
        # maybe construct one initially like goal
        # or perhaps this is part of mcs_goal
        # https://github.com/NextCenturyCorporation/MCS/blob/master/python_api/API.md#Goal-Metadata

        #category = self.__goal.metadata.get('category', None)
        category = self.__goal.metadata.get('category', 'GOTO') # testing
        #print(f"agent: {scene_event.metadata['agent']}")

        switch = {
            MCS_Goal_Category.RETRIEVAL.name: self._calc_retrieval_reward,
            MCS_Goal_Category.TRANSFERRAL.name: self._calc_transferral_reward,
            MCS_Goal_Category.GOTO.name: self._calc_goto_reward,
        }

        return switch.get(category, self._calculate_default_reward)(scene_event)

    def save_images(self, scene_event):
        image_list = []
        depth_mask_list = []
        object_mask_list = []

        for index, event in enumerate(scene_event.events):
            scene_image = Image.fromarray(event.frame)
            image_list.append(scene_image)

            # Divide the depth mask by 30 so it doesn't look all white (some odd side effect of the depth grayscaling).
            depth_mask = Image.fromarray(event.depth_frame / 30)
            depth_mask = depth_mask.convert('L')
            depth_mask_list.append(depth_mask)

            object_mask = Image.fromarray(event.instance_segmentation_frame)
            object_mask_list.append(object_mask)

            if self.__debug_to_file and self.__output_folder is not None:
                suffix = '_' + str(self.__step_number) + '-' + str(index) + '.png'
                scene_image.save(fp=self.__output_folder + 'frame_image' + suffix)
                depth_mask.save(fp=self.__output_folder + 'depth_mask' + suffix)
                object_mask.save(fp=self.__output_folder + 'object_mask' + suffix)

        return image_list, depth_mask_list, object_mask_list

    def wrap_output(self, scene_event):
        if self.__debug_to_file and self.__output_folder is not None:
            with open(self.__output_folder + 'ai2thor_output_' + str(self.__step_number) + '.json', 'w') as json_file:
                json.dump({
                    "metadata": scene_event.metadata
                }, json_file, sort_keys=True, indent=4)

        image_list, depth_mask_list, object_mask_list = self.save_images(scene_event)

        step_output = MCS_Step_Output(
            action_list=self.retrieve_action_list(self.__goal, self.__step_number),
            depth_mask_list=depth_mask_list,
            goal=self.__goal,
            head_tilt=self.retrieve_head_tilt(scene_event),
            image_list=image_list,
            object_list=self.retrieve_object_list(scene_event),
            object_mask_list=object_mask_list,
            pose=self.retrieve_pose(scene_event),
            position=self.retrieve_position(scene_event),
            return_status=self.retrieve_return_status(scene_event),
            reward=self.retrieve_reward(scene_event),
            rotation=self.retrieve_rotation(scene_event),
            step_number=self.__step_number
        )

        self.__head_tilt = step_output.head_tilt

        if self.__debug_to_terminal:
            print("RETURN STATUS: " + step_output.return_status)
            print("OBJECTS: " + str(len(step_output.object_list)) + " TOTAL")
            if len(step_output.object_list) > 0:
                for line in MCS_Util.generate_pretty_object_output(step_output.object_list):
                    print("    " + line)

        if self.__debug_to_file and self.__output_folder is not None:
            with open(self.__output_folder + 'mcs_output_' + str(self.__step_number) + '.json', 'w') as json_file:
                json_file.write(str(step_output))

        return step_output

    def wrap_step(self, **kwargs):
        # Create the step data dict for the AI2-THOR step function.
        step_data = dict(
            continuous=True,
            gridSize=self.GRID_SIZE,
            logs=True,
            renderDepthImage=True,
            renderObjectImage=True,
            # Yes, in AI2-THOR, the player's reach appears to be governed by the "visibilityDistance", confusingly...
            visibilityDistance=self.MAX_REACH_DISTANCE,
            **kwargs
        )

        if self.__debug_to_file and self.__output_folder is not None:
            with open(self.__output_folder + 'ai2thor_input_' + str(self.__step_number) + '.json', 'w') as json_file:
                json.dump(step_data, json_file, sort_keys=True, indent=4)

        return step_data

