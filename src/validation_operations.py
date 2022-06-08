import json

from objects.expectation_suite_name import ExpectationSuiteName

from constants.expectation_set_constants import PARAMETERS, EXPECTATIONS, EXPECTATION_NAME

from src.batch_operations import get_ge_batch
from src.expectation_suite_operations import create_empty_ge_expectation_suite
from src.low_level_operations import get_imported_dataset_path, get_expectation_set_path


def apply_expectation_to_dataset(
    batch, column_name: str, expectation_config: dict
) -> None:
    """
    Applies individual expectations to the batch.

    :param batch: GE's batch object.
    :param column_name: String with the name of the column where the expectation has to
    be applied.
    :param expectation_config: Dictionary that provides configuration for the expectation
    itself, that comes in the format of expectation set configuration.
    """
    expectation_id = expectation_config.get(EXPECTATION_NAME)
    parameters = expectation_config.get(PARAMETERS)
    parameters["column"] = column_name

    getattr(batch, expectation_id)(**parameters)


def validate_dataset(context, dataset_name: str, expectation_set_name: str) -> None:
    """
    This function is used to compute validation results when applying an Expectation
    Suite to a dataset.

    :param context: GE's context object.
    :param dataset_name: String with the name of the dataset to be validated.
    :param expectation_set_name: Expectation set name.
    """
    dataset_path = get_imported_dataset_path(dataset_name)

    expectation_set_path = get_expectation_set_path(expectation_set_name)
    with open(expectation_set_path, "r") as fp:
        config = json.load(fp)
    expectations_from_set_config = config.get(EXPECTATIONS)

    expectation_suite = create_empty_ge_expectation_suite(
        context, ExpectationSuiteName(expectation_set_name)
    )
    batch = get_ge_batch(context, expectation_suite, dataset_path)

    for column_name in expectations_from_set_config:
        for expectation_config in expectations_from_set_config.get(column_name):
            apply_expectation_to_dataset(batch, column_name, expectation_config)

    # Saving Expectation Suite to JSON file
    batch.save_expectation_suite(discard_failed_expectations=False)
