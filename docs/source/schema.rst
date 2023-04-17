Scene File Schema
#################

Scenes
======

A **scene** is a JSON object (called a :ref:`scene config<Scene Config>`) that, when passed to the MCS Unity application via the machine_common_sense python library, describes the objects, materials (colors and textures), environmental features, and scripted actions that are present in a specific instance of the MCS 3D simulation environment.

Scene Config
************

Example:

.. code-block:: json

    {
        "name": "Example MCS Scene Configuration",
        "verison": 2,
        "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
        "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
        "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
        "roomDimensions": {
            "x": 10,
            "y": 3,
            "z": 10
        },
        "roomMaterials": {
            "left":"AI2-THOR/Materials/Walls/DrywallGreen",
            "front":"AI2-THOR/Materials/Walls/Drywall4Tiled",
            "right": "AI2-THOR/Materials/Walls/Drywall4Tiled",
            "back": "AI2-THOR/Materials/Walls/Drywall4Tiled"
        },
        "performerStart": {
            "position": {
                "x": -1,
                "z": -1
            },
            "rotation": {
                "x": 0,
                "y": 90
            }
        },
        "objects": [{
            "id": "sofa",
            "type": "sofa_1",
            "mass": 50,
            "shows": [{
                "stepBegin": 0,
                "position": {
                    "x": -2,
                    "y": 0,
                    "z": -4.25
                }
            }]
        }, {
            "id": "ball_a",
            "type": "sphere",
            "mass": 0.05,
            "materials": ["AI2-THOR/Materials/Plastics/BlueRubber"],
            "pickupable": true,
            "salientMaterials": ["plastic"],
            "shows": [{
                "stepBegin": 0,
                "position": {
                    "x": 0,
                    "y": 0.025,
                    "z": 1
                },
                "scale": {
                    "x": 0.025,
                    "y": 0.025,
                    "z": 0.025
                }
            }]
        }]
    }


Each **scene config** has the following properties:

- `ceilingMaterial` (string, optional): The material (color/texture) for the room's ceiling. See the :ref:`material list <Material List>` for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/Drywall"`
- `floorMaterial` (string, optional): The material (color/texture) for the room's floor. See the :ref:`material list <Material List>` for options. Default (v0.0.3+): `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `floorProperties` (:ref:`physics config <Physics Config>`, optional): Enable custom friction, bounciness, and/or drag on the floor. Default: see :ref:`physics config <Physics Config>`.
- `floorTextures` (:ref:`material position config list <Material Position Config>`, optional): A list of materials to apply to specific areas of the room's floor. These materials override the material set by `floorMaterial` for those specific areas. Default: none
- `goal` (:ref:`goal config <Goal Config>`, optional): The goal for the scene. Default: none
- `holes` (:ref:`grid config list <Grid Config>`, optional): The list of X/Z coordinates corresponding to one or more holes in the room's floor. Coordinates must be integers. Holes are always size 1x1 centered on the given X/Z coordinate. Adjacent holes are combined. Y coordinates are ignored. Holes are too deep to escape. Default: none
- `intuitivePhysics` (bool, optional): Specific performer and room setup for intuitive physics scenes.
- `isometric` (bool, optional): Specific performer and room setup for agent scenes.
- `lava` (:ref:`grid config list <Grid Config>`, optional): The list of X/Z coordinates corresponding to one or more pools of lava in the room's floor. Coordinates must be integers. Each lava pool is always size 1x1 centered on the given X/Z coordinate. Adjacent pools of lava are combined. Y coordinates are ignored. Stepping in lava will either cause a reward penalty or immediately end the scene, depending on your settings. Default: none
- `name` (string, required): A unique name for the scene used for our logs. Default: the filename
- `objects` (:ref:`object config <Object Config>` array, optional): The objects for the scene. Default: `[]`
- `performerStart` (:ref:`transform config <Transform Config>`, optional): The starting position and rotation of the performer (the "player"). Only the `position.x`, `position.z`, `rotation.x` (head tilt), and `rotation.y` properties are used. Default: `{ "position": { "x": 0, "z": 0 }, "rotation": { "y": 0 } }`
- `restrictOpenDoors` (bool, optional): If there are multiple doors in a scene, only allow one door to ever be opened. Default: `false`
- `restrictOpenObjects` (bool, optional): If there are multiple openable objects in a scene, including containers and doors, only allow one of them to ever be opened. Default: `false`
- `roomDimensions` (Vector3, optional): Specify the size of the room, not including the thickness of walls, floor, and ceiling.  If omitted or set to 0, 0, 0, the default will be used.  Note: There is a maximum visibility which for objects and structures beyond will not be rendered.  Use caution when creating rooms where the maximum distance exceeds this maximum visibility.  The maximum visibility is 15 meters. Default: 10, 3, 10.
- `roomMaterials` (:ref:`room material config <Room Material Config>`, optional): The materials for each individual wall.  For any individual wall not provided, or all outer walls if object is not provided, they will use 'wallMaterial' property.
- `partitionFloor` (:ref:`floor partition config <Floor Partition Config>`, optional): Settings to partition the floor in specific ways. Overrides the `floorTextures`, `holes`, and `lava` configurations. Default: none
- `version` (int, optional): The version of this scene configuration. Default: the latest version
- `wallProperties` (:ref:`physics config <Physics Config>`, optional): Enable custom friction, bounciness, and/or drag on the walls. Default: see :ref:`physics config <Physics Config>`.
- `wallMaterial` (string, optional): The material (color/texture) for the room's four outer walls. See the :ref:`material list <Material List>` for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/DrywallBeige"`
- `toggleLights` (:ref:`step begin and end config config <Step Begin And End Config>` array, optional): The steps at which the lights in the scene should be turned off and back on. Default: `[]`

Object Config
*************

Each **object config** has the following properties:

- `id` (string, required): The object's unique ID.
- `type` (string, required): The object's type from the :ref:`object list <Object List>`.
- `actions` (:ref:`action config list <Action Config>`, optional): Specific animations to start at specific action steps. Available animations are based on the object's type. Currently animations are only available for :ref:`agent <Agents>` types. Default: none
- `agentMovement` (:ref:`agent movement config <Agent Movement>`, optional): The movement sequence for an individual :ref:`agent <Agents>`. Default: none
- `agentSettings` (:ref:`agent settings config <Agent Settings>`, optional): Specific configuration settings for :ref:`agent <Agents>` types. Default: none
-  associatedWithAgent` (string, optional):  The agent holding this object. Objects with this property have the following restrictions --- Must have a shape of ball, a bounding box scaled between 0.2 and 0.25, and a scale of (1,1,1). Default: ""
- `centerOfMass` (:ref:`vector config <Vector Config>`, optional): The object's center of mass/gravity, if not the default. Default: none
- `centerOfMass` (:ref:`vector config <Vector Config>`, optional): The object's center of mass/gravity, if not the default. Default: none
- `changeMaterials` (:ref:`change_materials config <Change Materials Config>` array, optional): The steps on which to change the material(s) (colors/textures) used on the object, and the new materials to use. See the :ref:`material list <Material List>` for options. Default: `[]`
- `forces` (:ref:`force config <Force Config>` array, optional): The steps on which to apply `force <https://docs.unity3d.com/ScriptReference/Rigidbody.AddForce.html>`_ to the object. The config `vector` describes the amount of force (in Newtons) to apply in each direction using the global coordinate system. Resets all existing forces on the object to 0 before applying the new force. Default: `[]`
- `ghosts` (:ref:`step begin and end config config <Step Begin And End Config>` array, optional): TBD
- `hides` (:ref:`single step config <Single Step Config>` array, optional): The steps on which to hide the object, completely removing its existence from the scene until it is shown again (see the `shows` property). Useful if you want to have impossible events (spontaneous disappearance). Default: `[]`
- `lidAttachment` :ref:`lid config <Lid Config>`, optional): If set this object will attach to the `lidAttachmentObjId` at the `stepBegin`. Default: none
- `kinematic` (boolean, optional): If true, the object will ignore all forces including gravity. See Unity's `isKinematic property <https://docs.unity3d.com/ScriptReference/Rigidbody-isKinematic.html>`_. Usually paired with `structure`. Default: `false`
- `locationParent` (string, optional): The `id` of another object in the scene. If given, this object's `shows.position` and `shows.rotation` will both start from the position and rotation of the `locationParent` object rather than from `0`. Default: none
- `mass` (float, optional): The mass of the object, which affects the physics simulation. Default: `1`
- `materials` (string array, optional): The material(s) (colors/textures) of the object. An object `type` may use multiple individual materials; if so, they must be listed in a specific order. Most non-primitive objects already have specific material(s). See the :ref:`material list <Material List>` for options. Default: none
- `materialFile` (string, optional): Deprecated (please use `materials` now). The material (color/texture) of the object. Most non-primitive objects already have specific material(s). See the :ref:`material list <Material List>` for options. Default: none
- `maxAngularVelocity` (force, optional): Override the object's maximum angular velocity in the physics simulation, affecting how it turns and rolls. Default: `7`
- `moveable` (boolean, optional): Whether the object should be moveable, if it is not already moveable based on its `type`. Default: depends on `type`
- `moves` (:ref:`move config<Move Config>` array, optional): The steps on which to move the object, moving it from one position in the scene to another. The config `vector` describes the amount of position to change, added to the object's current position. Useful if you want to move objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `nullParent` (:ref:`transform config <Transform Config>`, optional): Whether to wrap the object in a null parent object. Useful if you want to rotate an object by a point other than its center point. Default: none
- `openable` (boolean, optional): Whether the object should be openable, if it is not already openable based on its `type`. Default: depends on `type`
- `opened` (boolean, optional): Whether the object should begin opened. Must also be `openable`. Default: `false`
- `openClose` (:ref:`open close config <Open Close Config>`, optional): The steps where an object is opened or closed by the system.  Default: None
- `lips` (:ref:`platform lips config <Platform Lips Config>`, optional): The sides of a platform to add lips. Default: None
- `locked` (boolean, optional): Whether to lock the container at the start of the simulation.  Locked containers cannot be opened.  Default: false
- `physics` (boolean, optional): Whether to enable physics simulation on the object. Automatically `true` if `moveable`, `openable`, `pickupable`, or `receptacle` is `true`. Use `physics` if you want to enable physics but don't want to use any of those other properties. Default: `false`
- `physicsProperties` (:ref:`physics config <Physics Config>`, optional): Enable custom friction, bounciness, and/or drag on the object. Default: see :ref:`physics config <Physics Config>`.
- `pickupable` (boolean, optional): Whether the object should be pickupable, if it is not already openable based on its `type`. Pickupable objects are also automatically `moveable`. Default: depends on `type`
- `receptacle` (boolean, optional): TBD
- `resetCenterOfMass` (boolean, optional): Whether to reset the object's center of mass/gravity to its default value once the object's Y velocity becomes more than 0.1. Default: `false`
- `resizes` (:ref:`size config <Size Config>` array, optional): The steps on which to resize the object. The config `size` is multiplied by the object's current size. Useful if you want to have impossible events (spontaneous resizing). Default: `[]`
- `rotates` (:ref:`move config <Move Config>` array, optional): The steps on which to rotate the object. The config `vector` describes the amount of rotation (in degrees) to change, added to the object's current rotation. Useful if you want to rotate objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `salientMaterials` (string array, optional)
- `seesaw` (bool, optional): Whether this object should move like a seesaw. Default: `false`
- `shows` (:ref:`show config <Show Config>` array, optional): The steps on which to show the object, adding its existence to the scene. Each object begins hidden within the scene, so each object should have at least one element in its `shows` array to be useful. Default: `[]`
- `shrouds` (:ref:`step begin and end config config <Step Begin And End Config>` array, optional): The steps on which to shroud the object, temporarily making it invisible, but moving with its existing intertia and able to collide with objects. Useful if you want to have impossible events. Default: `[]`
- `states` (string array array, optional): An array of string arrays containing the state label(s) of the object at each step in the scene, returned by the simulation environment in the object's output metadata. Default: `[]`
- `structure` (boolean, optional): Whether the object is a structural part of the environment. Usually paired with `kinematic`. Default: `false`
- `teleports` (:ref:`teleport config <Teleport Config>` array, optional): The steps on which to teleport the object, teleporting it from one position in the scene to another. The config `position` describes the object's end position in global coordinates and is not affected by the object's current position. Useful if you want to have impossible events (spontaneous teleportation). Default: `[]`
- `togglePhysics` (:ref:`single step config <Single Step Config>` array, optional): The steps on which to toggle physics on the object. Useful if you want to have scripted movement in specific parts of the scene. Can work with the `kinematic` property. Default: `[]`
- `torques` (:ref:`force config <Force Config>` array, optional): The steps on which to apply `torque <https://docs.unity3d.com/ScriptReference/Rigidbody.AddTorque.html>`_ to the object. The config `vector` describes the amount of torque (in Newtons) to apply in each direction using the global coordinate system. Resets all existing torques on the object to 0 before applying the new torque. Default: `[]`

Goal Config
***********

Each **goal config** has the following properties:

- `action_list` (string array array, optional): The list of actions that are available for the scene at each step (outer list index).  Each inner list item is a list of action strings. For example, `['MoveAhead','RotateLook,rotation=180']` restricts the actions to either `'MoveAhead'` or `'RotateLook'` with the `'rotation'` parameter set to `180`. An empty outer `action_list` means that all actions are always available. An empty inner list means that all actions are available for that specific step. Default: none
- `info_list` (array, optional): A list of information for the visualization interface associated with this goal. Default: none
- `last_preview_phase_step` (integer, optional): The last step of the preview phase of this scene, if any. Default: -1
- `last_step` (integer, optional): The last step of this scene. This scene will automatically end following this step.
- `metadata` (:ref:`goal metadata config <Goal Metadata Config>`, optional): The metadata specific to this goal. Default: none
- `task_list` (string array, optional): A list of types for the visualization interface associated with this goal, including the relevant MCS core domains. Default: none
- `type_list` (string array, optional) A list of tasks for the visualization interface associated with this goal (secondary to its types).

Goal Metadata Config
********************

Each **goal metadata config** has the following properties:

(Coming soon!)

Action Config
*************

Each **action config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization. If the step begin occurs while the agent is interacting and there is no step end or the step end is after the agent interaction is complete, the animation will play after the interaction is complete. If the agent is moving, triggering an action will pause the agents movement until the action is complete either by finishing the animation or by reaching its step end. If it is a loop animation with no step end the agent will no longer move and endlessly perform its action. The exception to this is if the step begin of the movement configuration is after the step begin of the action. In that case the movement will begin and halt the action.
- `stepEnd` (integer, optional): The step on which the action should end. Must be non-negative. The animation will play infinitely if its isLoopAnimation is true. If stepEnd is not configured and isLoopAnimation is false then the animation will play once. For example, a jump animation with stepBegin of 2 and stepEnd of 4 will stop immediately at that stepEnd. However, you can set that jump to isLoopAnimation true and have its stepEnd be 104 so it will loop and stop at step 104. Triggering a step end while interacting with the agent will end the animation once the interaction is complete.
- `id` (string, required): The ID of the animation (action) to start. For a full list of available agent animations, please see :ref:`Agent Animations <Agent Animations>`.
- `isLoopAnimation` (bool, optional): Whether the newly set animation should loop after being played. If false, the agent animation will reset to idle after being played once. Default: `false`

Sequence Config
*************

Each **sequence config** has the following properties:

- `animation` (string, required): The animation to play while the agent moves to the next end point
- `endPoint` (:ref:`vector config <Vector Config>`, required): The end point of this part of the movement path

Agent Movement Config
*************

Each **agent movement config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization. If the step begin of the movement configuration is after the step begin of a currently playing action the movement will begin and immediately stop the action. If a step begin is triggered while the agent is interacting, the agent will begin its movement after the interaction is complete. If a step begin is triggered while the agent is interacting, but an action's step begin was also triggered during the interaction at a later step, the action will play first then agent will begin its movement. 
- `repeat` (bool, required): Whether the movement sequence should repeat after reaching the end. If true, once the last point is reached, the agent will move from its last end point to the first end point automatically. This means the last configured end point in the sequence does NOT need to be equal to the first end point for repeating to work. Once the first point is automatically reached, the agent will continue the sequence from the beginning.
- `sequence` (:ref:`vector config <Vector Config>` array, required): The sequence that the agent will follow. Only x and z coordinates are necessary. If a y is given it will be ignored.

Agent Settings Config
*********************

Each **agent settings config** has the following properties:

- `chest` (integer, optional): The chest and shirt (or dress) to use for the specific agent. See :ref:`Chest Options <Chest Options>` for the full list of available options. Default: `0`
- `chestMaterial` (integer, optional): The color/texture to use for the shirt of the specific agent. See :ref:`Chest Material Options <Chest Material Options>` for the full list of available options. Default: `0`
- `eyes` (integer, optional): The eyes to use for the specific agent. See :ref:`Eye Options <Eye Options>` for the full list of available options. Default: `0`
- `feet` (integer, optional): The feet and shoes to use for the specific agent. See :ref:`Feet Options <Feet Options>` for the full list of available options. Default: `0`
- `feetMaterial` (integer, optional): The color/texture to use for the shoes of the specific agent. See :ref:`Feet Material Options <Feet Material Options>` for the full list of available options. Default: `0`
- `glasses` (integer, optional): The glasses to use for the specific agent. The glasses are only visible if `showGlasses` is true. See :ref:`Glasses Options <Glasses Options>` for the full list of available options. Default: `0`
- `hair` (integer, optional): The hair (and possibly hat, for some options) to use for the specific agent. See :ref:`Hair Options <Hair Options>` for the full list of available options. Default: `0`
- `hairMaterial` (integer, optional): The color/texture to use for the hair of the specific agent. See :ref:`Hair Material Options <Hair Material Options>` for the full list of available options. Default: `0`
- `hatMaterial` (integer, optional): The color/texture to use for the hat (if one is present) of the specific agent. See :ref:`Hair Material Options <Hair Material Options>` for the full list of available options. Default: `0`
- `hideHair` (boolean, optional): Whether to hide hair on the specific agent. This ignores any configured `hair` option. Default: `false`
- `isElder` (boolean, optional): Whether to give the specific agent an elderly (wrinkly) face and skin. Default: `false`
- `legs` (integer, optional): The legs and pants/shorts/skirt to use for the specific agent. Please note that the legs may be overridden by some `chest` options. See :ref:`Legs Options <Legs Options>` for the full list of available options. Default: `0`
- `legsMaterial` (integer, optional): The color/texture to use for the pants/shorts/skirt of the specific agent. See :ref:`Legs Material Options <Legs Material Options>` for the full list of available options. Default: `0`
- `showBeard` (boolean, optional): Whether to show a beard on the specific agent. The agent type must be male. The beard's color will match the `hairMaterial`. Default: `false`
- `showGlasses` (boolean, optional): Whether to show glasses on the specific agent. Default: `false`
- `showTie` (boolean, optional): Whether to show a tie on the specific agent. The `chest` option must also be compatible with a tie. Default: `false`
- `skin` (integer, optional): The skin to use for the specific agent. See :ref:`Skin Options <Skin Options>` for the full list of available options. Default: `0`
- `tie` (integer, optional): The tie to use for the specific agent. A tie is only visible if `showTie` is true, and if the `chest` option is compatible with a tie. See :ref:`Tie Options <Tie Options>` for the full list of available options. Default: `0`
- `tieMaterial` (integer, optional): The color/texture to use for the tie (if one is present) of the specific agent. See :ref:`Tie Material Options <Tie Material Options>` for the full list of available options. Default: `0`

Change Materials Config
***********************

Each **change materials config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `materials` (string array, required): The new materials for the object.

Floor Partition Config
**********************

Each **floor partition config** has the following properties:

- `leftHalf` (float, optional): Percentage of the left half of the room to set as lava. Max value of `1`. Default: `0`
- `rightHalf` (float, optional): Percentage of the right half of the room to set as lava. Max value of `1`. Default: `0`

Force Config
************

Each **force config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `vector` (:ref:`vector config <Vector Config>`, required): The coordinates to describe the movement. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `impulse` (bool, optional): Whether to apply the force using Unity's impulse force mode, rather than the default force mode. Default: `false`
- `relative` (bool, optional): Whether to apply the force using the object's relative coordinate system, rather than the environment's absolute coordinate system. Default: `false`
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`

Grid Config
*************

Each **grid config** has the following properties:

- `x` (integer)
- `z` (integer)

Lid Config
*************

Each **lid config** has the following properties:

- `stepBegin` (integer, required): The step the lid will attach to the object specified by the `lidAttachmentObjId`.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `lidAttachmentObjId` (string, required): The id of the object that the lid will attach to.

Lip Gaps Config
**************

Each **lip gaps config** has the following properties:

- `front` (:ref:`lip gaps span config list <Lip Gaps Span Config>`):: Gaps on the positive Z axis
- `back` (:ref:`lip gaps span config list <Lip Gaps Span Config>`):: Gaps on the negative Z axis
- `left` (:ref:`lip gaps span config list <Lip Gaps Span Config>`):: Gaps on the negative X axis
- `right` (:ref:`lip gaps span config list <Lip Gaps Span Config>`):: Gaps on the positive X axis

Lip Gaps Span Config
**************

Each **lip gaps span config** has the following properties:

- `low` (float): Indicates where one side of the gap is located on an edge of a platform.  This 
value is 0 to 1 where 0 is one end of the edge and 1 is the other edge.  This value must be 
less than 'high'.
- `high` (float): Indicates where one side of the gap is located on an edge of a platform.  This 
value is 0 to 1 where 0 is one end of the edge and 1 is the other edge.  This value must be 
greater than 'low'.

Material Position Config
************************

Each **material position config** has the following properties:

- `material` (string, required): The material to use.
- `positions` (:ref:`grid config list <Grid Config>`): The list of X/Z coordinates corresponding to one or more areas in which to apply the material. Coordinates must be integers. Areas are always size 1x1 centered on the given X/Z coordinate. Adjacent areas are combined. Y coordinates are ignored.

Move Config
***********

Each **move config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `vector` (:ref:`vector config <Vector Config>`, required): The coordinates to describe the movement. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`
- `globalSpace` (bool, optional): If `true` the object will move using a global orientaion space and ignore the object's rotation. If false the object will move in local space oriented on the object's rotation. Default: `false`

Platform Lips Config
**************

Each **platform lips config** has the following properties:

- `front` (bool, optional): Positive Z axis
- `back` (bool, optional): Negative Z axis
- `left` (bool, optional): Negative X axis
- `right` (bool, optional): Positive X axis
- `gaps` (:ref:`lip gaps config <Lip Gaps Config>`, optional): gaps in the lits usually for ramps.

Physics Config
**************

Each **physics config** has the following properties:

- `enable` (bool, optional): Whether to enable customizing ALL physics properties on the object. You must either customize no properties or all of them. Any unset property in this config will automatically be set to `0`, NOT its Unity default (see below). Default: `false`
- `angularDrag` (float, optional): The object's `angular drag <https://docs.unity3d.com/ScriptReference/Rigidbody-angularDrag.html>`_, between 0 and 1. Default: `0`
- `bounciness` (float, optional): The object's `bounciness <https://docs.unity3d.com/ScriptReference/PhysicMaterial-bounciness.html>`_, between 0 and 1. Default: `0`
- `drag` (float, optional): The object's `drag <https://docs.unity3d.com/ScriptReference/Rigidbody-drag.html>`_. Default: `0`
- `dynamicFriction` (float, optional): The object's `dynamic friction <https://docs.unity3d.com/ScriptReference/PhysicMaterial-dynamicFriction.html>`_, between 0 and 1. Default: `0`
- `staticFriction` (float, optional): The object's `static friction <https://docs.unity3d.com/ScriptReference/PhysicMaterial-staticFriction.html>`_, between 0 and 1. Default: `0`

If no physics config is set, or if the physics config is not enabled, the object will have the following Unity defaults:

- Angular Drag: `0.5`
- Bounciness: `0`
- Drag: `0`
- Dynamic Friction: `0.6`
- Static Friction: `0.6`

Show Config
***********

Each **show config** has the following properties:

- `stepBegin` (integer, required): The step on which to show the object.  Must be non-negative.  A value of `0` means the object will be shown during scene initialization.
- `position` (:ref:`vector config <Vector Config>`, optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` (:ref:`vector config <Vector Config>`, optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` (:ref:`vector config <Vector Config>`, optional): The object's scale, which is multiplied by its base scale. Default: `{ "x": 1, "y": 1, "z": 1 }`

Size Config
***********

Each **size config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `size` (:ref:`vector config <Vector Config>`, required): The coordinates to describe the size, which is multiplied by the object's current size. Default: `{ "x": 1, "y": 1, "z": 1 }`
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`

Single Step Config
******************

Each **single step config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.

Step Begin and End Config
*************************

Each **step begin and end config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `repeat` (bool, optional): Whether to indefinitely repeat this action. Will wait `stepWait` number of steps after `stepEnd`, then will execute this action for `stepEnd - stepBegin + 1` number of steps, then repeat. Default: `false`
- `stepWait` (integer, optional): If `repeat` is `true`, the number of steps to wait after the `stepEnd` before repeating this action. Default: `0`

Open Close Config
*****************

Each **Open Close Config** has the following properties:
- `step` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.
- `open` (boolean, required): If true, the container will be opened, if false, the container will be closed

Teleport Config
***************

Each **teleport config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `position` (:ref:`vector config <Vector Config>`, required): The global coordinates to describe the end position. Default: `{ "x": 0, "y": 0, "z": 0 }`

Transform Config
****************

Each **transform config** has the following properties:

- `position` (:ref:`vector config <Vector Config>`, optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` (:ref:`vector config <Vector Config>`, optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` (:ref:`vector config <Vector Config>`, optional): The object's scale, which is multiplied by its base scale.  Default: `{ "x": 1, "y": 1, "z": 1 }`

Vector Config
*************

Each **vector config** has the following properties:

- `x` (float, optional)
- `y` (float, optional)
- `z` (float, optional)

Room Material Config
********************

- `left` (string, optional): The material (color/texture) for the room's left outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none
- `right` (string, optional): The material (color/texture) for the room's right outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none
- `front` (string, optional): The material (color/texture) for the room's front outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none
- `back` (string, optional): The material (color/texture) for the room's back outer wall. See the :ref:`material list <Material List>` for options.  If not provided, walls will use 'wallMaterial' property.  Default: none

Object List
===========

Attributes
**********

- Moveable: Can be pushed, pulled, and knocked over. Can be added to object types that are not `moveable` by default.
- Pickupable: Can be picked up with the `PickupObject` action (all pickupable objects are also moveable). Can be added to object types that are not `pickupable` by default.
- Receptacle: Can hold objects with the `PutObject` action.
- Openable: Can be opened with the `OpenObject` action.

Interactable Objects
********************

Some objects have attributes like `receptacle` or `openable` by default. Some objects have restrictions on categories of materials that can be used on them; only the listed categories are allowed. Each object's base size is using a scale of (x=1, y=1, z=1). Most objects will be positioned on top of the floor with `position.y = 0`; objects marked with `(*)` instead bisect the floor and must be offset by half their height.

Small Objects
-------------

All of the following object types have the `pickupable` attribute by default.

.. list-table::
    :header-rows: 1

    * - Object Type
      - Shape
      - Default Mass
      - Receptacle
      - Openable
      - Materials
      - Base Size
      - Facing
      - Details
    * - `"apple_1"`
      - apple
      - 0.25
      - 
      - 
      - none
      - x=0.111,y=0.12,z=0.122
      -
      - 
    * - `"apple_2"`
      - apple
      - 0.25
      - 
      - 
      - none
      - x=0.117,y=0.121,z=0.116
      -
      - 
    * - `"ball"`
      - ball
      - 1
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`rubber <Rubber Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=1
      -
      - 
    * - `"barrel_1"`
      - barrel
      - 5
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=0.86,y=0.8,z=0.86
      - Forward
      - Cylindrical wooden barrel
    * - `"barrel_2"`
      - barrel
      - 5
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=0.73,y=0.93,z=0.95
      - Forward
      - Cylindrical wooden barrel
    * - `"block_blank_blue_cube"`
      - blank block cube
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blank_blue_cylinder"`
      - blank block cylinder
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blank_red_cube"`
      - blank block cube
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blank_red_cylinder"` 
      - blank block cylinder 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blank_wood_cube"`
      - blank block cube 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blank_wood_cylinder"` 
      - blank block cylinder 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blank_yellow_cube"` 
      - blank block cube
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blank_yellow_cylinder"`
      - blank block cylinder 
      - 0.66
      - X
      -
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blue_letter_a"`
      - letter block cube
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blue_letter_b"` 
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blue_letter_c"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blue_letter_d"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blue_letter_m"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_blue_letter_s"`
      - letter block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_yellow_number_1"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_yellow_number_2"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_yellow_number_3"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_yellow_number_4"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_yellow_number_5"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"block_yellow_number_6"`
      - number block cube 
      - 0.66
      - X
      -
      - :ref:`block_letter_number <Block Materials (Letter/Number)>`, :ref:`wood <Wood Materials>`
      - x=0.1,y=0.1,z=0.1
      -
      -
    * - `"bowl_3"`
      - bowl
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.175,y=0.116,z=0.171
      -
      - 
    * - `"bowl_4"`
      - bowl
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.209,y=0.059,z=0.206
      -
      - 
    * - `"bowl_6"`
      - bowl
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.198,y=0.109,z=0.201
      -
      - 
    * - `"bobcat"`
      - bobcat
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.13,y=0.061,z=0.038
      - Right
      - Toy bobcat construction vehicle
    * - `"bus_1"`
      - bus
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.28,y=0.28,z=0.52
      - Forward
      - Toy Bus
    * - `"car_1"`
      - car
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.075,y=0.065,z=0.14
      - Forward
      - Toy sedan
    * - `"car_2"`
      - car
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.25,y=0.2,z=0.41
      - Forward
      - Toy car
    * - `"car_3"`
      - car
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.134,y=0.052,z=0.036
      - Right
      - Toy car
    * - `"cart_2"`
      - cart
      - 0.5
      - 
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.42,y=0.7,z=0.51
      - Forward
      - 
    * - `"case_1"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.71,y=0.19,z=0.54
      - Forward
      - Suitcase. Same as suitcase_1
    * - `"case_2"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.78,y=0.16,z=0.58
      - Forward
      - Suitcase
    * - `"case_3"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.81,y=0.21,z=0.78
      - Forward
      - Suitcase
    * - `"case_4"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=1.68,y=1.12,z=1.98
      - Forward
      - Suitcase
    * - `"case_5"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=1.18,y=0.94,z=1.94
      - Forward
      - Suitcase
    * - `"crate_1"`
      - crate
      - 5
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=0.8,y=0.8,z=0.98
      - Forward
      - Cuboid wooden crate
    * - `"crate_2"`
      - crate
      - 5
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=0.72,y=0.64,z=0.72
      - Forward
      - Cuboid wooden crate
    * - `"crayon_black"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      - Forward
      - 
    * - `"crayon_blue"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      -
      - 
    * - `"crayon_green"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      -
      - 
    * - `"crayon_pink"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      -
      - 
    * - `"crayon_red"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      -
      - 
    * - `"crayon_yellow"`
      - crayon
      - 0.125
      - 
      - 
      - none
      - x=0.01,y=0.085,z=0.01
      -
      - 
    * - `"cup_2"`
      - cup
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.105,y=0.135,z=0.104
      -
      - 
    * - `"cup_3"`
      - cup
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.123,y=0.149,z=0.126
      -
      - 
    * - `"cup_6"`
      - cup
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.106,y=0.098,z=0.106
      -
      - 
    * - `"dog_on_wheels"`
      - dog
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.355,y=0.134,z=0.071
      - Forward
      - Toy dog on wheels
    * - `"dog_on_wheels_2"`
      - dog
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.5,y=1.12,z=1.44
      - Forward
      - Toy dog on wheels
    * - `"duck_on_wheels"`
      - duck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.21,y=0.17,z=0.065
      - Right
      - Toy duck on wheels
    * - `"duck_on_wheels_2"`
      - duck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.224,y=0.176,z=0.06
      - Right
      - Toy duck on wheels
    * - `"jeep"`
      - jeep
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.06,y=0.057,z=0.098
      - Forward
      - Toy car
    * - `"military_case_1"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.66,y=0.82,z=0.62
      - Forward
      - 
    * - `"military_case_2"`
      - case
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.8,y=0.44,z=0.7
      - Forward
      - 
    * - `"pacifier"`
      - pacifier
      - 
      - 0.5
      - 
      - none
      - x=0.07,y=0.04,z=0.05
      -
      - 
    * - `"plate_1"`
      - plate
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.208,y=0.117,z=0.222
      -
      - 
    * - `"plate_3"`
      - plate
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.304,y=0.208,z=0.305
      -
      - 
    * - `"plate_4"`
      - plate
      - 0.25
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.202,y=0.113,z=0.206
      -
      - 
    * - `"racecar_red"`
      - car
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.07,y=0.06,z=0.15
      - Forward
      - Toy racecar
    * - `"roller"`
      - roller
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.102,y=0.062,z=0.047
      - Right
      - Toy roller construction vehicle
    * - `"skateboard"`
      - skateboard
      - 1
      - 
      - 
      - none
      - x=0.24,y=0.17,z=0.76
      - Forward
      - 
    * - `"soccer_ball"`
      - ball
      - 0.5
      - 
      - 
      - none
      - x=0.22,y=0.22,z=0.22
      -
      - (*)
    * - `"suitcase_1"`
      - case 
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.71,y=0.19,z=0.42
      - Forward
      - Same as case_1
    * - `"tank_1"`
      - tank
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.09,y=0.065,z=0.24
      - Forward
      - Toy tank
    * - `"tank_2"`
      - tank
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.065,y=0.067,z=0.17
      - Forward
      - Toy tank
    * - `"toolbox_1"`
      - toolbox
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.51,y=0.29,z=0.48
      - Forward
      - Toolbox
    * - `"toolbox_2"`
      - toolbox
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.58,y=0.33,z=0.44
      - Forward
      - Toolbox
    * - `"toolbox_3"`
      - toolbox
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.15,y=0.1,z=0.136
      - Forward
      - Toolbox
    * - `"toolbox_4"`
      - toolbox
      - 5
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.13,y=0.036,z=0.116
      - Forward
      - Toolbox
    * - `"train_1"`
      - train
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.16,y=0.2,z=0.23
      - Forward
      - Toy train
    * - `"train_2"`
      - train
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.09,y=0.064,z=0.036
      - Right
      - Toy train
    * - `"trolley_1"`
      - trolley
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.16,y=0.2,z=0.23
      - Forward
      - Toy trolley
    * - `"trophy"`
      - trophy
      - 0.5
      - 
      - 
      - none
      - x=0.19,y=0.3,z=0.14
      -
      - 
    * - `"truck_1"`
      - truck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.2,y=0.18,z=0.25
      - Forward
      - Toy truck
    * - `"truck_2"`
      - truck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.14,y=0.2,z=0.28
      - Forward
      - Toy truck
    * - `"truck_3"`
      - truck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.33,y=0.345,z=0.61
      - Forward
      - Toy truck
    * - `"truck_4"`
      - truck
      - 0.5
      - 
      - 
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.25,y=0.26,z=0.4
      - Forward
      - Toy truck
    * - `"turtle_on_wheels"`
      - turtle
      - 
      - 
      - 0.5
      - :ref:`block_blank <Block Materials (Blank)>`, :ref:`flat <Flat Materials>`, :ref:`wood <Wood Materials>`
      - x=0.24,y=0.14,z=0.085
      - Right
      - Toy turtle on wheels

Furniture Objects
-----------------

.. list-table::
    :header-rows: 1

    * - Object Type
      - Shape
      - Default Mass
      - Moveable
      - Receptacle
      - Openable
      - Materials
      - Base Size
      - Details
    * - `"antique_armchair_1"`
      - sofa chair
      - 5
      - X
      - X
      - 
      - :ref:`leather armchair <Leather Armchair Materials>`
      - x=0.35,y=0.45,z=0.33
      - 
    * - `"antique_chair_1"`
      - chair
      - 10
      - X
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=0.76,y=1.26,z=0.64
      - 
    * - `"antique_sofa_1"`
      - sofa
      - 20
      - X
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=2,y=1.4,z=0.68
      - 
    * - `"antique_table_1"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=0.77,y=0.48,z=0.77
      - 
    * - `"bed_1"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.3,y=1.02,z=2.11
      - 
    * - `"bed_2"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.54,y=1.1,z=2.43
      - 
    * - `"bed_3"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.48,y=0.73,z=2.11
      - 
    * - `"bed_4"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.95,y=1.75,z=2.28
      - Bunk bed
    * - `"bed_5"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.26,y=1.04,z=2.37
      - 
    * - `"bed_6"`
      - bed
      - 50
      - 
      -
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.15,y=2.2,z=2.53
      - Elevated bed
    * - `"bed_7"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.08,y=1.23,z=2.02
      - 
    * - `"bed_8"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=0.88,y=0.7,z=1.7
      - 
    * - `"bed_9"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1,y=1,z=2
      - 
    * - `"bed_10"`
      - bed
      - 50
      - 
      - X
      - 
      - :ref:`wood <Wood Materials>`
      - x=1.25,y=0.94,z=2.17
      - 
    * - `"bookcase_1_shelf"`
      - bookcase
      - 10
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=0.5
      - 
    * - `"bookcase_2_shelf"`
      - bookcase
      - 15
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1.5,z=0.5
      - 
    * - `"bookcase_3_shelf"`
      - bookcase
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2,z=0.5
      - 
    * - `"bookcase_4_shelf"`
      - bookcase
      - 25
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2.5,z=0.5
      - 
    * - `"bookcase_1_shelf_sideless"`
      - bookcase
      - 10
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=0.5
      - 
    * - `"bookcase_2_shelf_sideless"`
      - bookcase
      - 15
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1.5,z=0.5
      - 
    * - `"bookcase_3_shelf_sideless"`
      - bookcase
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2,z=0.5
      - 
    * - `"bookcase_4_shelf_sideless"`
      - bookcase
      - 25
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2.5,z=0.5
      - 
    * - `"cart_1"`
      - cart
      - 4
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`
      - x=0.725,y=1.29,z=0.55
      - 
    * - `"chair_1"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.54,y=1.04,z=0.46
      - 
    * - `"chair_2"`
      - stool
      - 2.5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.3,y=0.75,z=0.3
      - 
    * - `"chair_3"`
      - stool
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.42,y=0.8,z=0.63
      - 
    * - `"chair_4"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`
      - x=0.54,y=0.88,z=0.44
      - 
    * - `"chair_5"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.49,y=0.86,z=0.58
      - 
    * - `"chair_6"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.51,y=0.98,z=0.54
      - 
    * - `"chair_7"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.42,y=0.8,z=0.63
      - 
    * - `"chair_8"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.55,y=0.78,z=0.54
      - 
    * - `"chair_9"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.49,y=0.95,z=0.52
      - 
    * - `"chair_10"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.48,y=0.91,z=0.54
      - 
    * - `"chair_11"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.72,y=1.38,z=0.78
      - 
    * - `"chair_12"`
      - chair
      - 5
      - X
      - X
      - 
      - :ref:`plastic <Plastic Materials>`
      - x=0.6,y=0.84,z=0.76
      - 
    * - `"chair_13"`
      - stool
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.42,y=0.74,z=0.4
      - 
    * - `"chair_14"`
      - stool
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.5,y=0.8,z=0.5
      - 
    * - `"changing_table"`
      - changing table
      - 100
      - 
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=1.1,y=0.96,z=0.58
      - 
    * - `"chest_1"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.83,y=0.42,z=0.55
      - Chest with rectangular lid
    * - `"chest_2"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.52,y=0.42,z=0.31
      - Chest with domed lid
    * - `"chest_3"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.46,y=0.26,z=0.32
      - Chest with rectangular lid
    * - `"chest_4"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.72,y=0.35,z=0.6
      - Chest with rounded lid
    * - `"chest_5"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.46,y=0.28,z=0.52
      - Chest with rounded lid
    * - `"chest_6"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.5,y=0.36,z=0.74
      - Chest with trapezoidal lid
    * - `"chest_7"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.59,y=0.49,z=0.78
      - Chest with fancy lid
    * - `"chest_8"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.42,y=0.32,z=0.36
      - Chest with domed lid
    * - `"chest_9"`
      - chest
      - 15
      - 
      - X
      - X
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.84,y=0.41,z=0.68
      - Chest with trapezoidal lid
    * - `"crib"`
      - crib
      - 25
      - 
      - 
      - 
      - :ref:`wood <Wood Materials>`
      - x=0.65,y=0.9,z=1.25
      - 
    * - `"desk_1"`
      - desk
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=1
      - Square desk with 3 sides
    * - `"desk_2"`
      - desk
      - 15
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=1,z=1
      - Square desk with 2 sides and 1 leg
    * - `"desk_3"`
      - desk
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1.5,y=1,z=1.5
      - Circular desk with 3 sides
    * - `"desk_4"`
      - desk
      - 30
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=2,z=1
      - Square desk with 3 sides on bottom and top
    * - `"shelf_1"`
      - shelf
      - 10
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.78,y=0.77,z=0.4
      - Object with four cubbies
    * - `"shelf_2"`
      - shelf
      - 20
      - 
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.93,y=0.73,z=1.02
      - Object with three shelves
    * - `"sofa_1"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_1 <Sofa 1 Materials>`
      - x=2.64,y=1.15,z=1.23
      - 
    * - `"sofa_2"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_2 <Sofa 2 Materials>`
      - x=2.55,y=1.25,z=0.95
      - 
    * - `"sofa_3"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_3 <Sofa 3 Materials>`
      - x=2.4,y=1.25,z=0.95
      - 
    * - `"sofa_4"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_thorkea <Sofa THORKEA Materials>`
      - x=1.59,y=0.84,z=1.01
      - 
    * - `"sofa_5"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_thorkea <Sofa THORKEA Materials>`
      - x=1.86,y=0.9,z=1
      - 
    * - `"sofa_6"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_thorkea <Sofa THORKEA Materials>`
      - x=1.69,y=0.72,z=0.92
      - 
    * - `"sofa_7"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_thorkea <Sofa THORKEA Materials>`
      - x=1.61,y=0.85,z=0.93
      - 
    * - `"sofa_8"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_8 <Sofa 8 Materials>`
      - x=2.78,y=0.86,z=1.1
      - 
    * - `"sofa_9"`
      - sofa
      - 100
      - 
      - X
      - 
      - :ref:`sofa_9 <Sofa 9 Materials>`
      - x=2.54,y=1.62,z=1.52
      - 
    * - `"sofa_chair_1"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_chair_1 <Sofa Chair 1 Materials>`
      - x=1.43,y=1.15,z=1.23
      - 
    * - `"sofa_chair_2"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_2 <Sofa 2 Materials>`
      - x=1.425,y=1.25,z=0.95
      - 
    * - `"sofa_chair_3"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_3 <Sofa 3 Materials>`
      - x=1.425,y=1.25,z=0.95
      - 
    * - `"sofa_chair_4"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`armchair_thorkea <Armchair THORKEA Materials>`
      - x=1,y=0.86,z=0.87
      - 
    * - `"sofa_chair_5"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`armchair_thorkea <Armchair THORKEA Materials>`
      - x=0.96,y=0.92,z=1
      - 
    * - `"sofa_chair_6"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`armchair_thorkea <Armchair THORKEA Materials>`
      - x=0.67,y=0.64,z=0.67
      - 
    * - `"sofa_chair_7"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`armchair_thorkea <Armchair THORKEA Materials>`
      - x=0.69,y=0.68,z=0.63
      - 
    * - `"sofa_chair_8"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_chair_8 <Sofa Chair 8 Materials>`
      - x=2.18,y=1.24,z=1.6
      - 
    * - `"sofa_chair_9"`
      - sofa chair
      - 50
      - 
      - X
      - 
      - :ref:`sofa_9 <Sofa 9 Materials>`
      - x=1.38,y=1.46,z=1.36
      - 
    * - `"table_1"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.69,y=0.88,z=1.63
      - Rectangular table with legs
    * - `"table_2"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.67,y=0.74,z=0.67
      - Circular table
    * - `"table_3"`
      - table
      - 2.5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.573,y=1.018,z=0.557
      - Circular table
    * - `"table_4"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.62,y=0.62,z=1.17
      - Semi-circular table
    * - `"table_5"`
      - table
      - 20
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`wood <Wood Materials>`
      - x=1.2,y=0.7,z=0.9
      - Rectangular table with sides
    * - `"table_7"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`wood <Wood Materials>`
      - x=1.02,y=0.45,z=0.65
      - Rectangular table with legs
    * - `"table_8"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`wood <Wood Materials>`
      - x=0.65,y=0.71,z=1.02
      - Rectangular table with legs
    * - `"table_11"`
      - table
      - 15
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=0.5,z=1
      - Rectangular table with T legs
    * - `"table_12"`
      - table
      - 15
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1,y=0.5,z=1
      - Rectangular table with X legs
    * - `"table_13"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.58,y=0.62,z=0.59
      - Short circular table
    * - `"table_14"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.53,y=0.59,z=0.53
      - Short rectangular table
    * - `"table_15"`
      - table
      - 15
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1.33,y=0.9,z=0.79
      - Rectangular table
    * - `"table_16"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1.06,y=0.83,z=1.05
      - Circular table
    * - `"table_17"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1.16,y=0.82,z=0.75
      - Rectangular table
    * - `"table_18"`
      - table
      - 15
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=1.57,y=0.91,z=0.87
      - Rectangular table
    * - `"table_19"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.92,y=0.54,z=0.49
      - Rectangular table
    * - `"table_20"`
      - table
      - 10
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.96,y=0.64,z=0.93
      - Rectangular table
    * - `"table_26"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`metal <Metal Materials>`, :ref:`plastic <Plastic Materials>`, :ref:`wood <Wood Materials>`
      - x=0.65,y=0.68,z=0.75
      - Square table
    * - `"table_27"`
      - table
      - 5
      - X
      - X
      - 
      - :ref:`plastic <Plastic Materials>`
      - x=1.2,y=0.7,z=1.2
      - Circular plastic table
    * - `"tv_2"`
      - television
      - 5
      - 
      - 
      - 
      - none
      - x=1.234,y=0.896,z=0.256
      - (*)
    * - `"wardrobe"`
      - wardrobe
      - 100
      - 
      - X
      - X
      - :ref:`wood <Wood Materials>`
      - x=1.07,y=2.1,z=0.49
      - 

Tool Objects
-------------

All of the tools have the `tool` shape, `metal` material, `moveable` and `receptacle` attributes, and the same grey and black colors/textures.

.. list-table::
    :header-rows: 1

    * - Object Type
      - Default Mass
      - Base Size
    * - `"tool_rect_0_50_x_4_00"`
      - 3
      - x=0.5,y=0.3,z=4
    * - `"tool_rect_0_50_x_5_00"`
      - 3.25
      - x=0.5,y=0.3,z=5
    * - `"tool_rect_0_50_x_6_00"`
      - 3.5
      - x=0.5,y=0.3,z=6
    * - `"tool_rect_0_50_x_7_00"`
      - 3.75
      - x=0.5,y=0.3,z=7
    * - `"tool_rect_0_50_x_8_00"`
      - 4
      - x=0.5,y=0.3,z=8
    * - `"tool_rect_0_50_x_9_00"`
      - 4.25
      - x=0.5,y=0.3,z=9
    * - `"tool_rect_0_75_x_4_00"`
      - 3.33
      - x=0.75,y=0.3,z=4
    * - `"tool_rect_0_75_x_5_00"`
      - 3.66
      - x=0.75,y=0.3,z=5
    * - `"tool_rect_0_75_x_6_00"`
      - 4
      - x=0.75,y=0.3,z=6
    * - `"tool_rect_0_75_x_7_00"`
      - 4.33
      - x=0.75,y=0.3,z=7
    * - `"tool_rect_0_75_x_8_00"`
      - 4.66
      - x=0.75,y=0.3,z=8
    * - `"tool_rect_0_75_x_9_00"`
      - 5
      - x=0.75,y=0.3,z=9
    * - `"tool_rect_1_00_x_4_00"`
      - 4
      - x=1,y=0.3,z=4
    * - `"tool_rect_1_00_x_5_00"`
      - 4.5
      - x=1,y=0.3,z=5
    * - `"tool_rect_1_00_x_6_00"`
      - 5
      - x=1,y=0.3,z=6
    * - `"tool_rect_1_00_x_7_00"`
      - 5.5
      - x=1,y=0.3,z=7
    * - `"tool_rect_1_00_x_8_00"`
      - 6
      - x=1,y=0.3,z=8
    * - `"tool_rect_1_00_x_9_00"`
      - 6.5
      - x=1,y=0.3,z=9

Agents
******

These agents are used in scenes for the interactive tasks.

.. list-table::
    :header-rows: 1

    * - Object Type
      - Default Mass
      - Base Size
    * - `"agent_female_01"`
      - 70
      - x=0.5,y=1.6,z=0.5
    * - `"agent_female_02"`
      - 70
      - x=0.5,y=1.6,z=0.5
    * - `"agent_female_03"`
      - 70
      - x=0.5,y=1.6,z=0.5
    * - `"agent_female_04"`
      - 70
      - x=0.5,y=1.6,z=0.5
    * - `"agent_male_01"`
      - 80
      - x=0.5,y=1.6,z=0.5
    * - `"agent_male_02"`
      - 80
      - x=0.5,y=1.6,z=0.5
    * - `"agent_male_03"`
      - 80
      - x=0.5,y=1.6,z=0.5
    * - `"agent_male_04"`
      - 80
      - x=0.5,y=1.6,z=0.5

Primitive Objects
*****************

The following objects have a default mass of 1, base size of (x=1, y=1, z=1), and no material restrictions. By default, each primitive object's center Y position is 0, which will position it halfway inside the ground. You can configure them with properties like `physics`, `moveable`, `pickupable`, or `structure`. These are NOT the internal Unity primitive 3D GameObjects.

- `"circle_frustum"`
- `"cone"`
- `"cube"`
- `"cylinder"`
- `"pyramid"`
- `"sphere"`
- `"square_frustum"`
- `"triangle"`
- `"tube_narrow"`
- `"tube_wide"`

Other Objects
*************

The following objects have a default mass of 1 and no material restrictions. You can configure them with properties like `physics`, `moveable`, `pickupable`, or `structure`.

.. list-table::
    :header-rows: 1

    * - Object Type
      - Base Size
      - Default Center Y Position
    * - `"double_cone"`
      - (x=1,y=1,z=1)
      - 0
    * - `"cube_hollow_narrow"`
      - (x=1,y=1,z=1)
      - 0.5
    * - `"cube_hollow_wide"`
      - (x=1,y=1,z=1)
      - 0.5
    * - `"dumbbell_1"`
      - (x=1,y=1,z=1)
      - 0
    * - `"dumbbell_2"`
      - (x=1,y=1,z=1)
      - 0
    * - `"hash"`
      - (x=1,y=1,z=1)
      - 0.5
    * - `"letter_l_narrow"`
      - (x=0.5,y=1,z=0.5)
      - 0
    * - `"letter_l_wide"`
      - (x=1,y=1,z=0.5)
      - 0
    * - `"letter_l_wide_tall"`
      - (x=1,y=2,z=0.5)
      - 0
    * - `"letter_x"`
      - (x=1,y=1,z=1)
      - 0.5
    * - `"lock_wall"`
      - (x=1,y=1,z=1)
      - 0
    * - `"rollable_1"`
      - (x=1,y=1,z=1)
      - 0
    * - `"rollable_2"`
      - (x=1,y=1,z=1)
      - 0
    * - `"rollable_3"`
      - (x=1,y=1,z=1)
      - 0
    * - `"rollable_4"`
      - (x=1,y=1,z=1)
      - 0
    * - `"tie_fighter"`
      - (x=1,y=1,z=1)
      - 0

Deprecated Objects
******************

The following object types are not currently used:

* - `"box_2"`
* - `"box_3"`
* - `"box_4"`
* - `"cake"`
* - `"foam_floor_tiles"`
* - `"gift_box_1"`
* - `"painting_2"`
* - `"painting_4"`
* - `"painting_5"`
* - `"painting_9"`
* - `"painting_10"`
* - `"painting_16"`
* - `"plant_1"`
* - `"plant_5"`
* - `"plant_7"`
* - `"plant_9"`
* - `"plant_12"`
* - `"plant_16"`

Child Components
****************

Some objects have child components representing cabinets, drawers, or shelves. Child components are not found in the scene configuration file but are automatically generated by the MCS environment. Child components have their own object IDs so the player may use actions like OpenObject or PutObject with specific cabinets/drawers/shelves.

The following objects have the following child components:

* `"changing_table"`:
    * `"<id>_drawer_top"`
    * `"<id>_drawer_bottom"`
    * `"<id>_shelf_top"`
    * `"<id>_shelf_middle"`
    * `"<id>_shelf_bottom"`
* `"bookcase_1_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
* `"bookcase_1_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
* `"bookcase_2_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
* `"bookcase_2_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
* `"bookcase_3_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
* `"bookcase_3_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
* `"bookcase_4_shelf"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
    * `"<id>_shelf_4"`
* `"bookcase_4_shelf_sideless"`:
    * `"<id>_bottom"`
    * `"<id>_shelf_1"`
    * `"<id>_shelf_2"`
    * `"<id>_shelf_3"`
    * `"<id>_shelf_4"`
* `"shelf_1"`:
    * `"<id>_bottom_left_shelf"`
    * `"<id>_bottom_right_shelf"`
    * `"<id>_top_left_shelf"`
    * `"<id>_top_right_shelf"`
* `"shelf_2"`:
    * `"<id>_middle_shelf"`
    * `"<id>_lower_shelf"`
* `"wardrobe"`:
    * `"<id>_bottom_shelf_left"`
    * `"<id>_left_door"`
    * `"<id>_lower_drawer_bottom_left"`
    * `"<id>_lower_drawer_bottom_right"`
    * `"<id>_lower_drawer_top_left"`
    * `"<id>_lower_drawer_top_right"`
    * `"<id>_middle_shelf_left"`
    * `"<id>_middle_shelf_right"`
    * `"<id>_right_door"`
    * `"<id>_top_shelf"`

Material List
=============

In Unity, "Materials" are the colors and textures applied to objects in the 3D simulation environment. Some objects may have default materials. Some objects may have multiple materials. Some materials may have patterns intended for objects of a specific size, and may look odd if applied to objects that are too big or small.

For our training and evaluation datasets, we normally use the materials under "Walls", "Ceramics", "Fabrics", and "Woods" for the ceiling and the walls, and the materials under "Ceramics", "Fabrics", and "Woods" for the floors.

The following materials are currently available:

Armchair THORKEA Materials
****************

Specific textures for `sofa_chair_4`, `sofa_chair_5`, `sofa_chair_6`, AND `sofa_chair_7` only.

- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Ekemas_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Ektorp_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Emmabo_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Karlstad_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Overalt_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Armchair/Materials/THORKEA_Armchair_Tullsta_Fabric_Mat"`

Block Materials (Blank)
***********************

Colors that were designed for the blank blocks, and look good on some of the wooden baby toys.

- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/gray_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/green_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1"`

Block Materials (Letter/Number)
*******************************

Designs for the letter/number blocks.

- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_1_Yellow_1K/NumberBlockYellow_1"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_2_Yellow_1K/NumberBlockYellow_2"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_3_Yellow_1K/NumberBlockYellow_3"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_4_Yellow_1K/NumberBlockYellow_4"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_5_Yellow_1K/NumberBlockYellow_5"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_6_Yellow_1K/NumberBlockYellow_6"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_A_Blue_1K/ToyBlockBlueA"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_B_Blue_1K/ToyBlockBlueB"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_C_Blue_1K/ToyBlockBlueC"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_D_Blue_1K/ToyBlockBlueD"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_M_Blue_1K/ToyBlockBlueM"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_S_Blue_1K/ToyBlockBlueS"`

Cardboard Materials
*******************

- `"AI2-THOR/Materials/Misc/Cardboard_Brown"`
- `"AI2-THOR/Materials/Misc/Cardboard_Grey"`
- `"AI2-THOR/Materials/Misc/Cardboard_Tan"`

Ceramic Materials
*****************

- `"AI2-THOR/Materials/Ceramics/BrownMarbleFake 1"`
- `"AI2-THOR/Materials/Ceramics/ConcreteBoards1"`
- `"AI2-THOR/Materials/Ceramics/ConcreteFloor"`
- `"AI2-THOR/Materials/Ceramics/GREYGRANITE"`
- `"AI2-THOR/Materials/Ceramics/PinkConcrete_Bedroom1"`
- `"AI2-THOR/Materials/Ceramics/RedBrick"`
- `"AI2-THOR/Materials/Ceramics/TexturesCom_BrickRound0044_1_seamless_S"` (rough stone)
- `"AI2-THOR/Materials/Ceramics/WhiteCountertop"`

Fabric Materials
****************

- `"AI2-THOR/Materials/Fabrics/BedroomCarpet"` (blue pattern)
- `"AI2-THOR/Materials/Fabrics/Carpet2"`
- `"AI2-THOR/Materials/Fabrics/Carpet3"`
- `"AI2-THOR/Materials/Fabrics/Carpet4"`
- `"AI2-THOR/Materials/Fabrics/Carpet8"`
- `"AI2-THOR/Materials/Fabrics/CarpetDark"`
- `"AI2-THOR/Materials/Fabrics/CarpetDark 1"`
- `"AI2-THOR/Materials/Fabrics/CarpetDarkGreen"`
- `"AI2-THOR/Materials/Fabrics/CarpetGreen"`
- `"AI2-THOR/Materials/Fabrics/CarpetWhite"`
- `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `"AI2-THOR/Materials/Fabrics/HotelCarpet"` (red pattern)
- `"AI2-THOR/Materials/Fabrics/HotelCarpet3"` (red pattern)
- `"AI2-THOR/Materials/Fabrics/RUG2"` (red and blue pattern)
- `"AI2-THOR/Materials/Fabrics/Rug3"` (blue and red pattern)
- `"AI2-THOR/Materials/Fabrics/RUG4"` (red and yellow pattern)
- `"AI2-THOR/Materials/Fabrics/Rug5"` (white pattern)
- `"AI2-THOR/Materials/Fabrics/Rug6"` (green, purple, and red pattern)
- `"AI2-THOR/Materials/Fabrics/RUG7"` (red and blue pattern)
- `"AI2-THOR/Materials/Fabrics/RugPattern224"` (brown, green, and white pattern)
- `"Custom/Materials/AzureCarpetMCS"`
- `"Custom/Materials/BlueCarpetMCS"`
- `"Custom/Materials/ChartreuseCarpetMCS"`
- `"Custom/Materials/CyanCarpetMCS"`
- `"Custom/Materials/GreenCarpetMCS"`
- `"Custom/Materials/GreyCarpetMCS"`
- `"Custom/Materials/LimeCarpetMCS"`
- `"Custom/Materials/MagentaCarpetMCS"`
- `"Custom/Materials/MaroonCarpetMCS"`
- `"Custom/Materials/NavyCarpetMCS"`
- `"Custom/Materials/OliveCarpetMCS"`
- `"Custom/Materials/OrangeCarpetMCS"`
- `"Custom/Materials/PurpleCarpetMCS"`
- `"Custom/Materials/RedCarpetMCS"`
- `"Custom/Materials/RoseCarpetMCS"`
- `"Custom/Materials/SpringGreenCarpetMCS"`
- `"Custom/Materials/TealCarpetMCS"`
- `"Custom/Materials/VioletCarpetMCS"`
- `"Custom/Materials/WhiteCarpetMCS"`
- `"Custom/Materials/YellowCarpetMCS"`

Flat Materials
****************

Custom-made textures that are completely flat colors.

- `"Custom/Materials/Azure"`
- `"Custom/Materials/Black"`
- `"Custom/Materials/Blue"`
- `"Custom/Materials/Brown"`
- `"Custom/Materials/Chartreuse"`
- `"Custom/Materials/Cyan"`
- `"Custom/Materials/Goldenrod"`
- `"Custom/Materials/Green"`
- `"Custom/Materials/Grey"`
- `"Custom/Materials/Indigo"`
- `"Custom/Materials/Lime"`
- `"Custom/Materials/Magenta"`
- `"Custom/Materials/Maroon"`
- `"Custom/Materials/Navy"`
- `"Custom/Materials/Olive"`
- `"Custom/Materials/Orange"`
- `"Custom/Materials/Pink"`
- `"Custom/Materials/Purple"`
- `"Custom/Materials/Red"`
- `"Custom/Materials/Rose"`
- `"Custom/Materials/Silver"`
- `"Custom/Materials/SpringGreen"`
- `"Custom/Materials/Tan"`
- `"Custom/Materials/Teal"`
- `"Custom/Materials/Violet"`
- `"Custom/Materials/White"`
- `"Custom/Materials/Yellow"`

Leather Materials
*****************

- `"AI2-THOR/Materials/Fabrics/Leather"`
- `"AI2-THOR/Materials/Fabrics/Leather2"`
- `"AI2-THOR/Materials/Fabrics/Leather3"`
- `"AI2-THOR/Materials/Fabrics/Leather 2"`

Leather Armchair Materials
**************************

Specific textures for `antique_armchair_1` only.

- `"UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_1"`
- `"UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_2"`
- `"UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_3"`
- `"UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_NEW_4"`
- `"UnityAssetStore/Leather_Chair/Assets/Materials/Leather_Chair_normal_OLD"`

Metal Materials
***************

- `"AI2-THOR/Materials/Metals/BlackFoil"`
- `"AI2-THOR/Materials/Metals/BlackSmoothMeta"` (yes, it is misspelled)
- `"AI2-THOR/Materials/Metals/Brass 1"`
- `"AI2-THOR/Materials/Metals/Brass_Mat"`
- `"AI2-THOR/Materials/Metals/BrownMetal 1"`
- `"AI2-THOR/Materials/Metals/BrushedAluminum_Blue"`
- `"AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency"`
- `"AI2-THOR/Materials/Metals/GenericStainlessSteel"`
- `"AI2-THOR/Materials/Metals/HammeredMetal_AlbedoTransparency 1"`
- `"AI2-THOR/Materials/Metals/Metal"`
- `"AI2-THOR/Materials/Metals/WhiteMetal"`
- `"UnityAssetStore/Baby_Room/Models/Materials/cabinet metal"`

Plastic Materials
*****************

- `"AI2-THOR/Materials/Plastics/BlackPlastic"`
- `"AI2-THOR/Materials/Plastics/OrangePlastic"`
- `"AI2-THOR/Materials/Plastics/WhitePlastic"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1"` (flat red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2"` (flat blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 3"` (flat green)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4"` (flat yellow)

Rubber Materials
****************

- `"AI2-THOR/Materials/Plastics/BlueRubber"`
- `"AI2-THOR/Materials/Plastics/LightBlueRubber"`

Sofa 1 Materials
****************

Specific textures for `sofa_1` only.

- `"AI2-THOR/Materials/Fabrics/Sofa1_Blue"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_Brown"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_Gold"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_Red"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_Salmon"`
- `"AI2-THOR/Materials/Fabrics/Sofa1_White"`

Sofa Chair 1 Materials
**********************

Specific textures for `sofa_chair_1` only.

- `"AI2-THOR/Materials/Fabrics/SofaChair1_Black"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_Blue"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_Brown"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_Red"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_Salmon"`
- `"AI2-THOR/Materials/Fabrics/SofaChair1_White"`

Sofa 2 Materials
****************

Specific textures for `sofa_2` AND `sofa_chair_2` only.

- `"AI2-THOR/Materials/Fabrics/SofaChair2_Grey"`
- `"AI2-THOR/Materials/Fabrics/SofaChair2_White"`
- `"AI2-THOR/Materials/Fabrics/SofaChair2_Fabric_AlbedoTransparency"`

Sofa 3 Materials
****************

Specific textures for `sofa_3` AND `sofa_chair_3` only.

- `"AI2-THOR/Materials/Fabrics/Sofa3_Blue"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Blue_Light"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Brown"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Brown_Pattern"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Green_Dark"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Green_Pattern"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_Red"`
- `"AI2-THOR/Materials/Fabrics/Sofa3_White_Pattern"`

Sofa 8 Materials
****************

Specific textures for `sofa_8` only.

- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat_BaseColor"`
- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3SeatDirt_BaseColor"`
- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat2_BaseColor"`
- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/3Seat2D_BaseColor"`

Sofa Chair 8 Materials
****************

Specific textures for `sofa_chair_8` only.

- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/fotel2_BaseColor"`
- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/fotel2D_BaseColor"`

Sofa 9 Materials
****************

Specific textures for `sofa_9` AND `sofa_chair_9` only.

- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/2Seat_BaseColor"`
- `"Assets/Addressables/MCS/UnityAssetStore/Furniture/Source/Materials/2SeatD_BaseColor"`

Sofa THORKEA Materials
****************

Specific textures for `sofa_4`, `sofa_5`, `sofa_6`, AND `sofa_7` only.

- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Alrid_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Ektorp_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Kramfors_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Solsta_Fabric_Mat"`
- `"AI2-THOR/Objects/Physics/SimObjsPhysics/THORKEA Objects/THORKEA_Assets_Furniture/Sofa/Materials/THORKEA_Sofa_Vreta_Fabric_Mat"`

Wall Materials
**************

- `"AI2-THOR/Materials/Walls/BrownDrywall"`
- `"AI2-THOR/Materials/Walls/Drywall"`
- `"AI2-THOR/Materials/Walls/DrywallBeige"`
- `"AI2-THOR/Materials/Walls/DrywallGreen"`
- `"AI2-THOR/Materials/Walls/DrywallOrange"`
- `"AI2-THOR/Materials/Walls/Drywall4Tiled"`
- `"AI2-THOR/Materials/Walls/EggshellDrywall"`
- `"AI2-THOR/Materials/Walls/RedDrywall"`
- `"AI2-THOR/Materials/Walls/WallDrywallGrey"`
- `"AI2-THOR/Materials/Walls/YellowDrywall"`
- `"Custom/Materials/AzureDrywallMCS"`
- `"Custom/Materials/BlueDrywallMCS"`
- `"Custom/Materials/ChartreuseDrywallMCS"`
- `"Custom/Materials/CyanDrywallMCS"`
- `"Custom/Materials/GreenDrywallMCS"`
- `"Custom/Materials/GreyDrywallMCS"`
- `"Custom/Materials/LimeDrywallMCS"`
- `"Custom/Materials/MagentaDrywallMCS"`
- `"Custom/Materials/MaroonDrywallMCS"`
- `"Custom/Materials/NavyDrywallMCS"`
- `"Custom/Materials/OliveDrywallMCS"`
- `"Custom/Materials/OrangeDrywallMCS"`
- `"Custom/Materials/PurpleDrywallMCS"`
- `"Custom/Materials/RedDrywallMCS"`
- `"Custom/Materials/RoseDrywallMCS"`
- `"Custom/Materials/SpringGreenDrywallMCS"`
- `"Custom/Materials/TealDrywallMCS"`
- `"Custom/Materials/VioletDrywallMCS"`
- `"Custom/Materials/WhiteDrywallMCS"`
- `"Custom/Materials/YellowDrywallMCS"`

Wood Materials
**************

- `"AI2-THOR/Materials/Wood/BlackWood"`
- `"AI2-THOR/Materials/Wood/BedroomFloor1"`
- `"AI2-THOR/Materials/Wood/DarkWood2"`
- `"AI2-THOR/Materials/Wood/DarkWoodSmooth2"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters 1"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters3"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters4"`
- `"AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S"`
- `"AI2-THOR/Materials/Wood/WhiteWood"`
- `"AI2-THOR/Materials/Wood/WoodFloorsCross"`
- `"AI2-THOR/Materials/Wood/WoodGrain_Brown"`
- `"AI2-THOR/Materials/Wood/WoodGrain_Tan"`
- `"AI2-THOR/Materials/Wood/WornWood"`
- `"Custom/Materials/AzureWoodMCS"`
- `"Custom/Materials/BlueWoodMCS"`
- `"Custom/Materials/ChartreuseWoodMCS"`
- `"Custom/Materials/CyanWoodMCS"`
- `"Custom/Materials/GreenWoodMCS"`
- `"Custom/Materials/GreyWoodMCS"`
- `"Custom/Materials/LimeWoodMCS"`
- `"Custom/Materials/MagentaWoodMCS"`
- `"Custom/Materials/MaroonWoodMCS"`
- `"Custom/Materials/NavyWoodMCS"`
- `"Custom/Materials/OliveWoodMCS"`
- `"Custom/Materials/OrangeWoodMCS"`
- `"Custom/Materials/PurpleWoodMCS"`
- `"Custom/Materials/RedWoodMCS"`
- `"Custom/Materials/RoseWoodMCS"`
- `"Custom/Materials/SpringGreenWoodMCS"`
- `"Custom/Materials/TealWoodMCS"`
- `"Custom/Materials/VioletWoodMCS"`
- `"Custom/Materials/WhiteWoodMCS"`
- `"Custom/Materials/YellowWoodMCS"`
- `"UnityAssetStore/Baby_Room/Models/Materials/wood 1"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1"` (blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2"` (red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 3"` (green)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4"` (yellow)

Agent Settings
==============

All options are inclusive. Please note that some options may be restricted to female or male.

Chest Options
*************

.. list-table::
    :header-rows: 1

    * - Chest Option (Female)
      - Chest Option (Male)
      - Description
    * - 0
      -
      - Long dress (ignores `legs`)
    * - 1
      -
      - Tank top
    * - 2
      - 0
      - Long-sleeve formal button-down shirt (permits `tie`)
    * - 3
      - 1
      - Short-sleeve formal button-down shirt (permits `tie`)
    * - 4
      - 2
      - Long-sleeve casual button-down shirt
    * - 5
      - 3
      - Short-sleeve casual button-down shirt
    * - 6
      - 4
      - High-neck no-button shirt
    * - 7
      - 5
      - Long-sleeve no-button shirt
    * - 8
      - 6
      - Short-sleeve no-button shirt

Chest Material Options
**********************

.. list-table::
    :header-rows: 1

    * - Chest Option
      - Material Options (Female)
      - Material Options (Male)
    * - Dress or tank top
      - 0 to 13
      -
    * - Formal button-down shirt
      - 0 to 10
      - 0 to 9
    * - Casual button-down shirt
      - 0 to 11
      - 0 to 10
    * - Other shirts
      - 0 to 14
      - 0 to 11

Eye Options
***********

.. list-table::
    :header-rows: 1

    * - Eye Options
    * - 0 to 3

Feet Options
************

.. list-table::
    :header-rows: 1

    * - Feet Option (Female)
      - Feet Option (Male)
      - Description
    * - 0
      - 0
      - Formal shoe
    * - 1
      - 1
      - Sports shoe
    * - 2
      -
      - Formal shoe with heel

Feet Material Options
*********************

.. list-table::
    :header-rows: 1

    * - Feet Option
      - Material Options
    * - Formal shoe
      - 0 to 11
    * - Sports shoe
      - 0 to 9
    * - Formal shoe with heel
      - 0 to 10

Glasses Options
***************

.. list-table::
    :header-rows: 1

    * - Glasses Options
    * - 0 to 10

Hair Options
************

.. list-table::
    :header-rows: 1

    * - Hair Material Options
      - Hat?
    * - 0 to 6
      - No
    * - 7 to 9
      - Yes

Hair Material Options
*********************

.. list-table::
    :header-rows: 1

    * - Hair Options
      - Hair Material Options
    * - 0 to 9, excluding 5
      - 0 (yellow), 1 (brown), 2 (black), or 3 (white)
    * - 5
      - 0 (brown)

Hat Material Options
********************

.. list-table::
    :header-rows: 1

    * - Hair Option
      - Hat Material Options
    * - 7
      - 0 to 11
    * - 8
      - 0 to 11
    * - 9
      - 0 to 5

Legs Options
************

.. list-table::
    :header-rows: 1

    * - Legs Option (Female)
      - Legs Option (Male)
      - Description
    * - 0
      -
      - Leggings
    * - 1
      - 0
      - Long pants
    * - 2
      - 1
      - Short pants
    * - 3
      -
      - Skirt

Legs Material Options
*********************

.. list-table::
    :header-rows: 1

    * - Legs Option
      - Material Options
    * - Leggings and pants
      - 0 to 14
    * - Skirt
      - 0 to 13

Skin Options
************

.. list-table::
    :header-rows: 1

    * - Skin Option (Female)
      - Skin Option (Male)
      - Description
    * - 0
      - 0
      - Medium-light tone
    * - 1
      - 1
      - Darkest tone
    * - 2
      - 2
      - Medium-dark tone
    * - 3
      - 3
      - Dark tone
    * - 12
      - 4
      - Lightest tone
    * - 13
      - 5
      - Light tone
    * - 4
      -
      - Medium-light tone, with makeup
    * - 5
      -
      - Darkest tone, with makeup
    * - 6
      -
      - Medium-dark tone, with makeup
    * - 7
      -
      - Dark tone, with makeup
    * - 8
      -
      - Medium-light tone, with makeup
    * - 9
      -
      - Darkest tone, with makeup
    * - 10
      -
      - Medium-dark tone, with makeup
    * - 11
      -
      - Dark tone, with makeup

Tie Options
***********

.. list-table::
    :header-rows: 1

    * - Tie Option
      - Description
    * - 0
      - Bowtie
    * - 1
      - Long tie
    * - 2
      - Short tie

Tie Material Options
********************

.. list-table::
    :header-rows: 1

    * - Tie Material Options
    * - 0 to 9

Agent Actions
=============

Unrestricted Animations
***********************

- amazed
- angry
- disgust
- happy
- sad
- Point_start
- Point_hold

Elder Animations
****************

- TPE_clap
- TPE_cry
- TPE_freefall
- TPE_freeze
- TPE_hitbackwards
- TPE_hitforward
- TPE_idle1
- TPE_idle2
- TPE_idle3
- TPE_idle4
- TPE_idle5
- TPE_idleafraid
- TPE_idleangry
- TPE_idlehappy
- TPE_idlesad
- TPE_jump
- TPE_land
- TPE_laugh
- TPE_lookback
- TPE_phone1
- TPE_phone2
- TPE_run
- TPE_runbackwards
- TPE_runIN
- TPE_runjumpFLY
- TPE_runjumpIN
- TPE_runjumpOUT
- TPE_runL
- TPE_runOUT
- TPE_runR
- TPE_scream
- TPE_sitdownIN
- TPE_sitdownOUT
- TPE_sitidle1
- TPE_sitidle2
- TPE_sitphone1
- TPE_sitphone2
- TPE_stairsDOWN
- TPE_stairsUP
- TPE_strafeL
- TPE_strafeR
- TPE_talk1
- TPE_talk2
- TPE_telloff
- TPE_turnL45
- TPE_turnL90
- TPE_turnR45
- TPE_turnR90
- TPE_walk
- TPE_walkbackwards
- TPE_wave

Female Animations
*****************

- TPF_brake
- TPF_clap
- TPF_cry
- TPF_fallbackwardsFLY
- TPF_fallbackwardsIN
- TPF_fallbackwardsOUT
- TPF_fallforwardFLY
- TPF_fallforwardIN
- TPF_fallforwardOUT
- TPF_freefall
- TPF_freeze
- TPF_hitbackwards
- TPF_hitforward
- TPF_idle1
- TPF_idle2
- TPF_idle3
- TPF_idle4
- TPF_idle5
- TPF_idleafraid
- TPF_idleangry
- TPF_idlehappy
- TPF_idlesad
- TPF_jump
- TPF_land
- TPF_laugh
- TPF_lookback
- TPF_phone1
- TPF_phone2
- TPF_run
- TPF_runbackwards
- TPF_runIN
- TPF_runjumpFLY
- TPF_runjumpIN
- TPF_runjumpOUT
- TPF_runL
- TPF_runOUT
- TPF_runR
- TPF_runstrafeL
- TPF_runstrafeR
- TPF_scream
- TPF_sitdownIN
- TPF_sitdownOUT
- TPF_sitidle1
- TPF_sitidle2
- TPF_sitphone1
- TPF_sitphone2
- TPF_stairsDOWN
- TPF_stairsUP
- TPF_static
- TPF_strafeL
- TPF_strafeR
- TPF_talk1
- TPF_talk2
- TPF_telloff
- TPF_turnL45
- TPF_turnL90
- TPF_turnR45
- TPF_turnR90
- TPF_walk
- TPF_walkbackwards
- TPF_wave

Male Animations
***************

- TPM_brake
- TPM_clap
- TPM_cry
- TPM_fallbackwardsFLY
- TPM_fallbackwardsIN
- TPM_fallbackwardsOUT
- TPM_fallforwardFLY
- TPM_fallforwardIN
- TPM_fallforwardOUT
- TPM_freefall
- TPM_freeze
- TPM_hitbackwards
- TPM_hitforward
- TPM_idle1
- TPM_idle2
- TPM_idle3
- TPM_idle4
- TPM_idle5
- TPM_idleafraid
- TPM_idleangry
- TPM_idlehappy
- TPM_idlesad
- TPM_jump
- TPM_land
- TPM_laugh
- TPM_lookback
- TPM_phone1
- TPM_phone2
- TPM_run
- TPM_runbackwards
- TPM_runIN
- TPM_runjumpFLY
- TPM_runjumpIN
- TPM_runjumpOUT
- TPM_runL
- TPM_runOUT
- TPM_runR
- TPM_runstrafeL
- TPM_runstrafeR
- TPM_scream
- TPM_sitdownIN
- TPM_sitdownOUT
- TPM_sitidle1
- TPM_sitidle2
- TPM_sitphone1
- TPM_sitphone2
- TPM_stairsDOWN
- TPM_stairsUP
- TPM_static
- TPM_strafeL
- TPM_strafeR
- TPM_talk1
- TPM_talk2
- TPM_telloff
- TPM_turnL45
- TPM_turnL90
- TPM_turnR45
- TPM_turnR90
- TPM_walk
- TPM_walkbackwards
- TPM_wave

