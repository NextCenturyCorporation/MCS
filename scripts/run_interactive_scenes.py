from runner_script import MultipleFileRunnerScript


def action_callback(scene_data, step_metadata):
    if step_metadata.step_number <= 36:
        return 'RotateRight', {}
    return None, None


def main():
    MultipleFileRunnerScript(
        'Interactive Scenes',
        action_callback,
        rename=True
    )


if __name__ == "__main__":
    main()
