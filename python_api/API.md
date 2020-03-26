# MCS Python Library: API

- [Python Class: MCS](#MCS)
- [Python Class: MCS_Controller](#MCS_Controller)
- [Python Class: MCS_Goal](#MCS_Goal)
- [Python Class: MCS_Object](#MCS_Object)
- [Python Class: MCS_Step_Output](#MCS_Step_Output)
- [Actions](#Actions)
- [Future Actions (Not Yet Supported)](#Future-Actions)

## MCS

### static create_controller(unity_app_file_path)

Creates and returns an MCS Controller object using the Unity application at the given file path.

#### Parameters

- unity_app_file_path : string\
The file path to the MCS Unity application. The TA2 team will give you this application.

#### Returns

- controller : MCS_Controller\
The MCS controller object.

### static load_config_json_file(config_json_file_path)

Reads and returns the data from the given JSON scene configuration file.

#### Parameters

- config_json_file_path : string\
The file path to the MCS scene configuration JSON file. The TA2 team will give you these files, or you can make them yourself (more details on how to do this are coming soon).

#### Returns

- config_data : dict\
The MCS scene configuration data object.

## MCS_Controller

### end_scene([classification, confidence])

Ends the current MCS scene.

#### Parameters

- classification : string, optional\
Your selected classification for classification tasks. Not required for non-classification tasks.

- confidence : float, optional\
Your classification confidence (between 0 and 1) for classification tasks. Not required for non-classification tasks.

### start_scene(config_data)

Starts a new MCS scene.

#### Parameters

- config_data : dict\
The MCS scene configuration data dict.

#### Returns

- output : MCS_Step_Output\
The MCS scene output data object from the start of the scene.

### step(action[, params])

Runs the given action within the current scene and unpauses the scene’s physics simulation for a few frames.

#### Parameters

- action : string\
Your selected action string from the list of available actions (like "MoveAhead" or "PickupObject").

- params : dict, optional\
Any action-specific parameters.

#### Returns

- output : MCS_Step_Output\
The MCS scene output data object from after the action and the physics simulation were run. Returns None if you have passed the "last_step" of this scene.

## MCS_Goal

### action_list : list of lists of strings, or None

The list of actions that are available for the scene at each step (outer list index).  Each inner list item is a list of action strings. For example, ['MoveAhead','RotateLook,rotation=180'] restricts the actions to either 'MoveAhead' or 'RotateLook' with the 'rotation' parameter set to 180. An action_list of None means that all actions are always available. An empty inner list means that all actions are available for that specific step.

### info_list : list of strings

The list of information for the visualization interface associated with this goal.

### last_step : integer

The last step of this scene. This scene will automatically end following this step.

### task_list : list of strings

The list of tasks for the visualization interface associated with this goal (secondary to its types).

### type_list : list of strings

The list of types for the visualization interface associated with this goal, including the relevant MCS core domains.

### metadata : dict

The metadata specific to this goal. More details coming soon.

## MCS_Object

### uuid : string

The unique ID of this object, used with some actions.

### color : dict

The "r", "g", and "b" pixel values of this object in images from the MCS_Step_Output's "object_mask_list".

### direction : dict

The normalized direction vector of "x", "y", and "z" degrees between your position and this object's. Use "x" and "y" as "rotation" and "horizon" params (respectively) in a "RotateLook" action to face this object.

### distance : float

The distance along the 2-dimensional X/Z grid from you to this object in number of steps ("Move" actions).

### held : boolean

Whether you are holding this object.

### mass : float

Haptic feedback. The mass of this object.

### material_list : list of strings

Haptic feedback. The material(s) of this object. Possible materials: "Metal", "Wood", "Plastic", "Glass", "Ceramic", "Stone", "Fabric", "Rubber", "Food", "Paper", "Wax", "Soap", "Sponge", "Organic".

### point_list : list of dicts

The list of 3D points (dicts with "x", "y", and "z") that form the outer shape of this object.

### visible : boolean

Whether you can see this object in your camera viewport.

## MCS_Step_Output

### action_list : list of strings

The list of all actions (like "MoveAhead" or "PickupObject") that are available for the next step. May be a subset of all possible actions.

### depth_mask_list : list of Pillow.Image objects

The list of depth mask images from the scene after the last action and physics simulation were run. This is usually just a list with a single image, except for the MCS_Step_Output object returned from a call to controller.start_scene for a scene with a scripted Preview Phase.

### goal : MCS_Goal

The goal for the whole scene. Will be None in "Exploration" (a.k.a. "Free Play", or "Playroom") scenes.

### head_tilt : float

How far your head is tilted up/down in degrees (between 90 and -90). Changed by setting the "horizon" parameter in a "RotateLook" action.

### image_list : list of Pillow.Image objects

The list of images from the scene after the last action and physics simulation were run. This is usually just a list with a single image, except for the MCS_Step_Output object returned from a call to controller.start_scene for a scene with a scripted Preview Phase.

### object_list : list of MCS_Object objects

The list of metadata for all objects in the scene.

### object_mask_list : list of Pillow.Image objects

The list of object mask images from the scene after the last action and physics simulation were run. This is usually just a list with a single image, except for the MCS_Step_Output object returned from a call to controller.start_scene for a scene with a scripted Preview Phase.

### pose : string

Your current pose. Either "LIE", "CRAWL", "SQUAT", or "STAND".

### return_status : string

The return status from your last action.

### step_number : integer

The step number of your last action, recorded since you started the current scene.

## Actions

### MoveAhead

Move yourself ahead based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### MoveRight

Move yourself to your right based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### MoveLeft

Move yourself to your left based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### MoveBack

Move yourself back based on your current viewport.

#### Parameters

- amount : float\
Movement percentage between 0 (no distance) and 1 (maximum distance). Default: 0.5

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot move ahead because your path is obstructed.

### RotateLook

Rotate your viewport left/right and/or up/down based on your current viewport.

#### Parameters

- rotation : float\
Rotation degrees around the Y axis to change your look angle (left/right).
- horizon : float\
Rotation degrees around the X axis to change your look angle (up/down). This affects your current "head tilt".

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.

### PickupObject

Pickup a nearby object and hold it in your hand. This action incorporates reaching out your hand in front of you, opening your fingers, and grabbing the object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.

#### Returns

- "SUCCESSFUL"
- "HAND_IS_FULL"\
If you cannot pickup the object because your hand is full.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "NOT_PICKUPABLE"\
If the object itself cannot be picked up.
- "OBSTRUCTED"\
If you cannot pickup the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot pickup the object because you are out of reach.

### PutObject

Place an object you are holding into/onto a nearby receptacle object.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Defaults to the first held object.
- receptacleObjectId : string\
The "uuid" of the target receptacle. Required unless the "receptacleObjectDirection" properties are given.
- receptacleObjectDirectionX : float, optional\
The X of the directional vector pointing to the target receptacle based on your current viewport. Can be used in place of the "receptacleObjectId" property.
- receptacleObjectDirectionY : float, optional\
The Y of the directional vector pointing to the target receptacle based on your current viewport. Can be used in place of the "receptacleObjectId" property.
- receptacleObjectDirectionZ : float, optional\
The Z of the directional vector pointing to the target receptacle based on your current viewport. Can be used in place of the "receptacleObjectId" property.

#### Returns

- "SUCCESSFUL"
- "NOT_HELD"\
If you cannot place the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" or "receptacleObjectDirection" vectors is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" or "receptacleObjectId" (or object corresponding to the "objectDirection" or "receptacleObjectDirection" vectors) is not a real object.
- "NOT_RECEPTACLE"\
If the receptacleObjectId is not a receptacle object.
- "OBSTRUCTED"\
If you cannot place the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot place the object because you are out of reach of the receptacle.

### DropObject

Drop an object you are holding.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Defaults to the first held object.

#### Returns

- "SUCCESSFUL"
- "NOT_HELD"\
If you cannot drop the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### ThrowObject

Throw an object you are holding.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Defaults to the first held object.
- (Not Yet Supported) rotation : float\
Rotation degrees around the Y axis to throw the held object (left/right).
- (Not Yet Supported) horizon : float\
Rotation degrees around the X axis to throw the held object (up/down).
- force : float\
The amount of force, from 0 to 1, used to throw the held object. Default: 0.5

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.
- "NOT_HELD"\
If you cannot drop the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### PullObject

Pull a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- (Not Yet Supported) rotation : float\
Rotation degrees around the Y axis to pull the target object (left/right).
- (Not Yet Supported) horizon : float\
Rotation degrees around the X axis to pull the target object (up/down).
- force : float\
The amount of force, from 0 to 1, used to pull the target object. Default: 0.5

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "OBSTRUCTED"\
If you cannot pull the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot pull the object because you are out of reach.

### PushObject

Push a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- (Not Yet Supported) rotation : float\
Rotation degrees around the Y axis to push the target object (left/right).
- (Not Yet Supported) horizon : float\
Rotation degrees around the X axis to push the target object (up/down).
- force : float\
The amount of force, from 0 to 1, used to push the target object. Default: 0.5

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360] or the horizon is not between [-180, 180], 0 will be used in place of each invalid parameter.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "OBSTRUCTED"\
If you cannot push the object because your reach is obstructed.
- "OUT_OF_REACH"\
If you cannot push the object because you are out of reach.

### OpenObject

Open a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- amount : float\
The amount to open the object between 0 (completely closed) and 1 (completely opened). Default: 1

#### Returns

- "SUCCESSFUL"
- "IS_OPENED_COMPLETELY"\
If you cannot open the object because it is completely opened.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "NOT_OPENABLE"\
If you cannot open the object because it is not openable.
- "OUT_OF_REACH"\
If you cannot open the object because you are out of reach.
- "OBSTRUCTED"\
If you cannot open the object because you are obstructed.

### CloseObject

Close a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- amount : float\
The amount to close the object between 0 (completely opened) and 1 (completely closed). Default: 1

#### Returns

- "SUCCESSFUL"
- "IS_CLOSED_COMPLETELY"\
If you cannot close the object because it is completely closed.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.
- "NOT_OPENABLE"\
If you cannot close the object because it is not openable.
- "OUT_OF_REACH"\
If you cannot close the object because you are out of reach.
- "OBSTRUCTED"\
If you cannot close the object because you are obstructed.

### Pass

Do nothing.

#### Returns

- "SUCCESSFUL"

## Future Actions

(Not Yet Supported)

### LieDown

Change pose to "LIE".

#### Parameters

- rotation : float\
Rotation around the Y axis to change your look angle.

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the rotation is not between [-360, 360], 0 will be used in place of the invalid parameter.

### Crawl

Change pose to "CRAWL".

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot enter "CRAWL" pose because your path above you is obstructed.
- "WRONG_POSE"\
If you cannot enter "CRAWL" pose because you not in "LIE" pose face-down or are not in "CRAWL" or "STAND" pose.

### Squat

Change pose to "SQUAT".

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot enter "SQUAT" pose because your path above you is obstructed.
- "WRONG_POSE"\
If you cannot enter "SQUAT" pose because you are not in "CRAWL" or "STAND" pose.

### Stand

Change pose to "STAND".

#### Returns

- "SUCCESSFUL"
- "OBSTRUCTED"\
If you cannot enter "STAND" pose because your path above you is obstructed.
- "WRONG_POSE"\
If you cannot enter "STAND" pose because you are not in "SQUAT" pose.

### RotateObject

Rotate a held object.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- rotationX : float\
Rotation degrees around the X axis.
- rotationY : float\
Rotation degrees around the Y axis.
- rotationZ : float\
Rotation degrees around the Z axis.

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the X, Y, or Z is not between [-360, 360], 0 will be used in place of each invalid parameter.
- "NOT_HELD"\
If you cannot drop the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### RotateObject

Rotate a nearby object.

#### Parameters

- objectId : string, optional\
The "uuid" of the target object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- rotationX : float\
Rotation degrees around the X axis.
- rotationY : float\
Rotation degrees around the Y axis.
- rotationZ : float\
Rotation degrees around the Z axis.

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the X, Y, or Z is not between [-360, 360], 0 will be used in place of each invalid parameter.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### RotateObjectInHand

Rotate a held object.

#### Parameters

- objectId : string, optional\
The "uuid" of the held object. Required unless the "objectDirection" properties are given.
- objectDirectionX : float, optional\
The X of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionY : float, optional\
The Y of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- objectDirectionZ : float, optional\
The Z of the directional vector pointing to the target object based on your current viewport. Can be used in place of the "objectId" property.
- rotationX : float\
Rotation degrees around the X axis.
- rotationY : float\
Rotation degrees around the Y axis.
- rotationZ : float\
Rotation degrees around the Z axis.

#### Returns

- "SUCCESSFUL"
- "SUCCESSFUL_WITH_INVALID_PARAMETERS"\
If the X, Y, or Z is not between [-360, 360], 0 will be used in place of each invalid parameter.
- "NOT_HELD"\
If you cannot drop the object because you are not holding it.
- "NOT_INTERACTABLE"\
If the object corresponding to the "objectDirection" vector is not an interactable object.
- "NOT_OBJECT"\
If the object corresponding to the "objectId" (or object corresponding to the "objectDirection" vector) is not a real object.

### BangObject

TODO

### ChangeGrip

TODO

### Cry

TODO

### MoveHand

TODO

### Point

TODO

### Speak

TODO

### Stare

TODO

### SuckOnObject

TODO

### SwatObject

TODO

### SwitchHand

TODO

### ToggleObject

TODO

### WaveObject

TODO

