import json


def to_json(data) -> str:
    """
    Transforms JSON serializable data to JSON file.

    :param data: str, list, dict, bool, ...

    :return: JSON file.
    """
    return json.dumps(data)


def from_json(data: str):
    """
    Loads JSON file to python type.

    :param data: JSON file.

    :return: str, list, dict, bool, ...
    """
    return json.loads(data)


def read_json(file):
    """
    Reads JSON file and loads it to python type.

    :param file: Read file.

    :return: File to python type.
    """
    return json.load(file)


def has_json_name(filename: str) -> bool:
    """
    Returns if certain file name contains JSON extension.

    :param filename: Str with file name.

    :return: Boolean.
    """
    return filename[-5:] == ".json"
