Containerization
================

GPU Image
---------

Please note that the GPU image requires an Nvidia GPU and Nvidia Docker to be installed.

You can run the GPU image with:

.. code-block:: console

    docker run -it -e PYTHONIOENCODING=utf8 -e XAUTHORITY=/tmp/.docker.xauth -e DISPLAY=:1 \
           -v ${PWD}/machine_common_sense/scenes:/input -v ${PWD}/machine_common_sense/scripts:/scripts \
           -v /tmp/.X11-unix:/tmp/.X11-unix \
           -v /tmp/.docker.xauth:/tmp/.docker.xauth \
           --net host --gpus all --rm mcs-playroom:0.0.6 bash


You can then run a scene like this:

.. code-block:: console

    python3 /scripts/run_human_input.py /mcs/MCS-AI2-THOR-Unity-App-v0.4.0.x86_64 --config_file_path /scripts/config_oracle.ini /input/hinged_container_example.json

Missing X Authorization Error
*****************************

If you encounter an error like the following:

.. code-block:: console

    config_file_path $MCS_CONFIG_FILE_PATH /input/agents_preference_expected.json 
    No protocol specified
    xdpyinfo:  unable to open display ":1".
    Exception in create_controller() Invalid DISPLAY :1 - cannot find X server with xdpyinf

please try resetting your X authorization:

.. code-block:: console

    sudo rmdir /tmp/.docker.xauth
    touch /tmp/.docker.xauth
    xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -

CPU Image
---------

There is an image to run CPU-only without requiring an Nvidia GPU. Please only use it if your system does not meet the
prerequisites for the GPU image, since GPU acceleration will yield significantly better performance.

Build Image
***********

.. code-block:: console

    docker build -f CPU_Container.dockerfile -t mcs-playroom-cpu .

Run Image (bash)
****************

.. code-block:: console

    docker run -it -p 5900:5900 -v ${PWD}/machine_common_sense/scenes:/input -v ${PWD}/machine_common_sense/scripts:/scripts mcs-playroom-cpu bash

Run with VNC
************

Unless stated otherwise, the following commands are intended to be run inside the container.
Run tmux with `tmux` and open two panes via `C-b %`.

.. code-block:: console

    Xvnc :33 &
    export DISPLAY=:33
    python3 /scripts/run_human_input.py ${MCS_EXECUTABLE_PATH} --config_file_path ${MCS_CONFIG_FILE_PATH} /input/hinged_container_example.json

Switch panes with `C-b <arrow>`

.. code-block:: console

    window_id=$(xwininfo -root -tree | grep MCS-AI2-THOR | tail -n1 | sed "s/^[ \t]*//" | cut -d ' ' -f1) && echo ${window_id}
    x11vnc -id ${window_id} &

Afterwards, you should be able to connect to the VNC server from the host by running `vncviewer` and connecting to
`localhost:5900`.

Run Fully Headless
******************

As an alternative for batch runs you can also run MCS against X virtual framebuffers. In this case you do not get visual
output, but can run the images on headless servers without X server. To do so, execute the following command
from inside the container:

.. code-block:: console

    xvfb-run -s "-screen 0 1440x900x24" python3 /scripts/run_human_input.py ${MCS_EXECUTABLE_PATH} --config_file_path ${MCS_CONFIG_FILE_PATH} /input/agents_preference_expected.json
