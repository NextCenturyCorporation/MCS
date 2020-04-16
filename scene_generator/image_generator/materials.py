#Holding the bunches of materials- will probably be changed by whatever Thomas has planned 
#Names here are matching the object material types
#I.R.: an object with the "Ceramic" property will use "CERAMIC_MATERIALS"

BLOCK_BLANK_MATERIALS = [
    ("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/blue_1x1", ["blue"]),
    ("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/red_1x1", ["red"]),
    ("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/wood_1x1", ["brown"]),
    ("UnityAssetStore/Wooden_Toys_Bundle/ToyBlocks/meshes/Materials/yellow_1x1", ["yellow"])
]

BLOCK_LETTER_MATERIALS = [
    ("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_C_Blue_1K/ToyBlockBlueC", ["blue", "brown"]),
    ("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_M_Blue_1K/ToyBlockBlueM", ["blue", "brown"]),
    ("UnityAssetStore/KD_AlphabetBlocks/Assets/Textures/Blue/TOYBlocks_AlphabetBlock_S_Blue_1K/ToyBlockBlueS", ["blue", "brown"])
]

BLOCK_NUMBER_MATERIALS = [
    ("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_1_Yellow_1K/NumberBlockYellow_1", ["yellow", "brown"]),
    ("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_2_Yellow_1K/NumberBlockYellow_2", ["yellow", "brown"]),
    ("UnityAssetStore/KD_NumberBlocks/Assets/Textures/Yellow/TOYBlocks_NumberBlock_3_Yellow_1K/NumberBlockYellow_3", ["yellow", "brown"])
]

CERAMIC_MATERIALS = [
    ("AI2-THOR/Materials/Ceramics/BrownMarbleFake 1", ["brown"]),
    ("AI2-THOR/Materials/Ceramics/ConcreteBoards1", ["grey"]),
    ("AI2-THOR/Materials/Ceramics/GREYGRANITE", ["grey"]),
    ("AI2-THOR/Materials/Ceramics/RedBrick", ["red"]),
    ("AI2-THOR/Materials/Ceramics/TexturesCom_BrickRound0044_1_seamless_S", ["grey"]),
    ("AI2-THOR/Materials/Ceramics/WhiteCountertop", ["grey"])
]

FABRIC_MATERIALS = [
    ("AI2-THOR/Materials/Fabrics/Carpet2", ["brown"]),
    ("AI2-THOR/Materials/Fabrics/Carpet4", ["blue"]),
    ("AI2-THOR/Materials/Fabrics/CarpetDark", ["yellow"]),
    ("AI2-THOR/Materials/Fabrics/CarpetWhite 3", ["white"]),
    ("AI2-THOR/Materials/Fabrics/HotelCarpet3", ["red", "black"]),
    ("AI2-THOR/Materials/Fabrics/RugPattern224", ["green", "brown", "white"])
]

METAL_MATERIALS = [
    ("AI2-THOR/Materials/Metals/BlackSmoothMeta", ["black"]),
    ("AI2-THOR/Materials/Metals/Brass 1", ["yellow"]),
    ("AI2-THOR/Materials/Metals/BrownMetal 1", ["brown"]),
    ("AI2-THOR/Materials/Metals/BrushedIron_AlbedoTransparency", ["black"]),
    ("AI2-THOR/Materials/Metals/GenericStainlessSteel", ["grey"]),
    ("AI2-THOR/Materials/Metals/Metal", ["grey"]),
    ("AI2-THOR/Materials/Metals/WhiteMetal", ["white"]),
    ("UnityAssetStore/Baby_Room/Models/Materials/cabinet metal", ["grey"])
]

PLASTIC_MATERIALS = [
    ("AI2-THOR/Materials/Plastics/BlackPlastic", ["black"]),
    ("AI2-THOR/Materials/Plastics/OrangePlastic", ["orange"]),
    ("AI2-THOR/Materials/Plastics/WhitePlastic", ["white"]),
    ("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 1", ["blue"]),
    ("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 2", ["red"]),
    ("UnityAssetStore/Kindergarten_Interior/Models/Materials/color 4", ["yellow"])
]

RUBBER_MATERIALS = [
    ("AI2-THOR/Materials/Plastics/BlueRubber", ["blue"]),
    ("AI2-THOR/Materials/Plastics/LightBlueRubber", ["blue"])
]

WALL_MATERIALS = [
    ("AI2-THOR/Materials/Walls/Drywall", ["white"]),
    ("AI2-THOR/Materials/Walls/DrywallBeige", ["brown"]),
    ("AI2-THOR/Materials/Walls/DrywallOrange", ["orange"]),
    ("AI2-THOR/Materials/Walls/Drywall4Tiled", ["white"]),
    ("AI2-THOR/Materials/Walls/EggshellDrywall", ["blue"]),
    ("AI2-THOR/Materials/Walls/RedDrywall", ["red"]),
    ("AI2-THOR/Materials/Walls/WallDrywallGrey", ["grey"]),
    ("AI2-THOR/Materials/Walls/YellowDrywall", ["yellow"])
]

WOOD_MATERIALS = [
    ("AI2-THOR/Materials/Wood/BedroomFloor1", ["brown"]),
    ("AI2-THOR/Materials/Wood/DarkWood2", ["black"]),
    ("AI2-THOR/Materials/Wood/DarkWoodSmooth2", ["black"]),
    ("AI2-THOR/Materials/Wood/LightWoodCounters 1", ["brown"]),
    ("AI2-THOR/Materials/Wood/LightWoodCounters4", ["brown"]),
    ("AI2-THOR/Materials/Wood/TexturesCom_WoodFine0050_1_seamless_S", ["brown"]),
    ("AI2-THOR/Materials/Wood/WhiteWood", ["white"]),
    ("AI2-THOR/Materials/Wood/WoodFloorsCross", ["brown"]),
    ("AI2-THOR/Materials/Wood/WoodGrain_Brown", ["brown"]),
    ("AI2-THOR/Materials/Wood/WornWood", ["brown"]),
    ("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 1", ["blue"]),
    ("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 2", ["red"]),
    ("UnityAssetStore/Kindergarten_Interior/Models/Materials/color wood 4", ["yellow"]),
    ("UnityAssetStore/Baby_Room/Models/Materials/wood 1", ["brown"])
]

CEILING_AND_WALL_MATERIALS = CERAMIC_MATERIALS + METAL_MATERIALS + WALL_MATERIALS + WOOD_MATERIALS

OCCLUDER_MATERIALS = CERAMIC_MATERIALS + METAL_MATERIALS + WALL_MATERIALS + WOOD_MATERIALS

FLOOR_MATERIALS = CERAMIC_MATERIALS + FABRIC_MATERIALS + METAL_MATERIALS + WALL_MATERIALS + WOOD_MATERIALS

