Running Remotely
================

To run MCS on a remote GPU server, use the following steps to launch an X11 server.

.. code-block:: console

    # query the gpu bus ID
    $ nvidia-xconfig --query-gpu-info

    GPU #0:
    Name      : Tesla K80
    UUID      : GPU-d03a3d49-0641-40c9-30f2-5c3e4bdad498
    PCI BusID : PCI:0:23:0
    # create the xserver configuration
    $ sudo nvidia-xconfig --use-display-device=None --virtual=600x400 --output-xconfig=/etx/X11/xorg.conf --busid=PCI:0:23:0
    # launch Xserver
    $ sudo /usr/bin/Xorg :0 &
    # test using glxinfo
    $ DISPLAY=:0 glxinfo
    name of display: :0
    display: :0  screen: 0
    direct rendering: Yes
    server glx vendor string: NVIDIA Corporation
    server glx version string: 1.4


Remote Run Test Script
----------------------

Run the following script to test MCS with the X11 server created above.

.. code-block:: python

    # test.py
    import machine_common_sense as mcs
    # use your path to the MCS Unity executable
    controller = mcs.create_controller()
    # find a test scene
    scene_file_path = 'playroom.json'
    scene_data, status = mcs.load_scene_json_file(scene_file_path)
    scene_file_name = scene_file_path[scene_file_path.rfind('/')+1]
    if 'name' not in scene_data.keys():
        scene_data['name'] = scene_file_name[0:scene_file_name.find('.')]
    output = controller.start_scene(scene_data)
    for i in range(1, 12):
        output = controller.step('RotateLook')
        for j in range(len(output.image_list)):
            output.image_list[i].save(f'{i}-{j}.jpg')

From your python environment, run test.py and check the output images for proper rendering.

.. code-block:: console

    DISPLAY=:0 python test.py
