class MCS_Util:

    NUMBER_OF_SPACES = 4

    @staticmethod
    def class_to_str(input_class, depth=0):
        this_indent = " " * MCS_Util.NUMBER_OF_SPACES * depth
        next_indent = " " * MCS_Util.NUMBER_OF_SPACES * (depth + 1)
        text_list = []
        for prop_key, prop_value in vars(input_class).items():
            text_list.append(next_indent + "\"" + prop_key + "\": " + MCS_Util.value_to_str(prop_value, depth + 1))
        return "{}" if len(text_list) == 0 else "{\n" + (",\n").join(text_list) + "\n" + this_indent + "}"

    @staticmethod
    def value_to_str(input_value, depth=0):
        this_indent = " " * MCS_Util.NUMBER_OF_SPACES * depth
        next_indent = " " * MCS_Util.NUMBER_OF_SPACES * (depth + 1)
        if isinstance(input_value, list):
            text_list = []
            for list_item in input_value:
                text_list.append(next_indent + MCS_Util.value_to_str(list_item, depth + 1))
            return "[]" if len(text_list) == 0 else "[\n" + (",\n").join(text_list) + "\n" + this_indent + "]"
        elif isinstance(input_value, str):
            return "\"" + input_value.replace("\"", "\\\"") + "\""
        return str(input_value).replace("\n", "\n" + this_indent)

