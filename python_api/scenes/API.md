# MCS Scene Configuration Files: API

## Scenes

A **scene** is a JSON object (called a [scene config](#scene-config)) that, when passed to the MCS Unity application via the MCS Python Library, describes the objects, materials (colors and textures), and scripted actions that will happen in that specific instance of the MCS 3D simulation environment.

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
        "materialFile": "AI2-THOR/Materials/Plastics/BlueRubber",
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

### Scene Config

Each **scene config** has the following properties:

- `ceilingMaterial` (string, optional): The material (color/texture) for the room's ceiling. See the [Material List](#material-list) for options.
- `floorMaterial` (string, optional): The material (color/texture) for the room's floor. See the [Material List](#material-list) for options.
- `wallMaterial` (string, optional): The material (color/texture) for the room's four outer walls. See the [Material List](#material-list) for options.
- `performerStart` ([transform config](#transform-config), optional): The starting position and rotation of the performer (the "player").  Only the `position.x`, `position.z`, and `rotation.y` properties are used. Default: `{ "position": { "x": 0, "z": 0 }, "rotation": { "y": 0 } }`
- `objects` ([object config](#object-config) array, required): The objects for the scene.

### Object Config

Each **object config** has the following properties:

- `id` (string, required): The object's unique ID.
- `type` (string, required): The object's type from the [Object List](#object-list).
- `forces` ([move config](#move-config) array, optional): The steps on which to apply force to the object. The config `vector` describes the amount of force (in Newtons) to apply in each direction using the global coordinate system. Default: `[]`
- `hides` ([step config](#step-config) array, optional): The steps on which to hide the object, completely removing its existence from the scene until it is shown again (see the `shows` property). Useful if you want to have impossible events (spontaneous disappearance). Default: `[]`
- `kinematic` (boolean, optional): Whether the object should ignore gravity. Usually paired with `structure`. Default: `false`
- `mass` (float, optional): The mass of the object, which affects the physics simulation. Default: `1`
- `materialFile` (string, optional): The material (color/texture) of the object. Please note that most non-primitive objects already have specific material(s). See the [Material List](#material-list) for options. Default: none
- `moveable` (boolean, optional): Whether the object should be moveable, if it is not already moveable based on its `type`. Default: depends on `type`
- `moves` ([move config](#move-config) array, optional): The steps on which to move the object, teleporting it from one position in the scene to another. The config `vector` describes the final position in the global coordinate system. Useful if you want to have impossible events (spontaneous teleportation). Default: `[]`
- `nullParent` ([transform config](#transform-config), optional): Whether to wrap the object in a null parent object. Useful if you want to rotate an object by a point other than its center point. Default: none
- `openable` (boolean, optional): Whether the object should be openable, if it is not already openable based on its `type`. Default: depends on `type`
- `opened` (boolean, optional): Whether the object should begin opened. Must also be `openable`. Default: `false`
- `pickupable` (boolean, optional): Whether the object should be pickupable, if it is not already openable based on its `type`. Pickupable objects are also automatically `moveable`. Default: depends on `type`
- `resizes` ([size config](#size-config) array, optional): The steps on which to resize the object. Useful if you want to have impossible events (spontaneous resizing). Default: `[]`
- `rotates` ([move config](#move-config) array, optional): The steps on which to rotate the object. Useful if you want to have impossible events (spontaneous rotation). The config `vector` describes the final rotation (in degrees) in the global coordinate system. Default: `[]`
- `salientMaterials` (string array, optional)
- `shows` ([show config](#show-config) array, optional): The steps on which to show the object, adding its existence to the scene. Please note that each object begins hidden within the scene, so each object should have at least one element in its `shows` array to be useful. Default: `[]`
- `structure` (boolean, optional): Whether the object is a structural part of the environment. Usually paired with `kinematic`. Default: `false`
- `torques` ([move config](#move-config) array, optional): The steps on which to apply torque to the object. The config `vector` describes the amount of torque (in Newtons) to apply in each direction using the global coordinate system. Default: `[]`

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
- `scale` ([vector config](#vector-config), optional): The object's scale, which will be multipled by its base scale. Default: `{ "x": 1, "y": 1, "z": 1 }`

### Size Config

Each **size config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should begin.  Must be non-negative.  A value of `0` means the action will begin during scene initialization.
- `stepEnd` (integer, required): The step on which the action should end.  Must be equal to or greater than the `stepBegin`.
- `size` ([vector config](#vector-config), required): The coordinates to describe the size, which will be multiplied by its current size. Default: `{ "x": 1, "y": 1, "z": 1 }`

### Step Config

Each **step config** has the following properties:

- `stepBegin` (integer, required): The step on which the action should occur.  Must be non-negative.  A value of `0` means the action will occur during scene initialization.

### Transform Config

Each **transform config** has the following properties:

- `position` ([vector config](#vector-config), optional): The object's position within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `rotation` ([vector config](#vector-config), optional): The object's rotation (in degrees) within the environment using the global coordinate system. Default: `{ "x": 0, "y": 0, "z": 0 }`
- `scale` ([vector config](#vector-config), optional): The object's scale, which will be multipled by its base scale.  Default: `{ "x": 1, "y": 1, "z": 1 }`

### Vector Config

Each **vector config** has the following properties:

- `x` (float, optional)
- `y` (float, optional)
- `z` (float, optional)

## Object List

The following objects are currently available:

- `"apple_1"`
- `"apple_2"`
- `"block_blank_blue_cube"`
- `"block_blank_blue_cylinder"`
- `"block_blank_red_cube"`
- `"block_blank_red_cylinder"`
- `"block_blank_wood_cube"`
- `"block_blank_wood_cylinder"`
- `"block_blank_yellow_cube"`
- `"block_blank_yellow_cylinder"`
- `"block_blue_letter_c"`
- `"block_blue_letter_m"`
- `"block_blue_letter_s"`
- `"block_yellow_number_1"`
- `"block_yellow_number_2"`
- `"block_yellow_number_3"`
- `"bowl_3"`
- `"bowl_4"`
- `"box_2"`
- `"box_3"`
- `"chair_1"`
- `"chair_2"`
- `"changing_table"`
- `"crib"`
- `"cup_2"`
- `"cup_6"`
- `"duck_on_wheels"`
- `"foam_floor_tiles"`
- `"pacifier"`
- `"plate_1"`
- `"plate_3"`
- `"painting_2"`
- `"painting_4"`
- `"painting_5"`
- `"painting_9"`
- `"painting_10"`
- `"painting_16"`
- `"plant_1"`
- `"plant_5"`
- `"plant_7"`
- `"plant_9"`
- `"plant_12"`
- `"plant_16"`
- `"racecar_red"`
- `"shelf_1"`
- `"sofa_1"`
- `"sofa_chair_1"`
- `"table_1"`
- `"table_5"`
- `"table_6"`

## Material List

In Unity, "Materials" are the colors and textures applied to objects in the 3D simulation environment. Some objects may have default materials. Some objects may have multiple materials. Some materials may have patterns intended for objects of a specific size, and may look odd if applied to objects that are too big or small.

For our training and evaluation datasets, we normally use the materials under "Walls" for both the ceiling and the walls, and a combination of some of the materials under "Ceramics", "Fabrics", and "Woods" for the floors.

The following materials are currently available:

### Ceramics

- `"AI2-THOR/Materials/Ceramics/ConcreteBoards1"`
- `"AI2-THOR/Materials/Ceramics/GREYGRANITE"`
- `"AI2-THOR/Materials/Ceramics/KitchenFloor"`
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

- `"AI2-THOR/Materials/Metals/Brass 1"`
- `"AI2-THOR/Materials/Metals/BrownMetal 1"`
- `"AI2-THOR/Materials/Metals/GenericStainlessSteel"`
- `"AI2-THOR/Materials/Metals/Metal"`

### Plastics

- `"AI2-THOR/Materials/Plastics/BlueRubber"`
- `"AI2-THOR/Materials/Plastics/GreenPlastic"`
- `"AI2-THOR/Materials/Plastics/OrangePlastic"`
- `"AI2-THOR/Materials/Plastics/YellowPlastic2"`

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
- `"AI2-THOR/Materials/Wood/LightWoodCounters 1"`
- `"AI2-THOR/Materials/Wood/LightWoodCounters4"`
- `"AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S"`
- `"AI2-THOR/Materials/Wood/WoodFloorsCross"`
- `"AI2-THOR/Materials/Wood/WoodGrain_Brown"`
