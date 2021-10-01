from .runner_script import SingleFileRunnerScript


def action_callback(scene_data, step_metadata, runner_script):
    if step_metadata.step_number <= 36:
        return 'RotateRight', {}
    return None, None


def main():
    SingleFileRunnerScript('Just Rotate', action_callback)


if __name__ == "__main__":
    main()
