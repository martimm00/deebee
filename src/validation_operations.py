import os
from great_expectations.checkpoint import LegacyCheckpoint

from objects.expectation_suite_name import ExpectationSuiteName

from constants.path_constants import GE_VALIDATIONS_PATH, VALIDATION_RESULTS_PATH
from constants.great_expectations_constants import (
    MOSTLY,
    COLUMN,
    COLUMN_A,
    COLUMN_B,
    COLUMN_LIST,
    BATCH_KWARGS,
    EXPECTATION_SUITE_NAMES,
    MULTICOLUMN_EXPECTATIONS_N_COLUMNS
)
from constants.expectation_set_constants import (
    PARAMETERS,
    EXPECTATIONS,
    EXPECTATION_NAME,
    MULTICOLUMN_CONFIG_SEPARATOR
)

from src.dataset_operations import read_dataset
from src.utils import get_value, infer_csv_separator
from src.batch_operations import get_ge_batch, get_batch_kwargs
from src.expectation_set_operations import get_expectation_set_config
from src.expectation_suite_operations import create_empty_ge_expectation_suite
from src.low_level_operations import (
    move,
    rename,
    join_paths,
    is_directory,
    delete_directory,
    get_imported_dataset_path,
    get_elements_inside_directory
)


def is_dataset_compatible(
    dataset_path: os.path, expectations_from_set_config: dict
) -> bool:
    """
    This function checks if a dataset is compatible with previously defined expectations
    in an Expectation Suite.

    :param dataset_path: Dataset path.
    :param expectations_from_set_config: Dictionary that contains all currently defined
    expectations, the columns where they have to be applied and their params (if any).

    :return: String with the message that has to be displayed in a warning. If it returns
    an empty string, then it means no warning has to be popped.
    """
    separator = infer_csv_separator(dataset_path)
    dataset = read_dataset(dataset_path, sep=separator, n_rows=2)
    dataset_columns = set(dataset.columns)
    columns_with_expectations = list()
    for column_name in expectations_from_set_config.keys():
        columns_with_expectations += column_name.split(MULTICOLUMN_CONFIG_SEPARATOR)
    columns_with_expectations = set(columns_with_expectations)

    return columns_with_expectations.issubset(dataset_columns)


def save_validation(
        context,
        expectation_name_object: ExpectationSuiteName,
        batch_kwargs: dict,
):
    """
    This function is used to save the validation as a file.

    :param context: GE's context object.
    :param expectation_name_object: ExpectationSuiteName object.
    :param batch_kwargs: Dictionary with batch_kwargs.

    :return: GE's ValidationResultIdentifier object.
    """
    results = LegacyCheckpoint(
        name="_temp_checkpoint",
        data_context=context,
        batches=[
            {
                BATCH_KWARGS: batch_kwargs,
                EXPECTATION_SUITE_NAMES: [expectation_name_object.name],
            }
        ],
    ).run()
    validation_result_identifier = results.list_validation_result_identifiers()[0]
    return validation_result_identifier


def apply_expectation_to_dataset(
    batch, column_name: str, expectation_config: dict, confidence: int
) -> None:
    """
    Applies individual expectations to the batch.

    :param batch: GE's batch object.
    :param column_name: String with the name of the column where the expectation has to
    be applied.
    :param expectation_config: Dictionary that provides configuration for the expectation
    itself, that comes in the format of expectation set configuration.
    :param confidence: Integer with confidence ranging from 0 to 100.
    """
    expectation_id = expectation_config.get(EXPECTATION_NAME)

    parameters = expectation_config.get(PARAMETERS)
    parameters[MOSTLY] = confidence / 100

    if expectation_id not in MULTICOLUMN_EXPECTATIONS_N_COLUMNS:
        parameters[COLUMN] = column_name
    elif MULTICOLUMN_EXPECTATIONS_N_COLUMNS[expectation_id] == 2:
        parameters[COLUMN_A], parameters[COLUMN_B] = column_name.split(MULTICOLUMN_CONFIG_SEPARATOR)
    else:
        parameters[COLUMN_LIST] = column_name.split(MULTICOLUMN_CONFIG_SEPARATOR)

    getattr(batch, expectation_id)(**parameters)


def validate_dataset(
    context,
    dataset_name: str,
    expectation_name_object: ExpectationSuiteName,
    confidence: int
) -> None:
    """
    This function is used to compute validation results when applying an Expectation
    Suite to a dataset.

    :param context: GE's context object.
    :param dataset_name: String with the name of the dataset to be validated.
    :param expectation_name_object: Expectation set name.
    :param confidence: Integer with confidence ranging from 0 to 100.
    """
    dataset_path = get_imported_dataset_path(dataset_name)

    config = get_expectation_set_config(expectation_name_object.name)
    expectations_from_set_config = config.get(EXPECTATIONS)

    # If the selected dataset is compatible with the selected set of expectations
    if is_dataset_compatible(dataset_path, expectations_from_set_config):
        expectation_suite = create_empty_ge_expectation_suite(
            context, expectation_name_object
        )
        batch = get_ge_batch(context, expectation_suite, dataset_path)

        for column_name in expectations_from_set_config:
            for expectation_config in expectations_from_set_config.get(column_name):
                apply_expectation_to_dataset(
                    batch, column_name, expectation_config, confidence
                )

        # Saving Expectation Suite to JSON file
        batch.save_expectation_suite(discard_failed_expectations=False)

        batch_kwargs = get_batch_kwargs(context, dataset_path)
        save_validation(context, expectation_name_object, batch_kwargs)


def build_new_validation_file_name(
        set_name: str, dataset_name: str, confidence: str
) -> str:
    """
    Builds new name for validation file.

    :param set_name: String with expectation set name.
    :param dataset_name: String with dataset name.
    :param confidence: Numeric string representing the confidence.

    :return: String with new name for validation file.
    """
    return set_name + "_" + ".".join(
        dataset_name.split(".")[:-1]) + "_" + confidence + ".html"


def move_validation_to_app_system(dataset_name: str, confidence: str) -> None:
    """
    Changes the name of the last validation, then moves it to the app's file system.

    :param dataset_name: String with dataset name.
    :param confidence: Numeric string that represents the confidence in the
    validation results.
    """
    # Getting all elements inside GE's validation directory
    available_elements = get_elements_inside_directory(GE_VALIDATIONS_PATH)
    for set_name in available_elements:

        # Getting to validation
        set_element_path = join_paths(GE_VALIDATIONS_PATH, set_name)
        if is_directory(set_element_path):
            elements_inside = get_elements_inside_directory(set_element_path)
            unique_name = get_value(elements_inside)
            validation_path = os.path.join(
                *[set_element_path, unique_name, unique_name]
            )
            validation_file_name = get_value(
                get_elements_inside_directory(validation_path)
            )

            # Renaming it
            new_validation_file_name = build_new_validation_file_name(
                set_name, dataset_name, confidence
            )
            rename(validation_path, validation_file_name, new_validation_file_name)
            validation_file_path = join_paths(
                validation_path, new_validation_file_name
            )
            new_validation_file_path = join_paths(
                VALIDATION_RESULTS_PATH, new_validation_file_name
            )

            # Moving it
            move(validation_file_path, new_validation_file_path)

            # Deleting old directories
            delete_directory(set_element_path)
