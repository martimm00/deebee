import pandas as pd
from great_expectations.core import ExpectationConfiguration
from pandas.core.dtypes.common import is_string_dtype, is_numeric_dtype

from constants.defaults import EMPTY_STRING
from constants.great_expectations_constants import (
    EXPECTATIONS_MAP,
    NUMERIC_ONLY_EXPECTATIONS,
    NON_NUMERIC_ONLY_EXPECTATIONS
)

from src.utils import get_value
from src.json_operations import from_json, to_json
from src.expectation_parameters import (
    extract_parameters,
    check_number_of_params_is_correct,
)
from src.front_end_operations import (
    add_options_to_checklist,
    get_checklist_component,
    get_expectation_info_from_interface_name,
)


def remove_non_supported_expectations_from_expectation_suite(
    expectation_suite, supported_expectations_id=EXPECTATIONS_MAP.values()
) -> dict:
    """
    Removes expectations which are not supported by the app from the Expectation Suite
    object itself.
    :param expectation_suite: Great Expectations object.
    :param supported_expectations_id: List with all supported expectations, with GE name.
    """
    # Getting set and supported expectation names
    expectations = get_expectation_suite_expectations(expectation_suite)
    set_expectations = [get_expectation_name(e) for e in expectations]

    # Expectations that need to be removed
    expectations_to_be_removed = [
        e for e in set_expectations if e not in supported_expectations_id
    ]

    # Removing non-supported expectations
    for expectation in expectations:
        expectation_name = get_expectation_name(expectation)
        if expectation_name in expectations_to_be_removed:
            get_expectation_kwargs_and_remove_expectation(
                expectation, expectation_suite
            )

    # Removing expectation called "expect_table_row_count_to_be_between"
    expectations = get_expectation_suite_expectations(expectation_suite)
    for expectation in expectations:
        if get_expectation_name(expectation) == "expect_table_row_count_to_be_between":
            get_expectation_kwargs_and_remove_expectation(
                expectation, expectation_suite
            )
            break
    return expectation_suite


def get_expectation_kwargs_and_remove_expectation(
    expectation: dict, expectation_suite
) -> None:
    """
    Finds expectation kwargs and removes expectation from Expectation Suite.
    :param expectation: Dict that contains all the information about an expectation.
    :param expectation_suite: great_expectations object.
    """
    expectation_name = get_expectation_name(expectation)
    kwargs = get_expectation_kwargs(expectation)
    expectation_configuration = ExpectationConfiguration(expectation_name, kwargs)
    remove_expectation_from_expectation_suite(
        expectation_configuration, expectation_suite
    )


def remove_expectation_from_expectation_suite(
    expectation_configuration: ExpectationConfiguration, expectation_suite
) -> None:
    """
    Removes expectation from Expectation Suite.

    :param expectation_configuration: great_expectations ExpectationConfiguration object.
    :param expectation_suite: great_expectations object.
    """
    expectation_suite.remove_expectation(expectation_configuration)


def columns_used_in_expectation(expectations: list, expectation_name: str) -> list:
    """
    Returns list with dataset columns that need to be checked by a certain expectation.

    :param expectations: List of expectations defined in the Expectation Suite.
    :param expectation_name: String with te name of the expectation to be checked.

    :return: List of dataset columns.
    """
    columns = []
    for expectation in expectations:
        if get_expectation_name(expectation) == expectation_name:
            columns.append(get_expectation_column(expectation))
    return columns


def update_expectation_and_columns_if_necessary(
    column: str,
    expectation_and_columns: str,
    expectation_interface_name: str,
    expectation_parameters_str: str,
) -> str:
    """
    As its name suggests, it updates expectations and columns stored data if there are
    any valid changes.

    :param column: Str with the selected column.
    :param expectation_and_columns: JSON file that contains all currently set
    expectations and its columns.
    :param expectation_interface_name: Str with the selected expectation.
    :param expectation_parameters_str: Str with all expectation parameters, separated by
    a comma.

    :return: JSON file with updated expectations and its columns to be stored.
    """
    if expectation_interface_name and column:

        # Converting parameters from string to list
        extracted_parameters = extract_parameters(expectation_parameters_str)
        expectation_name = EXPECTATIONS_MAP[expectation_interface_name]
        expectation_and_columns = (
            update_expectation_and_columns_if_num_parameters_match(
                column, expectation_and_columns, expectation_name, extracted_parameters
            )
        )
    return expectation_and_columns


def get_columns_compatible_with_expectation(
    dataset: pd.DataFrame, selected_expectation: str
) -> list:
    """
    Returns only dataset columns which are compatible with selected the expectation,
    based on their type.

    :param dataset: Pandas DataFrame with some rows.
    :param selected_expectation: String with the interface expectation name.

    :return: List with compatible columns.
    """
    displayed_columns = []
    columns = list(dataset.columns)
    for column in columns:

        # Non numeric type
        if is_string_dtype(dataset[column]):
            if is_non_numeric_expectation(selected_expectation):
                displayed_columns.append(column)

        # Numeric type
        elif is_numeric_dtype(dataset[column]):
            if is_numeric_expectation(selected_expectation):
                displayed_columns.append(column)
    return displayed_columns


def update_expectation_and_columns_if_num_parameters_match(
    column: str,
    expectation_and_columns: str,
    expectation_name: str,
    extracted_parameters: list,
) -> str:
    """
    Updates currently set expectation and its columns to be stored only if number of
    parameters match.

    :param column: Str with the name of the selected column.
    :param expectation_and_columns: JSON file that contains all currently set
    expectations and its columns.
    :param expectation_name: Str with the selected expectation name.
    :param extracted_parameters: List that contains all entered parameter split.

    :return: JSON file with currently set expectations, the columns where they have to be
    applied and the parameters (if any).
    """
    if check_number_of_params_is_correct(expectation_name, extracted_parameters):

        # Depending on the expectation, parameters could not be
        # a list, so they have to be extracted
        if (
            expectation_name == "expect_column_values_to_be_of_type"
            or expectation_name == "expect_column_value_lengths_to_equal"
        ):
            extracted_parameters = get_value(extracted_parameters)
        expectation_and_columns = update_columns_to_be_expected(
            expectation_name,
            column,
            expectation_and_columns,
            extracted_parameters,
        )
    return expectation_and_columns


def remove_expectations_from_editor_added_expectations(
    current_expectations_items: list, expectations_items_to_be_removed: list
) -> None:
    """
    Removes selected expectations from Expectation Suite when editing.

    :param current_expectations_items: List with current expectation items in Expectation
    Suite editor.
    :param expectations_items_to_be_removed: List with expectations that have to be
    removed.
    """
    for item in expectations_items_to_be_removed:
        try:
            current_expectations_items.remove(item)
        except ValueError:
            continue


def update_current_expectations_if_removed(
    current_expectations: list, removed_expectations: list
) -> None:
    """
    This function updates currently set expectations in case any expectation has been
    removed at Expectation Suite editor, in order to update storage with set expectations
    and their columns.

    :param current_expectations: List with all current expectations.
    :param removed_expectations: List with expectations that have to be removed.
    """
    if removed_expectations:

        # First see if they have already been removed
        if removed_expectations[0] in current_expectations:

            # Remove them one by one
            remove_expectations_from_editor_added_expectations(
                current_expectations, removed_expectations
            )


def update_current_expectations_if_new(
    current_expectations: list, new_expectation: list
) -> list:
    """
    Updates currently set expectations in case there is a new expectation to be added, in
    order to update storage with set expectations and their columns.

    :param current_expectations: List that contains currently set expectations.
    :param new_expectation: List that contains one single new expectation to be added.

    :return: List with new current expectations to be stored in a JSON file.
    """
    if new_expectation:
        current_expectations = add_options_to_checklist(
            current_expectations, [get_value(new_expectation)]
        )
    return current_expectations


def read_expectation_and_columns_from_expectation_suite(
    expectation_suite: dict,
) -> dict:
    """
    Reads and loads dictionary expectation and columns to be stored from the Expectation
    Suite JSON file in form of a dictionary.

    :param expectation_suite: Dict that contains the JSON file with all the Expectation
    Suite content.

    :return: JSON file with Expectation Suite's expectations and what columns they have
    to be applied on.
    """
    expectation_and_columns = {}
    for expectation in get_expectation_suite_expectations(expectation_suite):

        # Getting expectation name, column and parameters
        expectation_name, column, parameters = get_expectation_info(expectation)

        # If there is no such expectation inside the dictionary
        if expectation_name not in expectation_and_columns:
            expectation_and_columns[expectation_name] = {}

        # Dictionary addition
        expectation_and_columns[expectation_name][column] = parameters
    return expectation_and_columns


def get_expectation_info(expectation: dict) -> (str, str, str):
    """
    Returns selected expectation information.

    :param expectation: Dict that contains the expectation name, the column where it has
    to be applied and the parameters (if any).

    :return: Three strings which include the expectation name, the column and the
    parameters (if any).
    """
    return (
        get_expectation_name(expectation),
        get_expectation_column(expectation),
        get_expectation_parameters(expectation),
    )


def get_expectation_suite_expectations(expectation_suite) -> list:
    """
    Returns a list of expectations contained in an Expectation Suite.

    :param expectation_suite: Expectation Suite object itself.

    :return: List of expectations.
    """
    return expectation_suite["expectations"]


def get_expectation_name(expectation: dict) -> str:
    """
    Returns expectation name from expectation dictionary.

    :param expectation: Dict with expectation information.

    :return: String with the expectation name.
    """
    return expectation["expectation_type"]


def get_expectation_kwargs(expectation: dict) -> dict:
    """
    Returns the expectation kwargs from expectation dictionary.

    :param expectation: Dict with expectation information.

    :return: Dict with expectation kwargs.
    """
    return expectation["kwargs"]


def get_expectation_column(expectation: dict) -> str:
    """
    Returns the column where the expectation has to be applied from the expectation
    dictionary.

    :param expectation: Dict with expectation information.

    :return: Str with the dataset column.
    """
    return get_expectation_kwargs(expectation)["column"]


def get_expectation_parameters(expectation: dict) -> str or (str, str):
    """
    Manages parameters extraction from expectation kwargs, by checking which field it
    contains.

    :param expectation: Dict with expectation information.

    :return: String with the parameters or an empty string if kwargs does not contain any
    of these fields.
    """
    kwargs = get_expectation_kwargs(expectation)
    if "value" in kwargs:
        return kwargs["value"]
    elif "value_set" in kwargs:
        return kwargs["value_set"]
    elif "min_value" in kwargs and "max_value" in kwargs:
        return [kwargs["min_value"], kwargs["max_value"]]
    elif "type_" in kwargs:
        return kwargs["type_"]
    elif "type_list" in kwargs:
        return kwargs["type_list"]
    elif "median" in kwargs:
        return kwargs["median"]
    return EMPTY_STRING


def get_numeric_only_expectations() -> list:
    """
    Returns a list with the names of numeric expectations.

    :return: List of strings.
    """
    return NUMERIC_ONLY_EXPECTATIONS


def get_non_numeric_only_expectations() -> list:
    """
    Returns a list with the names of non-numeric expectations.

    :return: List of strings.
    """
    return NON_NUMERIC_ONLY_EXPECTATIONS


def is_numeric_expectation(expectation: str) -> bool:
    """
    Returns if the given expectation can be applied to numeric values.

    :param expectation: String with the name of the expectation.

    :return: Boolean that tells the app if it is numeric.
    """
    return expectation not in get_non_numeric_only_expectations()


def is_non_numeric_expectation(expectation: str) -> bool:
    """
    Returns if the given expectation can be applied to non-numeric values.

    :param expectation: String with the name of the expectation.

    :return: Boolean that tells the app if it is non-numeric.
    """
    return expectation not in get_numeric_only_expectations()


def remove_expectations_from_expectation_suite_loop(
    expectation_suite, removed_expectations: list, selected_expectations: list
) -> None:
    """
    Loop that removes expectations from Expectation Suite object.

    :param expectation_suite: great expectations object.
    :param removed_expectations: List with the expectations that have to be removed from
    the suite.
    :param selected_expectations: List with currently selected expectations.
    """
    for interface_expectation in selected_expectations:
        expectation_interface_name, column = get_expectation_info_from_interface_name(
            interface_expectation
        )
        expectation_name = EXPECTATIONS_MAP[expectation_interface_name]
        set_expectations = get_expectation_suite_expectations(expectation_suite)
        look_for_selected_expectation_and_remove_it(
            expectation_suite, expectation_name, column, set_expectations
        )
        item = get_checklist_component(interface_expectation)
        removed_expectations.append(item)


def look_for_selected_expectation_and_remove_it(
    expectation_suite, expectation_name: str, column: str, set_expectations: list
) -> None:
    """
    This function searches for the expectation that has to be removed from the
    Expectation Suite and removes it.

    :param expectation_suite: great expectations object.
    :param expectation_name: Str with the expectation name.
    :param column: Str with the dataset column name.
    :param set_expectations: List that contains set expectations.
    """
    for expectation in set_expectations:
        if get_expectation_name(expectation) == expectation_name:
            if get_expectation_column(expectation) == column:
                get_expectation_kwargs_and_remove_expectation(
                    expectation, expectation_suite
                )
                break


def update_columns_to_be_expected(
    expectation_name: str,
    column: str,
    expectation_and_columns: str,
    extracted_parameters: list,
) -> str:
    """
    This function updates the dictionary that contains all the expectations and the
    columns where they have to be applied.

    :param expectation_name: Str with the name of the expectation.
    :param column: Str with the name of the dataset column.
    :param expectation_and_columns: JSON file that contains all set expectations, the
    columns where they have to be applied and the parameters (if any).
    :param extracted_parameters: List of extracted parameters.

    :return: JSON file with the updated expectations and columns.
    """
    if column:
        expectation_and_columns = from_json(expectation_and_columns)
        if expectation_and_columns:
            if expectation_name not in expectation_and_columns:
                expectation_and_columns[expectation_name] = {}
            expectation_and_columns[expectation_name][column] = extracted_parameters
            return to_json(expectation_and_columns)
        return to_json({expectation_name: {column: extracted_parameters}})
    return expectation_and_columns


def are_there_set_expectations(added_expectations: list) -> bool:
    """
    This function checks if the list that contains all currently added expectations is
    empty or not.

    :param added_expectations: List that contains currently added expectations.

    :return: Bool.
    """
    return bool(added_expectations)


def columns_used_in_expectations(defined_expectations: list) -> set:
    """
    Returns the set of columns where an expectation has to be applied. This function is
    used to get datasets that are compatible with the one that was originally used to
    create the Expectation Suite.

    :param defined_expectations: List that contains all defined expectations in the
    Expectation Suite.

    :return: Set of all used columns.
    """
    columns = []
    for expectation in defined_expectations:
        columns.append(get_expectation_column(expectation))

    # Converting it to a set to avoid duplicity
    return set(columns)


def is_expectation_set_name_valid(name: str) -> bool:
    """
    Returns if the given expectation set name is valid or not.

    :param name: String with the name to be checked.
    """
    return name and name.replace("_", "").isalnum()
