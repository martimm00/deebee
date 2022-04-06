import os
import pandas as pd

def is_list_empty(list_to_be_checked: list) -> bool:
    """
    Returns if a list is empty or not.

    :param list_to_be_checked: List to be checked.

    :return: Bool.
    """
    return not bool(list_to_be_checked)


def list_has_one_item(list_to_be_checked: list) -> bool:
    """
    Returns if a list has one item inside.

    :param list_to_be_checked: List to be checked.
    :return: Bool.
    """
    return len(list_to_be_checked) == 1


def get_value(something: any) -> any:
    """
    Returns the true value of a list-like data structure, only if it has a single value
    inside. Any other case, it returns nothing.

    :param something: List-like data structure.

    :return: The true value or None.
    """
    if something:
        if len(something) == 1:
            return something[0]
    return None


def read_dataset(path: os.path, sep=";", n_rows=None, type_dict=None) -> pd.DataFrame:
    """
    Returns a Pandas DataFrame given the specified path.

    :param path: Path of the dataset to be read.
    :param sep: String with the separator character between fields.
    :param n_rows: Integer with the number of rows to be read.
    :param type_dict: Dictionary with types.

    :return: Pandas DataFrame.
    """
    return pd.read_csv(path, sep=sep, nrows=n_rows, dtype=type_dict)
