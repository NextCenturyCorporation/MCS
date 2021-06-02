Examples
========

Run multiple scenes sequentially
--------------------------------

.. code-block:: python

    import machine_common_sense as mcs

    # Only create the MCS controller ONCE!
    controller = mcs.create_controller()

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
    mcs.init_logging()

    controller = mcs.create_controller(config_file_path='./some-path/config.ini')
    scene_data, status = mcs.load_scene_json_file(scene_json_file_path)
    output = controller.start_scene(scene_data)

    action, params = select_action(output)
    while action != '':
        logger.debug(f"Taking {action} with {params}")
        controller.step(action, params)
        action, params = select_action(output)

    controller.end_scene()

Initialize logging
------------------------

.. code-block:: python

    import logging
    import machine_common_sense as mcs
    from machine_common_sense.logging_config import LoggingConfig

    # The following are 3 built in methods to initialize logging.  Only one of these should
    # be called in a single execution as the last one will override any before it.

    # Below initializes default which logs to console
    mcs.init_logging()

    # Below initializes development default with file logging as well as console logging
    mcs.init_logging(LoggingConfig.get_dev_logging_config())

    # Below initializes 
    mcs.init_logging(LoggingConfig.get_errors_only_console_config())


Run with Human Input
--------------------

To start the Unity application and enter your actions and parameters from the terminal, you can run the `run_in_human_input_mode` script that was installed in the package with the MCS Python Library (the `mcs_unity_build_file` is the Unity executable downloaded previously):

.. code-block:: console

    run_in_human_input_mode <mcs_unity_build_file> <mcs_scene_json_file>

Run options:
- `--config_file_path <file_path>`

