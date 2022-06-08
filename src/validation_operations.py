import json
import pandas as pd
from great_expectations.checkpoint import LegacyCheckpoint

from objects.expectation_suite_name import ExpectationSuiteName

from constants.great_expectations_constants import BATCH_KWARGS, EXPECTATION_SUITE_NAMES
from constants.expectation_set_constants import (
    PARAMETERS,
    EXPECTATIONS,
    EXPECTATION_NAME
)

from src.low_level_operations import get_imported_dataset_path
from src.batch_operations import get_ge_batch, get_batch_kwargs
from src.expectation_suite_operations import create_empty_ge_expectation_suite


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
    parameters["column"] = column_name
    parameters["mostly"] = confidence/100

    getattr(batch, expectation_id)(**parameters)


def check_dataset_compatibility(
    dataset: pd.DataFrame, expectation_and_columns: dict
) -> bool:
    """
    This function checks if a dataset is compatible with previously defined expectations
    in an Expectation Suite.

    :param dataset: Pandas DataFrame that has to be checked.
    :param expectation_and_columns: Dictionary that contains all currently defined
    expectations, the columns where they have to be applied and their params (if any).

    :return: String with the message that has to be displayed in a warning. If it returns
    an empty string, then it means no warning has to be popped.
    """
    dataset_columns = set(list(dataset.columns))
    expectations_columns = list()

    for expectation_name in expectation_and_columns:
        expectations_columns += list(expectation_and_columns[expectation_name].keys())
    expectations_columns = set(expectations_columns)

    return expectations_columns.issubset(dataset_columns)


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


def validate_dataset(
    context,
    dataset_name: str,
    expectation_name_object: ExpectationSuiteName,
    confidence=100
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

    with open(expectation_name_object.set_path, "r") as fp:
        config = json.load(fp)
    expectations_from_set_config = config.get(EXPECTATIONS)

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
