# MCS Playroom Docker container
#
# docker build --tag mcs-playroom:0.0.6 .
# docker build --tag mcs-playroom:0.0.x --build-arg mcsversion=0.0.x .
#
# Allow X session connection
# xhost +si:localuser:root
#
# Run interactive bash shell
# docker run -it --rm --gpus all -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw mcs-playroom:0.0.6
#

# Older Alternative: FROM nvidia/cudagl:10.1-base-ubuntu18.04
FROM nvidia/cudagl:11.0.3-base-ubuntu20.04

ARG DEBIAN_FRONTEND=noninteractive

ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES},display
# ENV LANG C.UTF-8

# --build-arg mcsversion=0.0.x to override default in docker build command
ARG mcsversion=0.4.3
ARG mcs_library_version=master

WORKDIR /mcs

RUN apt-get update && \
    apt-get install -y git python3 python3-pip mesa-utils && \
    python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install git+https://github.com/NextCenturyCorporation/MCS@${mcs_library_version}#egg=machine_common_sense && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/python3 /usr/bin/python

# Add ai2thor/Unity resources
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/MCS-AI2-THOR-Unity-App-v${mcsversion}.x86_64 /mcs
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz /mcs
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/UnityPlayer.so /mcs
RUN tar -xzvf /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz -C /mcs && \
    chmod a+x /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}.x86_64 && \
    rm /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz
