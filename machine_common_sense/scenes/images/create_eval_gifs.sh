#!/bin/bash

declare -a scenes=(
    "eval_sample_1"
    "eval_sample_2"
    "eval_sample_3"
    "eval_sample_4"
    "eval_sample_5"
    "eval_sample_6"
    "eval_sample_7"
    "eval_sample_8"
    "eval_sample_9"
    "eval_sample_10"
    "eval_sample_11"
    "eval_sample_12"
)

for i in "${scenes[@]}"
do
    COUNT=$(ls -1q ../../machine_common_sense/$i/frame_image_* | wc -l)

    for j in 0 1 2 3 4
    do
        cp black_image.png ../../machine_common_sense/$i/frame_image_$((COUNT + j)).png
    done

    ffmpeg -y -r 10 -i ../../machine_common_sense/$i/frame_image_%d.png $i.gif

    for j in 0 1 2 3 4
    do
        rm ../../machine_common_sense/$i/frame_image_$((COUNT + j)).png
    done
done

