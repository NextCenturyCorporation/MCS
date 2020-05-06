# MCS Playroom Docker container
#
# docker build --tag mcs-playroom:0.0.6 .
#
# Allow X session connection
# xhost +si:localuser:root
#
# Run interactive bash shell
# docker run -it --rm --gpus all -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw mcs-playroom:0.0.6
#
# Run playroom with preloaded scene
# docker run --gpus all -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw mcs-playroom:0.0.6 \
#  python3.6 /mcs/python_api/machine_common_sense/run_mcs_just_pass.py /mcs/MCS-AI2-THOR-Unity-App-v0.0.6.x86_64 /mcs/python_api/scenes/playroom.json
#
# Run with scenes provided through volume mapping
# docker run --gpus all -e DISPLAY -v /home/HQ/dwetherby/Downloads/interaction_scenes:/scenes -v /tmp/.X11-unix:/tmp/.X11-unix:rw mcs-playroom:0.0.6 \
#  python3.6 /mcs/python_api/machine_common_sense/run_mcs_just_rotate.py /mcs/MCS-AI2-THOR-Unity-App-v0.0.6.x86_64 /scenes/retrieval/retrieval_goal-0002.json

FROM nvidia/opengl:1.0-glvnd-runtime-ubuntu18.04

ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display

WORKDIR /mcs

RUN apt-get update -y && \
    apt-get install -y xvfb mesa-utils python3.6 python3-pip && \
    python3.6 -m pip install --upgrade pip setuptools wheel

# copy the mcs repository into the image and install into default python environment
COPY . /mcs
RUN python3.6 -m pip install .
# or we could install from MCS tagged branch rather than copying into the container
# RUN pip install git+https://github.com/NextCenturyCorporation/MCS@latest

# add ai2thor/unity resources
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/0.0.6/MCS-AI2-THOR-Unity-App-v0.0.6.x86_64 /mcs
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/0.0.6/MCS-AI2-THOR-Unity-App-v0.0.6_Data.tar.gz /mcs
RUN tar -xzvf /mcs/MCS-AI2-THOR-Unity-App-v0.0.6_Data.tar.gz -C /mcs && \
    chmod a+x /mcs/MCS-AI2-THOR-Unity-App-v0.0.6.x86_64 && \
    rm /mcs/MCS-AI2-THOR-Unity-App-v0.0.6_Data.tar.gz
