import copy
import logging
import uuid

OBJECTS_PICKUPABLE_BALLS = [{
    "type": "sphere",
    "info": ["tiny", "ball"],
    "choose": [{
        "mass": 0.0625,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "mass": 0.125,
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "mass": 0.125,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "mass": 0.25,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.025,
        "y": 0.025,
        "z": 0.025
    },
    "position_y": 0.0125,
    "scale": {
        "x": 0.025,
        "y": 0.025,
        "z": 0.025
    }
}, {
    "type": "sphere",
    "info": ["tiny", "ball"],
    "choose": [{
        "mass": 0.125,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "mass": 0.25,
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "mass": 0.25,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "mass": 0.5,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.05,
        "y": 0.05,
        "z": 0.05,
    },
    "position_y": 0.025,
    "scale": {
        "x": 0.05,
        "y": 0.05,
        "z": 0.05
    }
}, {
    "type": "sphere",
    "info": ["tiny", "ball"],
    "choose": [{
        "mass": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "mass": 0.5,
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"]
    }, {
        "mass": 0.5,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "mass": 1,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.1,
        "y": 0.1,
        "z": 0.1
    },
    "position_y": 0.05,
    "scale": {
        "x": 0.1,
        "y": 0.1,
        "z": 0.1
    }
}, {
    "type": "sphere",
    "info": ["small", "ball"],
    "choose": [{
        "mass": 1,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic", "hollow"]
    }, {
        "mass": 2,
        "materialCategory": ["rubber"],
        "salientMaterials": ["rubber"],
    }, {
        "mass": 2,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }, {
        "mass": 4,
        "materialCategory": ["metal"],
        "salientMaterials": ["metal"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "position_y": 0.125,
    "scale": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    }
}]

OBJECTS_PICKUPABLE_BLOCKS = [{
    "type": "block_blank_wood_cube",
    "info": ["tiny", "blank block", "cube"],
    "choose": [{
        "mass": 0.66,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "block_blank_wood_cube",
    "info": ["tiny", "blank block", "cube"],
    "choose": [{
        "mass": 1.33,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.1,
        "y": 0.2,
        "z": 0.1
    },
    "offset": {
        "x": 0,
        "y": 0.1,
        "z": 0
    },
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 2,
        "z": 1
    }
}, {
    "type": "block_blank_wood_cube",
    "info": ["tiny", "blank block", "cube"],
    "choose": [{
        "mass": 2.66,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.2,
        "y": 0.1,
        "z": 0.2
    },
    "offset": {
        "x": 0,
        "y": 0.05,
        "z": 0
    },
    "position_y": 0,
    "scale": {
        "x": 2,
        "y": 1,
        "z": 2
    }
}, {
    "type": "block_blank_wood_cylinder",
    "info": ["tiny", "blank block", "cylinder"],
    "choose": [{
        "mass": 0.66,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable", "pickupable"],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "block_blank_wood_cylinder",
    "info": ["tiny", "blank block", "cylinder"],
    "choose": [{
        "mass": 1.33,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.1,
        "y": 0.2,
        "z": 0.1
    },
    "offset": {
        "x": 0,
        "y": 0.1,
        "z": 0
    },
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 2,
        "z": 1
    }
}, {
    "type": "block_blank_wood_cylinder",
    "info": ["tiny", "blank block", "cylinder"],
    "choose": [{
        "mass": 2.66,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.2,
        "y": 0.1,
        "z": 0.2
    },
    "offset": {
        "x": 0,
        "y": 0.05,
        "z": 0
    },
    "position_y": 0,
    "scale": {
        "x": 2,
        "y": 1,
        "z": 2
    }
}, {
    # Readers, please ignore the "yellow number 1" in the type: the object's chosen material will change this design.
    "type": "block_yellow_number_1",
    "info": ["tiny", "letter block", "cube"],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    # Readers, please ignore the "yellow number 1" in the type: the object's chosen material will change this design.
    "type": "block_yellow_number_1",
    "info": ["tiny", "number block", "cube"],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}]

OBJECTS_PICKUPABLE_TOYS = [{
    "type": "duck_on_wheels",
    "attributes": ["moveable", "pickupable"],
    "choose": [{
        "info": ["tiny", "duck"],
        "mass": 1,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"],
        "dimensions": {
            "x": 0.105,
            "y": 0.085,
            "z": 0.0325
        },
        "offset": {
            "x": 0,
            "y": 0.0425,
            "z": 0
        },
        "position_y": 0.01,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "info": ["tiny", "duck"],
        "mass": 2,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"],
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
        "position_y": 0.01,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "info": ["small", "duck"],
        "mass": 4,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"],
        "dimensions": {
            "x": 0.42,
            "y": 0.34,
            "z": 0.13
        },
        "offset": {
            "x": 0,
            "y": 0.17,
            "z": 0
        },
        "position_y": 0.01,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}, {
    "type": "racecar_red",
    "attributes": ["moveable", "pickupable"],
    "choose": [{
        "info": ["tiny", "racecar"],
        "mass": 1,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"],
        "dimensions": {
            "x": 0.0525,
            "y": 0.045,
            "z": 0.1125
        },
        "offset": {
            "x": 0,
            "y": 0.0225,
            "z": 0
        },
        "position_y": 0.01,
        "scale": {
            "x": 0.75,
            "y": 0.75,
            "z": 0.75
        }
    }, {
        "info": ["tiny", "racecar"],
        "mass": 2,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"],
        "dimensions": {
            "x": 0.105,
            "y": 0.09,
            "z": 0.225
        },
        "offset": {
            "x": 0,
            "y": 0.045,
            "z": 0
        },
        "position_y": 0.01,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "info": ["small", "racecar"],
        "mass": 4,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"],
        "dimensions": {
            "x": 0.21,
            "y": 0.18,
            "z": 0.45
        },
        "offset": {
            "x": 0,
            "y": 0.09,
            "z": 0
        },
        "position_y": 0.01,
        "scale": {
            "x": 3,
            "y": 3,
            "z": 3
        }
    }]
}, {
    "type": "pacifier",
    "info": ["tiny", "pacifier"],
    "mass": 0.125,
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
    "position_y": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "choose": [{
        "type": "crayon_blue",
        "info": ["tiny", "blue", "crayon"]
    }],
    "mass": 0.125,
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
    "position_y": 0.01,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}]

OBJECTS_PICKUPABLE_MISC = [{
    "type": "apple_1",
    "info": ["tiny", "red", "apple"],
    "mass": 0.5,
    "salientMaterials": ["food"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.111,
        "y": 0.12,
        "z": 0.122
    },
    "offset": {
        "x": 0,
        "y": 0.005,
        "z": 0
    },
    "position_y": 0.03,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "apple_2",
    "info": ["tiny", "green", "apple"],
    "mass": 0.5,
    "salientMaterials": ["food"],
    "attributes": ["moveable", "pickupable"],
    "dimensions": {
        "x": 0.117,
        "y": 0.121,
        "z": 0.116
    },
    "offset": {
        "x": 0,
        "y": 0.002,
        "z": 0
    },
    "position_y": 0.03,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "bowl_3",
    "info": ["tiny", "bowl"],
    "choose": [{
        "mass": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.175,
        "y": 0.116,
        "z": 0.171
    },
    "offset": {
        "x": 0,
        "y": 0.055,
        "z": -0.002
    },
    "position_y": 0.005,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "bowl_4",
    "info": ["tiny", "bowl"],
    "choose": [{
        "mass": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
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
    "position_y": 0.005,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "cup_2",
    "info": ["tiny", "cup"],
    "choose": [{
        "mass": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.105,
        "y": 0.135,
        "z": 0.104
    },
    "offset": {
        "x": 0,
        "y": 0.064,
        "z": 0
    },
    "position_y": 0.005,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "cup_6",
    "info": ["tiny", "cup"],
    "choose": [{
        "mass": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.106,
        "y": 0.098,
        "z": 0.106
    },
    "offset": {
        "x": 0,
        "y": 0.046,
        "z": 0
    },
    "position_y": 0.005,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "plate_1",
    "info": ["tiny", "plate"],
    "choose": [{
        "mass": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.208,
        "y": 0.117,
        "z": 0.222
    },
    "offset": {
        "x": 0,
        "y": 0.057,
        "z": 0
    },
    "position_y": 0.005,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "plate_3",
    "info": ["tiny", "plate"],
    "choose": [{
        "mass": 0.25,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"],
    }],
    "attributes": ["moveable", "pickupable", "stackTarget"],
    "dimensions": {
        "x": 0.304,
        "y": 0.208,
        "z": 0.305
    },
    "offset": {
        "x": 0,
        "y": 0.098,
        "z": 0
    },
    "position_y": 0.005,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "box_2",
    "info": ["small", "brown", "box"],
    "mass": 0.5,
    "salientMaterials": ["paper"],
    "attributes": ["moveable", "pickupable", "receptacle", "openable"],
    "enclosed_areas": [{
        "position": {
            "x": 0 * 1.25,
            "y": -0.074 * 0.75,
            "z": -0.145 * 1.25
        },
        "dimensions": {
            "x": 0.296 * 1.25,
            "y": 0.203 * 0.75,
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
    "position_y": 0.2 * 0.75,
    "scale": {
        "x": 1.25,
        "y": 0.75,
        "z": 1.25
    }
}, {
    "type": "box_2",
    "info": ["tiny", "brown", "box"],
    "mass": 0.25,
    "salientMaterials": ["paper"],
    "attributes": ["moveable", "pickupable", "receptacle", "openable"],
    "enclosed_areas": [{
        "position": {
            "x": 0 * 0.75,
            "y": -0.074 * 0.75,
            "z": -0.145 * 0.75
        },
        "dimensions": {
            "x": 0.296 * 0.75,
            "y": 0.203 * 0.75,
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
    "position_y": 0.2 * 0.75,
    "scale": {
        "x": 0.75,
        "y": 0.75,
        "z": 0.75
    }
}, {
    "type": "box_3",
    "info": ["small", "brown", "box"],
    "mass": 0.5,
    "salientMaterials": ["paper"],
    "attributes": ["moveable", "pickupable", "receptacle", "openable"],
    "enclosed_areas": [{
        "position": {
            "x": 0,
            "y": -0.0585,
            "z": -0.131
        },
        "dimensions": {
            "x": 0.399,
            "y": 0.1525,
            "z": 0.322
        }
    }],
    "dimensions": {
        "x": 0.712,
        "y": 0.25,
        "z": 0.503
    },
    "offset": {
        "x": 0.008,
        "y": -0.019,
        "z": -0.115
    },
    "position_y": 0.15,
    "scale": {
        "x": 1,
        "y": 0.5,
        "z": 1
    }
}, {
    "type": "box_3",
    "info": ["tiny", "brown", "box"],
    "mass": 0.25,
    "salientMaterials": ["paper"],
    "attributes": ["moveable", "pickupable", "receptacle", "openable"],
    "enclosed_areas": [{
        "position": {
            "x": 0,
            "y": -0.0585,
            "z": -0.655
        },
        "dimensions": {
            "x": 0.1995,
            "y": 0.1525,
            "z": 0.161
        }
    }],
    "dimensions": {
        "x": 0.356,
        "y": 0.25,
        "z": 0.2515
    },
    "offset": {
        "x": 0.004,
        "y": -0.019,
        "z": -0.0775
    },
    "position_y": 0.15,
    "scale": {
        "x": 0.5,
        "y": 0.5,
        "z": 0.5
    }
}]

OBJECTS_PICKUPABLE_LISTS = [OBJECTS_PICKUPABLE_BALLS, OBJECTS_PICKUPABLE_BLOCKS, OBJECTS_PICKUPABLE_TOYS,
                            OBJECTS_PICKUPABLE_MISC]
OBJECTS_PICKUPABLE = [item for sublist in OBJECTS_PICKUPABLE_LISTS for item in sublist]

OBJECTS_MOVEABLE = [{
    "type": "chair_1",
    "info": ["medium", "chair"],
    "choose": [{
        "mass": 5,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable", "receptacle", "stackTarget"],
    "dimensions": {
        "x": 0.54,
        "y": 1.04,
        "z": 0.46
    },
    "offset": {
        "x": 0,
        "y": 0.51,
        "z": -0.02
    },
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "chair_2",
    "info": ["medium", "stool"],
    "choose": [{
        "mass": 2.5,
        "materialCategory": ["plastic"],
        "salientMaterials": ["plastic"]
    }],
    "attributes": ["moveable", "receptacle", "stackTarget"],
    "dimensions": {
        "x": 0.3,
        "y": 0.75,
        "z": 0.3
    },
    "offset": {
        "x": 0,
        "y": 0.375,
        "z": 0
    },
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "block_blank_wood_cube",
    "info": ["small", "blank block", "cube"],
    "choose": [{
        "mass": 5,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable", "stackTarget"],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "offset": {
        "x": 0,
        "y": 0.125,
        "z": 0
    },
    "position_y": 0,
    "scale": {
        "x": 2.5,
        "y": 2.5,
        "z": 2.5
    }
}, {
    "type": "block_blank_wood_cylinder",
    "info": ["small", "blank block", "cylinder"],
    "choose": [{
        "mass": 5,
        "materialCategory": ["block_blank"],
        "salientMaterials": ["wood"]
    }],
    "attributes": ["moveable"],
    "dimensions": {
        "x": 0.25,
        "y": 0.25,
        "z": 0.25
    },
    "offset": {
        "x": 0,
        "y": 0.125,
        "z": 0
    },
    "position_y": 0,
    "scale": {
        "x": 2.5,
        "y": 2.5,
        "z": 2.5
    }
}, {
    "type": "box_2",
    "attributes": ["moveable", "receptacle", "openable"],
    "choose": [{
        "info": ["small", "brown", "box"],
        "mass": 1,
        "salientMaterials": ["paper"],
        "enclosed_areas": [{
            "position": {
                "x": 0 * 1.25,
                "y": -0.074 * 1.25,
                "z": -0.145 * 1.25
            },
            "dimensions": {
                "x": 0.296 * 1.25,
                "y": 0.203 * 1.25,
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
        "position_y": 0.2 * 1.25,
        "scale": {
            "x": 1.25,
            "y": 1.25,
            "z": 1.25
        }
    }, {
        "info": ["medium", "brown", "box"],
        "mass": 3,
        "salientMaterials": ["paper"],
        "enclosed_areas": [{
            "position": {
                "x": 0 * 1.75,
                "y": -0.074 * 1.75,
                "z": -0.145 * 1.75
            },
            "dimensions": {
                "x": 0.296 * 1.75,
                "y": 0.203 * 1.75,
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
        "position_y": 0.2 * 1.75,
        "scale": {
            "x": 1.75,
            "y": 1.75,
            "z": 1.75
        }
    }]
}, {
    "type": "box_3",
    "attributes": ["moveable", "receptacle", "openable"],
    "choose": [{
        "info": ["small", "brown", "box"],
        "mass": 1,
        "salientMaterials": ["paper"],
        "enclosed_areas": [{
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
        "position_y": 0.3,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "info": ["medium", "brown", "box"],
        "mass": 3,
        "salientMaterials": ["paper"],
        "enclosed_areas": [{
            "position": {
                "x": 0,
                "y": -0.117,
                "z": -0.1965
            },
            "dimensions": {
                "x": 0.5985,
                "y": 0.305,
                "z": 0.483
            }
        }],
        "dimensions": {
            "x": 1.068,
            "y": 0.5,
            "z": 0.7545
        },
        "offset": {
            "x": 0.012,
            "y": -0.038,
            "z": -0.1725
        },
        "position_y": 0.3,
        "scale": {
            "x": 1.5,
            "y": 1,
            "z": 1.5
        }
    }]
}, {
    "info": ["medium", "potted plant"],
    "mass": 2.5,
    "salientMaterials": ["organic", "ceramic"],
    "attributes": ["moveable"],
    "choose": [{
        "type": "plant_1",
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
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_5",
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
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_7",
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
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_9",
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
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_14",
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
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "type": "plant_16",
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
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }]
}, {
    "info": ["small", "potted plant"],
    "mass": 1,
    "salientMaterials": ["organic", "ceramic"],
    "attributes": ["moveable"],
    "choose": [{
        "type": "plant_1",
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
        "position_y": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_5",
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
        "position_y": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_7",
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
        "position_y": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_9",
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
        "position_y": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_14",
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
        "position_y": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "type": "plant_16",
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
        "position_y": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }]
}]

OBJECTS_IMMOBILE = [{
    "type": "changing_table",
    "info": ["huge", "brown", "changing table"],
    "mass": 100,
    "materialCategory": ["wood", "wood"],
    "salientMaterials": ["wood", "wood"],
    "attributes": ["receptacle", "openable", "stackTarget"],
    "enclosed_areas": [{
        "position": {
            "x": 0.165,
            "y": 0.47,
            "z": -0.03
        },
        "dimensions": {
            "x": 0.68,
            "y": 0.22,
            "z": 0.41
        }
    }, {
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
    "open_areas": [
        # TODO
    ],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "crib",
    "info": ["huge", "brown", "crib"],
    "materialCategory": ["wood"],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "table_1",
    "info": ["huge", "table"],
    "attributes": ["receptacle"],
    "choose": [{
        "mass": 5,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 0.69,
            "y": 0.88,
            "z": 1.63
        },
        "offset": {
            "x": 0.067,
            "y": 0.44,
            "z": -0.07
        },
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "mass": 10,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 1.6215,
            "y": 0.88,
            "z": 1.63
        },
        "offset": {
            "x": 0.15745,
            "y": 0.44,
            "z": -0.07
        },
        "position_y": 0,
        "scale": {
            "x": 2.35,
            "y": 1,
            "z": 1
        }
    }]
}, {
    "type": "table_5",
    "info": ["huge", "table"],
    "choose": [{
        "attributes": ["receptacle"],
        "mass": 20,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 1.2,
            "y": 0.7,
            "z": 1.9
        },
        "offset": {
            "x": -0.18,
            "y": 0.35,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "attributes": ["receptacle", "stackTarget"],
        "mass": 10,
        "materialCategory": ["wood", "wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 1.2,
            "y": 0.35,
            "z": 1.9
        },
        "offset": {
            "x": -0.18,
            "y": 0.175,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 0.5,
            "z": 1
        }
    }]
}, {
    "type": "table_6",
    "choose": [{
        "info": ["small", "shelf"],
        "attributes": ["receptacle", "stackTarget"],
        "mass": 5,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 0.93,
            "y": 0.75,
            "z": 1.02
        },
        "offset": {
            "x": 0.04,
            "y": 0.35,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            # Final scale: 0.5, 0.5, 0.5
            "x": 0.67451805685,
            "y": 0.5,
            "z": 0.22453039467
        }
    }, {
        "info": ["medium", "shelf"],
        "attributes": ["receptacle"],
        "mass": 10,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 0.93,
            "y": 0.75,
            "z": 1.02
        },
        "offset": {
            "x": 0.04,
            "y": 0.35,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            # Final scale: 1, 1, 1
            "x": 1.3490361137,
            "y": 1,
            "z": 0.44906078935,
        }
    }, {
        "info": ["huge", "shelf"],
        "attributes": ["receptacle"],
        "mass": 15,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 0.465,
            "y": 1.5,
            "z": 2.04
        },
        "offset": {
            "x": 0.02,
            "y": 0.7,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            # Final scale: 0.5, 2, 2
            "x": 0.67451805685,
            "y": 2,
            "z": 0.8981215787
        }
    }]
}, {
    "type": "shelf_1",
    "choose": [{
        "info": ["small", "shelf"],
        "attributes": ["receptacle", "stackTarget"],
        "mass": 5,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 0.39,
            "y": 0.385,
            "z": 0.2
        },
        "offset": {
            "x": 0,
            "y": 0.195,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            "x": 0.5,
            "y": 0.5,
            "z": 0.5
        }
    }, {
        "info": ["medium", "shelf"],
        "attributes": ["receptacle"],
        "mass": 10,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 0.78,
            "y": 0.77,
            "z": 0.4
        },
        "offset": {
            "x": 0,
            "y": 0.39,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            "x": 1,
            "y": 1,
            "z": 1
        }
    }, {
        "info": ["huge", "shelf"],
        "attributes": ["receptacle"],
        "mass": 15,
        "materialCategory": ["wood"],
        "salientMaterials": ["wood"],
        "open_areas": [
            # TODO
        ],
        "dimensions": {
            "x": 1.56,
            "y": 1.54,
            "z": 0.8
        },
        "offset": {
            "x": 0,
            "y": 0.78,
            "z": 0
        },
        "position_y": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}, {
    "type": "sofa_1",
    "info": ["huge", "brown", "sofa"],
    "mass": 100,
    "attributes": ["receptacle", "stackTarget"],
    "open_areas": [
        # TODO
    ],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "type": "sofa_chair_1",
    "info": ["huge", "black", "sofa chair"],
    "mass": 50,
    "attributes": ["receptacle", "stackTarget"],
    "open_areas": [
        # TODO
    ],
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
    "position_y": 0,
    "scale": {
        "x": 1,
        "y": 1,
        "z": 1
    }
}, {
    "info": ["large", "potted plant"],
    "mass": 5,
    "salientMaterials": ["organic", "ceramic"],
    "attributes": [],
    "choose": [{
        "type": "plant_1",
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
        "position_y": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_5",
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
        "position_y": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_7",
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
        "position_y": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_9",
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
        "position_y": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_14",
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
        "position_y": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }, {
        "type": "plant_16",
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
        "position_y": 0,
        "scale": {
            "x": 2,
            "y": 2,
            "z": 2
        }
    }]
}]

OCCLUDER_INSTANCE_NORMAL = [{
    "id": "occluder_wall_uuid",
    "type": "cube",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "material": "AI2-THOR/Materials/Walls/DrywallBeige",
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0.625,
            "z": 1
        },
        "scale": {
            "x": 1,
            "y": 1.25,
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
        "stepBegin": 35,
        "stepEnd": 40,
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
        "stepBegin": 35,
        "stepEnd": 36,
        "vector": {
            "x": 0,
            "y": 45,
            "z": 0
        }
    }]
}, {
    "id": "occluder_pole_uuid",
    "type": "cylinder",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "material": "AI2-THOR/Materials/Walls/DrywallBeige",
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
        "stepBegin": 35,
        "stepEnd": 40,
        "vector": {
            "x": 0,
            "y": 0.25,
            "z": 0
        }
    }]
}]

OCCLUDER_INSTANCE_SIDEWAYS = [{
    "id": "occluder_wall_uuid",
    "type": "cube",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "material": "AI2-THOR/Materials/Walls/DrywallBeige",
    "shows": [{
        "stepBegin": 0,
        "position": {
            "x": 0,
            "y": 0.625,
            "z": 1
        },
        "scale": {
            "x": 1,
            "y": 1.25,
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
        "stepBegin": 25,
        "stepEnd": 28,
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
        "stepBegin": 29,
        "stepEnd": 30,
        "vector": {
            "x": 45,
            "y": 0,
            "z": 0
        }
    }]
}, {
    "id": "occluder_pole_uuid",
    "type": "cylinder",
    "kinematic": True,
    "structure": True,
    "mass": 100,
    "material": "AI2-THOR/Materials/Walls/DrywallBeige",
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
        "stepBegin": 25,
        "stepEnd": 28,
        "vector": {
            "x": 0.25,
            "y": 0,
            "z": 0
        }
    }]
}]

def create_occluder(wall_material, pole_material, x_position, x_scale, sideways=False):
    if sideways:
        occluder = copy.deepcopy(OCCLUDER_INSTANCE_SIDEWAYS)
    else:
        occluder = copy.deepcopy(OCCLUDER_INSTANCE_NORMAL)

    WALL = 0
    POLE = 1

    occluder[WALL]['id'] = str(uuid.uuid4())
    occluder[POLE]['id'] = str(uuid.uuid4())

    occluder[WALL]['material'] = wall_material
    occluder[POLE]['material'] = pole_material

    occluder[WALL]['shows'][0]['position']['x'] = x_position
    occluder[POLE]['shows'][0]['position']['x'] = x_position

    occluder[WALL]['shows'][0]['scale']['x'] = x_position

    if sideways:
        if x_position > 0:
            occluder[POLE]['shows'][0]['position']['x'] = 3 + x_position + x_scale / 2
        else:
            occluder[POLE]['shows'][0]['position']['x'] = -3 + x_position - x_scale / 2
    elif x_position > 0:
        for rot in occluder[WALL]['rotates']:
            rot['vector']['y'] *= -1

    return occluder


_ALL_OBJECTS = None
_ALL_OBJECTS_LISTS = [OBJECTS_PICKUPABLE_BALLS, OBJECTS_PICKUPABLE_BLOCKS, OBJECTS_PICKUPABLE_TOYS, OBJECTS_PICKUPABLE_MISC, OBJECTS_MOVEABLE, OBJECTS_IMMOBILE]

def get_all_object_defs():
    global _ALL_OBJECTS
    if _ALL_OBJECTS is None:
        _ALL_OBJECTS = [item for def_list in _ALL_OBJECTS_LISTS for item in def_list]
    return _ALL_OBJECTS


_ENCLOSED_CONTAINERS = None


def get_enclosed_containers():
    """Return all object definitions that have 'enclosed_areas' whose value is a non-empty list."""
    global _ENCLOSED_CONTAINERS
    if _ENCLOSED_CONTAINERS is None:
        all_defs = get_all_object_defs()
        _ENCLOSED_CONTAINERS = [obj_def for obj_def in all_defs if 'enclosed_areas' in obj_def and len(obj_def['enclosed_areas']) > 0]
    return _ENCLOSED_CONTAINERS

