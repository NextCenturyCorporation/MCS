# Encapsulate the opening of a sub process (the one running unity)
# in a separate file.  If we do not do this, then we have difficulty
# saving session because subprocess includes a thread lock object.
#
# TODO: Figure out why you can't pickle an object that does the below

import os
import re
import subprocess

from flask import current_app


def start_subprocess(command_dir, image_dir):
    logger = current_app.logger
    proc = subprocess.Popen(
        ["python3", "run_scene_with_dir.py",
         "--mcs_command_in_dir", command_dir,
         "--mcs_image_out_dir", image_dir])
    logger.info(f"Unity controller process started:  {proc.pid}")
    return proc.pid


def is_file_open(pid, file_to_check_on):
    """We can see that image filename on disk before unity controller
    is finished writing writing to it, in which case might be read
    and shown in the UI before it's done.  To see if it is
    still being written to, check to see if the controller process is
    accessing it.

    return true if the file is still open; false if it is closed
    """
    logger = current_app.logger
    dir = '/proc/' + str(pid) + '/fd'

    # Check to see if it is a live process, if not return
    if not os.access(dir, os.R_OK | os.X_OK):
        return False

    logger.debug(f"starting check for {file_to_check_on} -----------")
    for fds in os.listdir(dir):
        logger.debug(f"fds: {fds}")
        for fd in fds:
            logger.debug(f"fd:  {fd}")
            full_name = os.path.join(dir, fd)
            logger.debug(f"full_name {full_name}")
            try:
                file = os.readlink(full_name)
                logger.debug(f"file itself: {file}")
                if file == '/dev/null' or \
                        re.match(r'pipe:\[\d+\]', file) or \
                        re.match(r'socket:\[\d+\]', file):
                    continue

                if file.endswith(file_to_check_on):
                    logger.debug("Found it --------------------------------------")
                    return True

            except OSError:
                # TODO:  Do something more intelligent here???
                return False

    logger.debug(f" did not find {file_to_check_on} in process {pid}")
    return False
