import os

from objects.expectation_suite_name import ExpectationSuiteName

from src.low_level_operations import ends_with


def create_empty_ge_expectation_suite(context, name: ExpectationSuiteName):
    """
    Creates a new, empty GE Expectation Suite.

    :param context: Great Expectations' context object.
    :param name: ExpectationSuiteName object defining the name.

    :return: GE's Expectation Suite object.
    """
    return context.create_expectation_suite(name.ge_name, overwrite_existing=True)


def get_expectation_suite(context, name: ExpectationSuiteName):
    """
    Loads GE's Expectation Suite object from file.

    :param context: GE's context object.
    :param name: ExpectationSuiteName object.

    :return: GE's Expectation Suite object.
    """
    return context.get_expectation_suite(name.ge_name)


def add_expectations_to_ge_expectation_suite(
    expectation_suite, expectations: list
) -> None:
    """
    Opens GE's Expectation Suite object from the ExpectationSuiteName object, then adds
    the given expectations to it.

    :param expectation_suite: GE's Expectation Suite object.
    :param expectations: List of new expectations to be added.
    """
    expectation_suite.expectations = expectations


def create_ge_expectation_suite(context, name: ExpectationSuiteName, expectations: list):
    """
    Creates a GE Expectation Suite with all its expectations.

    :param context: GE's context object.
    :param name: ExpectationSuiteName object.
    :param expectations: List of expectations.

    :return: GE's Expectation Suite object.
    """
    expectation_suite = create_empty_ge_expectation_suite(context, name)
    add_expectations_to_ge_expectation_suite(expectation_suite, expectations)
    return expectation_suite


def get_expectation_suite_name_object(name: str) -> ExpectationSuiteName:
    """
    Returns GE's Expectation Suite name object.

    :param name: String with the name of the Expectation Suite.

    :return: Expectation Suite name object.
    """
    return ExpectationSuiteName(name)


def get_batch_kwargs(context, dataset_path: os.path) -> dict:
    """
    Returns batch kwargs based on Great Expectations' context, a path to the dataset file
    and the name of the dataset.

    :param context: GE object.
    :param dataset_path: String that contains the path to the file.

    :return: Dictionary that contains GE batch kwargs.
    """
    context.add_datasource("datasource", class_name="PandasDatasource")
    reader_method = "read_csv" if ends_with(".csv", dataset_path) else "read_excel"
    return {
        "data_asset_name": "Dataset",
        "datasource": "datasource",
        "path": dataset_path,
        "reader_method": reader_method,
    }


def get_ge_batch(context, expectation_suite: dict, dataset_path: os.path):
    """
    Returns data batch, loaded from Expectation Suite name and dataset path.

    :param context: GE object.
    :param expectation_suite: GE's Expectation Suite object.
    :param dataset_path: String with the path to the dataset that is used to create the
    batch.

    :return: GE's batch object.
    """
    batch_kwargs = get_batch_kwargs(context, dataset_path)
    batch = context.get_batch(batch_kwargs, expectation_suite)
    return batch
