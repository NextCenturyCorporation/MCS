import logging
import sys

from runner_script import SingleFileRunnerScript


# formatString = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logger = logging.getLogger('machine_common_sense')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
# stream_handler.setFormatter(logging.Formatter(formatString))
logger.addHandler(stream_handler)


def action_callback(scene_data, step_metadata, runner_script):
    last_step = 60
    if 'goal' in scene_data.keys():
        if 'last_step' in scene_data['goal'].keys():
            last_step = scene_data['goal']['last_step']
    if step_metadata.step_number < last_step:
        return 'Pass', {}
    return None, None


def main():
    logger.info(f"Running Just Pass with {sys.argv}")
    SingleFileRunnerScript('Just Pass', action_callback)


if __name__ == "__main__":
    main()
