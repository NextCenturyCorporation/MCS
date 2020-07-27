<!-- MCS documentation master file, created by
sphinx-quickstart
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive. -->
# MCS Documentation

# _init_

# mcs


### class machine_common_sense.mcs.MCS()
Defines utility functions for machine learning modules to create MCS controllers and handle config data files.

# mcs_action


### class machine_common_sense.mcs_action.MCS_Action(value)
An enumeration.

# mcs_action_api_desc


### class machine_common_sense.mcs_action_api_desc.MCS_Action_API_DESC(value)
An enumeration.

# mcs_action_keys


### class machine_common_sense.mcs_action_keys.MCS_Action_Keys(value)
An enumeration.

# mcs_controller


### class machine_common_sense.mcs_controller.MCS_Controller(enable_noise=False)
Starts and ends scenes, runs actions on each step, and returns scene output data.

enable_noise

    An optional flag to enable noise in the system for move, amount, force actions

# mcs_controller_ai2thor


### class machine_common_sense.mcs_controller_ai2thor.MCS_Controller_AI2THOR(unity_app_file_path, debug=False, enable_noise=False)
MCS Controller class implementation for the AI2-THOR library.

[https://ai2thor.allenai.org/ithor/documentation/](https://ai2thor.allenai.org/ithor/documentation/)

# mcs_goal


### class machine_common_sense.mcs_goal.MCS_Goal(action_list=None, info_list=None, last_preview_phase_step=0, last_step=None, task_list=None, type_list=None, metadata=None)
Defines attributes of an MCS goal.

action_list

    The list of actions that are available for the scene at each step (outer list index).  Each inner list item is
    a list of action strings. For example, [‘MoveAhead’,’RotateLook,rotation=180’] restricts the actions to either
    ‘MoveAhead’ or ‘RotateLook’ with the ‘rotation’ parameter set to 180. An action_list of None means that all
    actions are always available. An empty inner list means that all actions are available for that specific step.

info_list

    The list of information for the visualization interface associated with this goal.

last_preview_phase_step

    The last step of the preview phase of this scene (scripted in its configuration), if any. Default: 0

last_step

    The last step of this scene. This scene will automatically end following this step.

task_list

    The list of tasks for the visualization interface associated with this goal (secondary to its types).

type_list

    The list of types for the visualization interface associated with this goal, including relevant core domains.

metadata

    The metadata specific to this goal.

# mcs_goal_category


### class machine_common_sense.mcs_goal_category.MCS_Goal_Category(value)
An enumeration.

# mcs_material


### class machine_common_sense.mcs_material.MCS_Material(value)
An enumeration.

# mcs_object


### class machine_common_sense.mcs_object.MCS_Object(uuid='', color=None, dimensions=None, direction=None, distance=- 1.0, distance_in_steps=- 1.0, distance_in_world=- 1.0, held=False, mass=0.0, material_list=None, position=None, rotation=0.0, visible=False)
Defines attributes of an object in the MCS 3D environment.

uuid

    The unique ID of this object, used with some actions.

color

    The “r”, “g”, and “b” pixel values of this object in images from the MCS_Step_Output’s “object_mask_list”.

dimensions

    The dimensions of this object in the environment’s 3D global coordinate system as a list of 8 points (dicts
    with “x”, “y”, and “z”).

direction

    The normalized direction vector of “x”, “y”, and “z” degrees between your position and this object’s.
    Use “x” and “y” as “rotation” and “horizon” params (respectively) in a “RotateLook” action to face this object.

distance

    DEPRECATED. Same as distance_in_steps. Please use distance_in_steps or distance_in_world.

distance_in_steps

    The distance from you to this object in number of steps (“Move” actions) on the 2D X/Z movement grid.

distance_in_world

    The distance from you to this object in the environment’s 3D global coordinate system.

held

    Whether you are holding this object.

mass

    Haptic feedback.  The mass of this object.

material_list

    Haptic feedback.  The material(s) of this object.  See MCS_Material.

position

    The “x”, “y”, and “z” coordinates for the global position of the center of this object’s 3D model.

rotation

    This object’s rotation angle in degrees.

visible

    Whether you can see this object in your camera viewport.

# mcs_pose


### class machine_common_sense.mcs_pose.MCS_Pose(value)
An enumeration.

# mcs_return_status


### class machine_common_sense.mcs_return_status.MCS_Return_Status(value)
An enumeration.

# mcs_reward


### class machine_common_sense.mcs_reward.MCS_Reward()
Reward utility class


#### static calculate_reward(goal: machine_common_sense.mcs_goal.MCS_Goal, objects: Dict, agent: Dict)
Determine if the agent achieved the objective/task/goal.

Args:

    goal: MCS_Goal
    objects: Dict
    agent: Dict

Returns:

    int: reward is 1 if goal achieved, 0 otherwise

# mcs_scene_history

# mcs_step_output


### class machine_common_sense.mcs_step_output.MCS_Step_Output(action_list=None, camera_aspect_ratio=None, camera_clipping_planes=None, camera_field_of_view=0.0, camera_height=0.0, depth_mask_list=None, goal=None, head_tilt=0.0, image_list=None, object_list=None, object_mask_list=None, pose=<MCS_Pose.UNDEFINED: 'UNDEFINED'>, position=None, return_status=<MCS_Return_Status.UNDEFINED: 'UNDEFINED'>, reward=0, rotation=0.0, step_number=0, structural_object_list=None)
Defines attributes of the output from a single step in the MCS 3D environment.

action_list

    The list of all actions that are available for the next step. May be a subset of all possible actions. See
    MCS_Action.

camera_aspect_ratio

    The player camera’s aspect ratio. This will remain constant for the whole scene.

camera_clipping_planes

    The player camera’s near and far clipping planes. This will remain constant for the whole scene.

camera_field_of_view

    The player camera’s field of view. This will remain constant for the whole scene.

camera_height

    The player camera’s height. This will change if the player uses actions like “LieDown”, “Sit”, or “Crouch”.

depth_mask_list

    The list of depth mask images from the scene after the last action and physics simulation were run.
    This is normally a list with five images, where the physics simulation has unpaused and paused again
    for a little bit between each image, and the final image is the state of the environment before your
    next action. The MCS_Step_Output object returned from a call to controller.start_scene will normally
    have a list with only one image, except for a scene with a scripted Preview Phase. A pixel value of
    255 translates to 25 (the far clipping plane) in the environment’s global coordinate system.

goal

    The goal for the whole scene.  Will be None in “Exploration” scenes.

head_tilt

    How far your head is tilted up/down in degrees (between 90 and -90).  Changed by setting the horizon parameter
    in a “RotateLook” action.

image_list

    The list of images from the scene after the last action and physics simulation were run. This is
    normally a list with five images, where the physics simulation has unpaused and paused again for a
    little bit between each image, and the final image is the state of the environment before your next
    action. The MCS_Step_Output object returned from a call to controller.start_scene will normally have
    a list with only one image, except for a scene with a scripted Preview Phase.

object_list

    The list of metadata for all the interactive objects in the scene. For metadata on structural objects like
    walls, please see structural_object_list

object_mask_list

    The list of object mask (instance segmentation) images from the scene after the last action and
    physics simulation were run. This is normally a list with five images, where the physics simulation
    has unpaused and paused again for a little bit between each image, and the final image is the state
    of the environment before your next action. The MCS_Step_Output object returned from a call to
    controller.start_scene will normally have a list with only one image, except for a scene with a
    scripted Preview Phase. The color of each object in the mask corresponds to the “color” property
    in its MCS_Object object.

pose

    Your current pose.  See MCS_Pose.

position

    The “x”, “y”, and “z” coordinates for your global position.

return_status

    The return status from your last action.  See MCS_Return_Status.

reward

    Reward is 1 on successful completion of a task, 0 otherwise.

rotation

    Your current rotation angle in degrees.

step_number

    The step number of your last action, recorded since you started the current scene.

structural_object_list

    The list of metadata for all the structural objects (like walls) in the scene.

# mcs_util


### class machine_common_sense.mcs_util.MCS_Util()
Defines utility functions for MCS classes.


#### NUMBER_OF_SPACES( = 4)
Transforms the given class into a string.

input_value

    The input class.

depth

    The indent depth (default 0).

string

# run_mcs_environment

# run_mcs_eval_samples

# run_mcs_human_input

# run_mcs_intphys_samples

# run_mcs_just_pass

# run_mcs_just_rotate

# run_mcs_last_action

# run_mcs_scene_timer

# Indices and tables


* Index


* Module Index


* Search Page
