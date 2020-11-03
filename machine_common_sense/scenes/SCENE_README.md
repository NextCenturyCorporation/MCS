# MCS Scene Configuration Files: README

## Documentation

[SCHEMA.md](./SCHEMA.md)

## Examples

### Playroom

An open room containing over 60 objects for undirected exploration.

- [playroom.json](./playroom.json)

![playroom_3_2](./images/playroom_3_2.gif)

### IntPhys

Please see the `intphys*.json` files in this folder.

#### Object Permanence: Objects Moving Across Behind Occluders

| Plausible | Implausible |
| --------- | ----------- |
| ![](./images/intphys_object_permanence_quartet_1A_v2.gif) | ![](./images/intphys_object_permanence_quartet_1C_v2.gif) |
| ![](./images/intphys_object_permanence_quartet_1B_v2.gif) | ![](./images/intphys_object_permanence_quartet_1D_v2.gif) |

#### Object Permanence: Objects Falling Down Behind Occluders

| Plausible | Implausible |
| --------- | ----------- |
| ![](./images/intphys_object_permanence_quartet_2A_v2.gif) | ![](./images/intphys_object_permanence_quartet_2C_v2.gif) |
| ![](./images/intphys_object_permanence_quartet_2B_v2.gif) | ![](./images/intphys_object_permanence_quartet_2D_v2.gif) |

#### Shape Constancy: Objects Moving Across Behind Occluders

| Plausible | Implausible |
| --------- | ----------- |
| ![](./images/intphys_shape_constancy_quartet_1A_v2.gif) | ![](./images/intphys_shape_constancy_quartet_1C_v2.gif) |
| ![](./images/intphys_shape_constancy_quartet_1B_v2.gif) | ![](./images/intphys_shape_constancy_quartet_1D_v2.gif) |

#### Shape Constancy: Objects Falling Down Behind Occluders

| Plausible | Implausible |
| --------- | ----------- |
| ![](./images/intphys_shape_constancy_quartet_2A_v2.gif) | ![](./images/intphys_shape_constancy_quartet_2C_v2.gif) |
| ![](./images/intphys_shape_constancy_quartet_2B_v2.gif) | ![](./images/intphys_shape_constancy_quartet_2D_v2.gif) |

#### Spatio-Temporal Continuity: Objects Moving Across Behind Occluders

For implausible spatio-temporal continuity scenes in which an object teleports forward from one occluder to a second occluder, there are two variants, and each quartet will use one of them. In both variants, the object disappears once it moves behind an occluder. Then, either the object appears immediately from behind a second occluder, or the object waits until it would normally appear behind the occluder (as if it had never disappeared and rolled behind it).

| Plausible | Implausible |
| --------- | ----------- |
| ![](./images/intphys_spatio_temporal_continuity_quartet_1A_v2.gif) | ![](./images/intphys_spatio_temporal_continuity_quartet_1C_v2.gif) |
| | ![](./images/intphys_spatio_temporal_continuity_quartet_1C_alt_v2.gif) |
| ![](./images/intphys_spatio_temporal_continuity_quartet_1B_v2.gif) | ![](./images/intphys_spatio_temporal_continuity_quartet_1D_v2.gif) |

#### Spatio-Temporal Continuity: Objects Falling Down Behind Occluders

| Plausible | Implausible |
| --------- | ----------- |
| ![](./images/intphys_spatio_temporal_continuity_quartet_2A_v2.gif) | ![](./images/intphys_spatio_temporal_continuity_quartet_2C_v2.gif) |
| ![](./images/intphys_spatio_temporal_continuity_quartet_2B_v2.gif) | ![](./images/intphys_spatio_temporal_continuity_quartet_2D_v2.gif) |

#### Gravity: Objects Rolling Up or Down Ramps

Coming soon!

### Walls

- [wall_ahead.json](./wall_ahead.json)
- [wall_diagonal.json](./wall_diagonal.json)
- [wall_offset.json](./wall_offset.json)
- [wall_right.json](./wall_right.json)

