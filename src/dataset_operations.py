import pandas as pd
from rapidfuzz import fuzz

from constants.supported_constants import SUPPORTED_DATASET_TYPES

from src.low_level_operations import (
    ends_with,
    delete_file,
    get_import_dir_path,
    get_imported_dataset_path,
    get_elements_inside_directory
)


def dataset_can_be_imported(dataset_name: str) -> bool:
    """
    Returns if a dataset can be imported or not.

    :param dataset_name: String with the name of the dataset.

    :return: Bool
    """
    return not dataset_name_is_already_in_use(dataset_name)


def is_dataset_name(name: str) -> bool:
    """
    Returns whether the name belongs to a potential dataset or not.

    :param name: String to be checked.

    :return: Bool.
    """
    return any([ends_with("." + ending, name) for ending in SUPPORTED_DATASET_TYPES])


def get_imported_dataset_names() -> list:
    """
    Returns the names of all uploaded datasets from the upload path.

    :return: List with the names of all uploaded datasets.
    """
    upload_dir_path = get_import_dir_path()
    return [
        d for d in get_elements_inside_directory(upload_dir_path) if is_dataset_name(d)
    ]


def delete_datasets(datasets_to_delete: list) -> None:
    """
    Deletes the selected datasets and updates available options in the checklist.

    :param datasets_to_delete: List with components to be deleted.

    :return: List with updated available options in the checklist.
    """
    for dataset_name in datasets_to_delete:

        # Getting the dataset path and removing it from disk
        dataset_path = get_imported_dataset_path(dataset_name)
        delete_file(dataset_path)


def dataset_name_is_already_in_use(dataset_name: str) -> bool:
    """
    Returns if the name of a recently imported dataset is already in use.

    :param dataset_name: String with the name of the dataset.

    :return: Bool.
    """
    return dataset_name in get_imported_dataset_names()


def is_new_dataset_name_valid(current_names: list, name: str) -> bool or None:
    """
    Returns if the new name for a dataset is valid.

    :param current_names: List with current names.
    :param name: String with the new name.

    :return: Bool.
    """
    if len(name.split(".")) == 2:
        name_without_extension, _ = name.split(".")
        if name_without_extension:
            if is_dataset_name(name):

                # If the name is not already in use for other datasets
                return name not in current_names


def build_duplicates_removed_dataset_name(original_name: str) -> str:
    """
    Builds a new name for a dataset whose duplicated rows have been removed, given
    its original name.

    :param original_name: String with original dataset name.
    """
    name, extension = original_name.split(".")
    if "_type_corrected" in name:
        name = name.replace("_type_corrected", "")
        name += "_corrected"
    else:
        name += "_no_duplicates"
    return name + "." + extension


def build_type_corrected_dataset_name(original_name: str) -> str:
    """
    Builds a new name for a type corrected dataset, given its original name.

    :param original_name: String with original dataset name.
    """
    name, extension = original_name.split(".")
    if "_no_duplicates" in name:
        name = name.replace("_no_duplicates", "")
        name += "_corrected"
    else:
        name += "_type_corrected"
    return name + "." + extension


def get_string_matching_dict_with_partial_ratio(
    table: pd.DataFrame, columns: list, number_of_rows: int, matching_dict: dict
) -> None:
    """
    Fills the given matching dictionary with values coming from fuzzy string
    matching, using standard method "ratio".

    :param table: Pandas DataFrame with dataset.
    :param columns: List with column names that the user selected.
    :param number_of_rows: Number of rows in the dataset.
    :param matching_dict: Dictionary to be filled.
    """
    for column_name in columns:
        for first_line in range(number_of_rows):
            for second_line in range(first_line + 1, number_of_rows):
                matching_dict["row_pair"].append(
                    str(first_line) + "," + str(second_line)
                )
                matching_score = fuzz.ratio(
                    table.loc[first_line, column_name],
                    table.loc[second_line, column_name]
                )
                matching_dict[column_name].append(matching_score)


def get_string_matching_dict_with_ratio(
    table: pd.DataFrame, columns: list, number_of_rows: int, matching_dict: dict
) -> None:
    """
    Fills the given matching dictionary with values coming from fuzzy string
    matching, using the method called "partial_ratio".

    :param table: Pandas DataFrame with dataset.
    :param columns: List with column names that the user selected.
    :param number_of_rows: Number of rows in the dataset.
    :param matching_dict: Dictionary to be filled.
    """
    for column_name in columns:
        for first_line in range(number_of_rows):
            for second_line in range(first_line + 1, number_of_rows):
                matching_dict["row_pair"].append(
                    str(first_line) + "," + str(second_line)
                )
                matching_score = fuzz.partial_ratio(
                    table.loc[first_line, column_name],
                    table.loc[second_line, column_name]
                )
                matching_dict[column_name].append(matching_score)


def get_string_matching_dict(
    table: pd.DataFrame, columns: list, partial_ratio: bool
) -> dict:
    """
    Returns a dictionary with matching values between pairs of rows, for the selected
    table columns.

    :param table: Pandas DataFrame with dataset.
    :param columns: List with column names that the user selected.
    :param partial_ratio: Bool telling if partial ratio needs to be used or not.

    :return: Dictionary with matching values.
    """
    number_of_rows = len(table)

    matching_df_columns = columns + ["row_pair"]
    matching_dict = dict()
    for df_column in matching_df_columns:
        matching_dict[df_column] = list()

    if partial_ratio:
        get_string_matching_dict_with_ratio(
            table, columns, number_of_rows, matching_dict
        )

    else:
        get_string_matching_dict_with_partial_ratio(
            table, columns, number_of_rows, matching_dict
        )

    return matching_dict
