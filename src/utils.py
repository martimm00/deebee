import os
import csv
import pandas as pd
from pandas_profiling import ProfileReport

from src.low_level_operations import (
    is_csv_file_by_name,
    is_excel_file_by_name,
    get_file_name_by_path,
    get_profile_report_path,
    get_imported_dataset_path,
    get_profile_report_title_from_dataset_name
)


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


def read_csv_dataset(path: os.path, sep=";", n_rows=None, type_dict=None) -> pd.DataFrame:
    """
    Returns a Pandas DataFrame given the specified path of a CSV file.

    :param path: Path of the dataset to be read.
    :param sep: String with the separator character between fields.
    :param n_rows: Integer with the number of rows to be read.
    :param type_dict: Dictionary with types.

    :return: Pandas DataFrame.
    """
    return pd.read_csv(path, sep=sep, nrows=n_rows, dtype=type_dict)


def read_excel_dataset(path: os.path, n_rows=None, type_dict=None) -> pd.DataFrame:
    """
    Returns a Pandas DataFrame given the specified path of an XLSX file.

    :param path: Path of the dataset to be read.
    :param sep: String with the separator character between fields.
    :param n_rows: Integer with the number of rows to be read.
    :param type_dict: Dictionary with types.

    :return: Pandas DataFrame.
    """
    return pd.read_excel(path, nrows=n_rows, dtype=type_dict)


def read_dataset(path: os.path, sep=";", n_rows=None, type_dict=None) -> pd.DataFrame or None:
    """
    This function acts a wrapper to read a dataset from a file, no matter the file
    format.

    :param path: Path where the dataset can be found.
    :param sep: Separator character.
    :param n_rows: Number of rows to be read.
    :param type_dict: Dictionary with types

    :return: Pandas DataFrame.
    """
    # Getting file name from its path
    file_name = get_file_name_by_path(path)

    dataset = None

    # Depending on the format, read the dataset with the appropriate Pandas function
    if is_csv_file_by_name(file_name):
        dataset = read_csv_dataset(path, sep=sep, n_rows=n_rows, type_dict=type_dict)
    elif is_excel_file_by_name(file_name):
        dataset = read_excel_dataset(path, n_rows=n_rows, type_dict=type_dict)

    return dataset


def write_csv_dataset(dataset: pd.DataFrame, path: os.path, sep=";") -> None:
    """
    Writes Pandas DataFrame to CSV format.
    """
    if sep is None:
        sep = ";"
    dataset.to_csv(path, sep=sep, index=False)


def write_excel_dataset(dataset: pd.DataFrame, path: os.path) -> None:
    """
    Writes Pandas DataFrame to CSV format.
    """
    dataset.to_excel(path, index=False)


def write_dataset(dataset: pd.DataFrame, path: os.path, sep=";") -> None:
    """
    This function acts a wrapper to write a dataset to a file, no matter the file format.

    :param dataset: Pandas DataFrame containing the dataset to be written.
    :param path: Path where the dataset can be found.
    :param sep: Separator character.
    """
    file_name = get_file_name_by_path(path)

    if is_csv_file_by_name(file_name):
        write_csv_dataset(dataset, path, sep=sep)
    elif is_excel_file_by_name(file_name):
        write_excel_dataset(dataset, path)


def infer_csv_separator(file_path: os.path) -> str or None:
    """
    Infers the separator of a CSV file.

    :param file_path: Path of the CSV file to be checked.
    :return:
    """
    separator = None
    file_name = get_file_name_by_path(file_path)
    if is_csv_file_by_name(file_name):
        try:
            with open(file_path, "rb") as csvfile:
                separator = str(csv.Sniffer().sniff(csvfile.read(1024), delimiters=";,|"))
        except TypeError:
            pass
    return separator


def build_profile_report(dataset_name: str) -> None:
    """
    This function builds a profile report of a dataset, given its name.

    :param dataset_name: String with the full name of the dataset.
    """
    # Getting dataset path
    dataset_path = get_imported_dataset_path(dataset_name)

    # Inferring the separator char in the file
    separator = infer_csv_separator(dataset_path)

    # Loading the file into a Pandas DataFrame
    dataframe = read_dataset(dataset_path, sep=separator)
    dataset_name = dataset_name.replace(".", "_")
    title = get_profile_report_title_from_dataset_name(dataset_name)
    file_path = get_profile_report_path(dataset_name)

    # Building the profile report itself and saving it to a file
    report = ProfileReport(dataframe, title=title)
    try:
        report.to_file(file_path)
    except ValueError:
        pass
