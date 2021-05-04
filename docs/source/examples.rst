Examples
========

Run multiple scenes sequentially
--------------------------------

.. code-block:: python

    import machine_common_sense as mcs

    # Only create the MCS controller ONCE!
    controller = mcs.create_controller(unity_app_file_path)

    for scene_json_file_path in scene_json_file_list:
        scene_data, status = mcs.load_scene_json_file(scene_json_file_path)
        output = controller.start_scene(scene_data)
        action, params = select_action(output)
        while action != '':
            controller.step(action, params)
            action, params = select_action(output)
        controller.end_scene()

        
Run with console logging
------------------------

.. code-block:: python

    import logging
    import machine_common_sense as mcs

    logger = logging.getLogger('machine_common_sense')
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    controller = mcs.create_controller(unity_app_file_path, config_file_path='./some-path/config.ini')
    scene_data, status = mcs.load_scene_json_file(scene_json_file_path)
    output = controller.start_scene(scene_data)

    action, params = select_action(output)
    while action != '':
        logger.debug(f"Taking {action} with {params}")
        controller.step(action, params)
        action, params = select_action(output)

    controller.end_scene()

Run with Human Input
--------------------

To start the Unity application and enter your actions and parameters from the terminal, you can run the `run_in_human_input_mode` script that was installed in the package with the MCS Python Library (the `mcs_unity_build_file` is the Unity executable downloaded previously):

.. code-block:: console

    run_in_human_input_mode <mcs_unity_build_file> <mcs_scene_json_file>

Run options:
- `--config_file_path <file_path>`

