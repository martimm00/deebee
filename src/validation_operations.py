import os
import pandas as pd
from great_expectations.checkpoint import LegacyCheckpoint

from constants.defaults import EMPTY_STRING
from constants.great_expectations_constants import OUTDATED
from constants.path_constants import EXPECTATION_SUITES_PATH

from src.json_operations import from_json
from src.objects import ExpectationSuiteName
from src.json_operations import read_json, to_json
from src.utils import get_value, read_dataset, is_list_empty
from src.front_end_operations import get_list_group_item_elements, build_list_group_item
from src.expectation_parameters import (
    requires_parameters,
    get_number_of_arguments_required,
)
from src.expectation_operations import (
    read_expectation_and_columns_from_expectation_suite,
)
from src.expectation_suite_operations import (
    list_expectation_suites,
    get_expectation_suite_name_object,
    get_expectation_suite,
)
from src.batch_operations import (
    get_batch_kwargs,
    get_batch,
    load_batch_from_params,
    get_batch_expectation_functions,
)
from src.low_level_operations import (
    delete_file,
    write_file,
    get_file_name,
    get_validations_path,
    get_directory_path,
    get_directory_name,
    join_paths,
    delete_directory,
    change_extension,
    get_expectation_suite_folder,
    get_great_expectations_validations_folder,
    get_elements_inside_directory,
    get_validations_folder_directory,
    exists_path,
    get_to_the_validation_file,
    get_dataset_path,
)


def apply_expectation_suite(
    context, selected_datasets: list, selected_expectation_suites: list, validate: int
):
    """
    Used to apply Expectation Suite to an available dataset.
    :param context: great_expectations context object.
    :param validate: Int with its number of clicks.
    :param selected_expectation_suites: List that contains currently
    selected Expectation Suites.
    :param selected_datasets: List that contains currently selected
    datasets.
    :return: Whether a warning has to be displayed, its message and a
    JSON file that tells the app there is a new dataset validation.
    """
    # If validate button has been clicked at least once
    if validate:
        return apply_expectation_suite_to_dataset(
            context,
            selected_datasets,
            selected_expectation_suites,
        )
    return False, defaults.WARNING_MESSAGES["empty_message"], to_json({})


def remove_tmp_validation_file(exporting: str) -> None:
    """
    This function helps to remove temporary created validation file
    once it is successfully exported.
    :param exporting: JSON file that tells the function whether the
    app is exporting a validation result or not.
    """
    if exporting != "true":
        path = from_json(exporting)
        if path:
            delete_file(path)


def build_tmp_validation_file(file_path: os.path) -> os.path:
    """
    Builds temporary validation file so that it can be exported with
    a proper name.
    :param file_path: String with the path to the original validation
    file.
    :return: String with the path to the new temporary validation
    file.
    """
    validation_result = load_validation_result(file_path)
    tmp_file_path = build_tmp_validation_file_path_from_result(
        file_path, validation_result
    )
    write_file(tmp_file_path, to_json(validation_result))
    return tmp_file_path


def build_tmp_validation_file_path_from_result(
    file_path: os.path, validation_result: dict
) -> os.path:
    """
    Builds temporary validation file path from original validation
    result JSON file path.
    :param file_path: String with original validation file path.
    :param validation_result: Dict with validation result.
    :return: String with temporary validation file path.
    """
    dataset_name, expectation_suite_name = get_elements_for_tmp_file_name(
        validation_result
    )
    tmp_file_name = build_tmp_validation_file_name(expectation_suite_name, dataset_name)
    tmp_file_path = join_paths(get_directory_path(file_path), tmp_file_name)
    return tmp_file_path


def get_elements_for_tmp_file_name(validation_result: dict) -> (str, str):
    """
    Returns the name of the Expectation Suite name used to validate
    the dataset, as well as the dataset name from validated dataset
    path.
    :param validation_result: Dict with validation result.
    :return: Two strings, one containing dataset name and the other
    containing Expectation Suite name.
    """
    expectation_suite_name = get_validation_expectation_suite_name(validation_result)
    dataset_path = get_validated_dataset_path(validation_result)
    dataset_name = get_file_name(dataset_path).split(".")[0]
    return dataset_name, expectation_suite_name


def build_tmp_validation_file_name(
    expectation_suite_name: str, dataset_name: str
) -> str:
    """
    Builds temporary validation file name in order to export a file
    with a name that has sense.
    :param expectation_suite_name: String with Expectation Suite
    name.
    :param dataset_name: String with validated dataset name.
    :return: String with full file name.
    """
    return expectation_suite_name + " over " + dataset_name + ".json"


def get_validation_result_info(validation_result: dict) -> (str, str, str):
    """
    Returns some validation result information, such as dataset name,
    timestamp and success.
    :param validation_result: Dict that contains all validation
    result details.
    :return: String with the dataset name, string with validation
    timestamp and string with success.
    """
    filename = get_file_name(get_validated_dataset_path(validation_result))
    date = get_validation_timestamp(validation_result)
    success = is_validation_successful(validation_result)
    return filename, date, success


def get_validation_result_json_path(validation_html: str) -> str:
    """
    Returns validation result JSON file from List Group Item href
    (great_expectations HTML file).
    :param validation_html: String with path to great_expectations
    HTML validation result file.
    :return: String with the path to the validation result JSON file.
    """
    validations_folder = get_validations_path()

    # Getting validation result file to be exported
    expectation_suite_folder = EXPECTATION_SUITES_PATH  # EXPECTATION_SUITE_NAME_DIR
    expectation_suite_name = get_directory_name(
        get_directory_path(get_directory_path(get_directory_path(validation_html)))
    )
    file_name = change_extension(get_file_name(validation_html), "json")
    dataset_path = get_directory_name(get_directory_path(validation_html))
    validation_json_path = build_path_to_validation_file(
        validations_folder,
        expectation_suite_folder,
        expectation_suite_name,
        dataset_path,
        file_name,
    )
    return validation_json_path


def build_path_to_validation_file(
    validations_folder: os.path,
    expectation_suite_folder: os.path,
    expectation_suite_name: os.path,
    dataset_path: os.path,
    file_name: str,
) -> os.path:
    """
    As its name suggests, this function builds the path to a
    validation file allocated at validation_results directory.
    :param validations_folder: String with the path to this folder.
    :param expectation_suite_folder: String with the path to this
    folder.
    :param expectation_suite_name: String with the path to this
    folder.
    :param dataset_path: String with the path to this folder.
    :param file_name: String with the path to this file.
    :return: String with path to validation file.
    """
    return os.path.join(
        *[
            validations_folder,
            expectation_suite_folder,
            expectation_suite_name,
            dataset_path,
            dataset_path,
            file_name,
        ]
    )


def remove_validation(href: str) -> None:
    """
    Removes a validation from both the interface and the file system,
    based on a given href.
    :param href: String that contains the path to HTML validation
    summary.
    """
    # Getting directories to be removed
    validation_html_path = get_directory_path(get_directory_path(href))
    expectation_suite_name = get_directory_name(
        get_directory_path(validation_html_path)
    )
    validation_json_path = get_validation_result_json_path(href)
    validation_json_path = get_directory_path(get_directory_path(validation_json_path))

    # Removing both directories
    remove_validation_file_and_docs(validation_html_path, validation_json_path)

    # Remove directories if they are left empty
    look_for_empty_validation_directories(expectation_suite_name)


def remove_validation_file_and_docs(
    validation_html: os.path, validation_json: os.path
) -> None:
    """
    Removes validation JSON and HTML files, which are allocated in
    different paths.
    :param validation_html: String with the path to the HTML
    validation summary.
    :param validation_json: String with the path to the JSON
    validation file.
    """
    try:
        delete_directory(validation_html)
        delete_directory(validation_json)
    except FileNotFoundError:
        pass


def look_for_empty_validation_directories(expectation_suite_name: str) -> None:
    """
    Looks for empty validation directories and removes them if they
    are left empty.
    :param expectation_suite_name: String with Expectation Suite
    name.
    """
    validations_folder = get_validations_path()
    expectation_suite_folder = get_expectation_suite_folder()
    validation_name_folder = join_paths(
        validations_folder, expectation_suite_folder
    )
    validation_extension_folder = join_paths(
        validation_name_folder, expectation_suite_name
    )
    validation_docs_folder = get_great_expectations_validations_folder()
    ge_validation_name_folder = join_paths(
        validation_docs_folder, expectation_suite_folder
    )
    ge_validation_extension_folder = join_paths(
        ge_validation_name_folder, expectation_suite_name
    )
    remove_empty_validation_folders(
        ge_validation_extension_folder,
        ge_validation_name_folder,
        validation_extension_folder,
        validation_name_folder,
    )


def remove_empty_validation_folders(
    ge_validation_extension_folder: os.path,
    ge_validation_name_folder: os.path,
    validation_extension_folder: os.path,
    validation_name_folder: os.path,
) -> None:
    """
    Removes validation folders if they are left empty.
    :param ge_validation_extension_folder: String with the path to
    HTML validation summary file.
    :param ge_validation_name_folder: String with the path to HTML
    validation summary folder.
    :param validation_extension_folder: String with the path to JSON
    validation file.
    :param validation_name_folder: String with the path to JSON
    validation folder.
    """
    try:
        if is_list_empty(get_elements_inside_directory(validation_extension_folder)):
            delete_directory(validation_extension_folder)
            delete_directory(ge_validation_extension_folder)
        if is_list_empty(get_elements_inside_directory(validation_name_folder)):
            delete_directory(validation_name_folder)
            delete_directory(ge_validation_name_folder)
    except FileNotFoundError:
        pass


def load_validation_result(validation_path: os.path) -> dict:
    """
    Loads validation result from JSON stored file.
    :param validation_path: String with the path to JSON validation
    file.
    :return: Dict with validation result.
    """
    with open(validation_path, "r") as vr:
        validation_result = read_json(vr)
    return validation_result


def get_validation_metadata(validation_result: dict) -> dict:
    """
    Returns validation metadata.
    :param validation_result: Dict that contains validation
    information.
    :return: Dict with validation metadata.
    """
    return validation_result["meta"]


def get_validated_dataset_path(validation_result: dict) -> str:
    """
    Returns validated dataset path.
    :param validation_result: Dict with validation result.
    :return: String that contains path to validated dataset.
    """
    validation_metadata = get_validation_metadata(validation_result)
    return validation_metadata["batch_kwargs"]["path"]


def get_validation_expectation_suite_name(validation_result: dict) -> str:
    """
    Returns the name of the Expectation Suite used to validate the
    dataset.
    :param validation_result: Dict with validation result.
    :return: String that contains Expectation Suite name.
    """
    validation_metadata = get_validation_metadata(validation_result)
    return validation_metadata["expectation_suite_name"].split(".")[-1]


def get_validation_timestamp(validation_result: dict) -> str:
    """
    Returns validation timestamp.
    :param validation_result: Dict with validation result.
    :return: String that contains validation timestamp.
    """
    validation_metadata = get_validation_metadata(validation_result)
    return validation_metadata["run_id"]["run_time"]


def is_validation_successful(validation_result: dict) -> str:
    """
    Returns validation success.
    :param validation_result: Dict with validation result.
    :return: String with validation success or failure.
    """
    return validation_result["success"]


def list_validations() -> list:
    """
    This function is used to list all available validations, and
    focuses on showing different name validations.
    :return: List with different validations that is going to be
    shown in the interface.
    """
    children = []
    expectation_suite_folder = get_expectation_suite_folder()
    expectation_suite_folder_directory = get_validations_folder_directory()
    if not exists_path(expectation_suite_folder_directory):
        return children
    validation_results_counter = 0
    append_different_extension_validations_loop(
        children,
        expectation_suite_folder,
        expectation_suite_folder_directory,
        validation_results_counter,
    )
    return children


def append_different_extension_validations_loop(
    children: list,
    expectation_suite_folder: str,
    expectation_suite_folder_directory: os.path,
    validation_results_counter: int,
) -> int:
    """
    This function is used to list all available validations, and
    focuses on showing different name validations.
    :param children: List of validations that are going to be shown
    in the interface.
    :param expectation_suite_folder: String with the name of the
    Expectation Suite without the extension.
    :param expectation_suite_folder_directory: String with the path
    to different extension validations.
    :param validation_results_counter: Integer with the amount of
    validations that were found.
    :return: Integer with the amount of validations that are found.
    """
    expectation_suites_names = os.listdir(expectation_suite_folder_directory)

    # For each expectation suite extension
    for expectation_suite_name in expectation_suites_names:
        outdated = EMPTY_STRING
        if expectation_suite_name not in list_expectation_suites():
            outdated = OUTDATED
        expectation_suites_extensions_directory = join_paths(
            expectation_suite_folder_directory, expectation_suite_name
        )
        validation_results_counter = append_different_dataset_validations_loop(
            children,
            expectation_suite_folder,
            expectation_suites_extensions_directory,
            expectation_suite_name,
            outdated,
            validation_results_counter,
        )
    return validation_results_counter


def append_different_dataset_validations_loop(
    children: list,
    expectation_suite_folder: str,
    expectation_suites_extensions_directory: str,
    expectation_suite_name: str,
    outdated: str,
    validation_results_counter: int,
) -> int:
    """
    This function is used to list all available validations, and
    focuses on showing different name validations.
    :param children: List of validations that are going to be shown
    in the interface.
    :param expectation_suite_folder: String with the name of the
    Expectation Suite without the extension.
    :param expectation_suites_extensions_directory: String with the
    path to different validation files.
    :param expectation_suite_name: String with the name of the
    Expectation Suite.
    :param outdated: String that tells whether the Expectation Suite
    used to validate is still valid and usable.
    :param validation_results_counter: Integer with the amount of
    validations that were found.
    :return: Integer with the amount of validations that are found.
    """
    datasets_validations = os.listdir(expectation_suites_extensions_directory)

    # For each validated dataset
    for dataset in datasets_validations:
        tree_validation_path = join_paths(
            expectation_suites_extensions_directory, dataset
        )

        # To finally get to the validation file
        tree_validation_path = get_to_the_validation_file(tree_validation_path)
        validation_result = load_validation_result(tree_validation_path)

        filename, date, success = get_validation_result_info(validation_result)

        # Mandatory elements to build validation list group item
        (
            color,
            href,
            list_group_item_id,
            suite_and_file_names,
        ) = get_list_group_item_elements(
            dataset,
            date,
            expectation_suite_folder,
            expectation_suite_name,
            filename,
            outdated,
            success,
            tree_validation_path,
            validation_results_counter,
        )

        validation_results_counter += 1
        children.append(
            build_list_group_item(list_group_item_id, suite_and_file_names, color, href)
        )
    return validation_results_counter


def apply_expectation_suite_to_dataset(
    context,
    selected_datasets: list,
    selected_expectation_suites: list,
) -> (bool, str, list):
    """
    This function applies an Expectation Suite to a dataset.
    :param context: great_expectations object.
    :param selected_datasets: List with all selected datasets.
    :param selected_expectation_suites: List with all selected
    expectation suites.
    :return: Boolean that manages if a warning displays or not, a
    string with its message and a JSON file with the data of a new
    dataset.
    """
    error_message = check_if_one_expectation_suite_and_one_dataset_are_selected(
        selected_expectation_suites, selected_datasets
    )
    if error_message:
        return True, error_message, to_json({})

    # Getting expectation suite and dataset names
    expectation_suite_name = get_value(selected_expectation_suites)
    expectation_suite_name_object = get_expectation_suite_name_object(
        expectation_suite_name
    )
    dataset_name = get_value(selected_datasets)

    # Loading required content
    dataset_path = get_dataset_path(dataset_name)
    expectation_suite = get_expectation_suite(context, expectation_suite_name_object)
    expectation_and_columns = read_expectation_and_columns_from_expectation_suite(
        expectation_suite
    )
    dataset = read_dataset(dataset_name, n_rows=5)
    error_message = check_dataset_compatibility(dataset, expectation_and_columns)
    if error_message:
        return True, error_message, to_json({})
    batch_kwargs = get_batch_kwargs(context, dataset_path)
    batch = get_batch(context, batch_kwargs, expectation_suite)

    # Computing results
    error_message = compute_results(
        get_batch_expectation_functions(batch), expectation_and_columns, batch
    )
    if error_message:
        return True, error_message, to_json({})

    # Storing validation
    store_validation(
        context,
        expectation_suite_name_object,
        batch_kwargs,
    )
    return False, error_message, to_json(True)


def check_dataset_compatibility(
    dataset: pd.DataFrame, expectation_and_columns: dict
) -> str:
    """
    This function checks if a dataset is compatible with previously
    defined expectations in an Expectation Suite.
    :param dataset: Pandas DataFrame that has to be checked.
    :param expectation_and_columns: Dictionary that contains all
    currently defined expectations, the columns where they have to be
    applied and their params (if any).
    :return: String with the message that has to be displayed in a
    warning. If it returns an empty string, then it means no warning
    has to be popped.
    """
    message = defaults.WARNING_MESSAGES["empty_message"]
    dataset_columns = set(list(dataset.columns))
    expectations_columns = []
    for expectation_name in expectation_and_columns:
        expectations_columns += list(expectation_and_columns[expectation_name].keys())
    expectations_columns = set(expectations_columns)
    if not expectations_columns.issubset(dataset_columns):
        message = defaults.WARNING_MESSAGES["validation_warning"][
            "dataset_not_compatible"
        ]
    return message


def check_if_one_expectation_suite_and_one_dataset_are_selected(
    selected_expectation_suites: list, selected_datasets: list
) -> str:
    """
    Returns warning messages when not only one dataset and one
    Expectation Suite are selected.
    :param selected_expectation_suites: List with selected
    expectation suites.
    :param selected_datasets: List with selected datasets.
    :return: String with respective warning message, or an empty
    string if no warning has to be popped.
    """
    message = defaults.WARNING_MESSAGES["empty_message"]
    if not selected_expectation_suites:
        message = defaults.WARNING_MESSAGES["validation_warning"][
            "select_expectation_suite_and_file"
        ]
    elif len(selected_expectation_suites) != 1:
        message = defaults.WARNING_MESSAGES["validation_warning"][
            "only_one_expectation_suite"
        ]
    elif not selected_datasets:
        message = defaults.WARNING_MESSAGES["validation_warning"]["select_a_dataset"]
    elif len(selected_datasets) != 1:
        message = defaults.WARNING_MESSAGES["validation_warning"][
            "select_only_one_dataset"
        ]
    return message


def compute_results_from_expectation_suite_and_dataset(
    context,
    expectation_and_columns: dict,
    expectation_suite_name: str,
    test_dataset_path: str,
) -> str:
    """
    Computes result of applying an Expectation Suite to a dataset
    with the Expectation Suite name, its expectations and dataset
    path.
    :param context: great_expectations context object.
    :param expectation_and_columns: Dict with expectations, the
    columns where they have to be applied and parameters, if any.
    :param expectation_suite_name: String with Expectation Suite
    name.
    :param test_dataset_path: String that contains the path to the
    dataset that is going to be validated.
    :return: String with an warning message.
    """
    expectation_suite_name_object = get_expectation_suite_name_object(
        expectation_suite_name
    )
    expectation_suite = get_expectation_suite(context, expectation_suite_name_object)
    batch = load_batch_from_params(context, expectation_suite, test_dataset_path)
    expectations_ids = get_batch_expectation_functions(batch)

    # Computing results
    error_message = compute_results(expectations_ids, expectation_and_columns, batch)
    return error_message


def compute_results(
    expectations_ids: dict, expectation_and_columns: dict, batch
) -> (bool, str):
    """
    This function is used to compute validation results when applying
    an Expectation Suite to a dataset.
    :param expectations_ids: String with great_expectations
    expectation names.
    :param expectation_and_columns: Dictionary that contains all
    currently defined expectations, the columns where they have to
    be applied and their params (if any).
    :param batch: great_expectations data batch object.
    :return: String with warning message.
    """
    error_message = compute_results_by_expectation_type(
        expectation_and_columns, expectations_ids
    )
    if error_message:
        return error_message

    # Saving Expectation Suite to JSON file
    batch.save_expectation_suite(discard_failed_expectations=False)
    return error_message


def compute_results_by_expectation_type(
    expectation_and_columns: dict, expectations_ids: dict
) -> str:
    """
    This function is used to compute validation results when applying
    an Expectation Suite to a dataset, by expectation type.
    :param expectation_and_columns: Dictionary that contains all
    currently defined expectations, the columns where they have to
    be applied and their params (if any).
    :param expectations_ids: String with great_expectations
    expectation names.
    :return: String with warning message.
    """
    error_message = defaults.WARNING_MESSAGES["empty_message"]
    for expectation_name in expectation_and_columns:
        error_message = compute_result_for_each_expectation(
            expectation_and_columns[expectation_name],
            expectation_name,
            expectations_ids,
        )
        if error_message:
            return error_message
    return error_message


def compute_result_for_each_expectation(
    expectation_type_dict: dict,
    expectation_name: str,
    expectations_ids: dict,
) -> str:
    """
    This function is used to compute validation results when applying
    an Expectation Suite to a dataset, one expectation at a time.
    :param expectation_type_dict: Dictionary that contains all
    currently defined expectations, the columns where they have to be
    applied and their params (if any).
    :param expectation_name: String with expectation name.
    :param expectations_ids: String with great_expectations
    expectation names.
    :return: String with warning message.
    """
    message = defaults.WARNING_MESSAGES["empty_message"]
    for column in expectation_type_dict:
        parameters = expectation_type_dict[column]
        try:
            if requires_parameters(expectation_name):
                if get_number_of_arguments_required(expectation_name) == 1:
                    expectations_ids[expectation_name](column, parameters)
                elif get_number_of_arguments_required(expectation_name) == 2:
                    value1, value2 = parameters
                    expectations_ids[expectation_name](column, value1, value2)
            else:
                expectations_ids[expectation_name](column)
        except:
            message = defaults.WARNING_MESSAGES["validation_warning"][
                "wrong_expectations"
            ]
    return message


def store_validation(
    context,
    expectation_suite_name: ExpectationSuiteName,
    batch_kwargs: dict,
):
    """
    This function is used to store the validation as a file.
    :param context: great_expectations context object.
    :param expectation_suite_name: ExpectationSuiteName object.
    :param batch_kwargs: Dict with batch_kwargs.
    :return: great_expectations ValidationResultIdentifier object.
    This output is not actually not being used by the app for now.
    """
    results = LegacyCheckpoint(
        name="_temp_checkpoint",
        data_context=context,
        batches=[
            {
                "batch_kwargs": batch_kwargs,
                "expectation_suite_names": [expectation_suite_name.ge_name],
            }
        ],
    ).run()
    validation_result_identifier = results.list_validation_result_identifiers()[0]
    return validation_result_identifier
