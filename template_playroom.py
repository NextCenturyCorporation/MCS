import sys
import argparse
import pathlib

from machine_common_sense.mcs import MCS

# TEMPLATE: import TA1 packages


def parse_args():
    '''Parse command line arguments'''
    parser = argparse.ArgumentParser()
    parser.add_argument('scene', help="Playroom scene JSON file")
    return parser.parse_args()


def find_unity_executable():
    '''
    Search the /mcs folder for the unity executable.

    There should be only one executable but the version number may change.
    '''
    return str(next(pathlib.Path('/mcs').glob('MCS-AI2-THOR*.x86_64'), None))


def run_playroom(controller, scene):
    '''Run the MCS interactive playroom'''
    output = controller.start_scene(scene)

    # loop for max steps or until goal achieved
    # TODO how do we know max steps? intphys vs interaction
    last_step = 50
    for i in range(1, last_step + 1):

        # TEMPLATE: determine action
        action = 'Pass'

        # take action
        print(f"Taking action - {action} on step {i}")
        output = controller.step(action=action)

        # TEMPLATE: break out of loop if goal achieved


def main():
    args = parse_args()

    unity_exe_path = find_unity_executable()
    if unity_exe_path is None:
        print("Unity executable not found in /mcs")
        exit()

    scene_config, status = MCS.load_config_json_file(args.scene)
    if status is not None:
        print(status)
        exit()

    controller = MCS.create_controller(unity_exe_path, debug=False)
    run_playroom(controller, scene_config)


if __name__ == "__main__":
    main()
