file_path_prefix = "/Users/jacob.audick_cn/Documents/ai2thor/unity/"
unity_editor_log_file_name = "unity_editor_console.log"
output_file = "unity_editor_actions.txt"

with open(file_path_prefix + unity_editor_log_file_name, "r") as f:
    lines = f.readlines()


with open(output_file, "w") as f:
    actions = []
    action = ""
    object_id = ""
    for line in lines:
        if line.startswith("MCS: Action Debug "):
            line_string = line.replace('MCS: Action Debug (', '')
            action_string_split = line_string.split(",")
            for substring in action_string_split[:]:
                if (substring.strip().startswith("objectImageCoords") or
                    substring.strip().startswith("Parameters") or
                        substring.strip().startswith("Step")):
                    action_string_split.remove(substring)
            action = action_string_split[0].replace("Action = ", '')
            parameters = "," + ",".join(action_string_split[1:])
            actions.append(
                f"{action}{parameters if len(parameters) > 1 else ''}\n")
        elif line.startswith("MCS: Resolved Object = "):
            object_id = line.replace('MCS: Resolved Object = ', '')
            if object_id:
                actions[-1] = actions[-1][:-1] + f",objectId={object_id}"

    for line in actions:
        f.write(line)
