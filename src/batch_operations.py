import os

from src.low_level_operations import ends_with


def get_batch_kwargs(context, dataset_path: os.path) -> dict:
    """
    Returns batch kwargs based on Great Expectations' context, a path to the dataset file
    and the name of the dataset.

    :param context: GE object.
    :param dataset_path: String that contains the path to the CSV or XLSX file.

    :return: Dict that contains GE batch kwargs.
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
    Returns data batch, loaded from Expectation Suite name and dataset path.

    :param context: Great Expectations object.
    :param expectation_suite: GE Expectation Suite object.
    :param dataset_path: String with the path to the dataset that is used to create the
    batch.

    :return: GE batch object.
    """
    batch_kwargs = get_batch_kwargs(context, dataset_path)
    batch = get_batch(context, batch_kwargs, expectation_suite)
    return batch


def get_batch(context, batch_kwargs: dict, expectation_suite: dict):
    """
    This function loads a Great Expectations data batch from the app context, batch
    kwargs and Expectation Suite object.

    :param context: GE object.
    :param batch_kwargs: Dict with all necessary batch kwargs.
    :param expectation_suite: GE object.

    :return: GE data batch object.
    """
    return context.get_batch(batch_kwargs, expectation_suite)


def get_batch_expectation_functions(batch, function_name: str) -> dict:
    """
    Used when creating or editing Expectation Suites, relates each Great Expectations
    internal expectation name to its respective batch function.

    :param batch: GE batch object, which contains the loaded dataset.
    :param function_name: String with the name of the method to be called.

    :return: Dictionary where the keys are strings with GE internal expectation names and
    the values are batch functions.
    return getattr(batch, function_name)
    """
    return {
        "expect_column_values_to_be_unique": batch.expect_column_values_to_be_unique,
        "expect_column_values_to_not_be_null": batch.expect_column_values_to_not_be_null,
        "expect_column_values_to_be_in_set": batch.expect_column_values_to_be_in_set,
        "expect_column_values_to_be_of_type": batch.expect_column_values_to_be_of_type,
        "expect_column_values_to_be_between": batch.expect_column_values_to_be_between,
        "expect_column_value_lengths_to_equal": batch.expect_column_value_lengths_to_equal,
    }
