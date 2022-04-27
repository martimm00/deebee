import os
import pandas as pd
from pandas_profiling import ProfileReport

from constants import path_constants
from src.json_operations import to_json
from src.data_structure_operations import get_value, is_empty
from src.low_level_operations import (
    make_dir,
    write_file,
    rename,
    exists_path,
    remove_file,
    remove_folder,
    get_upload_folder_path,
    get_reports_folder,
    ends_in,
    is_csv,
    is_xlsx,
    has_dataset_name,
    get_name_from_file_name,
    get_elements_inside_directory,
    get_uploaded_datasets_names,
    get_test_dataset_name,
    get_dataset_path,
    get_report_path,
)


def load_current_dataset(
    dataset_name_creator: str, dataset_name_editor: str
) -> pd.DataFrame:
    """
    This function loads the dataset that is being currently used, which can be creating
    or editing an Expectation Suite.

    :param dataset_name_creator: String with the name of the dataset that is being used
    to create an Expectation Suite.
    :param dataset_name_editor: String with the name of the dataset that is being used to
    edit an Expectation Suite.

    :return: Pandas DataFrame.
    """
    dataset_name = dataset_name_editor
    if dataset_name_creator:
        dataset_name = dataset_name_creator
    dataset_path = get_dataset_path(dataset_name)

    # Load only first lines to save time
    dataset = load_dataset(dataset_path, n_rows=5)
    return dataset


def return_dataset_columns(dataset: pd.DataFrame) -> list:
    """
    As its name suggests, it returns the columns of the dataset that
    has been provided as an argument.
    :param dataset: Pandas DataFrame with all the data.
    :return: List with the dataset columns.
    """
    return dataset.columns.tolist()


def build_dataset_report(dataset_file_name: str) -> os.path:
    """
    This function builds a dataset report from its name.
    :param dataset_file_name: String with the name of the file that
    contains the dataset.
    """
    dataset_name = get_name_from_file_name(dataset_file_name)
    report_path = get_report_path(dataset_name)

    # If a report of this dataset has not been made before
    if not exists_path(report_path):

        # Making the report and converting it to a HTML file
        dataset = load_dataset(dataset_file_name)
        make_dataset_report(dataset, dataset_file_name, report_path)

    # Opening report in the browser
    return report_path


def which_dataset_could_have_been_used_to_create_expectation_suite(
    expectation_suite: dict,
) -> (str or None, list or None):
    """
    Used to find a dataset that is compatible with the one that was
    originally used to create the Expectation Suite, by checking
    compatibility between dataset columns and columns where set
    expectations have to be applied.
    :param expectation_suite: great expectations object.
    :return: String with the name of the dataset and a list with its
    columns.
    """
    compatible_datasets_and_columns = get_compatible_datasets(expectation_suite)

    # Returning the first one is fine
    for dataset in compatible_datasets_and_columns:
        return dataset, compatible_datasets_and_columns[dataset]
    return None, None


def get_compatible_datasets(expectation_suite: dict) -> dict:
    """
    Used to get all uploaded datasets which are compatible with the
    one originally used to create the Expectation Suite and its
    expectations.
    :param expectation_suite: great expectations object.
    :return: Dict whose keys are strings with dataset name and whose
    values are lists with their columns.
    """
    defined_expectations = expectation_suite["expectations"]
    uploaded_datasets_names = get_uploaded_datasets_names()

    # Checking defined expectations
    if not is_empty(defined_expectations):
        columns = return_dataset_columns_set(defined_expectations)

        # Searching for columns on all datasets
        compatible_datasets_and_columns = get_datasets_compatible_with_expectations(
            columns, uploaded_datasets_names
        )
    else:
        compatible_datasets_and_columns = get_uploaded_datasets_name_and_columns(
            uploaded_datasets_names
        )
    return compatible_datasets_and_columns


def return_dataset_columns_set(defined_expectations: list):
    """
    Finds which columns have been used to apply expectations in an
    Expectation Suite, puts them into a list and then converts it to
    a set, in order to avoid duplicity. This way, we are able to know
    which columns need to be in the set of columns of a dataset in
    order to apply this Expectation Suite.
    :param defined_expectations: List of expectations inside the
    Expectation Suite.
    :return: Set of mandatory columns.
    """
    columns = [expectation["kwargs"]["column"] for expectation in defined_expectations]

    # Converting it to a set to avoid duplicity
    columns = set(columns)
    return columns


def get_uploaded_datasets_name_and_columns(uploaded_datasets_names: list) -> dict:
    """
    Provides all uploaded datasets name and their columns.
    :param uploaded_datasets_names: List of names of uploaded
    datasets.
    :return: Dict whose keys are strings with dataset names and whose
    values are lists with their columns.
    """
    compatible_datasets_and_columns = {}
    for dataset_name in uploaded_datasets_names:
        try:
            dataset = load_dataset(dataset_name, n_rows=5)
            compatible_datasets_and_columns[dataset_name] = return_dataset_columns(
                dataset
            )
        except PermissionError:
            continue
        except:
            continue
    return compatible_datasets_and_columns


def get_datasets_compatible_with_expectations(
    columns: set,
    uploaded_datasets_names: list,
) -> dict:
    """
    Returns datasets whose columns are compatible with set
    expectations and the columns where they have to be applied.
    :param columns: Set that contains strings with columns where
    expectations have to be applied.
    :param uploaded_datasets_names: List with names of updated
    datasets.
    :return: Dict with dataset name as key and its columns as value.
    """
    compatible_datasets_and_columns = {}
    for dataset_name in uploaded_datasets_names:
        try:
            dataset = load_dataset(dataset_name, n_rows=5)
            dataset_columns = set(return_dataset_columns(dataset))

            # If it contains the columns in expectations, it is compatible
            if columns.issubset(dataset_columns):
                compatible_datasets_and_columns[dataset_name] = list(dataset_columns)
        except PermissionError:
            continue
    return compatible_datasets_and_columns


def build_test_dataset(original_dataset_name: str) -> os.path:
    """
    Creates new dataset with only 5 rows in order to accelerate some
    checks that have to be done in the app.
    :param original_dataset_name: String with the name of the dataset
    that has to be based on.
    :return: String with the path of the new short, temporary
    dataset.
    """
    test_dataset_name = get_test_dataset_name(original_dataset_name)
    test_dataset_path = get_dataset_path(test_dataset_name)
    if ends_in(".csv", original_dataset_name):
        test_dataset = load_dataset(original_dataset_name, n_rows=5).to_csv(index=False)
        write_file(test_dataset_path, test_dataset)
    else:
        load_dataset(original_dataset_name, n_rows=5).to_excel(
            test_dataset_path, index=False
        )
    return test_dataset_path


def import_dataset(dataset_name: str) -> (str, bool):
    """
    This function is used when importing a new dataset. It checks
    that the new uploaded file can be read by Pandas as a DataFrame.
    If it is not Pandas readable, it removes the dataset.
    :param dataset_name: String with the name of the imported
    dataset.
    :return: JSON file with a boolean that tells the app if the
    dataset has been successfully imported, and a boolean that
    manages warning pops.
    """
    uploaded_file_path = get_dataset_path(dataset_name)
    is_dataset_imported = True
    display_dataset_warning = False
    is_excel_format = False

    # If the file is not CSV dataset
    if not is_csv(uploaded_file_path):
        is_excel_format = is_xlsx(uploaded_file_path)

        # If the file is not XLSX dataset
        if not is_excel_format:
            remove_file(uploaded_file_path)

            # If the file has an incorrect XLSX dataset table
            is_dataset_imported = False
            if is_excel_format is not None:
                display_dataset_warning = True
    return to_json(is_dataset_imported), display_dataset_warning, is_excel_format


def dataset_to_dict(dataset: pd.DataFrame) -> dict:
    """
    Converts Pandas DataFrame to dictionary. Used to show dataset
    summary tables.
    :param dataset: Pandas DataFrame object.
    :return: Dict with the Pandas DataFrame converted to dictionary.
    """
    return dataset.to_dict("records")


def get_dataset_and_its_columns(dataset_name: str) -> (pd.DataFrame, list):
    """
    This function loads a CSV or XLSX file to Pandas DataFrame, as
    well as its columns in order to be shown in a dataset summary
    table.
    :param dataset_name: String with dataset name.
    :return: Pandas DataFrame and its columns in the form of objects
    for a dash_table component.
    """
    dataset = load_dataset(dataset_name, n_rows=5)
    columns = [{"name": column, "id": column} for column in dataset.columns.tolist()]
    return dataset, columns


def get_uploaded_datasets_paths() -> list:  #
    """
    Returns all uploaded dataset paths.
    :return: List with paths of all uploaded datasets.
    """
    dataset_names = get_uploaded_datasets_names()
    return [get_dataset_path(d) for d in dataset_names]


def is_dataset_already_imported(dataset_name: str) -> bool:  #
    """
    Checks if there is already an uploaded dataset with the same
    name.
    :param dataset_name: String with the name of the dataset that
    has to be uploaded next.
    :return: Bool that tells the app whether the dataset is already
    uploaded or not.
    """
    return dataset_name in get_uploaded_datasets_names()
