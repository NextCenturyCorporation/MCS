import argparse
import sys


def process_unity_editor_log(file_path_prefix):
    unity_editor_log_file_name = "unity_editor_console.log"
    output_file = "unity_editor_actions.txt"

    with open(file_path_prefix + unity_editor_log_file_name, "r") as f:
        lines = f.readlines()

    actions = []
    action = ""
    object_id = ""
    for line in lines:
        if line.startswith("MCS: Action Debug "):
            line_string = line.replace('MCS: Action Debug (', '')
            action_string_split = line_string.split(",")
            action_string_split = [
                substring for substring in action_string_split
                if not substring.strip().startswith(
                    ("objectImageCoords", "Parameters", "Step"))
            ]
            action = action_string_split[0].replace("Action = ", '')
            parameters = "," + ",".join(action_string_split[1:])
            actions.append(
                f"{action}{parameters if len(parameters) > 1 else ''}\n")
        elif line.startswith("MCS: Resolved Object = "):
            object_id = line.replace('MCS: Resolved Object = ', '')
            if object_id:
                actions[-1] = actions[-1][:-1] + f",objectId={object_id}"

    with open(output_file, "w") as f:
        for line in actions:
            f.write(line)


def main():
    parser = argparse.ArgumentParser(description='Process Unity Editor Log')
    parser.add_argument('prefix', type=str, help='File path prefix')
    args = parser.parse_args(sys.argv[1:2])

    file_path_prefix = args.prefix.rstrip('/') + '/'
    process_unity_editor_log(file_path_prefix)


if __name__ == "__main__":
    main()
