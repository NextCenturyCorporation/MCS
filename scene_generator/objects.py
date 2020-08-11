import copy
import uuid
from typing import Any, Dict, List, Tuple, Union

_BALL = {
    "type": "sphere",
    "shape": ["ball"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "massMultiplier": 0.5,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "massMultiplier": 2,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }, {
        "novelCombination": True,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.025,
            "y": 0.025,
            "z": 0.025
        },
        "mass": 0.125,
        "positionY": 0.0125,
        "scale": {
            "x": 0.025,
            "y": 0.025,
            "z": 0.025
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.05,
            "y": 0.05,
            "z": 0.05,
        },
        "mass": 0.25,
        "positionY": 0.025,
        "scale": {
            "x": 0.05,
            "y": 0.05,
            "z": 0.05
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "mass": 0.5,
        "positionY": 0.05,
        "scale": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.25,
            "y": 0.25,
            "z": 0.25
        },
        "mass": 2,
        "positionY": 0.125,
        "scale": {
            "x": 0.25,
            "y": 0.25,
            "z": 0.25
        }
    }]
}


_BLOCK_BLANK_CUBE = {
    "type": "block_blank_wood_cube",
    "obstruct": "vision",
    "shape": ["blank block", "cube"],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "mass": 0.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.2,
            "z": 0.1
        },
        "mass": 1.33,
        "offset": {
            "x": 0,
            "y": 0.1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 2,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.2,
            "y": 0.1,
            "z": 0.2
        },
        "mass": 2.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 2
        }
    }]
}


_BLOCK_BLANK_CYLINDER = {
    "type": "block_blank_wood_cylinder",
    "obstruct": "vision",
    "shape": ["blank block", "cylinder"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.1,
            "z": 0.1
        },
        "mass": 0.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.1,
            "y": 0.2,
            "z": 0.1
        },
        "mass": 1.33,
        "offset": {
            "x": 0,
            "y": 0.1,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 2,
            "z": 1
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.2,
            "y": 0.1,
            "z": 0.2
        },
        "mass": 2.66,
        "offset": {
            "x": 0,
            "y": 0.05,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 1,
            "z": 2
        }
    }]
}


_BLOCK_LETTER = {
    # Readers, please ignore the "blue letter c" in the type: the object's
    # chosen material will change this design.
    "type": "block_blue_letter_c",
    "obstruct": "vision",
    "shape": ["letter block", "cube"],
    "size": "tiny",
    "mass": 0.66,
    "materialCategory": ["block_letter"],
    "salientMaterials": ["wood"],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.1,
        "y": 0.1,
        "z": 0.1
    },
    "offset": {
        "x": 0,
        "y": 0.05,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_BLOCK_NUMBER = {
    # Readers, please ignore the "yellow number 1" in the type: the object's
    # chosen material will change this design.
    "type": "block_yellow_number_1",
    "obstruct": "vision",
    "shape": ["number block", "cube"],
    "size": "tiny",
    "mass": 0.66,
    "materialCategory": ["block_number"],
    "salientMaterials": ["wood"],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.1,
        "y": 0.1,
        "z": 0.1
    },
    "offset": {
        "x": 0,
        "y": 0.05,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_DUCK_ON_WHEELS = {
    "type": "duck_on_wheels",
    "shape": ["duck"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.105,
            "y": 0.085,
            "z": 0.0325
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.0425,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.21,
            "y": 0.17,
            "z": 0.065
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.085,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.42,
            "y": 0.34,
            "z": 0.13
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.17,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_TOY_RACECAR = {
    "type": "racecar_red",
    "shape": ["car"],
    "attributes": ["moveable", "pickupable"],
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.0525,
            "y": 0.045,
            "z": 0.1125
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.0225,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.105,
            "y": 0.09,
            "z": 0.225
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.045,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.21,
            "y": 0.18,
            "z": 0.45
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.09,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 3
        }
    }]
}


_PACIFIER = {
    "type": "pacifier",
    "shape": ["pacifier"],
    "size": "tiny",
    "color": ["blue"],
    "mass": 0.125,
    "materialCategory": [],
    "salientMaterials": ["plastic"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.07,
        "y": 0.04,
        "z": 0.05
    },
    "offset": {
        "x": 0,
        "y": 0.02,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_CRAYON = {
    "chooseMaterial": [{
        # TODO
        "type": "crayon_blue",
        "color": ["blue"]
    }],
    "shape": ["crayon"],
    "size": "tiny",
    "mass": 0.125,
    "materialCategory": [],
    "salientMaterials": ["wax"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.01,
        "y": 0.085,
        "z": 0.01
    },
    "offset": {
        "x": 0,
        "y": 0.0425,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_TURTLE_ON_WHEELS = {
    "type": "turtle_on_wheels",
    "shape": ["turtle"],
    "attributes": ["moveable", "pickupable"],
    "novelShape": True,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.24 * 0.5,
            "y": 0.14 * 0.5,
            "z": 0.085 * 0.5
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.07 * 0.5,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.24,
            "y": 0.14,
            "z": 0.085
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.07,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.24 * 2,
            "y": 0.14 * 2,
            "z": 0.085 * 2
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.07 * 2,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_TOY_CAR = {
    "type": "car_1",
    "shape": ["car"],
    "attributes": ["moveable", "pickupable"],
    "novelShape": True,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "tiny",
        "dimensions": {
            "x": 0.075 * 0.75,
            "y": 0.065 * 0.75,
            "z": 0.14 * 0.75
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.03 * 0.75,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "size": "tiny",
        "dimensions": {
            "x": 0.075 * 1.5,
            "y": 0.065 * 1.5,
            "z": 0.14 * 1.5
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.03 * 1.5,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 1.5
        }
    }, {
        "size": "small",
        "dimensions": {
            "x": 0.075 * 3,
            "y": 0.065 * 3,
            "z": 0.14 * 3
        },
        "mass": 4,
        "offset": {
            "x": 0,
            "y": 0.03 * 3,
            "z": 0
        },
        "positionY": 0.01,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 3
        }
    }]
}


_APPLE = {
    "chooseType": [{
        "type": "apple_1",
        "color": ["red"],
        "dimensions": {
            "x": 0.111,
            "y": 0.12,
            "z": 0.122
        },
        "offset": {
            "x": 0,
            "y": 0.005,
            "z": 0
        }
    }, {
        "type": "apple_2",
        "color": ["green"],
        "dimensions": {
            "x": 0.117,
            "y": 0.121,
            "z": 0.116
        },
        "offset": {
            "x": 0,
            "y": 0.002,
            "z": 0
        }
    }],
    "shape": ["apple"],
    "size": "tiny",
    "mass": 0.5,
    "materialCategory": [],
    "salientMaterials": ["food"],
    "attributes": ["moveable", "pickupable"],
    "positionY": 0.03,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_BOWL = {
    "chooseType": [{
        "type": "bowl_3",
        "dimensions": {
            "x": 0.175,
            "y": 0.116,
            "z": 0.171
        },
        "offset": {
            "x": 0,
            "y": 0.055,
            "z": -0.002
        }
    }, {
        "type": "bowl_4",
        "dimensions": {
            "x": 0.209,
            "y": 0.059,
            "z": 0.206
        },
        "offset": {
            "x": 0.001,
            "y": 0.027,
            "z": 0
        },
    }, {
        "novelShape": True,
        "type": "bowl_6",
        "dimensions": {
            "x": 0.198,
            "y": 0.109,
            "z": 0.201
        },
        "offset": {
            "x": 0,
            "y": 0.052,
            "z": 0
        }
    }],
    "shape": ["bowl"],
    "size": "tiny",
    "chooseMaterial": [{
        "massMultiplier": 0.5,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "mass": 0.5,
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_CUP = {
    "chooseType": [{
        "type": "cup_2",
        "dimensions": {
            "x": 0.105,
            "y": 0.135,
            "z": 0.104
        },
        "offset": {
            "x": 0,
            "y": 0.064,
            "z": 0
        }
    }, {
        "novelShape": True,
        "type": "cup_3",
        "dimensions": {
            "x": 0.123,
            "y": 0.149,
            "z": 0.126
        },
        "offset": {
            "x": 0,
            "y": 0.072,
            "z": 0
        }
    }, {
        "type": "cup_6",
        "dimensions": {
            "x": 0.106,
            "y": 0.098,
            "z": 0.106
        },
        "offset": {
            "x": 0,
            "y": 0.046,
            "z": 0
        }
    }],
    "shape": ["cup"],
    "size": "tiny",
    "chooseMaterial": [{
        "massMultiplier": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "mass": 0.5,
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_PLATE = {
    "chooseType": [{
        "type": "plate_1",
        "dimensions": {
            "x": 0.208,
            "y": 0.117,
            "z": 0.222
        },
        "offset": {
            "x": 0,
            "y": 0.057,
            "z": 0
        }
    }, {
        "type": "plate_3",
        "dimensions": {
            "x": 0.304,
            "y": 0.208,
            "z": 0.305
        },
        "offset": {
            "x": 0,
            "y": 0.098,
            "z": 0
        }
    }, {
        "type": "plate_4",
        "dimensions": {
            "x": 0.202,
            "y": 0.113,
            "z": 0.206
        },
        "offset": {
            "x": 0,
            "y": 0.053,
            "z": 0
        },
    }],
    "shape": ["plate"],
    "size": "tiny",
    "chooseMaterial": [{
        "massMultiplier": 0.5,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "mass": 0.5,
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_BOX_SMALL_XZ_TINY_Y = {
    "obstruct": "vision",
    "shape": ["box"],
    "size": "small",
    "mass": 0.5,
    "materialCategory": ["cardboard"],
    "salientMaterials": ["paper"],
    "attributes": ["moveable", "pickupable", "receptacle", "openable"],
    "chooseType": [{
        "type": "box_2",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0 * 1.25,
                "y": -0.075 * 0.75,
                "z": -0.145 * 1.25
            },
            "dimensions": {
                "x": 0.296 * 1.25,
                "y": 0.193 * 0.75,
                "z": 0.339 * 1.25
            }
        }],
        "dimensions": {
            "x": 0.623 * 1.25,
            "y": 0.381 * 0.75,
            "z": 0.567 * 1.25
        },
        "offset": {
            "x": -0.007 * 1.25,
            "y": 0 * 0.75,
            "z": -0.144 * 1.25
        },
        "closedDimensions": {
            "x": 0.31 * 1.25,
            "y": 0.21 * 0.75,
            "z": 0.36 * 1.25
        },
        "closedOffset": {
            "x": 0,
            "y": -0.08 * 0.75,
            "z": -0.145 * 1.25
        },
        "positionY": 0.2 * 0.75,
        "scale": {
            "x": 1.25,
            "y": 0.75,
            "z": 1.25
        }
    }, {
        "type": "box_3",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.117 * 0.5,
                "z": -0.131
            },
            "dimensions": {
                "x": 0.399,
                "y": 0.305 * 0.5,
                "z": 0.322
            }
        }],
        "dimensions": {
            "x": 0.712,
            "y": 0.5 * 0.5,
            "z": 0.503
        },
        "offset": {
            "x": 0.008,
            "y": -0.038 * 0.5,
            "z": -0.115
        },
        "closedDimensions": {
            "x": 0.41,
            "y": 0.31 * 0.5,
            "z": 0.34
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125 * 0.5,
            "z": -0.13
        },
        "positionY": 0.15,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }, {
        "type": "box_4",
        "color": ["grey"],
        "novelColor": True,
        "novelShape": True,
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.125 * 0.5,
                "z": -0.132
            },
            "dimensions": {
                "x": 0.272,
                "y": 0.308 * 0.5,
                "z": 0.323
            }
        }],
        "dimensions": {
            "x": 0.45,
            "y": 0.491 * 0.5,
            "z": 0.46
        },
        "offset": {
            "x": 0.024,
            "y": -0.046 * 0.5,
            "z": -0.136
        },
        "closedDimensions": {
            "x": 0.3,
            "y": 0.32 * 0.5,
            "z": 0.34
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125 * 0.5,
            "z": -0.13
        },
        "positionY": 0.15,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }]
}


_BOX_TINY = {
    "obstruct": "vision",
    "shape": ["box"],
    "size": "tiny",
    "mass": 0.25,
    "materialCategory": ["cardboard"],
    "salientMaterials": ["paper"],
    "attributes": ["moveable", "pickupable", "receptacle", "openable"],
    "chooseType": [{
        "type": "box_2",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0 * 0.75,
                "y": -0.075 * 0.75,
                "z": -0.145 * 0.75
            },
            "dimensions": {
                "x": 0.296 * 0.75,
                "y": 0.193 * 0.75,
                "z": 0.339 * 0.75
            }
        }],
        "dimensions": {
            "x": 0.623 * 0.75,
            "y": 0.381 * 0.75,
            "z": 0.567 * 0.75
        },
        "offset": {
            "x": -0.007 * 0.75,
            "y": 0 * 0.75,
            "z": -0.144 * 0.75
        },
        "closedDimensions": {
            "x": 0.31 * 0.75,
            "y": 0.21 * 0.75,
            "z": 0.36 * 0.75
        },
        "closedOffset": {
            "x": 0,
            "y": -0.08 * 0.75,
            "z": -0.145 * 0.75
        },
        "positionY": 0.2 * 0.75,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "type": "box_3",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.117 * 0.5,
                "z": -0.131 * 0.5
            },
            "dimensions": {
                "x": 0.399 * 0.5,
                "y": 0.305 * 0.5,
                "z": 0.322 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.712 * 0.5,
            "y": 0.5 * 0.5,
            "z": 0.503 * 0.5
        },
        "offset": {
            "x": 0.008 * 0.5,
            "y": -0.038 * 0.5,
            "z": -0.115 * 0.5
        },
        "closedDimensions": {
            "x": 0.41 * 0.5,
            "y": 0.31 * 0.5,
            "z": 0.34 * 0.5
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125 * 0.5,
            "z": -0.13 * 0.5
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "box_4",
        "color": ["grey"],
        "novelColor": True,
        "novelShape": True,
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.125 * 0.5,
                "z": -0.132 * 0.5
            },
            "dimensions": {
                "x": 0.272 * 0.5,
                "y": 0.308 * 0.5,
                "z": 0.323 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.45 * 0.5,
            "y": 0.491 * 0.5,
            "z": 0.46 * 0.5
        },
        "offset": {
            "x": 0.024 * 0.5,
            "y": -0.046 * 0.5,
            "z": -0.136 * 0.5
        },
        "closedDimensions": {
            "x": 0.3 * 0.5,
            "y": 0.32 * 0.5,
            "z": 0.34 * 0.5
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125 * 0.5,
            "z": -0.13 * 0.5
        },
        "positionY": 0.15,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_CHAIR_BASIC = {
    "type": "chair_1",
    "shape": ["chair"],
    "attributes": ["moveable", "receptacle", "stackTarget"],
    "chooseMaterial": [{
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "novelCombination": True,
        "massMultiplier": 0.5,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "novelCombination": True,
        "massMultiplier": 2,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01,
                "y": 0.5,
                "z": -0.02
            },
            "dimensions": {
                "x": 0.38,
                "y": 0,
                "z": 0.38
            }
        }],
        "dimensions": {
            "x": 0.54,
            "y": 1.04,
            "z": 0.46
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.51,
            "z": -0.02
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.01 * 0.5,
                "y": 0.5 * 0.5,
                "z": -0.02 * 0.5
            },
            "dimensions": {
                "x": 0.38 * 0.5,
                "y": 0,
                "z": 0.38 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.54 * 0.5,
            "y": 1.04 * 0.5,
            "z": 0.46 * 0.5
        },
        "mass": 2.5,
        "offset": {
            "x": 0,
            "y": 0.51 * 0.5,
            "z": -0.02 * 0.5
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_CHAIR_STOOL = {
    "type": "chair_2",
    "shape": ["stool"],
    "obstruct": "navigation",
    "attributes": ["moveable", "receptacle", "stackTarget"],
    "chooseMaterial": [{
        "massMultiplier": 0.5,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }, {
        "novelCombination": True,
        "massMultiplier": 2,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseSize": [{
        "size": "medium",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75,
                "z": 0
            },
            "dimensions": {
                "x": 0.2,
                "y": 0,
                "z": 0.2
            }
        }],
        "dimensions": {
            "x": 0.3,
            "y": 0.75,
            "z": 0.3
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.375,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "small",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.75 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.2 * 0.5,
                "y": 0,
                "z": 0.2 * 0.5
            }
        }],
        "mass": 2.5,
        "dimensions": {
            "x": 0.3 * 0.5,
            "y": 0.75 * 0.5,
            "z": 0.3 * 0.5
        },
        "offset": {
            "x": 0,
            "y": 0.375 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_BLOCK_NOT_PICKUPABLE = {
    "obstruct": "vision",
    "size": "small",
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "novelCombination": True,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "chooseType": [{
        "type": "block_blank_wood_cube",
        "shape": ["blank block", "cube"],
        "attributes": ["moveable", "stackTarget"],
        "dimensions": {
            "x": 0.25,
            "y": 0.25,
            "z": 0.25
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.125,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.5,
            "y": 2.5,
            "z": 2.5
        }
    }, {
        "type": "block_blank_wood_cylinder",
        "shape": ["blank block", "cylinder"],
        "attributes": ["moveable"],
        "dimensions": {
            "x": 0.25,
            "y": 0.25,
            "z": 0.25
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.125,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2.5,
            "y": 2.5,
            "z": 2.5
        }
    }]
}


_BOX_SMALL = {
    "shape": ["box"],
    "size": "small",
    "mass": 1,
    "obstruct": "vision",
    "attributes": ["moveable", "receptacle", "openable"],
    "materialCategory": ["cardboard"],
    "salientMaterials": ["paper"],
    "chooseType": [{
        "type": "box_2",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0 * 1.25,
                "y": -0.075 * 1.25,
                "z": -0.145 * 1.25
            },
            "dimensions": {
                "x": 0.296 * 1.25,
                "y": 0.193 * 1.25,
                "z": 0.339 * 1.25
            }
        }],
        "dimensions": {
            "x": 0.623 * 1.25,
            "y": 0.381 * 1.25,
            "z": 0.567 * 1.25
        },
        "offset": {
            "x": -0.007 * 1.25,
            "y": 0 * 1.25,
            "z": -0.144 * 1.25
        },
        "closedDimensions": {
            "x": 0.31 * 1.25,
            "y": 0.21 * 1.25,
            "z": 0.36 * 1.25
        },
        "closedOffset": {
            "x": 0,
            "y": -0.08 * 1.25,
            "z": -0.145 * 1.25
        },
        "positionY": 0.2 * 1.25,
        "scale": {
            "x": 1.25,
            "y": 1.25,
            "z": 1.25
        }
    }, {
        "type": "box_3",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.117,
                "z": -0.131
            },
            "dimensions": {
                "x": 0.399,
                "y": 0.305,
                "z": 0.322
            }
        }],
        "dimensions": {
            "x": 0.712,
            "y": 0.5,
            "z": 0.503
        },
        "offset": {
            "x": 0.008,
            "y": -0.038,
            "z": -0.115
        },
        "closedDimensions": {
            "x": 0.41,
            "y": 0.31,
            "z": 0.34
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125,
            "z": -0.13
        },
        "positionY": 0.3,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "box_4",
        "color": ["grey"],
        "novelColor": True,
        "novelShape": True,
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.125,
                "z": -0.132
            },
            "dimensions": {
                "x": 0.272,
                "y": 0.308,
                "z": 0.323
            }
        }],
        "dimensions": {
            "x": 0.45,
            "y": 0.491,
            "z": 0.46
        },
        "offset": {
            "x": 0.024,
            "y": -0.046,
            "z": -0.136
        },
        "closedDimensions": {
            "x": 0.3,
            "y": 0.32,
            "z": 0.34
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125,
            "z": -0.13
        },
        "positionY": 0.3,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_BOX_MEDIUM_XZ_SMALL_Y = {
    "shape": ["box"],
    "size": "medium",
    "mass": 3,
    "obstruct": "vision",
    "attributes": ["moveable", "receptacle", "openable"],
    "materialCategory": ["cardboard"],
    "salientMaterials": ["paper"],
    "chooseType": [{
        "type": "box_2",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0 * 1.75,
                "y": -0.075 * 1.75,
                "z": -0.145 * 1.75
            },
            "dimensions": {
                "x": 0.296 * 1.75,
                "y": 0.193 * 1.75,
                "z": 0.339 * 1.75
            }
        }],
        "dimensions": {
            "x": 0.623 * 1.75,
            "y": 0.381 * 1.75,
            "z": 0.567 * 1.75
        },
        "offset": {
            "x": -0.007 * 1.75,
            "y": 0 * 1.75,
            "z": -0.144 * 1.75
        },
        "closedDimensions": {
            "x": 0.31 * 1.75,
            "y": 0.21 * 1.75,
            "z": 0.36 * 1.75
        },
        "closedOffset": {
            "x": 0,
            "y": -0.08 * 1.75,
            "z": -0.145 * 1.75
        },
        "positionY": 0.2 * 1.75,
        "scale": {
            "x": 1.75,
            "y": 1.75,
            "z": 1.75
        }
    }, {
        "type": "box_3",
        "color": ["brown"],
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.117,
                "z": -0.131 * 1.5
            },
            "dimensions": {
                "x": 0.399 * 1.5,
                "y": 0.305,
                "z": 0.322 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.712 * 1.5,
            "y": 0.5,
            "z": 0.503 * 1.5
        },
        "offset": {
            "x": 0.008 * 1.5,
            "y": -0.038,
            "z": -0.115 * 1.5
        },
        "closedDimensions": {
            "x": 0.41 * 1.5,
            "y": 0.31,
            "z": 0.34 * 1.5
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125,
            "z": -0.13 * 1.5
        },
        "positionY": 0.3,
        "scale": {
            "x": 1.5,
            "y": 1,
            "z": 1.5
        }
    }, {
        "type": "box_4",
        "color": ["grey"],
        "novelColor": True,
        "novelShape": True,
        "enclosedAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": -0.125,
                "z": -0.132 * 1.5
            },
            "dimensions": {
                "x": 0.272 * 1.5,
                "y": 0.308,
                "z": 0.323 * 1.5
            }
        }],
        "dimensions": {
            "x": 0.45 * 1.5,
            "y": 0.491,
            "z": 0.46 * 1.5
        },
        "offset": {
            "x": 0.024 * 1.5,
            "y": -0.046,
            "z": -0.136 * 1.5
        },
        "closedDimensions": {
            "x": 0.3 * 1.5,
            "y": 0.32,
            "z": 0.34 * 1.5
        },
        "closedOffset": {
            "x": 0,
            "y": -0.125,
            "z": -0.13 * 1.5
        },
        "positionY": 0.3,
        "scale": {
            "x": 1.5,
            "y": 1,
            "z": 1.5
        }
    }]
}


_POTTED_PLANT_MEDIUM = {
    "shape": ["potted plant"],
    "size": "medium",
    "mass": 2.5,
    "materialCategory": [],
    "salientMaterials": ["organic", "ceramic"],
    "attributes": ["moveable"],
    "chooseType": [{
        "type": "plant_1",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.931,
            "y": 0.807,
            "z": 0.894
        },
        "offset": {
            "x": -0.114,
            "y": 0.399,
            "z": -0.118
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_5",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.522,
            "y": 0.656,
            "z": 0.62
        },
        "offset": {
            "x": -0.024,
            "y": 0.32,
            "z": -0.018
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_7",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.72,
            "y": 1.094,
            "z": 0.755
        },
        "offset": {
            "x": 0,
            "y": 0.546,
            "z": -0.017
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_9",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.679,
            "y": 0.859,
            "z": 0.546
        },
        "offset": {
            "x": 0.037,
            "y": 0.41,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_14",
        "color": ["red", "brown"],
        "dimensions": {
            "x": 0.508,
            "y": 0.815,
            "z": 0.623
        },
        "offset": {
            "x": 0.036,
            "y": 0.383,
            "z": 0.033
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_16",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.702,
            "y": 1.278,
            "z": 0.813
        },
        "offset": {
            "x": -0.008,
            "y": 0.629,
            "z": -0.012
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}


_POTTED_PLANT_SMALL = {
    "shape": ["potted plant"],
    "size": "small",
    "mass": 1,
    "materialCategory": [],
    "salientMaterials": ["organic", "ceramic"],
    "attributes": ["moveable"],
    "chooseType": [{
        "type": "plant_1",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.931 / 0.5,
            "y": 0.807 / 0.5,
            "z": 0.894 / 0.5
        },
        "offset": {
            "x": -0.114 / 0.5,
            "y": 0.399 / 0.5,
            "z": -0.118 / 0.5
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_5",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.522 / 0.5,
            "y": 0.656 / 0.5,
            "z": 0.62 / 0.5
        },
        "offset": {
            "x": -0.024 / 0.5,
            "y": 0.32 / 0.5,
            "z": -0.018 / 0.5
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_7",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.72 / 0.5,
            "y": 1.094 / 0.5,
            "z": 0.755 / 0.5
        },
        "offset": {
            "x": 0 / 0.5,
            "y": 0.546 / 0.5,
            "z": -0.017 / 0.5
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_9",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.679 / 0.5,
            "y": 0.859 / 0.5,
            "z": 0.546 / 0.5
        },
        "offset": {
            "x": 0.037 / 0.5,
            "y": 0.41 / 0.5,
            "z": 0 / 0.5
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_14",
        "color": ["red", "brown"],
        "dimensions": {
            "x": 0.508 / 0.5,
            "y": 0.815 / 0.5,
            "z": 0.623 / 0.5
        },
        "offset": {
            "x": 0.036 / 0.5,
            "y": 0.383 / 0.5,
            "z": 0.033 / 0.5
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_16",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.702 / 0.5,
            "y": 1.278 / 0.5,
            "z": 0.813 / 0.5
        },
        "offset": {
            "x": -0.008 / 0.5,
            "y": 0.629 / 0.5,
            "z": -0.012 / 0.5
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}


_CHANGING_TABLE = {
    "type": "changing_table",
    "obstruct": "vision",
    "shape": ["changing table"],
    "size": "huge",
    "mass": 100,
    "materialCategory": ["wood"],
    "salientMaterials": ["wood"],
    "attributes": ["receptacle", "openable"],
    "enclosedAreas": [{
        # Remove the top drawer for now.
        #        "id": "_drawer_top",
        #        "position": {
        #            "x": 0.165,
        #            "y": 0.47,
        #            "z": -0.03
        #        },
        #        "dimensions": {
        #            "x": 0.68,
        #            "y": 0.22,
        #            "z": 0.41
        #            }
        #    }, {
        "id": "_drawer_bottom",
        "position": {
            "x": 0.165,
            "y": 0.19,
            "z": -0.03
        },
        "dimensions": {
            "x": 0.68,
            "y": 0.2,
            "z": 0.41
        }
    }],
    "openAreas": [{
        # Remove the top shelves for now.
        #        "id": "",
        #        "position": {
        #            "x": 0,
        #            "y": 0.85,
        #            "z": 0
        #        },
        #        "dimensions": {
        #            "x": 1,
        #            "y": 0,
        #            "z": 0.55
        #            }
        #    }, {
        #        "id": "_shelf_top",
        #        "position": {
        #            "x": -0.01,
        #            "y": 0.725,
        #            "z": -0.05
        #        },
        #        "dimensions": {
        #            "x": 1.05,
        #            "y": 0.2,
        #            "z": 0.44
        #            }
        #    }, {
        #        "id": "_shelf_middle",
        #        "position": {
        #            "x": -0.375,
        #            "y": 0.475,
        #            "z": -0.05
        #        },
        #        "dimensions": {
        #            "x": 0.32,
        #            "y": 0.25,
        #            "z": 0.44
        #            }
        #    }, {
        "id": "_shelf_bottom",
        "position": {
            "x": -0.375,
            "y": 0.2,
            "z": -0.05
        },
        "dimensions": {
            "x": 0.32,
            "y": 0.25,
            "z": 0.44
        }
    }],
    "dimensions": {
        "x": 1.1,
        "y": 0.96,
        "z": 0.89
    },
    "offset": {
        "x": -0.01,
        "y": 0.48,
        "z": 0.155
    },
    "closedDimensions": {
        "x": 1.1,
        "y": 0.96,
        "z": 0.58
    },
    "closedOffset": {
        "x": -0.01,
        "y": 0.48,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_CRIB = {
    "type": "crib",
    "shape": ["crib"],
    "size": "huge",
    "materialCategory": ["wood"],
    "salientMaterials": ["wood"],
    "mass": 25,
    "attributes": [],
    "dimensions": {
        "x": 0.65,
        "y": 0.9,
        "z": 1.25
    },
    "offset": {
        "x": 0,
        "y": 0.45,
        "z": 0
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_TABLE_LONG = {
    "type": "table_1",
    "shape": ["table"],
    "attributes": ["receptacle"],
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "novelCombination": True,
        "massMultiplier": 2,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "huge",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0.065 * 1.175,
        #                "y": 0.88,
        #                "z": -0.07
        #            },
        #            "dimensions": {
        #                "x": 0.68 * 1.175,
        #                "y": 0,
        #                "z": 1.62
        #            }
        #        }],
        "dimensions": {
            "x": 0.69 * 1.175,
            "y": 0.88,
            "z": 1.63
        },
        "mass": 5,
        "offset": {
            "x": 0.067 * 1.175,
            "y": 0.44,
            "z": -0.07
        },
        "positionY": 0,
        "scale": {
            "x": 1.175,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0.065 * 2.35,
        #                "y": 0.88,
        #                "z": -0.07
        #            },
        #            "dimensions": {
        #                "x": 0.68 * 2.35,
        #                "y": 0,
        #                "z": 1.62
        #            }
        #        }],
        "dimensions": {
            "x": 0.69 * 2.35,
            "y": 0.88,
            "z": 1.63
        },
        "mass": 10,
        "offset": {
            "x": 0.067 * 2.35,
            "y": 0.44,
            "z": -0.07
        },
        "positionY": 0,
        "scale": {
            "x": 2.35,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "medium",
        "obstruct": "navigation",
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0.065 * 0.5875,
                "y": 0.88 * 0.5,
                "z": -0.07 * 0.25
            },
            "dimensions": {
                "x": 0.68 * 0.5875,
                "y": 0,
                "z": 1.62 * 0.25
            }
        }],
        "dimensions": {
            "x": 0.69 * 0.5875,
            "y": 0.88 * 0.5,
            "z": 1.63 * 0.25
        },
        "mass": 2.5,
        "offset": {
            "x": 0.067 * 0.5875,
            "y": 0.44 * 0.5,
            "z": -0.07 * 0.25
        },
        "positionY": 0,
        "scale": {
            "x": 0.5875,
            "y": 0.5,
            "z": 0.25
        }
    }]
}


_TABLE_TRAY = {
    "type": "table_3",
    "shape": ["table"],
    "obstruct": "navigation",
    "novelShape": True,
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "novelCombination": True,
        "massMultiplier": 2,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "large",
        "attributes": ["moveable", "receptacle"],
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": 0,
        #                "y": 0.84,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 0.4,
        #                "y": 0,
        #                "z": 0.4
        #            }
        #        }],
        "dimensions": {
            "x": 0.573,
            "y": 1.018,
            "z": 0.557
        },
        "mass": 2,
        "offset": {
            "x": 0,
            "y": 0.509,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "size": "medium",
        "attributes": ["moveable", "receptacle", "stackTarget"],
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.84 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.4,
                "y": 0,
                "z": 0.4
            }
        }],
        "dimensions": {
            "x": 0.573,
            "y": 1.018 * 0.5,
            "z": 0.557
        },
        "mass": 1,
        "offset": {
            "x": 0,
            "y": 0.509 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }]
}


_TABLE_COFFEE = {
    "type": "table_5",
    "shape": ["table"],
    "obstruct": "navigation",
    "chooseMaterial": [{
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
    }, {
        "novelCombination": True,
        "massMultiplier": 2,
        "materialCategory": ["metal", "metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "attributes": ["receptacle"],
        "size": "large",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": -0.18 * 0.5,
        #                "y": 0.7,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 1.2 * 0.5,
        #                "y": 0,
        #                "z": 0.9 * 0.667
        #            }
        #        }],
        "dimensions": {
            "x": 1.2 * 0.5,
            "y": 0.7,
            "z": 0.9 * 0.667
        },
        "mass": 10,
        "offset": {
            "x": -0.18 * 0.5,
            "y": 0.35,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 0.667
        }
    }, {
        "attributes": ["receptacle", "stackTarget"],
        "size": "huge",
        # Remove for now because it's too high up.
        #        "openAreas": [{
        #            "id": "",
        #            "position": {
        #                "x": -0.18,
        #                "y": 0.7,
        #                "z": 0
        #            },
        #            "dimensions": {
        #                "x": 1.2,
        #                "y": 0,
        #                "z": 0.9 * 0.667
        #            }
        #        }],
        "dimensions": {
            "x": 1.2,
            "y": 0.7,
            "z": 0.9 * 0.667
        },
        "mass": 20,
        "offset": {
            "x": -0.18,
            "y": 0.35,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 0.667
        }
    }, {
        "attributes": ["receptacle", "stackTarget"],
        "size": "large",
        "openAreas": [{
            "id": "",
            "position": {
                "x": -0.18,
                "y": 0.7 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 1.2,
                "y": 0,
                "z": 0.9 * 0.667
            }
        }],
        "mass": 10,
        "dimensions": {
            "x": 1.2,
            "y": 0.7 * 0.5,
            "z": 0.9 * 0.667
        },
        "offset": {
            "x": -0.18,
            "y": 0.35 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 0.667
        }
    }]
}


_SHELF_CUBBY = {
    "type": "shelf_2",
    "shape": ["shelf"],
    "obstruct": "navigation",
    "chooseMaterial": [{
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "novelCombination": True,
        "massMultiplier": 2,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "small",
        "attributes": ["receptacle", "stackTarget"],
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.73,
                "z": 0
            },
            "dimensions": {
                "x": 0.92 * 0.5,
                "y": 0,
                "z": 1.01 * 0.5
            }
        }, {
            "id": "_middle_shelf",
            "position": {
                "x": 0,
                "y": 0.52,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 0.5,
                "y": 0.22,
                "z": 0.87 * 0.5
            }
        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225,
                "z": 0
            },
            "dimensions": {
                "x": 0.8 * 0.5,
                "y": 0.235,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93 * 0.5,
            "y": 0.73,
            "z": 1.02 * 0.5
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.355,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 1,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "attributes": ["receptacle"],
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.73 * 1.5,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.92 * 1.5,
            #                "y": 0,
            #                "z": 1.01 * 0.5
            #            }
            #        }, {
            "id": "_middle_shelf",
            "position": {
                "x": 0,
                "y": 0.52 * 1.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.65 * 1.5,
                "y": 0.22 * 1.5,
                "z": 0.87 * 0.5
            }
        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225 * 1.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.8 * 1.5,
                "y": 0.235 * 1.5,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93 * 1.5,
            "y": 0.73 * 1.5,
            "z": 1.02 * 0.5
        },
        "mass": 10,
        "offset": {
            "x": 0,
            "y": 0.355 * 1.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1.5,
            "y": 1.5,
            "z": 0.5
        }
    }, {
        "size": "huge",
        "attributes": ["receptacle"],
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.73 * 3,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.92 * 3,
            #                "y": 0,
            #                "z": 1.01 * 0.5
            #            }
            #        }, {
            #            "id": "_middle_shelf",
            #            "position": {
            #                "x": 0,
            #                "y": 0.52 * 3,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.65 * 3,
            #                "y": 0.22 * 3,
            #                "z": 0.87 * 0.5
            #            }
            #        }, {
            "id": "_lower_shelf",
            "position": {
                "x": 0,
                "y": 0.225 * 3,
                "z": 0
            },
            "dimensions": {
                "x": 0.8 * 3,
                "y": 0.235 * 3,
                "z": 0.95 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.93 * 3,
            "y": 0.73 * 3,
            "z": 1.02 * 0.5
        },
        "mass": 15,
        "offset": {
            "x": 0,
            "y": 0.355 * 3,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 0.5
        }
    }]
}


_SHELF_TABLE = {
    "type": "shelf_1",
    "shape": ["shelf"],
    "chooseMaterial": [{
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
    }, {
        "novelCombination": True,
        "massMultiplier": 2,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"],
    }],
    "chooseSize": [{
        "size": "small",
        "attributes": ["receptacle", "stackTarget"],
        "openAreas": [{
            "id": "",
            "position": {
                "x": 0,
                "y": 0.78 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.77 * 0.5,
                "y": 0,
                "z": 0.39 * 0.5
            }
        }, {
            "id": "_top_right_shelf",
            "position": {
                "x": 0.175 * 0.5,
                "y": 0.56 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }, {
            "id": "_top_left_shelf",
            "position": {
                "x": -0.175 * 0.5,
                "y": 0.56 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }, {
            "id": "_bottom_right_shelf",
            "position": {
                "x": 0.175 * 0.5,
                "y": 0.21 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }, {
            "id": "_bottom_left_shelf",
            "position": {
                "x": -0.175 * 0.5,
                "y": 0.21 * 0.5,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 0.5,
                "y": 0.33 * 0.5,
                "z": 0.38 * 0.5
            }
        }],
        "dimensions": {
            "x": 0.78 * 0.5,
            "y": 0.77 * 0.5,
            "z": 0.4 * 0.5
        },
        "mass": 5,
        "offset": {
            "x": 0,
            "y": 0.385 * 0.5,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "size": "medium",
        "attributes": ["receptacle"],
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.78,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.77,
            #                "y": 0,
            #                "z": 0.39
            #            }
            #        }, {
            "id": "_top_right_shelf",
            "position": {
                "x": 0.175,
                "y": 0.56,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }, {
            "id": "_top_left_shelf",
            "position": {
                "x": -0.175,
                "y": 0.56,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }, {
            "id": "_bottom_right_shelf",
            "position": {
                "x": 0.175,
                "y": 0.21,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }, {
            "id": "_bottom_left_shelf",
            "position": {
                "x": -0.175,
                "y": 0.21,
                "z": 0
            },
            "dimensions": {
                "x": 0.33,
                "y": 0.33,
                "z": 0.38
            }
        }],
        "dimensions": {
            "x": 0.78,
            "y": 0.77,
            "z": 0.4
        },
        "mass": 10,
        "offset": {
            "x": 0,
            "y": 0.385,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "novelCombination": True,
        "size": "huge",
        "attributes": ["receptacle"],
        "openAreas": [{
            # Remove for now because it's too high up.
            #            "id": "",
            #            "position": {
            #                "x": 0,
            #                "y": 0.78 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.77 * 2,
            #                "y": 0,
            #                "z": 0.39 * 2
            #            }
            #        }, {
            #            "id": "_top_right_shelf",
            #            "position": {
            #                "x": 0.175 * 2,
            #                "y": 0.56 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.33 * 2,
            #                "y": 0.33 * 2,
            #                "z": 0.38 * 2
            #            }
            #        }, {
            #            "id": "_top_left_shelf",
            #            "position": {
            #                "x": -0.175 * 2,
            #                "y": 0.56 * 2,
            #                "z": 0
            #            },
            #            "dimensions": {
            #                "x": 0.33 * 2,
            #                "y": 0.33 * 2,
            #                "z": 0.38 * 2
            #            }
            #        }, {
            "id": "_bottom_right_shelf",
            "position": {
                "x": 0.175 * 2,
                "y": 0.21 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 2,
                "y": 0.33 * 2,
                "z": 0.38 * 2
            }
        }, {
            "id": "_bottom_left_shelf",
            "position": {
                "x": -0.175 * 2,
                "y": 0.21 * 2,
                "z": 0
            },
            "dimensions": {
                "x": 0.33 * 2,
                "y": 0.33 * 2,
                "z": 0.38 * 2
            }
        }],
        "dimensions": {
            "x": 0.78 * 2,
            "y": 0.77 * 2,
            "z": 0.4 * 2
        },
        "mass": 15,
        "offset": {
            "x": 0,
            "y": 0.385 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_SOFA_1 = {
    "type": "sofa_1",
    "obstruct": "vision",
    "color": ["brown"],
    "shape": ["sofa"],
    "size": "huge",
    "mass": 100,
    "materialCategory": ["sofa_1"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget"],
    "openAreas": [{
        "id": "",
        "position": {
            "x": 0,
            "y": 0.62,
            "z": 0
        },
        "dimensions": {
            "x": 1.95,
            "y": 0,
            "z": 0.63
        }
    }],
    "dimensions": {
        "x": 2.5,
        "y": 1.1,
        "z": 1.1
    },
    "offset": {
        "x": 0,
        "y": 0.55,
        "z": -0.025
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_SOFA_2 = {
    "type": "sofa_2",
    "obstruct": "vision",
    "color": ["grey"],
    "shape": ["sofa"],
    "size": "huge",
    "mass": 100,
    "materialCategory": ["sofa_2"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget"],
    "openAreas": [{
        "id": "",
        "position": {
            "x": 0,
            "y": 0.59,
            "z": 0.125
        },
        "dimensions": {
            "x": 1.95,
            "y": 0,
            "z": 0.625
        }
    }],
    "dimensions": {
        "x": 2.5,
        "y": 1.1,
        "z": 1.1
    },
    "offset": {
        "x": 0,
        "y": 0.55,
        "z": -0.025
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_SOFA_CHAIR_1 = {
    "type": "sofa_chair_1",
    "obstruct": "vision",
    "color": ["black"],
    "shape": ["sofa chair"],
    "size": "huge",
    "mass": 50,
    "materialCategory": ["sofa_chair_1"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget"],
    "openAreas": [{
        "id": "",
        "position": {
            "x": -0.03,
            "y": 0.62,
            "z": 0
        },
        "dimensions": {
            "x": 0.77,
            "y": 0,
            "z": 0.63
        }
    }],
    "dimensions": {
        "x": 1.3,
        "y": 1.1,
        "z": 1.1
    },
    "offset": {
        "x": -0.025,
        "y": 0.55,
        "z": -0.025
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_SOFA_CHAIR_2 = {
    "type": "sofa_chair_2",
    "obstruct": "vision",
    "color": ["grey"],
    "shape": ["sofa chair"],
    "size": "huge",
    "mass": 50,
    "materialCategory": ["sofa_2"],
    "salientMaterials": ["fabric"],
    "attributes": ["receptacle", "stackTarget"],
    "openAreas": [{
        "id": "",
        "position": {
            "x": 0.005,
            "y": 0.59,
            "z": 0.125
        },
        "dimensions": {
            "x": 0.975,
            "y": 0,
            "z": 0.65
        }
    }],
    "dimensions": {
        "x": 1.3,
        "y": 1.1,
        "z": 1.1
    },
    "offset": {
        "x": -0.025,
        "y": 0.55,
        "z": -0.025
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_WARDROBE = {
    "type": "wardrobe",
    "obstruct": "vision",
    "shape": ["wardrobe"],
    "size": "huge",
    "mass": 100,
    "materialCategory": ["wood"],
    "salientMaterials": ["wood"],
    "attributes": ["receptacle", "openable"],
    "novelShape": True,
    "enclosedAreas": [{
        # Remove the top drawers and shelves for now.
        #        "id": "_middle_shelf_right",
        #        "position": {
        #            "x": 0.255,
        #            "y": 1.165,
        #            "z": -0.085
        #        },
        #        "dimensions": {
        #            "x": 0.49,
        #            "y": 1.24,
        #            "z": 0.46
        #        }
        #    }, {
        #        "id": "_middle_shelf_left",
        #        "position": {
        #            "x": -0.255,
        #            "y": 1.295,
        #            "z": -0.085
        #        },
        #        "dimensions": {
        #            "x": 0.49,
        #            "y": 0.98,
        #            "z": 0.46
        #        }
        #    }, {
        #        "id": "_bottom_shelf_left",
        #        "position": {
        #            "x": -0.255,
        #            "y": 0.665,
        #            "z": -0.085
        #        },
        #        "dimensions": {
        #            "x": 0.49,
        #            "y": 0.24,
        #            "z": 0.46
        #        }
        #    }, {
        #        "id": "_lower_drawer_top_left",
        #        "position": {
        #            "x": -0.265,
        #            "y": 0.42,
        #            "z": -0.075
        #        },
        #        "dimensions": {
        #            "x": 0.445,
        #            "y": 0.16
        #            "z": 0.425
        #        }
        #    }, {
        #        "id": "_lower_drawer_top_right",
        #        "position": {
        #            "x": 0.265,
        #            "y": 0.42,
        #            "z": -0.075
        #        },
        #        "dimensions": {
        #            "x": 0.445,
        #            "y": 0.16
        #            "z": 0.425
        #        }
        #    }, {
        "id": "_lower_drawer_bottom_left",
        "position": {
            "x": -0.265,
            "y": 0.21,
            "z": -0.075
        },
        "dimensions": {
            "x": 0.445,
            "y": 0.16,
            "z": 0.425
        }
    }, {
        "id": "_lower_drawer_bottom_right",
        "position": {
            "x": 0.265,
            "y": 0.21,
            "z": -0.075
        },
        "dimensions": {
            "x": 0.445,
            "y": 0.16,
            "z": 0.425
        }
    }],
    "dimensions": {
        "x": 1.07,
        "y": 2.1,
        "z": 0.49
    },
    "offset": {
        "x": 0,
        "y": 1.05,
        "z": -0.09
    },
    "closedDimensions": {
        "x": 1.07,
        "y": 2.1,
        "z": 1
    },
    "closedOffset": {
        "x": 0,
        "y": 1.05,
        "z": 0.17
    },
    "positionY": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}


_POTTED_PLANT_LARGE = {
    "shape": ["potted plant"],
    "size": "large",
    "mass": 5,
    "materialCategory": [],
    "salientMaterials": ["organic", "ceramic"],
    "attributes": [],
    "chooseType": [{
        "type": "plant_1",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.931 * 2,
            "y": 0.807 * 2,
            "z": 0.894
        },
        "offset": {
            "x": -0.114 * 2,
            "y": 0.399 * 2,
            "z": -0.118
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_5",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.522 * 2,
            "y": 0.656 * 2,
            "z": 0.62
        },
        "offset": {
            "x": -0.024 * 2,
            "y": 0.32 * 2,
            "z": -0.018
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_7",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.72 * 2,
            "y": 1.094 * 2,
            "z": 0.755
        },
        "offset": {
            "x": 0 * 2,
            "y": 0.546 * 2,
            "z": -0.017
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_9",
        "color": ["green", "grey", "brown"],
        "dimensions": {
            "x": 0.679 * 2,
            "y": 0.859 * 2,
            "z": 0.546
        },
        "offset": {
            "x": 0.037 * 2,
            "y": 0.41 * 2,
            "z": 0
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_14",
        "color": ["red", "brown"],
        "dimensions": {
            "x": 0.508 * 2,
            "y": 0.815 * 2,
            "z": 0.623
        },
        "offset": {
            "x": 0.036 * 2,
            "y": 0.383 * 2,
            "z": 0.033
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_16",
        "color": ["green", "brown"],
        "dimensions": {
            "x": 0.702 * 2,
            "y": 1.278 * 2,
            "z": 0.813
        },
        "offset": {
            "x": -0.008 * 2,
            "y": 0.629 * 2,
            "z": -0.012
        },
        "positionY": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}


_OCCLUDER_INSTANCE_NORMAL = [{
    "id": "occluder_wall_",
    "shape": ["wall"],
    "size": "huge",
    "type": "cube",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0.75,
            "z": 1
        },
        "scale": {
            "x": 1,
            "y": 1.5,
            "z": 0.1
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 6,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }, {
        "stepBegin": 7,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -0.25,
            "z": 0
        }
    }, {
        "stepBegin": 55,
        "stepEnd": 60,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }],
    "rotates": [{
        "stepBegin": 1,
        "stepEnd": 2,
        "vector": {
            "x": 0,
            "y": 45,
            "z": 0
        }
    }, {
        "stepBegin": 11,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -45,
            "z": 0
        }
    }, {
        "stepBegin": 55,
        "stepEnd": 56,
        "vector": {
            "x": 0,
            "y": 45,
            "z": 0
        }
    }]
}, {
    "id": "occluder_pole_",
    "shape": ["pole"],
    "size": "medium",
    "type": "cylinder",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 2.25,
            "z": 1
        },
        "scale": {
            "x": 0.1,
            "y": 1,
            "z": 0.1
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 6,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }, {
        "stepBegin": 7,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -0.25,
            "z": 0
        }
    }, {
        "stepBegin": 55,
        "stepEnd": 60,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }]
}]


_OCCLUDER_INSTANCE_SIDEWAYS = [{
    "id": "occluder_wall_",
    "shape": ["wall"],
    "size": "huge",
    "type": "cube",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0.75,
            "z": 1
        },
        "scale": {
            "x": 1,
            "y": 1.5,
            "z": 0.1
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 4,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }, {
        "stepBegin": 9,
        "stepEnd": 12,
        "vector": {
            "x": 0,
            "y": -0.25,
            "z": 0
        }
    }, {
        "stepBegin": 35,
        "stepEnd": 38,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }],
    "rotates": [{
        "stepBegin": 5,
        "stepEnd": 6,
        "vector": {
            "x": 45,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 7,
        "stepEnd": 8,
        "vector": {
            "x": -45,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 39,
        "stepEnd": 40,
        "vector": {
            "x": 45,
            "y": 0,
            "z": 0
        }
    }]
}, {
    "id": "occluder_pole_",
    "shape": ["pole"],
    "size": "medium",
    "type": "cylinder",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "materials": ["AI2-THOR/Materials/Walls/DrywallBeige"],
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0.75,
            "z": 1
        },
        "rotation": {
            "x": 0,
            "y": 0,
            "z": 90
        },
        "scale": {
            "x": 0.1,
            "y": 3,
            "z": 0.1
        }
    }],
    "moves": [{
        "stepBegin": 1,
        "stepEnd": 4,
        "vector": {
            "x": 0.25,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 9,
        "stepEnd": 12,
        "vector": {
            "x": -0.25,
            "y": 0,
            "z": 0
        }
    }, {
        "stepBegin": 35,
        "stepEnd": 38,
        "vector": {
            "x": 0.25,
            "y": 0,
            "z": 0
        }
    }]
}]


_INTPHYS: List[Dict[str, Any]] = [{
    "type": "sphere",
    "shape": ["ball"],
    "size": "medium",
    "mass": 0.75,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.75,
        "y": 0.75,
        "z": 0.75
    },
    "positionY": 0.375,
    "scale": {
        "x": 0.75,
        "y": 0.75,
        "z": 0.75
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.38,
            0.759,
            1.139,
            1.518,
            1.898,
            2.278,
            2.657,
            3.037,
            3.416,
            3.796,
            4.176,
            4.555,
            4.935,
            5.314,
            5.694,
            6.074,
            6.453,
            6.833,
            7.213,
            7.592,
            7.972,
            8.351,
            8.731,
            9.111,
            9.49,
            9.87,
            10.249,
            10.629
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.604,
            1.209,
            1.813,
            2.417,
            3.022,
            3.626,
            4.231,
            4.835,
            5.439,
            6.044,
            6.648,
            7.252,
            7.857,
            8.461,
            9.066,
            9.67,
            10.274,
            10.879
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.829,
            1.659,
            2.488,
            3.317,
            4.147,
            4.976,
            5.806,
            6.635,
            7.464,
            8.294,
            9.123,
            9.952,
            10.782
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.832,
            6.212,
            6.591,
            6.971,
            7.35,
            7.73,
            8.11,
            8.489,
            8.869,
            9.248,
            9.628,
            10.008,
            10.387,
            10.767
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.757,
            9.361,
            9.966,
            10.57
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "sphere",
    "shape": ["ball"],
    "size": "small",
    "mass": 0.5,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.5,
        "y": 0.5,
        "z": 0.5
    },
    "positionY": 0.25,
    "scale": {
        "x": 0.5,
        "y": 0.5,
        "z": 0.5
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.379,
            0.759,
            1.138,
            1.517,
            1.897,
            2.276,
            2.656,
            3.035,
            3.414,
            3.794,
            4.173,
            4.552,
            4.932,
            5.311,
            5.691,
            6.07,
            6.449,
            6.829,
            7.208,
            7.587,
            7.967,
            8.346,
            8.725,
            9.105,
            9.484,
            9.864,
            10.243,
            10.622
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.604,
            1.209,
            1.813,
            2.417,
            3.022,
            3.626,
            4.231,
            4.835,
            5.439,
            6.044,
            6.648,
            7.252,
            7.857,
            8.461,
            9.066,
            9.67,
            10.274,
            10.879
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.829,
            1.659,
            2.488,
            3.317,
            4.147,
            4.976,
            5.806,
            6.635,
            7.464,
            8.294,
            9.123,
            9.952,
            10.782
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.832,
            6.211,
            6.591,
            6.97,
            7.349,
            7.729,
            8.108,
            8.487,
            8.867,
            9.246,
            9.625,
            10.005,
            10.384
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.757,
            9.361,
            9.966,
            10.57
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "sphere",
    "shape": ["ball"],
    "size": "tiny",
    "mass": 0.25,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "positionY": 0.125,
    "scale": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.379,
            0.759,
            1.138,
            1.517,
            1.897,
            2.276,
            2.656,
            3.035,
            3.414,
            3.794,
            4.173,
            4.552,
            4.932,
            5.311,
            5.691,
            6.07,
            6.449,
            6.829,
            7.208,
            7.587,
            7.967,
            8.346,
            8.725,
            9.105,
            9.484,
            9.864,
            10.243
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.604,
            1.209,
            1.813,
            2.417,
            3.022,
            3.626,
            4.231,
            4.835,
            5.439,
            6.044,
            6.648,
            7.252,
            7.857,
            8.461,
            9.066,
            9.67,
            10.274
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.829,
            1.659,
            2.488,
            3.317,
            4.147,
            4.976,
            5.806,
            6.635,
            7.464,
            8.294,
            9.123,
            9.952,
            10.782
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.832,
            6.211,
            6.591,
            6.97,
            7.349,
            7.729,
            8.108,
            8.487,
            8.867,
            9.246,
            9.625,
            10.005,
            10.384
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.757,
            9.361,
            9.966,
            10.57
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "cube",
    "shape": ["cube"],
    "size": "medium",
    "mass": 0.75,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.75,
        "y": 0.75,
        "z": 0.75
    },
    "positionY": 0.375,
    "scale": {
        "x": 0.75,
        "y": 0.75,
        "z": 0.75
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.245,
            0.484,
            0.807,
            1.208,
            1.564,
            1.794,
            2.075,
            2.451,
            2.862,
            3.121,
            3.363,
            3.693,
            4.096,
            4.44,
            4.669,
            4.956,
            5.336,
            5.748,
            5.998,
            6.241,
            6.574,
            6.978,
            7.315,
            7.545,
            7.839,
            8.224,
            8.636,
            8.877,
            9.121,
            9.455,
            9.859,
            10.195,
            10.424,
            10.719,
            11.104
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.46,
            0.861,
            1.466,
            2.1,
            2.584,
            2.991,
            3.605,
            4.24,
            4.727,
            5.134,
            5.741,
            6.375,
            6.861,
            7.272,
            7.881,
            8.514,
            8.995,
            9.405,
            10.021,
            10.654,
            11.136
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.684,
            1.31,
            2.141,
            2.999,
            3.709,
            4.327,
            5.177,
            6.035,
            6.742,
            7.36,
            8.212,
            9.027,
            10.402,
            11.245
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.801,
            6.033,
            6.293,
            6.648,
            7.056,
            7.358,
            7.591,
            7.904,
            8.301,
            8.683,
            8.915,
            9.178,
            9.537,
            9.945,
            10.241,
            10.475,
            10.792,
            11.19
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.724,
            9.145,
            9.592,
            10.239,
            10.876
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "cube",
    "shape": ["cube"],
    "size": "small",
    "mass": 0.5,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.5,
        "y": 0.5,
        "z": 0.5
    },
    "positionY": 0.25,
    "scale": {
        "x": 0.5,
        "y": 0.5,
        "z": 0.5
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.247,
            0.511,
            0.909,
            1.205,
            1.461,
            1.848,
            2.169,
            2.416,
            2.789,
            3.133,
            3.373,
            3.73,
            4.092,
            4.33,
            4.668,
            5.048,
            5.285,
            5.593,
            6.003,
            6.248,
            6.525,
            6.93,
            7.206,
            7.468,
            7.864,
            8.161,
            8.419,
            8.807,
            9.123,
            9.373,
            9.751,
            10.086,
            10.329,
            10.695
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.454,
            0.898,
            1.558,
            2.059,
            2.5,
            3.155,
            3.676,
            4.099,
            4.751,
            5.291,
            5.713,
            6.358,
            6.888,
            7.308,
            7.958,
            8.499,
            8.923,
            9.567,
            10.093,
            10.515,
            11.166
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.679,
            1.351,
            2.236,
            2.96,
            3.618,
            4.5,
            5.239,
            5.891,
            6.772,
            7.526,
            8.169,
            9.047,
            9.804,
            10.45,
            11.325
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.8,
            6.037,
            6.341,
            6.755,
            7.008,
            7.269,
            7.664,
            7.96,
            8.223,
            8.608,
            8.933,
            9.187,
            9.559,
            9.903,
            10.148,
            10.502
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.723,
            9.147,
            9.73,
            10.304,
            10.736
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "cube",
    "shape": ["cube"],
    "size": "tiny",
    "mass": 0.25,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "positionY": 0.125,
    "scale": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.253,
            0.616,
            0.867,
            1.223,
            1.492,
            1.841,
            2.117,
            2.469,
            2.754,
            3.093,
            3.374,
            3.723,
            3.991,
            4.351,
            4.626,
            4.976,
            5.26,
            5.602,
            5.886,
            6.23,
            6.514,
            6.864,
            7.147,
            7.492,
            7.774,
            8.125,
            8.414,
            8.747,
            9.037,
            9.378,
            9.671,
            10.005,
            10.293,
            10.643
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.469,
            1.064,
            1.536,
            2.121,
            2.613,
            3.16,
            3.642,
            4.244,
            4.751,
            5.284,
            5.814,
            6.349,
            6.892,
            7.413,
            7.954,
            8.485,
            9.022,
            9.552,
            10.082,
            10.621
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.694,
            1.514,
            2.211,
            3.019,
            3.738,
            4.509,
            5.222,
            6.042,
            6.775,
            7.533,
            8.288,
            9.05,
            9.798,
            10.571
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.8,
            6.062,
            6.413,
            6.69,
            7.037,
            7.304,
            7.666,
            7.931,
            8.294,
            8.56,
            8.92,
            9.185,
            9.547,
            9.809,
            10.177,
            10.44
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.72,
            9.219,
            9.758,
            10.243,
            10.852
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "cylinder",
    "shape": ["cylinder"],
    "size": "medium",
    "mass": 0.75,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.75,
        "y": 0.75,
        "z": 0.75
    },
    "positionY": 0.375,
    "rotation": {
        "x": 90,
        "y": 0,
        "z": 0
    },
    "scale": {
        "x": 0.75,
        "y": 0.375,  # Must be half
        "z": 0.75
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.38,
            0.759,
            1.139,
            1.518,
            1.898,
            2.278,
            2.657,
            3.037,
            3.416,
            3.796,
            4.176,
            4.555,
            4.935,
            5.314,
            5.694,
            6.074,
            6.453,
            6.833,
            7.213,
            7.592,
            7.972,
            8.351,
            8.731,
            9.111,
            9.49,
            9.87,
            10.249,
            10.629,
            11.009
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.604,
            1.209,
            1.813,
            2.417,
            3.022,
            3.626,
            4.231,
            4.835,
            5.439,
            6.044,
            6.648,
            7.252,
            7.857,
            8.461,
            9.066,
            9.67,
            10.274,
            10.879
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.829,
            1.659,
            2.488,
            3.317,
            4.147,
            4.976,
            5.806,
            6.635,
            7.464,
            8.294,
            9.123,
            9.952,
            10.782
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.828,
            6.208,
            6.588,
            6.967,
            7.347,
            7.727,
            8.106,
            8.486,
            8.865,
            9.245,
            9.624,
            10.004,
            10.384,
            10.763
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.753,
            9.357,
            9.962,
            10.566,
            11.171
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.75,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "cylinder",
    "shape": ["cylinder"],
    "size": "small",
    "mass": 0.5,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.5,
        "y": 0.5,
        "z": 0.5
    },
    "positionY": 0.25,
    "rotation": {
        "x": 90,
        "y": 0,
        "z": 0
    },
    "scale": {
        "x": 0.5,
        "y": 0.25,  # Must be half
        "z": 0.5
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.379,
            0.759,
            1.138,
            1.517,
            1.897,
            2.276,
            2.656,
            3.035,
            3.414,
            3.794,
            4.173,
            4.552,
            4.932,
            5.311,
            5.691,
            6.07,
            6.449,
            6.829,
            7.208,
            7.587,
            7.967,
            8.346,
            8.725,
            9.105,
            9.484,
            9.864,
            10.243,
            10.622
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.604,
            1.209,
            1.813,
            2.417,
            3.022,
            3.626,
            4.231,
            4.835,
            5.439,
            6.044,
            6.648,
            7.252,
            7.857,
            8.461,
            9.066,
            9.67,
            10.274,
            10.879
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.829,
            1.659,
            2.488,
            3.317,
            4.147,
            4.976,
            5.806,
            6.635,
            7.464,
            8.294,
            9.123,
            9.952,
            10.782
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.832,
            6.211,
            6.591,
            6.97,
            7.349,
            7.727,
            8.108,
            8.487,
            8.867,
            9.246,
            9.625,
            10.004,
            10.384,
            10.764
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.757,
            9.361,
            9.966,
            10.57
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.5,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}, {
    "type": "cylinder",
    "shape": ["cylinder"],
    "size": "tiny",
    "mass": 0.25,
    "chooseMaterial": [{
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "positionY": 0.125,
    "rotation": {
        "x": 90,
        "y": 0,
        "z": 0
    },
    "scale": {
        "x": 0.25,
        "y": 0.125,  # Must be half
        "z": 0.25
    },
    "intphysOptions": [{
        "y": 0,
        "force": {
            "x": 300 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.379,
            0.759,
            1.138,
            1.517,
            1.897,
            2.276,
            2.656,
            3.035,
            3.414,
            3.794,
            4.173,
            4.552,
            4.932,
            5.311,
            5.691,
            6.07,
            6.449,
            6.829,
            7.208,
            7.587,
            7.967,
            8.346,
            8.725,
            9.105,
            9.484,
            9.864,
            10.243,
            10.622
        ]
    }, {
        "y": 0,
        "force": {
            "x": 450 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.604,
            1.209,
            1.813,
            2.417,
            3.022,
            3.626,
            4.231,
            4.835,
            5.439,
            6.044,
            6.648,
            7.252,
            7.857,
            8.461,
            9.066,
            9.67,
            10.274,
            10.879
        ]
    }, {
        "y": 0,
        "force": {
            "x": 600 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.829,
            1.659,
            2.488,
            3.317,
            4.147,
            4.976,
            5.806,
            6.635,
            7.464,
            8.294,
            9.123,
            9.952,
            10.782
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 300 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.45,
            0.9,
            1.35,
            1.8,
            2.25,
            2.7,
            3.15,
            3.6,
            4.05,
            4.5,
            4.95,
            5.4,
            5.832,
            6.211,
            6.591,
            6.97,
            7.349,
            7.727,
            8.108,
            8.487,
            8.867,
            9.246,
            9.625,
            10.004,
            10.384
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 450 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.675,
            1.35,
            2.025,
            2.7,
            3.375,
            4.05,
            4.725,
            5.4,
            6.075,
            6.75,
            7.425,
            8.1,
            8.757,
            9.361,
            9.966,
            10.57
        ]
    }, {
        "y": 1.5,
        "force": {
            "x": 600 * 0.25,
            "y": 0,
            "z": 0
        },
        "position_by_step": [
            0.9,
            1.8,
            2.7,
            3.6,
            4.5,
            5.4,
            6.3,
            7.2,
            8.1,
            9,
            9.9,
            11.8
        ]
    }]
}]


_INTPHYS_NOVEL = [{
    "type": "duck_on_wheels",
    "novelShape": True,  # This is a novel shape for IntPhys scenes
    "attributes": ["moveable", "pickupable"],
    "shape": ["duck"],
    "size": "tiny",
    "mass": 2,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        "x": 0.21,
        "y": 0.17,
        "z": 0.065
    },
    "offset": {
        "x": 0,
        "y": 0.085,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "duck_on_wheels",
    "novelShape": True,  # This is a novel shape for IntPhys scenes
    "attributes": ["moveable", "pickupable"],
    "shape": ["duck"],
    "size": "small",
    "mass": 4,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        "x": 0.21 * 2.5,
        "y": 0.17 * 2.5,
        "z": 0.065 * 2.5
    },
    "offset": {
        "x": 0,
        "y": 0.085 * 2.5,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 2.5,
        "y": 2.5,
        "z": 2.5
    }
}, {
    "type": "duck_on_wheels",
    "novelShape": True,  # This is a novel shape for IntPhys scenes
    "attributes": ["moveable", "pickupable"],
    "shape": ["duck"],
    "size": "medium",
    "mass": 8,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        "x": 0.21 * 4,
        "y": 0.17 * 4,
        "z": 0.065 * 4
    },
    "offset": {
        "x": 0,
        "y": 0.085 * 4,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 4,
        "y": 4,
        "z": 4
    }
}, {
    "type": "racecar_red",
    "novelShape": True,  # This is a novel shape for IntPhys scenes
    "attributes": ["moveable", "pickupable"],
    "shape": ["car"],
    "size": "tiny",
    "mass": 2,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        # The X and Z dimensions here are switched due to the Y rotation that's
        # configured below.
        "x": 0.15 * 2,
        "y": 0.06 * 2,
        "z": 0.07 * 2
    },
    "offset": {
        "x": 0,
        "y": 0.03 * 2,
        "z": 0
    },
    "rotation": {
        "x": 0,
        "y": 90,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 2,
        "y": 2,
        "z": 2
    }
}, {
    "type": "racecar_red",
    "novelShape": True,  # This is a novel shape for IntPhys scenes
    "attributes": ["moveable", "pickupable"],
    "shape": ["car"],
    "size": "small",
    "mass": 4,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        # The X and Z dimensions here are switched due to the Y rotation that's
        # configured below.
        "x": 0.15 * 3.5,
        "y": 0.06 * 3.5,
        "z": 0.07 * 3.5
    },
    "offset": {
        "x": 0,
        "y": 0.03 * 3.5,
        "z": 0
    },
    "rotation": {
        "x": 0,
        "y": 90,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 3.5,
        "y": 3.5,
        "z": 3.5
    }
}, {
    "type": "racecar_red",
    "novelShape": True,  # This is a novel shape for IntPhys scenes
    "attributes": ["moveable", "pickupable"],
    "shape": ["car"],
    "size": "medium",
    "mass": 4,
    "chooseMaterial": [{
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }, {
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "dimensions": {
        # The X and Z dimensions here are switched due to the Y rotation that's
        # configured below.
        "x": 0.15 * 5,
        "y": 0.06 * 5,
        "z": 0.07 * 5
    },
    "offset": {
        "x": 0,
        "y": 0.03 * 5,
        "z": 0
    },
    "rotation": {
        "x": 0,
        "y": 90,
        "z": 0
    },
    "positionY": 0.01,
    "scale": {
        "x": 5,
        "y": 5,
        "z": 5
    }
}]


def create_occluder(wall_material: Tuple[str,
                                         List[str]],
                    pole_material: Tuple[str,
                                         List[str]],
                    x_position: float,
                    x_scale: float,
                    sideways: bool = False) -> Tuple[Dict[str,
                                                          Any],
                                                     Dict[str,
                                                          Any]]:
    """Create an occluder pair of objects: (wall, pole)."""
    if sideways:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_SIDEWAYS)
    else:
        occluder = copy.deepcopy(_OCCLUDER_INSTANCE_NORMAL)

    WALL = 0
    POLE = 1

    occluder_id = str(uuid.uuid4())
    occluder[WALL]['id'] = occluder[WALL]['id'] + occluder_id
    occluder[POLE]['id'] = occluder[POLE]['id'] + occluder_id

    occluder[WALL]['materials'] = [wall_material[0]]
    occluder[POLE]['materials'] = [pole_material[0]]

    occluder[WALL]['color'] = wall_material[1]
    occluder[POLE]['color'] = pole_material[1]

    # Just set the occluder's info to its color for now.
    occluder[WALL]['info'] = wall_material[1]
    occluder[POLE]['info'] = pole_material[1]

    occluder[WALL]['shows'][0]['position']['x'] = x_position
    occluder[POLE]['shows'][0]['position']['x'] = x_position

    occluder[WALL]['shows'][0]['scale']['x'] = x_scale

    # is_occluder is needed by SpatioTemporalContinuityQuartet
    occluder[WALL]['intphysOption'] = {
        'is_occluder': True
    }

    if sideways:
        if x_position > 0:
            occluder[POLE]['shows'][0]['position']['x'] = 3 + \
                x_position + x_scale / 2
        else:
            occluder[POLE]['shows'][0]['position']['x'] = - \
                3 + x_position - x_scale / 2
    elif x_position > 0:
        for rot in occluder[WALL]['rotates']:
            rot['vector']['y'] *= -1

    return occluder


_PICKUPABLE_BALLS = [_BALL]
_PICKUPABLE_BLOCKS = [
    _BLOCK_BLANK_CUBE,
    _BLOCK_BLANK_CYLINDER,
    _BLOCK_LETTER,
    _BLOCK_NUMBER]
_PICKUPABLE_TOYS = [
    _TOY_CAR,
    _TOY_RACECAR,
    _DUCK_ON_WHEELS,
    _TURTLE_ON_WHEELS,
    _CRAYON,
    _PACIFIER
]
_PICKUPABLE_MISC = [
    _APPLE,
    _BOWL,
    _CUP,
    _PLATE,
    _BOX_TINY,
    _BOX_SMALL_XZ_TINY_Y
]


# Moveable (push/pull) but not pickupable
_MOVEABLE = [
    # TODO Change definitions to CHAIR_SMALL and CHAIR_MEDIUM when their novel
    # targs are no longer needed
    _CHAIR_BASIC,
    _CHAIR_STOOL,
    _BLOCK_NOT_PICKUPABLE,
    _BOX_SMALL,
    _BOX_MEDIUM_XZ_SMALL_Y,
    _POTTED_PLANT_MEDIUM,
    _POTTED_PLANT_SMALL
]


# Not moveable by babies
_IMMOBILE = [
    _CHANGING_TABLE,
    _CRIB,
    _TABLE_LONG,
    _TABLE_TRAY,
    _TABLE_COFFEE,
    _SHELF_CUBBY,
    _SHELF_TABLE,
    _SOFA_1,
    _SOFA_2,
    _SOFA_CHAIR_1,
    _SOFA_CHAIR_2,
    _WARDROBE,
    _POTTED_PLANT_LARGE
]


_PICKUPABLE_LISTS = [
    _PICKUPABLE_BALLS,
    _PICKUPABLE_BLOCKS,
    _PICKUPABLE_TOYS,
    _PICKUPABLE_MISC]
_PICKUPABLE = [
    item for object_list in _PICKUPABLE_LISTS for item in object_list]
_ALL_LISTS = [_PICKUPABLE, _MOVEABLE, _IMMOBILE]
_ALL = [item for object_list in _ALL_LISTS for item in object_list]


def get(prop: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Returns a deep copy of the global property with the given name (normally either an object definition or an object
    definition list)."""
    return copy.deepcopy(globals()['_' + prop])
