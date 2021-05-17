# Build: docker build -f CPU_Container.dockerfile -t mcs-playroom-cpu .
# Run: docker run -it -p 5900:5900 -v ${PWD}/machine_common_sense/scenes:/input -v ${PWD}/scripts:/scripts -e XAUTHORITY=/tmp/.docker.xauth -e DISPLAY=:1 -v /tmp/.X11-unix:/tmp/.X11-unix -v /tmp/.docker.xauth:/tmp/.docker.xauth mcs-playroom-cpu bash

FROM ubuntu:20.04

LABEL maintainer="Next Century Corporation"

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

# --build-arg mcsversion=0.0.x to override default in docker build command
ARG mcsversion=0.4.3
ARG mcs_library_version=master

WORKDIR /mcs


ENV DEBIAN_FRONTEND=noninteractive
ENV MCS_EXECUTABLE_PATH="/MCS-AI2-THOR-Unity-App-v${mcsversion}.x86_64"
ENV MCS_CONFIG_FILE_PATH="/mcs_sample_config.ini"

COPY machine_common_sense/scenes/agents_preference_expected.json /input/test.json

RUN apt-get update -qq \
    && apt-get install -qq -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        dirmngr \
        ffmpeg \
        freeglut3-dev \
        git \
        gpg-agent \
        graphviz \
        hdf5-tools \
        libglib2.0-0 \
        libgmp-dev \
        mesa-utils \
        neovim \
        python3-dev \
        python3-pip \
        python3-tk \
        rsync \
        software-properties-common \
        tigervnc-standalone-server \
        tmux \
        tzdata \
        unzip \
        wget \
        x11-utils \
        x11vnc \
        xvfb \
        zlib1g-dev \
        cmake pkg-config libgtk-3-dev libavcodec-dev libavformat-dev \
        libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev gfortran openexr \
        libatlas-base-dev libtbb2 libtbb-dev libdc1394-22-dev libopenexr-dev libgstreamer-plugins-base1.0-dev \
        libgstreamer1.0-dev && \
    python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install git+https://github.com/NextCenturyCorporation/MCS@${mcs_library_version}#egg=machine_common_sense && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /mcs

# Add ai2thor/Unity resources
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/MCS-AI2-THOR-Unity-App-v${mcsversion}.x86_64 /mcs
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz /mcs
ADD https://github.com/NextCenturyCorporation/MCS/releases/download/${mcsversion}/UnityPlayer.so /mcs
RUN tar -xzvf /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz -C /mcs && \
    chmod a+x /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}.x86_64 && \
    rm /mcs/MCS-AI2-THOR-Unity-App-v${mcsversion}_Data.tar.gz && echo "[MCS]\nmetadata: oracle" > /mcs/mcs_config_oracle.yaml && \
    echo "[MCS]\nmetadata:  level1" > /mcs/mcs_config_level1.yaml && echo "[MCS]\nmetadata: level2" > /mcs/mcs_config_level2.yaml
