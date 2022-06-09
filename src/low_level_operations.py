import os
import shutil

from constants.supported_constants import SUPPORTED_DATASET_TYPES
from constants.path_constants import (
    PROFILE_REPORTS_PATH,
    UPLOAD_DIRECTORY_PATH,
    IMPORT_DIRECTORY_PATH,
    EXPECTATION_SETS_PATH,
    EXPECTATION_SUITES_PATH,
    VALIDATION_RESULTS_PATH,
)


def join_paths(path1: os.path, path2: os.path) -> os.path:
    """
    Joins two given paths into one.

    :param path1: os.path.
    :param path2: os.path.

    :return: os.path object.
    """
    return os.path.join(path1, path2)


def has_extension(file_name: str) -> bool:
    """
    Returns if a file name contains an extension.

    :param file_name: String with the name of a file.

    :return: Bool.
    """
    if "." in file_name:
        name, extension = file_name.split(".")
        return name and extension
    return False


def ends_with(ending: str, string: str) -> bool:
    """
    This function returns if a given string ends in a certain ending or extension.

    :param ending: String with the ending to check.
    :param string: String with the text to be checked.

    :return: Bool.
    """
    ending_length = len(ending)
    return (
            string[-ending_length:] == ending.lower() or
            string[-ending_length:] == ending.upper()
    )


def get_absolute_path(directory: os.path) -> os.path:
    """
    Returns the absolute path of a directory.

    :param directory: Name of the directory in the form of a path.

    :return: Absolute path to the directory.
    """
    return os.path.abspath(directory)


def exists_path(path: os.path) -> bool:
    """
    Returns if a path exists or not.

    :param path: String with a path.

    :return: Bool that tells the app if the given path exists or not.
    """
    return os.path.exists(path)


def get_elements_inside_directory(directory: os.path) -> list:
    """
    Returns a list of the elements inside a directory.

    :param directory: Path.

    :return: List with all the elements inside the given directory.
    """
    try:
        return os.listdir(directory)
    except FileNotFoundError:
        return list()


def is_dataset_name(name: str) -> bool:
    """
    Returns whether the name belongs to a potential dataset or not.

    :param name: String to be checked.

    :return: Bool.
    """
    return any([ends_with("." + ending, name) for ending in SUPPORTED_DATASET_TYPES])


def is_profile_report_name(name: str) -> bool:
    """
    Returns whether the name belongs to a potential profile report or not.

    :param name: String to be checked.

    :return: Bool.
    """
    return ends_with(".html", name)


def is_csv_file_by_name(name: str) -> bool:
    """
    Returns whether the name belongs to a potential CSV file or not.

    :param name: String to be checked.

    :return: Bool.
    """
    return any([ends_with("." + ending, name) for ending in ["csv", "CSV"]])


def is_excel_file_by_name(name: str) -> bool:
    """
    Returns whether the name belongs to a potential Excel (XLSX) file or not.

    :param name: String to be checked.

    :return: Bool.
    """
    return any([ends_with("." + ending, name) for ending in ["xlsx", "XLSX"]])


def is_validation_name(name: str) -> bool:
    """
    Returns if the given name belongs to a validation file.

    :param name: String with a filename.

    :return: Bool.
    """
    return ends_with(".html", name)


def get_imported_dataset_names() -> list:
    """
    Returns the names of all uploaded datasets from the upload path.

    :return: List with the names of all uploaded datasets.
    """
    upload_dir_path = get_import_dir_path()
    return [
        d for d in get_elements_inside_directory(upload_dir_path) if is_dataset_name(d)
    ]


def get_validation_file_names() -> list:
    """
    Returns the names of all available validation files.

    :return: List with the names of all validation files.
    """
    validations_path = get_validations_path()
    return [
        n
        for n in get_elements_inside_directory(validations_path)
        if is_validation_name(n)
    ]


def is_directory(path: os.path) -> bool:
    """
    This function checks whether the given path belongs to a directory or not, by trying
    to list the elements inside it.

    :param path: Path.

    :return: Bool.
    """
    try:
        get_elements_inside_directory(path)
        return True
    except NotADirectoryError:
        pass
    except FileNotFoundError:
        pass
    return False


def get_import_dir_path() -> os.path:
    """
    Returns main app path.

    :return: Path
    """
    return IMPORT_DIRECTORY_PATH


def get_upload_dir_path() -> os.path:
    """
    Returns main app path.

    :return: Path
    """
    return UPLOAD_DIRECTORY_PATH


def get_profile_reports_path() -> os.path:
    """
    Returns the path where profile reports are allocated.

    :return: Path.
    """
    return PROFILE_REPORTS_PATH


def get_expectations_path() -> os.path:
    """
    Returns the directory that contains all Expectation Suites.

    :return: Path.
    """
    return EXPECTATION_SUITES_PATH


def get_expectation_sets_path() -> os.path:
    """
    Returns the directory that contains configuration for all Expectation Suites.

    :return: Path.
    """
    return EXPECTATION_SETS_PATH


def get_available_expectation_sets() -> list:
    """
    Returns a list with all the available expectation sets.

    :return: List with available expectation sets.
    """
    expectations_config_path = get_expectation_sets_path()
    return [f for f in os.listdir(expectations_config_path) if ".json" in f]


def get_expectation_set_path(expectation_set_name: str) -> os.path:
    """
    Returns the path of the config of the given expectation set.

    :return: Path.
    """
    extension = "" if ends_with(".json", expectation_set_name) else ".json"
    expectations_config_path = get_expectation_sets_path()
    return join_paths(expectations_config_path, expectation_set_name + extension)


def get_validations_path() -> os.path:
    """
    Returns Great Expectations' validation path. Used to look for Great Expectations docs
    HTML files.

    :return: Path.
    """
    return VALIDATION_RESULTS_PATH


def get_validation_path(name: str) -> os.path:
    """
    Returns the path of the given validation.

    :param name: String with validation name.

    :return: Path.
    """
    validations_path = get_validations_path()
    return join_paths(validations_path, name)


def get_imported_dataset_path(dataset_name: str) -> os.path:
    """
    This is used to get dataset path from its name.

    :param dataset_name: String with the name of the dataset.

    :return: Path.
    """
    import_dir_path = get_import_dir_path()
    return join_paths(import_dir_path, dataset_name)


def get_uploaded_dataset_path(dataset_name: str) -> os.path:
    """
    This is used to get dataset path from its name.

    :param dataset_name: String with the name of the dataset.

    :return: Path.
    """
    upload_dir_path = get_upload_dir_path()
    return join_paths(upload_dir_path, dataset_name)


def get_profile_report_title_from_dataset_name(dataset_name: str) -> str:
    """
    Returns the title of the profile report of a dataset, given the dataset name.

    :param dataset_name: The name of the dataset.

    :return: String with the title of the profile report for that dataset.
    """
    return dataset_name.replace(".", "_") + "_pr"


def get_profile_report_name_from_dataset_name(dataset_name: str) -> str:
    """
    Returns the name of the profile report file of a dataset, given the dataset name.

    :param dataset_name: The name of the dataset.

    :return: String with the name of the profile report file for that dataset.
    """
    title = get_profile_report_title_from_dataset_name(dataset_name)
    return title + ".html"


def get_profile_report_path(dataset_name: str) -> os.path:
    """
    Returns the path of the profile report of a dataset, given a dataset name.

    :param dataset_name: The name of the dataset.

    :return: String with the name of the
    """
    profile_reports_path = get_profile_reports_path()
    profile_report_file_name = get_profile_report_name_from_dataset_name(dataset_name)
    return join_paths(profile_reports_path, profile_report_file_name)


def is_profile_report_available(dataset_name: str) -> bool:
    """
    Returns if a profile report of the selected dataset has already been created or not.

    :param dataset_name: String with the name of the dataset to be checked.

    :return: Bool.
    """
    profile_reports_path = get_profile_reports_path()
    elements_in_directory = get_elements_inside_directory(profile_reports_path)
    profile_report_file_name = get_profile_report_name_from_dataset_name(dataset_name)
    return profile_report_file_name in elements_in_directory


def delete_directory(path: os.path, try_hard=False) -> None:
    """
    Deletes the specified directory, no matter if it is not empty.

    :param path: Path to the directory.
    :param try_hard: Bool that tells the function to delete the folder no matter what.
    When true, unexpected errors can be fired.
    """
    if not try_hard:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        return
    shutil.rmtree(path)


def delete_file(path: os.path, try_hard=False) -> None:
    """
    Deletes the specified file if it exists.

    :param path: File path.
    :param try_hard: Bool that tells the function to delete the file no matter what. When
    true, unexpected errors can be fired.
    """
    if not try_hard:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        return
    shutil.rmtree(path)


def write_file(path: os.path, content: str) -> None:
    """
    Writes string as a file onto a file system.

    :param path: Path where the files have to be written.
    :param content: String hat has to be written as a file.
    """
    with open(path, "w") as ftw:
        ftw.write(content)


def system_call(instruction: str) -> None:
    """
    Makes a terminal system call with an instruction, which is given as a string.

    :param instruction: String with the instruction
    """
    os.system(instruction)


def move(origin: os.path, destination: os.path) -> None:
    """
    Moves a directory or a file to a new name or new path.

    :param origin: Origin path.
    :param destination: Destination path.
    """
    try:
        shutil.move(origin, destination)
    except shutil.Error as m:
        print("ERROR:", m)


def rename(directory: os.path, old_name: str, new_name: str) -> None:
    """
    This function can be used to rename any basename element in a path file, such as
    directories or files. To change path, use move().

    :param directory: Path to the directory or file.
    :param old_name: String with its old name.
    :param new_name: String with its new name.
    """
    old_path = join_paths(directory, old_name)
    new_path = join_paths(directory, new_name)
    os.rename(old_path, new_path)


def make_dir(path: os.path) -> None:
    """
    Makes the directory specified in path argument.

    :param path: A new path.
    """
    os.makedirs(path)


def get_name_from_file_name(file_name: str) -> str:
    """
    Returns the name of the file given the whole filename, including the extension.

    :param file_name: String with the whole filename, including the extension.
    """
    return ".".join(file_name.split(".")[:-1])


def get_file_name_by_path(path: os.path) -> str:
    """
    Returns the name of a file based on its path.

    :param path: String

    :return: Path to be checked.
    """
    last_name = os.path.basename(path)
    return last_name if has_extension(last_name) else None
