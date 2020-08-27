#!/usr/bin/env python3
#
import argparse
import os
import sys
import logging

from machine_common_sense.mcs import MCS
from scene_generator import write_file

# no public way to find this, apparently :(
LOG_LEVELS = logging._nameToLevel.keys()


def update_file(controller, filename, keep_backups):
    config_data, err_status = MCS.load_config_json_file(filename)
    if err_status is not None:
        logging.error(f'could not load scene file "{filename}": {err_status}')
        return False

    if 'name' not in config_data:
        base = os.path.basename(filename)
        config_data['name'] = base.rsplit('.', 1)[-1]

    output = controller.start_scene(config_data)

    metadata = config_data['goal']['metadata']
    target_ids = [
        metadata[key]['id']
        for key in ('target', 'target_1', 'target_2')
        if key in metadata
    ]
    logging.debug(f'target_ids: {target_ids}')
    logging.debug(f'num objects = {len(output.object_list)}')

    targets_visible = False
    targets_not_visible = False
    for obj in output.object_list:
        if obj.uuid in target_ids:
            # If it's in the object list to begin with, it should be visible,
            # but just to make sure...
            if obj.visible:
                targets_visible = True
                target_ids.remove(obj.uuid)
                logging.debug(f'target visible: {obj.uuid}')
            else:
                targets_not_visible = True
                logging.debug(f'target not visible: {obj.uuid}')
        if targets_visible and targets_not_visible:
            break
    if targets_visible:
        config_data['goal']['type_list'].append('target_starts_visible')
    if targets_not_visible or len(target_ids) > 0:
        config_data['goal']['type_list'].append('target_starts_invisible')

    backup_name = filename + '.backup'
    os.replace(filename, backup_name)
    try:
        write_file(filename, config_data)
    except Exception as e:
        logging.error(f'error writing file "{filename}": {e}')
        logging.error(f'backup file is at "{backup_name}"')
        return
    if not keep_backups:
        os.remove(backup_name)


def main(argv):
    parser = argparse.ArgumentParser(
        description='Update scene descriptions with target visibility info')
    parser.add_argument(
        '--app',
        metavar='UNITY_MCS_APP',
        required=True,
        help='Path to Unity MCS application')
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Enable debugging output')
    parser.add_argument(
        '--backup',
        action='store_true',
        default=False,
        help='Keep backup files')
    parser.add_argument(
        '--loglevel',
        choices=LOG_LEVELS,
        help='set logging level')
    parser.add_argument(
        'scene_files',
        metavar='SCENE_FILE',
        nargs='+',
        help='scene file to update')

    args = parser.parse_args(argv[1:])

    if args.loglevel:
        logging.getLogger().setLevel(args.loglevel)
    elif args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    controller = MCS.create_controller(args.app, args.debug)

    for f in args.scene_files:
        update_file(controller, f, args.backup)


if __name__ == '__main__':
    main(sys.argv)
