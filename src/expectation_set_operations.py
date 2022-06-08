import json
from datetime import datetime

from constants.defaults import EMPTY_DICT
from constants.expectation_set_constants import (
    PARAMETERS,
    LAST_EDITED,
    EXPECTATIONS,
    EXPECTATION_NAME,
    EXPECTATION_SET_NAME
)

from src.low_level_operations import (
    exists_path,
    delete_file,
    get_expectation_set_path,
    get_available_expectation_sets
)


def get_expectation_set_config(expectation_set_name: str) -> dict:
    """
    Returns the content of a defined expectation set.

    :param expectation_set_name: String with the name of the expectation set to be
    returned.

    :return: Dictionary with configuration.
    """
    expectation_set_path = get_expectation_set_path(expectation_set_name)
    with open(expectation_set_path, "r") as fp:
        config = json.load(fp)
    return config


def get_empty_expectation_set_content(expectation_set_name: str) -> dict:
    """
    Returns the content for an empty expectation set.

    :param expectation_set_name: String with the name of the new expectation set.

    :return: Dictionary with content for empty expectation set.
    """
    return {
        EXPECTATION_SET_NAME: expectation_set_name,
        LAST_EDITED: str(datetime.now()),
        EXPECTATIONS: EMPTY_DICT
    }


def get_expectation_content(expectation_id: str, params_dict: dict) -> dict:
    """
    Returns content for a new expectation.

    :param expectation_id: String with GE's name for the expectation.
    :param params_dict: Dictionary with expectation's parameters.

    :return: Dictionary with content for the expectation.
    """
    return {
        EXPECTATION_NAME: expectation_id,
        PARAMETERS: params_dict
    }


def check_all_expectation_sets_are_not_empty() -> None:
    """
    This function checks that no defined set is empty. If it is, it will be removed.
    """
    # Getting the name of all sets
    expectation_sets = get_available_expectation_sets()
    for set_name in expectation_sets:

        # Getting the content of each set
        content = get_expectation_content(set_name)

        # If there is no content, then that is an empty expectation set. Let's delete
        # it
        if not content[EXPECTATIONS]:
            expectation_set_path = get_expectation_set_path(set_name)
            delete_file(expectation_set_path)


def check_existing_expectation_sets_integrity() -> None:
    """
    Responsible for checking all listed expectation sets are valid.
    """
    # Check they are not empty
    check_all_expectation_sets_are_not_empty()


def write_expectation_in_config(
    expectation_set_name: str,
    column_name: str,
    expectation_id: str,
    parameters_dict: dict
) -> None:
    """
    This function creates a new file to write down a configuration for an expectation
    set, or opens a created file to append new expectations and their parameters.

    :param expectation_set_name: String with the name of the expectation set.
    :param column_name: String with the name of the selected table column, where the
    expectation will have to be applied to.
    :param expectation_id: String with the name of the new expectation to be added.
    :param parameters_dict: Dictionary with parameters of this new expectation.
    """
    expectation_set_path = get_expectation_set_path(expectation_set_name)
    if not exists_path(expectation_set_path):
        empty_expectation_set_content = get_empty_expectation_set_content(expectation_set_name)
        with open(expectation_set_path, "w") as fp:
            json.dump(empty_expectation_set_content, fp)

    # Getting current expectation set configuration
    config_dict = get_expectation_set_config(expectation_set_name)

    if column_name not in config_dict[EXPECTATIONS]:
        config_dict[EXPECTATIONS][column_name] = list()

    expectation_content = get_expectation_content(expectation_id, parameters_dict)
    config_dict[EXPECTATIONS][column_name].append(expectation_content)

    with open(expectation_set_path, "w") as fp:
        json.dump(config_dict, fp)


def delete_expectation_in_config(
    expectation_set_name: str, column_names: list, expectation_ids: list
) -> None:
    """
    This function creates a new file to write down a configuration for an expectation
    set, or opens a created file to append new expectations and their parameters.

    :param expectation_set_name: String with the name of the expectation set.
    :param column_names: List with column names.
    :param expectation_ids: List with names of expectations to be deleted.
    """
    expectation_set_config_path = get_expectation_set_path(expectation_set_name)
    with open(expectation_set_config_path, "r") as fp:
        config_dict = json.load(fp)

    # Deleting all expectations from configuration
    for column_name, expectation_id in zip(column_names, expectation_ids):
        for expectation_content in config_dict[EXPECTATIONS][column_name]:
            if expectation_content[EXPECTATION_NAME] == expectation_id:
                config_dict[EXPECTATIONS][column_name].remove(expectation_content)
                break

        # If that column has no expectations, delete it from configuration
        if not config_dict[EXPECTATIONS][column_name]:
            del config_dict[EXPECTATIONS][column_name]

    with open(expectation_set_config_path, "w") as fp:
        json.dump(config_dict, fp)
