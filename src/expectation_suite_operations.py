import os

from objects.expectation_suite_name import ExpectationSuiteName

from src.low_level_operations import ends_with


def create_ge_expectation_suite(context, name: ExpectationSuiteName) -> None:
    """
    Creates a new, empty GE Expectation Suite.

    :param context: Great Expectations' context object.
    :param name: ExpectationSuiteName object defining the name.
    """
    context.create_expectation_suite(name.ge_name, overwrite_existing=True)


def get_expectation_suite_name_object(name: str) -> ExpectationSuiteName:
    """
    Returns GE Expectation Suite name object.

    :param name: String with the name of the Expectation Suite.

    :return: Expectation Suite name object.
    """
    return ExpectationSuiteName(name)


def get_batch_kwargs(context, dataset_path: os.path) -> dict:
    """
    Returns batch kwargs based on great_expectations context, a path
    to the dataset file and the name of the dataset.
    :param context: great_expectations object.
    :param dataset_path: String that contains the path to the CSV or
    XLSX file.
    :return: Dict that contains great_expectations batch kwargs.
    """
    context.add_datasource("datasource", class_name="PandasDatasource")
    reader_method = "read_csv" if ends_with(".csv", dataset_path) else "read_excel"
    return {
        "data_asset_name": "Dataset",
        "datasource": "datasource",
        "path": dataset_path,
        "reader_method": reader_method,
    }


def load_batch_from_params(context, expectation_suite: dict, dataset_path: os.path):
    """
    Returns data batch, loaded from Expectation Suite name and
    dataset path.
    :param context: great_expectations object.
    :param expectation_suite: great_expectations Expectation Suite
    object.
    :param dataset_path: String with the path to the dataset that is
    used to create the batch.
    :return: great_expectations batch object.
    """
    batch_kwargs = get_batch_kwargs(context, dataset_path)
    batch = get_batch(context, batch_kwargs, expectation_suite)
    return batch


def get_batch(context, batch_kwargs: dict, expectation_suite: dict):
    """
    This function loads a great_expectations data batch from the app
    context, batch kwargs and Expectation Suite object.
    :param context: great_expectations object.
    :param batch_kwargs: Dict with all necessary batch kwargs.
    :param expectation_suite: great_expectations object.
    :return: great_expectations data batch object.
    """
    return context.get_batch(batch_kwargs, expectation_suite)
