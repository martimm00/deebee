import os
import shutil

from src.defaults import (
    LOCAL_SITE,
    UPLOAD_DIRECTORY_PATH,
    IMPORT_DIRECTORY_PATH,
    EXPECTATION_SUITE_DIR,
    SUPPORTED_DATASET_TYPES,
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


def ends_in(ending: str, string: str) -> bool:
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
    return any([ends_in("." + ending, name) for ending in SUPPORTED_DATASET_TYPES])


def get_uploaded_dataset_names() -> list:
    """
    Returns the names of all uploaded datasets from the upload path.

    :return: List with the names of all uploaded datasets.
    """
    upload_dir_path = get_import_dir_path()
    return [
        d for d in get_elements_inside_directory(upload_dir_path) if is_dataset_name(d)
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


def get_expectation_dir() -> os.path:
    """
    Returns the directory that contains all Expectation Suites.

    :return: Path.
    """
    return EXPECTATION_SUITE_DIR


def get_validation_dir() -> os.path:
    """
    Returns Great Expectations validation path. Used to look for Great Expectations docs
    HTML files.

    :return: Path.
    """
    return LOCAL_SITE


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
    shutil.move(origin, destination)


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

    :param path: String with a new path.
    """
    os.makedirs(path)
