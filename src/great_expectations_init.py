import os
import sys
import warnings
from yaml import load, dump, Loader
from great_expectations.cli import toolkit
from great_expectations.data_context import DataContext
from great_expectations.cli.pretty_printing import cli_message
from great_expectations.exceptions import DataContextError, DatasourceInitializationError

from src.low_level_operations import make_dir, exists_path, join_paths, get_absolute_path

from constants.path_constants import (
    DATA_DIRECTORY,
    IMPORT_DIRECTORY_PATH,
    GREAT_EXPECTATIONS_DIR,
    EXPECTATION_SUITES_DIR,
    VALIDATION_RESULTS_PATH,
    PATH_FOR_GE_STORES_CONFIG
)


def get_full_path_to_ge_dir(target_directory: os.path) -> os.path:
    """
    Returns the full path to Great Expectations directory.

    :param target_directory: Path to the directory where GE environment is deployed.

    :return: The absolute path to that directory.
    """
    return get_absolute_path(join_paths(target_directory, DataContext.GE_DIR))


def check_if_structure_exists(ge_dir: os.path) -> None:
    """
    This function tries to check if everything is correct in the Great Expectations' file
    system.

    :param ge_dir: Path containing GE directory that has to be checked for
    inconsistencies.
    """
    try:
        DataContext.does_config_exist_on_disk(ge_dir)
        DataContext.all_uncommitted_directories_exist(ge_dir)
        DataContext.config_variables_yml_exist(ge_dir)
    except (DataContextError, DatasourceInitializationError) as e:
        cli_message(f"<red>{e.message}</red>")
        sys.exit(1)


def try_to_create_structure_again(target_directory: os.path) -> None:
    """
    This function tries to create the whole Great Expectations file system again, in case
    it is not how it is meant to be.

    :param target_directory: Path to the directory where the file system has to be
    created.
    """
    try:
        DataContext.create(target_directory)
    except DataContextError as e:
        cli_message(f"<red>{e.message}</red>")
        sys.exit(5)


def check_for_inconsistencies(ge_dir: os.path, target_directory: os.path) -> None:
    """
    Checks whether everything in the file system is how it is meant to be or not. In case
    it is not, it tries to repair it or to create it again from scratch.

    :param ge_dir: Full path to GE directory.
    :param target_directory: Target directory to path.
    """
    message = (
        f"""Warning. An existing `{DataContext.GE_YML}` was found here: {ge_dir}."""
    )
    warnings.warn(message)
    check_if_structure_exists(ge_dir)
    try_to_create_structure_again(target_directory)


def change_storage_paths(target_directory: os.path) -> None:
    """
    This function loads Great Expectations' configuration yaml file to Python, modifies
    it and then writes it again. This provides an automatic change to GE's configuration.

    :param target_directory: Path to the target directory.
    """
    path_to_yaml = os.path.join(
        *[target_directory, GREAT_EXPECTATIONS_DIR, "great_expectations.yml"]
    )

    # Opening and reading the YML file
    with open(path_to_yaml, "r") as stream:
        yaml = load(stream, Loader=Loader)

    # Changing paths
    yaml["stores"]["validations_store"]["store_backend"][
        "base_directory"
    ] = PATH_FOR_GE_STORES_CONFIG

    # Writing back the updated YML to a file
    with open(path_to_yaml, "w") as stream:
        dump(yaml, stream)


def create_file_system(target_directory: os.path) -> None:
    """
    Creates a Great Expectations file system from scratch.

    :param target_directory: Path to the directory where the file system has to be
    created.
    """
    try:
        context = DataContext.create(target_directory)
        toolkit.send_usage_message(
            data_context=context, event="cli_init.create", success=True
        )
        change_storage_paths(target_directory)
    except DataContextError as e:
        cli_message(f"<red>{e.message}</red>")


def get_ge_file_system_ready(ge_dir: os.path, target_directory: os.path) -> None:
    """
    Repairs great_expectations file system or creates it again from scratch.

    :param ge_dir: Path to the GE file system.
    :param target_directory: Path where GE's file system is meant to be.
    """
    if DataContext.does_config_exist_on_disk(ge_dir):
        check_for_inconsistencies(ge_dir, target_directory)
    else:
        create_file_system(target_directory)
    if not exists_path(EXPECTATION_SUITES_DIR):
        make_dir(EXPECTATION_SUITES_DIR)
    if not exists_path(VALIDATION_RESULTS_PATH):
        make_dir(VALIDATION_RESULTS_PATH)


def initialize() -> None:
    """
    Initialize a new Great Expectations project. It scaffolds directories, sets up
    notebooks, creates a project file, and appends to a .gitignore file.
    """
    data_path = IMPORT_DIRECTORY_PATH
    toolkit.parse_cli_config_file_location(config_file_location=data_path)

    target_directory = get_absolute_path(DATA_DIRECTORY)
    ge_dir = get_full_path_to_ge_dir(target_directory)

    get_ge_file_system_ready(ge_dir, target_directory)
