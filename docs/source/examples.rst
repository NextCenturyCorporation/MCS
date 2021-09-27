Example Usage
=============

Here are some example usage snippets for different use cases. Note that there are also additional scripts that may be useful in the scripts/ folder of the github project. 

Using your own config data and/or unity build
----------------------------------------------

Please note that for the below example, make sure `MCS_CONFIG_FILE_PATH` is not set, since it will override the `config_file_or_dict` specified below and is meant more for internal use by TA2 during evaluation:

.. code-block:: python

    import machine_common_sense as mcs

    # Specify a location for the Unity app as opposed to downloading it automatically
    controller = mcs.create_controller(unity_app_file_path='./some-path/unity-app', 
                                       config_file_or_dict='./some-path/config.ini')

    # Either load the scene data dict from an MCS scene config JSON file or create your own.
    # We will give you the training scene config JSON files and the format to make your own.
    scene_data, status = mcs.load_scene_json_file(scene_json_file_path)

    output = controller.start_scene(scene_data)

    # Use your machine learning algorithm to select your next action based on the scene
    # output (goal, actions, images, metadata, etc.) from your previous action.
    action, params = select_action(output)

    # Continue to select actions until your algorithm decides to stop.
    while action != '':
        controller.step(action, params)
        action, params = select_action(output)

    # For interaction-based goals, your series of selected actions will be scored.
    # For observation-based goals, you will pass a classification and a confidence
    # to the end_scene function here.
    controller.end_scene()

Note that you can alternatively pass in a dictionary of config values:

.. code-block:: python

    controller = mcs.create_controller(unity_app_file_path='./some-path/unity-app', 
                                       config_file_or_dict={'metadata': 'oracle', 'history_enabled': True})


Run multiple scenes sequentially
--------------------------------

.. code-block:: python

    import machine_common_sense as mcs

    # Only create the MCS controller ONCE!
    controller = mcs.create_controller(config_file_or_dict={})

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

*Note that logging is only available in versions 0.4.4 and above.*

.. code-block:: python

    import logging
    import machine_common_sense as mcs

    logger = logging.getLogger('machine_common_sense')
    mcs.init_logging()

    controller = mcs.create_controller(config_file_or_dict='./some-path/config.ini')
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

*Note that logging is only available in versions 0.4.4 and above.*

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

