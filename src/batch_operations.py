import os

from src.low_level_operations import ends_with


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
