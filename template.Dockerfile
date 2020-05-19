# Templated MCS submission Dockerfile for Evaluation 2
#
# Building your docker image
# docker build --tag <your-tag>:<version>  -f template.Dockerfile .
#
# Run interactive bash shell for testing build (nvidia-smi, glxgears, xeyes)
# xhost +si:localuser:root
# docker run -it --rm --gpus all -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw <your-tag>:<version>
# 
# Running the playroom using volume mapping scene files into /scenes
# $ docker run -t --gpus all -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
#   -v /Downloads/interaction_scenes:/scenes mcs-submission:0.0.1 \
#   python3.8 /mcs/playroom.py /mcs/MCS-AI2-THOR-Unity-App-v0.0.6.x86_64 /scenes/retrieval/retrieval_goal-0001.json

# This is a multi-stage build based upon the MCS playroom base image
FROM mcs-playroom:0.0.6

# Install any software dependencies for your TA1 submission
# if you have a requirements.txt file, copy it into the image before installing
# COPY requirements.txt /requirements.txt
# python3.8 -m pip install -r /requirements.txt

# Copy your filled out template python file to /mcs
# and rename it to playroom.py
COPY template_playroom.py /mcs/playroom.py

# COPY over trained model(s) and anything else you need
