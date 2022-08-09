Running Remotely
================

Requirements:
* Make sure your system has Python 3.7 or greater.
* Make sure MCS has been installed per the install instructions

To run MCS on a remote GPU server, use the following steps to launch an X11 server.

.. code-block:: console

    # Update and install dependencies
    $ sudo apt-get install xserver-xorg
    $ sudo apt-get install xorg
    $ sudo apt-get install nvidia-driver-470
    $ sudo apt-get install glxinfo

    # Identify your machine's GPU BusID
    $ nvidia-xconfig --query-gpu-info
    GPU #0:
    Name      : Tesla K80
    UUID      : GPU-d03a3d49-0641-40c9-30f2-5c3e4bdad498
    PCI BusID : PCI:0:30:0

    # Create the Xserver configuration using the BusID
    $ sudo nvidia-xconfig --use-display-device=None --virtual=600x400 --output-xconfig=/etc/X11/xorg.conf --busid=PCI:0:30:0

    # Launch Xserver
    $ sudo /usr/bin/Xorg :0 &

    # Test the display setting using glxinfo
    $ DISPLAY=:0 glxinfo
    name of display: :0
    display: :0  screen: 0
    direct rendering: Yes
    server glx vendor string: NVIDIA Corporation
    server glx version string: 1.4


Remote Cache Addressables Script
--------------------------------

.. code-block:: console

    # Activate your python virtual environment
    $ DISPLAY=:0 cache_addressables

Remote Runs on AWS 
------------------

The following code was run on an AWS p2-xlarge with the Ubuntu Deep Learning AMI.

.. code-block:: bash

    # Follow the instructions listed above to launch Xserver
    $ sudo nvidia-xconfig --use-display-device=None --virtual=600x400 --output-xconfig=/etc/X11/xorg.conf --busid=PCI:0:30:0
    $ sudo /usr/bin/Xorg :0 &

    # Download the MCS repository
    $ git clone https://github.com/NextCenturyCorporation/MCS.git
    $ cd MCS

    # Install and activate a new python virtual environment
    $ sudo apt-get install python3-venv
    $ sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
    $ python -m venv venv
    $ . venv/bin/activate

    # Install the python dependencies
    $ pip install --upgrade pip setuptools wheel
    $ python -m pip install -r requirements.txt
    $ python -m pip install -e .

    # Do a test run
    $ python machine_common_sense/scripts/run_just_rotate.py docs/source/scenes/ball_far.json

