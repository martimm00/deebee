import os
import logging
import warnings

from src.app import create_app
from src.great_expectations_init import initialize
from src.front_end_operations import open_in_browser
from src.low_level_operations import (
    move,
    make_dir,
    exists_path,
    system_call,
)
from constants.path_constants import (
    LOCALHOST,
    DATA_DIRECTORY,
    IMPORT_DIRECTORY_PATH,
    GREAT_EXPECTATIONS_DIR,
    GREAT_EXPECTATIONS_PATH,
    EXPECTATION_SUITES_DIR,
    VALIDATION_RESULTS_DIR,
)


def make_sure_dirs_exist() -> None:
    """
    Can create the three directories in case they do not exist.
    """
    data_path = DATA_DIRECTORY
    expectations_path = EXPECTATION_SUITES_DIR
    validations_path = VALIDATION_RESULTS_DIR
    imports_path = IMPORT_DIRECTORY_PATH

    # If the path does not exist, create it
    if not exists_path(data_path):
        make_dir(data_path)

    # If expectation directory does not exist, then create expectation and validation
    # directories
    if not exists_path(expectations_path):
        make_dir(expectations_path)
    if not exists_path(validations_path):
        make_dir(validations_path)
    if not exists_path(imports_path):
        make_dir(imports_path)


def repair_ge_file_system(path: os.path) -> None:
    """
    Changes the path of Great Expectations directory to repair the file system.

    :param path: The new path.
    """
    move("great_expectations", path)


def initialize_ge() -> None:
    """
    Initializes Great Expectations if the file system needs to be repaired or created
    from scratch.
    """
    # If Great Expectations' path exists, then repair it if needed
    if exists_path(GREAT_EXPECTATIONS_DIR):
        repair_ge_file_system(GREAT_EXPECTATIONS_PATH)

    # If it does not exist, or it has been removed, initialize it
    if not exists_path(GREAT_EXPECTATIONS_PATH):
        initialize()


def configure_logging() -> None:
    """
    Configures console logging so that only errors are displayed.
    """
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)


def configure_warnings() -> None:
    """
    Configures console warnings so that they are not displayed.
    """
    warnings.filterwarnings("ignore")


def display_welcome_message() -> None:
    """
    Shows welcome message when launching the app.
    """
    system_call("echo Welcome message")


def launch_web_browser() -> None:
    """
    Launches web browser with localhost address.
    """
    open_in_browser(LOCALHOST)


def main():

    # Getting path to all directories
    data_path = DATA_DIRECTORY

    # Creating environment directories
    make_sure_dirs_exist()

    # Initializing Great Expectations
    initialize_ge()

    # Defining app
    app = create_app(upload_dir_path=data_path)

    # Removing all logs and warnings
    configure_logging()
    configure_warnings()

    # Welcome message
    display_welcome_message()

    # Opening app in browser
    launch_web_browser()

    # Running server
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
