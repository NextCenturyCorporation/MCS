#!/bin/bash

declare -a scenes=(
    "intphys_object_permanence_quartet_1A"
    "intphys_object_permanence_quartet_1B"
    "intphys_object_permanence_quartet_1C"
    "intphys_object_permanence_quartet_1D"
    "intphys_object_permanence_quartet_2A"
    "intphys_object_permanence_quartet_2B"
    "intphys_object_permanence_quartet_2C"
    "intphys_object_permanence_quartet_2D"
    "intphys_shape_constancy_quartet_1A"
    "intphys_shape_constancy_quartet_1B"
    "intphys_shape_constancy_quartet_1C"
    "intphys_shape_constancy_quartet_1D"
    "intphys_shape_constancy_quartet_2A"
    "intphys_shape_constancy_quartet_2B"
    "intphys_shape_constancy_quartet_2C"
    "intphys_shape_constancy_quartet_2D"
    "intphys_spatio_temporal_continuity_quartet_1A"
    "intphys_spatio_temporal_continuity_quartet_1B"
    "intphys_spatio_temporal_continuity_quartet_1C"
    "intphys_spatio_temporal_continuity_quartet_1D"
    "intphys_spatio_temporal_continuity_quartet_2A"
    "intphys_spatio_temporal_continuity_quartet_2B"
    "intphys_spatio_temporal_continuity_quartet_2C"
    "intphys_spatio_temporal_continuity_quartet_2D"
    "intphys_gravity_quartet_1A"
    "intphys_gravity_quartet_1B"
    "intphys_gravity_quartet_1C"
    "intphys_gravity_quartet_1D"
)

for i in "${scenes[@]}"
do
    COUNT=$(ls -1q ../../machine_common_sense/$i/frame_image_* | wc -l)

    for j in 0 1 2 3 4
    do
        cp black_image.png ../../machine_common_sense/$i/frame_image_$((COUNT + j)).png
    done

    ffmpeg -y -r 60 -i ../../machine_common_sense/$i/frame_image_%d.png $i.gif

    for j in 0 1 2 3 4
    do
        rm ../../machine_common_sense/$i/frame_image_$((COUNT + j)).png
    done
done

