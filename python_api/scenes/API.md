# MCS Scene Configuration Files: API

- [Scenes](#scenes)
  - [Scene Config](#scene-config)
  - [Object Config](#object-config)
  - [Goal Config](#goal-config)
  - [Goal Metadata Config](#goal-metadata-config)
  - [Answer Config](#answer-config)
  - [Move Config](#move-config)
  - [Show Config](#show-config)
  - [Size Config](#size-config)
  - [Step Config](#step-config)
  - [Teleport Config](#teleport-config)
  - [Transform Config](#transform-config)
  - [Vector Config](#vector-config)
- [Object List](#object-list)
- [Material List](#material-list)

## Scenes

A **scene** is a JSON object (called a [scene config](#scene-config)) that, when passed to the MCS Unity application via the MCS Python Library, describes the objects, materials (colors and textures), and scripted actions that will happen in that specific instance of the MCS 3D simulation environment.

Please note that all scenes are currently in a room that is 5-by-5 (X/Z) and 3 high (Y) using Unity's global coordinate system, where we consider 1 unit to be approximately 2 feet.

### Scene Config

Example:

```json
{
    "ceilingMaterial": "AI2-THOR/Materials/Walls/Drywall",
    "floorMaterial": "AI2-THOR/Materials/Fabrics/CarpetWhite 3",
    "wallMaterial": "AI2-THOR/Materials/Walls/DrywallBeige",
    "performerStart": {
        "position": {
            "x": -1,
            "z": -1
        },
        "rotation": {
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
```

Each **scene config** has the following properties:

- `name` (string, optional): A unique name for the scene used for our logs. Default: none
- `ceilingMaterial` (string, optional): The material (color/texture) for the room's ceiling. See the [Material List](#material-list) for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/Drywall"`
- `floorMaterial` (string, optional): The material (color/texture) for the room's floor. See the [Material List](#material-list) for options. Default (v0.0.3+): `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `wallMaterial` (string, optional): The material (color/texture) for the room's four outer walls. See the [Material List](#material-list) for options. Default (v0.0.3+): `"AI2-THOR/Materials/Walls/DrywallBeige"`
- `performerStart` ([transform config](#transform-config), optional): The starting position and rotation of the performer (the "player").  Only the `position.x`, `position.z`, and `rotation.y` properties are used. Default: `{ "position": { "x": 0, "z": 0 }, "rotation": { "y": 0 } }`
- `objects` ([object config](#object-config) array, optional): The objects for the scene. Default: `[]`
- `goal` ([goal config](#goal-config), optional): The goal for the scene. Default: none
- `answer` ([answer config](#answer-config), optional): The best answer to the goal for the scene. Default: none

### Object Config

Each **object config** has the following properties:

- `id` (string, required): The object's unique ID.
- `type` (string, required): The object's type from the [Object List](#object-list).
- `forces` ([move config](#move-config) array, optional): The steps on which to apply force to the object. The config `vector` describes the amount of force (in Newtons) to apply in each direction using the global coordinate system. Resets all existing forces on the object to 0 before applying the new force. Default: `[]`
- `hides` ([step config](#step-config) array, optional): The steps on which to hide the object, completely removing its existence from the scene until it is shown again (see the `shows` property). Useful if you want to have impossible events (spontaneous disappearance). Default: `[]`
- `kinematic` (boolean, optional): If true, the object will ignore all forces including gravity. See Unity's [isKinematic property](https://docs.unity3d.com/ScriptReference/Rigidbody-isKinematic.html). Usually paired with `structure`. Default: `false`
- `locationParent` (string, optional): The `id` of another object in the scene. If given, this object's `shows.position` and `shows.rotation` will both start from the position and rotation of the `locationParent` object rather than from `0`. Default: none
- `mass` (float, optional): The mass of the object, which affects the physics simulation. Default: `1`
- `materials` (string array, optional): The material(s) (colors/textures) of the object. An object `type` may use multiple individual materials; if so, they must be listed in a specific order. Please note that most non-primitive objects already have specific material(s). See the [Material List](#material-list) for options. Default: none
- `materialFile` (string, optional): Deprecated (please use `materials` now). The material (color/texture) of the object. Please note that most non-primitive objects already have specific material(s). See the [Material List](#material-list) for options. Default: none
- `moveable` (boolean, optional): Whether the object should be moveable, if it is not already moveable based on its `type`. Default: depends on `type`
- `moves` ([move config](#move-config) array, optional): The steps on which to move the object, moving it from one position in the scene to another. The config `vector` describes the amount of position to change, added to the object's current position. Useful if you want to move objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `nullParent` ([transform config](#transform-config), optional): Whether to wrap the object in a null parent object. Useful if you want to rotate an object by a point other than its center point. Default: none
- `openable` (boolean, optional): Whether the object should be openable, if it is not already openable based on its `type`. Default: depends on `type`
- `opened` (boolean, optional): Whether the object should begin opened. Must also be `openable`. Default: `false`
- `pickupable` (boolean, optional): Whether the object should be pickupable, if it is not already openable based on its `type`. Pickupable objects are also automatically `moveable`. Default: depends on `type`
- `resizes` ([size config](#size-config) array, optional): The steps on which to resize the object. The config `size` is multiplied by the object's current size. Useful if you want to have impossible events (spontaneous resizing). Default: `[]`
- `rotates` ([move config](#move-config) array, optional): The steps on which to rotate the object. The config `vector` describes the amount of rotation (in degrees) to change, added to the object's current rotation. Useful if you want to rotate objects that are `kinematic`. A fifth of each move is made over each of the five substeps (five screenshots) during the step. Default: `[]`
- `salientMaterials` (string array, optional)
- `shows` ([show config](#show-config) array, optional): The steps on which to show the object, adding its existence to the scene. Please note that each object begins hidden within the scene, so each object should have at least one element in its `shows` array to be useful. Default: `[]`
- `structure` (boolean, optional): Whether the object is a structural part of the environment. Usually paired with `kinematic`. Default: `false`
- `teleports` ([teleport config](#teleport-config) array, optional): The steps on which to teleport the object, teleporting it from one position in the scene to another. The config `position` describes the object's end position in global coordinates and is not affected by the object's current position. Useful if you want to have impossible events (spontaneous teleportation). Default: `[]`
- `torques` ([move config](#move-config) array, optional): The steps on which to apply torque to the object. The config `vector` describes the amount of torque (in Newtons) to apply in each direction using the global coordinate system. Resets all existing torques on the object to 0 before applying the new torque. Default: `[]`

### Goal Config

Each **goal config** has the following properties:

- `action_list` (string array array, optional): The list of actions that are available for the scene at each step (outer list index).  Each inner list item is a list of action strings. For example, `['MoveAhead','RotateLook,rotation=180']` restricts the actions to either `'MoveAhead'` or `'RotateLook'` with the `'rotation'` parameter set to `180`. An empty outer `action_list` means that all actions are always available. An empty inner list means that all actions are available for that specific step. Default: none
- `info_list` (array, optional): A list of information for the visualization interface associated with this goal. Default: none
- `last_preview_phase_step` (integer, optional): The last step of the preview phase of this scene, if any. Default: -1
- `last_step` (integer, optional): The last step of this scene. This scene will automatically end following this step.
- `metadata` ([goal metadata config](#goal-metadata-config), optional): The metadata specific to this goal. Default: none
- `task_list` (string array, optional): A list of types for the visualization interface associated with this goal, including the relevant MCS core domains. Default: none
- `type_list` (string array, optional) A list of tasks for the visualization interface associated with this goal (secondary to its types).

### Goal Metadata Config

Each **goal metadata config** has the following properties:

(Coming soon!)

### Answer Config

Each **answer config** has the following properties:

(Coming soon!)

### Move Config

Each **move config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `vector` ([vector config](#vector-config), required): The coordinates to describe the movement. Default: `{ "x": 0, "y": 0, "z": 0 }`

### Show Config

Each **show config** has the following properties:

- `stepBegin` (integer, required): The step on which to show the object.  Must be non-negative.  A value of `0` means the object will be shown during scene initialization.
- `position` ([vector config](#vector-config), optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` ([vector config](#vector-config), optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` ([vector config](#vector-config), optional): The object's scale, which is multiplied by its base scale. Default: `{ "x": 1, "y": 1, "z": 1 }`

### Size Config

Each **size config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `size` ([vector config](#vector-config), required): The coordinates to describe the size, which is multiplied by the object's current size. Default: `{ "x": 1, "y": 1, "z": 1 }`

### Step Config

Each **step config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.

### Teleport Config

Each **teleport config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `position` ([vector config](#vector-config), required): The global coordinates to describe the end position. Default: `{ "x": 0, "y": 0, "z": 0 }`

### Transform Config

Each **transform config** has the following properties:

- `position` ([vector config](#vector-config), optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` ([vector config](#vector-config), optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` ([vector config](#vector-config), optional): The object's scale, which is multiplied by its base scale.  Default: `{ "x": 1, "y": 1, "z": 1 }`

### Vector Config

Each **vector config** has the following properties:

- `x` (float, optional)
- `y` (float, optional)
- `z` (float, optional)

## Object List

You can use any of these strings with an object's `type` property.

The following primitive shapes are available, and can be set as `moveable` or `pickupable`:

- `"capsule"`
- `"cube"`
- `"cylinder"`
- `"sphere"`

The following objects are also available:

| Object Type | Moveable | Pickupable | Receptacle | Openable | Materials |
| --- | --- | --- | --- | --- | --- |
| `"apple_1"` | X | X | | | none |
| `"apple_2"` | X | X | | | none |
| `"block_blank_blue_cube"` | X | X | | | blocks (blank) |
| `"block_blank_blue_cylinder"` | X | X | | | blocks (blank) |
| `"block_blank_red_cube"` | X | X | | | blocks (blank) |
| `"block_blank_red_cylinder"` | X | X | | | blocks (blank) |
| `"block_blank_wood_cube"` | X | X | | | blocks (blank) |
| `"block_blank_wood_cylinder"` | X | X | | | blocks (blank) |
| `"block_blank_yellow_cube"` | X | X | | | blocks (blank) |
| `"block_blank_yellow_cylinder"` | X | X | | | blocks (blank) |
| `"block_blue_letter_c"` | X | X | | | blocks (designs) |
| `"block_blue_letter_m"` | X | X | | | blocks (designs) |
| `"block_blue_letter_s"` | X | X | | | blocks (designs) |
| `"block_yellow_number_1"` | X | X | | | blocks (designs) |
| `"block_yellow_number_2"` | X | X | | | blocks (designs) |
| `"block_yellow_number_3"` | X | X | | | blocks (designs) |
| `"bowl_3"` | X | X | | | plastics |
| `"bowl_4"` | X | X | | | plastics |
| `"box_2"` | X | X | X | X | none |
| `"box_3"` | X | X | X | X | none |
| `"chair_1"` | X | | | | woods |
| `"chair_2"` | X | | | | plastics |
| `"changing_table"` | | | X | X | woods |
| `"crib"` | | | | | woods |
| `"cup_2"` | X | X | | | plastics |
| `"cup_6"` | X | X | | | plastics |
| `"duck_on_wheels"` | X | X | | | blocks (blank) |
| `"foam_floor_tiles"` | | | | | none |
| `"pacifier"` | X | X | | | none |
| `"plate_1"` | X | X | | | plastics |
| `"plate_3"` | X | X | | | plastics |
| `"painting_2"` | | | | | none |
| `"painting_4"` | | | | | none |
| `"painting_5"` | | | | | none |
| `"painting_9"` | | | | | none |
| `"painting_10"` | | | | | none |
| `"painting_16"` | | | | | none |
| `"plant_1"` | | | | | none |
| `"plant_5"` | | | | | none |
| `"plant_7"` | | | | | none |
| `"plant_9"` | | | | | none |
| `"plant_12"` | | | | | none |
| `"plant_16"` | | | | | none |
| `"racecar_red"` | X | X | | | blocks (blank) |
| `"shelf_1"` | | | X | | woods |
| `"sofa_1"` | | | | | none | woods |
| `"sofa_chair_1"` | | | | | none |
| `"table_1"` | | | X | | woods |
| `"table_5"` | | | X | | woods |
| `"table_6"` | | | X | | woods |

- Moveable: Can be pushed, pulled, and knocked over.
- Pickupable: Can be picked up (all pickupable objects are also moveable).
- Receptacle: Can hold objects.
- Openable: Can be opened.
- Materials: Only the listed materials are allowed to be used on the object. If "none", any configured materials will be ignored, and the object's default materials will be used.

### Child Components

Some objects have child components representing cabinets, drawers, or shelves. Child components are not found in the scene configuration file but are automatically generated by the MCS environment. Child components have their own object IDs so the player may use actions like OpenObject or PutObject with specific cabinets/drawers/shelves.

The following objects have the following child components:

- `"changing_table"`:
  - `"<id>_drawer_top"`
  - `"<id>_drawer_bottom"`
  - `"<id>_shelf_top"`
  - `"<id>_shelf_middle"`
  - `"<id>_shelf_bottom"`

## Material List

In Unity, "Materials" are the colors and textures applied to objects in the 3D simulation environment. Some objects may have default materials. Some objects may have multiple materials. Some materials may have patterns intended for objects of a specific size, and may look odd if applied to objects that are too big or small.

For our training and evaluation datasets, we normally use the materials under "Walls", "Ceramics", "Fabrics", and "Woods" for the ceiling and the walls, and the materials under "Ceramics", "Fabrics", and "Woods" for the floors.

The following materials are currently available:

### Blocks (Blank)

- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1"`
- `"UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1"`

### Ceramics

- `"AI2-THOR/Materials/Ceramics/BrownMarbleFake 1"`
- `"AI2-THOR/Materials/Ceramics/ConcreteBoards1"`
- `"AI2-THOR/Materials/Ceramics/GREYGRANITE"`
- `"AI2-THOR/Materials/Ceramics/RedBrick"`
- `"AI2-THOR/Materials/Ceramics/TexturesCom_BrickRound0044_1_seamless_S"` (rough stone)
- `"AI2-THOR/Materials/Ceramics/WhiteCountertop"`

### Fabrics

- `"AI2-THOR/Materials/Fabrics/Carpet2"`
- `"AI2-THOR/Materials/Fabrics/Carpet4"`
- `"AI2-THOR/Materials/Fabrics/CarpetDark"`
- `"AI2-THOR/Materials/Fabrics/CarpetWhite 3"`
- `"AI2-THOR/Materials/Fabrics/HotelCarpet3"` (red pattern)
- `"AI2-THOR/Materials/Fabrics/RugPattern224"` (brown, green, and white pattern)

### Metals

- `"AI2-THOR/Materials/Metals/BlackSmoothMeta"` (yes, it is misspelled)
- `"AI2-THOR/Materials/Metals/Brass 1"`
- `"AI2-THOR/Materials/Metals/BrownMetal 1"`
- `"AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency"`
- `"AI2-THOR/Materials/Metals/GenericStainlessSteel"`
- `"AI2-THOR/Materials/Metals/Metal"`
- `"AI2-THOR/Materials/Metals/WhiteMetal"`
- `"UnityAssetStore/Baby_Room/Models/Materials/cabinet metal"`

### Plastics

- `"AI2-THOR/Materials/Plastics/BlackPlastic"`
- `"AI2-THOR/Materials/Plastics/OrangePlastic"`
- `"AI2-THOR/Materials/Plastics/WhitePlastic"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1"` (flat red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2"` (flat blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4"` (flat yellow)

### Rubbers

- `"AI2-THOR/Materials/Plastics/BlueRubber"`
- `"AI2-THOR/Materials/Plastics/LightBlueRubber"`

### Walls

- `"AI2-THOR/Materials/Walls/Drywall"`
- `"AI2-THOR/Materials/Walls/DrywallBeige"`
- `"AI2-THOR/Materials/Walls/DrywallOrange"`
- `"AI2-THOR/Materials/Walls/Drywall4Tiled"`
- `"AI2-THOR/Materials/Walls/EggshellDrywall"`
- `"AI2-THOR/Materials/Walls/RedDrywall"`
- `"AI2-THOR/Materials/Walls/WallDrywallGrey"`
- `"AI2-THOR/Materials/Walls/YellowDrywall"`

### Woods

- `"AI2-THOR/Materials/Wood/BedroomFloor1"`
- `"AI2-THOR/Materials/Wood/DarkWoodSmooth2"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters 1"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters4"`
- `"AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S"`
- `"AI2-THOR/Materials/Wood/WhiteWood"`
- `"AI2-THOR/Materials/Wood/WoodFloorsCross"`
- `"AI2-THOR/Materials/Wood/WoodGrain_Brown"`
- `"AI2-THOR/Materials/Wood/WornWood"`
- `"UnityAssetStore/Baby_Room/Models/Materials/wood 1"`
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1"` (blue)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2"` (red)
- `"UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4"` (yellow)

The following materials are available for the letter and number block objects:

- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_1_Yellow_1K/NumberBlockYellow_1"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_2_Yellow_1K/NumberBlockYellow_2"`
- `"UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_3_Yellow_1K/NumberBlockYellow_3"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_C_Blue_1K/ToyBlockBlueC"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_M_Blue_1K/ToyBlockBlueM"`
- `"UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_S_Blue_1K/ToyBlockBlueS"`

