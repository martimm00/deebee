import json


def read_json(file_pointer):
    """
    Reads JSON file and loads it to Python type.

    :param file_pointer: Local file pointer or buffer.

    :return: File to Python dictionary type.
    """
    return json.load(file_pointer)


def write_json(content: dict, file_pointer):
    """
    Writes JSON file from Python type.

    :param content: Python dictionary to be converted.
    :param file_pointer: Local file pointer or buffer.

    :return: File to Python dictionary type.
    """
    return json.dump(content, file_pointer)
