from datetime import datetime

from constants.defaults import EMPTY_DICT
from constants.expectation_set_constants import (
    PARAMETERS,
    LAST_EDITED,
    EXPECTATIONS,
    EXPECTATION_NAME,
    EXPECTATION_SET_NAME,
    MULTICOLUMN_CONFIG_SEPARATOR
)
from constants.great_expectations_constants import (
    TYPE,
    LENGTH,
    COLUMN_A,
    COLUMN_B,
    OR_EQUAL,
    MIN_VALUE,
    MAX_VALUE,
    COLUMN_LIST,
    VALUE_SET_MULTI,
    VALUE_SET_SINGLE,
    EXPECTATION_PARAMS,
    SUPPORTED_GE_EXP_TYPES,
    NUMERIC_ONLY_EXPECTATIONS,
    MULTICOLUMN_EXPECTATIONS_MAP,
    NON_NUMERIC_ONLY_EXPECTATIONS,
    MULTICOLUMN_EXPECTATIONS_N_COLUMNS,
    SINGLE_COLUMN_EXPECTATIONS_MAP,
)

from src.utils import is_list_empty
from src.json_operations import read_json, write_json
from src.front_end_operations import (
    build_expectation_interface_name,
    expectation_is_already_in_checklist,
    get_expectation_id_and_column_name_from_interface_name
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
        config = read_json(fp)
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


def get_expectation_config(expectation_id: str, params_dict: dict) -> dict:
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
        content = get_expectation_set_config(set_name)

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


def write_single_column_expectation_in_config(
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
            write_json(empty_expectation_set_content, fp)

    # Getting current expectation set configuration
    config_dict = get_expectation_set_config(expectation_set_name)

    if column_name not in config_dict[EXPECTATIONS]:
        config_dict[EXPECTATIONS][column_name] = list()

    expectation_content = get_expectation_config(expectation_id, parameters_dict)
    config_dict[EXPECTATIONS][column_name].append(expectation_content)

    with open(expectation_set_path, "w") as fp:
        write_json(config_dict, fp)


def write_multicolumn_expectation_in_config(
    expectation_set_name: str,
    column_names: list,
    expectation_id: str,
    parameters_dict: dict
) -> None:
    """
    This function creates a new file to write down a configuration for an expectation
    set, or opens a created file to append new expectations and their parameters.

    :param expectation_set_name: String with the name of the expectation set.
    :param column_names: String with the name of the selected table column, where the
    expectation will have to be applied to.
    :param expectation_id: String with the ID of the new expectation to be added.
    :param parameters_dict: Dictionary with parameters of this new expectation.
    """
    expectation_set_path = get_expectation_set_path(expectation_set_name)
    if not exists_path(expectation_set_path):
        empty_expectation_set_content = get_empty_expectation_set_content(expectation_set_name)
        with open(expectation_set_path, "w") as fp:
            write_json(empty_expectation_set_content, fp)

    # Getting current expectation set configuration
    config_dict = get_expectation_set_config(expectation_set_name)

    # Getting new column names key in expectation set config
    column_names = MULTICOLUMN_CONFIG_SEPARATOR.join(column_names)

    # If the new expectations already exist in the config but with another order, then
    # keep the existing order rather than the new one
    if MULTICOLUMN_EXPECTATIONS_N_COLUMNS[expectation_id] != 2:
        new_columns = set(column_names.split(MULTICOLUMN_CONFIG_SEPARATOR))
        for existing_columns in config_dict[EXPECTATIONS]:
            if new_columns == set(existing_columns.split(MULTICOLUMN_CONFIG_SEPARATOR)):
                column_names = existing_columns

    if column_names not in config_dict[EXPECTATIONS]:
        print("column set already exists in config")
        config_dict[EXPECTATIONS][column_names] = list()

    expectation_content = get_expectation_config(expectation_id, parameters_dict)
    if expectation_content not in config_dict[EXPECTATIONS][column_names]:
        config_dict[EXPECTATIONS][column_names].append(expectation_content)

    with open(expectation_set_path, "w") as fp:
        write_json(config_dict, fp)


def delete_expectations_in_config(
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
        config_dict = read_json(fp)

    # Deleting all expectations from configuration
    for column_name, expectation_id in zip(column_names, expectation_ids):
        built_column_name = MULTICOLUMN_CONFIG_SEPARATOR.join(column_name)
        for idx in range(len(config_dict[EXPECTATIONS][built_column_name])-1, -1, -1):
            expectation_content = config_dict[EXPECTATIONS][built_column_name][idx]
            if expectation_content[EXPECTATION_NAME] == expectation_id:
                config_dict[EXPECTATIONS][built_column_name].pop(idx)

        # If that column has no expectations, delete it from configuration
        if not config_dict[EXPECTATIONS][built_column_name]:
            del config_dict[EXPECTATIONS][built_column_name]

    with open(expectation_set_config_path, "w") as fp:
        write_json(config_dict, fp)


def get_numeric_only_expectations() -> list:
    """
    Returns a list with the names of numeric expectations.
    :return: List of strings.
    """
    return NUMERIC_ONLY_EXPECTATIONS


def get_non_numeric_only_expectations() -> list:
    """
    Returns a list with the names of non numeric expectations.
    :return: List of strings.
    """
    return NON_NUMERIC_ONLY_EXPECTATIONS


def is_numeric_expectation(expectation: str) -> bool:
    """
    Returns if the given expectation can be applied to numeric
    values.
    :param expectation: String with the name of the expectation.
    :return: Boolean that tells the app if it is numeric.
    """
    return expectation not in get_non_numeric_only_expectations()


def is_non_numeric_expectation(expectation: str) -> bool:
    """
    Returns if the given expectation can be applied to non- numeric
    values.
    :param expectation: String with the name of the expectation.
    :return: Boolean that tells the app if it is non-numeric.
    """
    return expectation not in get_numeric_only_expectations()


def is_expectation_set_name_valid(name: str) -> bool:
    """
    Returns if the given expectation set name is valid or not.

    :param name: String with the name to be checked.
    """
    return name and name.replace("_", "").isalnum()


def get_two_columns_expectations() -> list:
    """
    Returns the ID of those expectations that work with two table columns.

    :return: List with expectation IDs.
    """
    return [
        e
        for e in MULTICOLUMN_EXPECTATIONS_N_COLUMNS
        if MULTICOLUMN_EXPECTATIONS_N_COLUMNS[e] == 2
    ]


def get_any_column_count_expectations() -> list:
    """
    Returns the ID of those expectations that work with any number of table columns.

    :return: List with expectation IDs.
    """
    return [
        e
        for e in MULTICOLUMN_EXPECTATIONS_N_COLUMNS
        if MULTICOLUMN_EXPECTATIONS_N_COLUMNS[e] is None
    ]


def get_expectation_set_name_from_filename(filename: str) -> str:
    """
    Returns the expectation set name given its filename, in other words, it removes
    the JSON extension.

    :param filename: String with the filename.

    :return: Expectation set name, without the extension.
    """
    return filename.split(".")[0]


def multicolumn_value_set_matches_expression(value: str) -> bool:
    """
    Returns if the value set of a multicolumn expectation matches the required
    format.

    :param value: String with value set.

    :return: Bool.
    """
    matches_format = True

    opening_clause_count = value.count("[")
    closing_clause_count = value.count("]")
    if (opening_clause_count + closing_clause_count) % 2 != 0:
        matches_format = False

    if opening_clause_count != closing_clause_count:
        matches_format = False

    if matches_format:
        value_count = 0
        comma_count = 1
        for character in value:
            if character == "[":
                if comma_count != 1:
                    matches_format = False
                value_count = comma_count = 0
            elif character == "]":
                if value_count < 2 or comma_count != 1:
                    matches_format = False
                comma_count = 0
            elif character == ",":
                comma_count += 1
            else:
                value_count += 1

    return matches_format


def parse_parameter(param_name: str, value) -> any or None:
    """
    Returns a parsed parameter in case it is correct. If not, it returns None.

    :param param_name: String with the name of the parameter.
    :param value: Non-parsed value given to the parameter.
    """
    parsed_param = None
    if param_name == TYPE:
        if value in SUPPORTED_GE_EXP_TYPES:
            parsed_param = value
    elif param_name == LENGTH:
        if value.isnumeric():
            parsed_param = value
    elif param_name == VALUE_SET_SINGLE:
        value = value.replace(" ", "")
        parsed_param = value.split(",")
        for i in range(len(parsed_param)):
            if parsed_param[i].isnumeric():
                parsed_param[i] = int(parsed_param[i])
            else:
                try:
                    parsed_param[i] = float(parsed_param[i])
                except ValueError:
                    pass
    elif param_name == MIN_VALUE or param_name == MAX_VALUE:
        value = value.replace(",", ".")
        try:
            parsed_param = float(value)
        except ValueError:
            pass
    elif param_name == VALUE_SET_MULTI:
        value = value.replace(" ", "").strip(",")
        if multicolumn_value_set_matches_expression(value):
            value = value.split("],")
            value = [
                pair.replace("[", "").replace("]", "") for pair in value
            ]
            value = [pair.split(",") for pair in value]
            if not is_list_empty(value):
                if all([len(pair) == 2 for pair in value]):
                    parsed_param = value
                    for i in range(len(value)):
                        for j in range(2):
                            parsed_param[i][j] = parsed_param[i][j].replace("'", "")
                            if parsed_param[i][j].isnumeric():
                                parsed_param[i][j] = int(parsed_param[i][j])
                            else:
                                try:
                                    parsed_param[i][j] = float(parsed_param[i][j])
                                except ValueError:
                                    pass
                    parsed_param = [tuple(pair) for pair in parsed_param]
    elif param_name == OR_EQUAL:
        parsed_param = False if is_list_empty(value) else True
    return parsed_param


def add_single_column_expectation(
    current_expectations: list,
    expectation_set_name: str,
    selected_table_column: str,
    expectation_name: str,
    length_input: str,
    min_value_input: str,
    max_value_input: str,
    type_input: str,
    values_input: str
) -> None:
    """
    Adds an expectation working for a single table column, to expectation set config.

    :param current_expectations: List with all current expectations in definer
    checklist.
    :param expectation_set_name: String with the name of the expectation set that is
    being created.
    :param selected_table_column: String with the name of the table column (one
    only).
    :param expectation_name: String with the interface name of the expectation that
    the user wants to apply to that column.
    :param length_input: String containing most likely a numeric value.
    :param min_value_input: String containing most likely a numeric value.
    :param max_value_input: String containing most likely a numeric value.
    :param type_input: String with the parameter for type expectation.
    :param values_input: String with the parameter for the values in set
    expectation.
    """
    params_map = {
        TYPE: type_input,
        LENGTH: length_input,
        VALUE_SET_SINGLE: values_input,
        MIN_VALUE: min_value_input,
        MAX_VALUE: max_value_input
    }
    all_params_are_set = True
    expectation_id = SINGLE_COLUMN_EXPECTATIONS_MAP[expectation_name]
    expectation_params = EXPECTATION_PARAMS[expectation_id]
    params_of_interest = dict()
    for param in expectation_params:
        parsed_param = parse_parameter(param, params_map[param])
        params_of_interest[param] = parsed_param
        if parsed_param is None:
            all_params_are_set = False

        # Expectation will not be added if min value is greater than max
        # value
        if MIN_VALUE in params_of_interest and MAX_VALUE in params_of_interest:
            if params_of_interest[MIN_VALUE] > params_of_interest[MAX_VALUE]:
                all_params_are_set = False
    if all_params_are_set:
        write_single_column_expectation_in_config(
            expectation_set_name, selected_table_column, expectation_id, params_of_interest
        )
        expectation_interface_name = build_expectation_interface_name(
            expectation_name, [selected_table_column]
        )
        if not expectation_is_already_in_checklist(
                expectation_interface_name, current_expectations
        ):
            current_expectations.append(expectation_interface_name)


def add_multicolumn_expectation(
    current_expectations: list,
    expectation_set_name: str,
    table_column_a: str,
    table_column_b: str,
    selected_table_columns: list,
    expectation_name: str,
    or_equal: list,
    values_input: str
) -> None:
    """
    Adds an expectation working for a multiple table columns, to expectation set
    config.

    :param current_expectations: List with all current expectations in definer
    checklist.
    :param expectation_set_name: String with the name of the expectation set that is
    being created.
    :param table_column_a: String with the name of the first column to be used in
    expectations which require two of them.
    :param table_column_b: String with the name of the second column to be used in
    expectations which require two of them.
    :param selected_table_columns: List with the names of selected columns to be used
    in expectations which do not require a certain amount of table columns.
    :param expectation_name: String with the interface name of the expectation that
    the user wants to apply to that column.
    :param or_equal: List that can be empty or have one single value.
    :param values_input: String with the parameter for the values in set
    expectation.
    """
    params_map = {
        COLUMN_A: table_column_a,
        COLUMN_B: table_column_b,
        OR_EQUAL: or_equal,
        COLUMN_LIST: selected_table_columns,
        VALUE_SET_MULTI: values_input,
    }
    all_params_are_set = True
    expectation_id = MULTICOLUMN_EXPECTATIONS_MAP[expectation_name]
    expectation_params = EXPECTATION_PARAMS[expectation_id]
    params_of_interest = dict()
    for param in expectation_params:
        if "column" not in param:
            parsed_param = parse_parameter(param, params_map[param])
            params_of_interest[param] = parsed_param
            if parsed_param is None:
                all_params_are_set = False
    if COLUMN_A in expectation_params and COLUMN_B in expectation_params:
        if not params_map[COLUMN_A] or not params_map[COLUMN_B]:
            all_params_are_set = False
    if COLUMN_LIST in expectation_params:
        if is_list_empty(params_map[COLUMN_LIST]):
            all_params_are_set = False
    if all_params_are_set:
        if not is_list_empty(selected_table_columns):
            table_columns = selected_table_columns
        else:
            table_columns = [table_column_a, table_column_b]
        write_multicolumn_expectation_in_config(
            expectation_set_name, table_columns, expectation_id, params_of_interest
        )
        expectation_interface_name = build_expectation_interface_name(
            expectation_name, list(table_columns)
        )
        if not expectation_is_already_in_checklist(
                expectation_interface_name, current_expectations
        ):
            current_expectations.append(expectation_interface_name)


def delete_expectation(
    current_expectations: list,
    expectation_set_name: str,
    selected_expectations: str
) -> None:
    """
    Deletes selected expectations from expectation config.

    :param current_expectations: List with current expectations in the definer
    checklist.
    :param expectation_set_name: String with the name of the expectation set that is
    being created.
    :param selected_expectations: List with selected expectations that the user wants
    to delete.
    """
    column_names = list()
    expectation_ids = list()
    for interface_name in selected_expectations:
        (
            expectation_id,
            column_name
        ) = get_expectation_id_and_column_name_from_interface_name(interface_name)

        # Getting the expectations to be removed
        expectation_ids.append(expectation_id)

        # Getting column names where expectations are set at
        column_names.append(column_name)

        # Removing the expectations from the interface
        current_expectations.remove(interface_name)
    # Finally, deleting selected expectations in configuration
    delete_expectations_in_config(expectation_set_name, column_names, expectation_ids)