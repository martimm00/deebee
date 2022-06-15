from constants.supported_constants import SUPPORTED_DATASET_TYPES

from src.low_level_operations import (
    ends_with,
    delete_file,
    get_import_dir_path,
    get_imported_dataset_path,
    get_elements_inside_directory
)


def dataset_can_be_imported(dataset_name: str) -> bool:
    """
    Returns if a dataset can be imported or not.

    :param dataset_name: String with the name of the dataset.

    :return: Bool
    """
    return not dataset_name_is_already_in_use(dataset_name)


def is_dataset_name(name: str) -> bool:
    """
    Returns whether the name belongs to a potential dataset or not.

    :param name: String to be checked.

    :return: Bool.
    """
    return any([ends_with("." + ending, name) for ending in SUPPORTED_DATASET_TYPES])


def get_imported_dataset_names() -> list:
    """
    Returns the names of all uploaded datasets from the upload path.

    :return: List with the names of all uploaded datasets.
    """
    upload_dir_path = get_import_dir_path()
    return [
        d for d in get_elements_inside_directory(upload_dir_path) if is_dataset_name(d)
    ]


def delete_datasets(datasets_to_delete: list) -> None:
    """
    Deletes the selected datasets and updates available options in the checklist.

    :param datasets_to_delete: List with components to be deleted.

    :return: List with updated available options in the checklist.
    """
    for dataset_name in datasets_to_delete:

        # Getting the dataset path and removing it from disk
        dataset_path = get_imported_dataset_path(dataset_name)
        delete_file(dataset_path)


def dataset_name_is_already_in_use(dataset_name: str) -> bool:
    """
    Returns if the name of a recently imported dataset is already in use.

    :param dataset_name: String with the name of the dataset.

    :return: Bool.
    """
    return dataset_name in get_imported_dataset_names()


def is_new_dataset_name_valid(current_names: list, name: str) -> bool or None:
    """
    Returns if the new name for a dataset is valid.

    :param current_names: List with current names.
    :param name: String with the new name.

    :return: Bool.
    """
    if len(name.split(".")) == 2:
        name_without_extension, _ = name.split(".")
        if name_without_extension:
            if is_dataset_name(name):

                # If the name is not already in use for other datasets
                return name not in current_names
