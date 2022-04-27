import os
from great_expectations.checkpoint import LegacyCheckpoint
from great_expectations.profile.user_configurable_profiler import (
    UserConfigurableProfiler,
)

from constants import path_constants
from src.objects import ExpectationSuiteName
from src.json_operations import to_json, has_json_name
from src.data_structure_operations import get_value, split, list_to_dictionary
from src.batch_operations import load_batch_from_params, get_batch, get_batch_kwargs
from src.front_end_operations import (
    get_checklist_options_from_expectation_and_columns,
    is_trigger,
)
from src.expectation_operations import (
    read_expectation_and_columns_from_expectation_suite,
    remove_expectations_from_expectation_suite_loop,
    get_expectation_suite_expectations,
    remove_non_supported_expectations_from_expectation_suite,
)
from src.dataset_operations import (
    get_dataset_path,
    get_ignored_dataset_columns,
    which_dataset_could_have_been_used_to_create_expectation_suite,
    build_test_dataset,
    load_dataset,
    return_dataset_columns,
)
from src.low_level_operations import (
    get_file_name,
    get_expectation_suite_path,
    remove_file,
    get_upload_folder_path,
    join_paths,
    move_uploaded_expectation_suite_to_expectations_suite_folder,
    get_elements_inside_directory,
    get_expectation_suite_folder_path,
)


# Functions that end with a "#" are not actually used by the app, so they
# can be removed with no impact on its performance.


def create_auto_expectation_suite(
    context, dataset_name: str, expectation_suite_name: str, selected_columns: list
):
    """
    Creates automatic expectation suite, with all available
    expectations in great_expectations and wanted columns.
    :param context: great_expectations context object.
    :param dataset_name: String with dataset name.
    :param expectation_suite_name: String with Expectation Suite
    name.
    :param selected_columns: List with selected dataset columns,
    which are going to be used to create the Expectation Suite.
    """
    # Getting expectation suite name object and dataset
    # path
    expectation_suite_name_object = ExpectationSuiteName(expectation_suite_name)
    expectation_suite = create_expectation_suite(context, expectation_suite_name_object)
    dataset = load_dataset(dataset_name, n_rows=5)
    dataset_columns = return_dataset_columns(dataset)
    dataset_path = get_dataset_path(dataset_name)
    batch_kwargs = get_batch_kwargs(context, dataset_path)
    batch = get_batch(context, batch_kwargs, expectation_suite)
    ignored_columns = get_ignored_dataset_columns(dataset_columns, selected_columns)
    expectation_suite = build_scaffold_expectation_suite(batch, ignored_columns)

    # Removing validations that are not supported by the app
    expectation_suite = remove_non_supported_expectations_from_expectation_suite(
        expectation_suite
    )
    save_expectation_suite(context, expectation_suite, expectation_suite_name_object)


def import_expectation_suite_manager(context, uploaded_file_names: list) -> (str, bool):
    """
    It checks that the uploaded expectation suite name contains the
    JSON extension, and calls import_expectation_suite() function.
    :param context: great_expectations context object.
    :param uploaded_file_names: List that contains expectation suites
    that have been uploaded this time (only one).
    :return: JSON file to store that there has been an expectation suite
    upload and whether or not the app has to pop a warning.
    """
    is_es_imported, es_warning = to_json(False), False

    # If an expectation suite has been uploaded
    if uploaded_file_names:
        uploaded_file_name = get_value(uploaded_file_names)

        # If it seems to be a JSON file
        if has_json_name(uploaded_file_name):
            is_es_imported, es_warning = import_expectation_suite(
                context, uploaded_file_name
            )
    return is_es_imported, es_warning


def delete_expectation_suite(
    n_clicks: int, options: list, selected_expectation_suites: list
) -> str:
    """
    Called when deleting an Expectation Suite.
    :param n_clicks: Int with its number of clicks.
    :param options: List with all available options at expectation
    suites checklist.
    :param selected_expectation_suites: List with all selected
    options at expectation suites checklist.
    :return: JSON file that tells the app whether such Expectation
    Suite has been successfully removed or not.
    """
    if n_clicks and options and selected_expectation_suites:

        # Remove all selected expectation suites
        for expectation_suite_name in selected_expectation_suites:
            expectation_suite_name_object = get_expectation_suite_name_object(
                expectation_suite_name
            )
            remove_expectation_suite(expectation_suite_name_object)
        return to_json(True)
    return to_json(False)


def define_batch_from_expectation_suite(
    context,
    selected_expectation: str,
    expectation_suite_name: str,
    dataset_name: str,
    added_expectations: list,
    batch_kwargs_store: str,
) -> str or dict:
    """
    Used when defining a dataset batch.
    :param context: great_expectations context object.
    :param selected_expectation: String with selected expectation
    name.
    :param expectation_suite_name: String with Expectation Suite
    name.
    :param dataset_name: Str with dataset name.
    :param added_expectations: List with currently added
    expectations.
    :param batch_kwargs_store: JSON file that contains a dictionary
    with batch kwargs.
    :return: JSON file that contains a dict with batch kwargs.
    """
    if (
        selected_expectation
        and dataset_name
        and is_expectation_suite_name_valid(expectation_suite_name)
    ):
        if not added_expectations:

            # Expectation suite load
            clear_expectation_suite_expectations(context, expectation_suite_name)
            dataset_path = get_dataset_path(dataset_name)

            # Batch creation
            batch_kwargs = get_batch_kwargs(context, dataset_path)
            return to_json(batch_kwargs)
        return batch_kwargs_store
    return dict()


def remove_selected_expectations_from_expectation_suite(
    context,
    dataset_name: str,
    expectation_suite_name: str,
    remove_expectation: int,
    selected_expectations: list,
) -> str:
    """
    Has to be used to remove set expectations from Expectation Suite
    when editing.
    :param context: great_expectations context object.
    :param remove_expectation: Int with its number of clicks.
    :param selected_expectations: List with currently set
    expectations.
    :param expectation_suite_name: Str that contains Expectation
    Suite name.
    :param dataset_name: Str with dataset name.
    :return: JSON file with the removed expectations.
    """
    removed_expectations = remove_selected_expectations(
        context,
        dataset_name,
        expectation_suite_name,
        bool(remove_expectation),
        selected_expectations,
    )
    return to_json(removed_expectations)


def store_expectation_suite(
    context,
    expectation_suite_name: ExpectationSuiteName,
    batch_kwargs: dict,
):
    """
    This function is used to store the Expectation Suite as a file.
    :param context: great_expectations context object.
    :param expectation_suite_name: ExpectationSuiteName object.
    :param batch_kwargs: Dict with batch_kwargs.
    :return: great_expectations ValidationResultIdentifier object.
    This output is not actually not being used by the app for now.
    """
    results = LegacyCheckpoint(
        name="_temp_checkpoint",
        data_context=context,
        batches=[
            {
                "batch_kwargs": batch_kwargs,
                "expectation_suite_names": [expectation_suite_name.ge_name],
            }
        ],
    ).run()
    validation_result_identifier = results.list_validation_result_identifiers()[0]
    return validation_result_identifier


def build_scaffold_expectation_suite(batch, ignored_columns: list) -> dict:
    """
    Builds and returns Expectation Suite from automatic expectation
    selection and only non-ignored dataset columns.
    :param batch: great_expectations batch object.
    :param ignored_columns: List with unwanted columns.
    :return: great_expectations object.
    """
    profiler = UserConfigurableProfiler(
        profile_dataset=batch,
        ignored_columns=ignored_columns,
    )
    expectation_suite = profiler.build_suite()
    return expectation_suite


def load_expectation_suite_data(
    context, selected_expectation_suites: list
) -> (str, str, bool, list, str, str, str):
    """
    This function loads Expectation Suite data from the JSON file
    itself.
    :param context: great expectations context object.
    :param selected_expectation_suites: List with all selected
    Expectation Suites in the interface (can only be one).
    :return: String with the name of the Expectation Suite, JSON file
    with checklist options to be stored, bool, list with dataset
    columns, str with the name of a dataset that is, at least,
    compatible with the dataset originally used to create the suite
    and a JSON file that contains a bool.
    """
    # Getting the name
    expectation_suite_name = get_value(selected_expectation_suites)
    expectation_suite_name_object = get_expectation_suite_name_object(
        expectation_suite_name
    )
    expectation_suite = get_expectation_suite(context, expectation_suite_name_object)

    # Filling checklist options
    expectation_and_columns = read_expectation_and_columns_from_expectation_suite(
        expectation_suite
    )
    checklist_options = get_checklist_options_from_expectation_and_columns(
        expectation_and_columns
    )

    # Reading compatible dataset columns
    (
        original_dataset_name,
        dataset_columns,
    ) = which_dataset_could_have_been_used_to_create_expectation_suite(
        expectation_suite
    )
    if not original_dataset_name:
        no_compatible_dataset = defaults.WARNING_MESSAGES[
            "edit_expectation_suite_warning"
        ]["no_datasets_compatible"]
        return erase_selected_expectation_suite_data(message=no_compatible_dataset)
    return (
        expectation_suite_name_object.name,
        to_json(checklist_options),
        False,
        defaults.WARNING_MESSAGES["empty_message"],
        dataset_columns,
        original_dataset_name,
        original_dataset_name,
        to_json(True),
    )


def erase_selected_expectation_suite_data(
    message=defaults.WARNING_MESSAGES["empty_message"], pop_warning=True
):
    """
    Returns values to clear some data from the interface.
    :param message: String with the warning message to be displayed.
    :param pop_warning: Boolean that tells the function to return
    True or false in the third position.
    :return: Empty string, two empty JSON files, Bool and three None.
    """
    return (
        defaults.EMPTY_STRING,
        to_json(list()),
        pop_warning,
        message,
        None,
        None,
        None,
        to_json({}),
    )


def get_expectation_suite_name_from_path(
    expectation_suite_path: os.path,
) -> ExpectationSuiteName:
    """
    This function can be used to get Expectation Suite name from
    path.
    :param expectation_suite_path: String with its path.
    :return: String with its name.
    """
    file_name = get_file_name(expectation_suite_path)
    name = get_expectation_suite_name_from_file_name(file_name)
    return ExpectationSuiteName(name)


def get_expectation_suite_name_from_file_name(file_name: str) -> str:
    """
    Returns Expectation Suite name, which is file name without the
    JSON extension.
    :param file_name: String with the name of the file.
    :return: String with the name of the Expectation Suite.
    """
    return split(file_name, ".")[-2]


def create_expectation_suite(context, name: ExpectationSuiteName):
    """
    Creates a new Expectation Suite object
    :param context: great_expectations object.
    :param name: String with the name of the new Expectation Suite.
    :return: Expectation Suite object.
    """
    return context.create_expectation_suite(name.ge_name, overwrite_existing=True)


def save_expectation_suite(
    context, expectation_suite, name_object: ExpectationSuiteName
) -> None:
    """
    This function can be used to store an Expectation Suite when
    creating it, with no need to make any validation.
    :param context: great_expectations context object.
    :param expectation_suite: great_expectations object.
    :param name_object: String with Expectation Suite name object.
    """
    context.save_expectation_suite(expectation_suite, name_object.ge_name)


def remove_expectation_suite(expectation_suite_name: ExpectationSuiteName) -> None:
    """
    Removes expectation suite from its name.
    :param expectation_suite_name: ExpectationSuiteName object.
    """
    expectation_suite_path = get_expectation_suite_path(expectation_suite_name.name)
    remove_file(expectation_suite_path)


def clear_expectation_suite_expectations(context, expectation_suite_name: str) -> None:
    """
    Clears expectations in Expectation Suite.
    :param context: great_expectations context object.
    :param expectation_suite_name: String with the name of the
    Expectation Suite.
    """
    expectation_suite_name_object = get_expectation_suite_name_object(
        expectation_suite_name
    )
    expectation_suite = get_expectation_suite(context, expectation_suite_name_object)
    expectation_suite.expectations = []


def remove_selected_expectations(
    context,
    dataset_name: str,
    expectation_suite_name: str,
    remove_expectation: bool,
    selected_expectations: list,
) -> list:
    """
    Removes selected expectations in the Expectation Suite editor.
    :param context: great_expectations object.
    :param dataset_name: String with the name of the dataset.
    :param expectation_suite_name: String with the name of the
    Expectation Suite.
    :param remove_expectation: Bool that tells the function if the
    selected expectations have to be removed.
    :param selected_expectations: List of selected expectations in
    the editor.
    :return: List with removed expectations.
    """
    removed_expectations = []
    if remove_expectation:

        # Expectation suite load
        try:
            expectation_suite_name_object = get_expectation_suite_name_object(
                expectation_suite_name
            )
            expectation_suite = get_expectation_suite(
                context, expectation_suite_name_object
            )

            # For all expectations to be removed
            remove_expectations_from_expectation_suite_loop(
                expectation_suite, removed_expectations, selected_expectations
            )

            # Save expectation removal
            test_dataset_path = build_test_dataset(dataset_name)
            batch = load_batch_from_params(
                context, expectation_suite, test_dataset_path
            )
            batch.save_expectation_suite(discard_failed_expectations=False)
            remove_file(test_dataset_path)
        except:
            pass
    return removed_expectations


def import_expectation_suite(context, uploaded_file_name: str) -> (str, bool):
    """
    Used to import expectation suites from local storage. Checks if
    the imported file is a great_expectations Expectation Suite
    object and moves it to its respective directory.
    :param context: great_expectations context object.
    :param uploaded_file_name: String with the name of the
    Expectation Suite.
    :return: JSON file with a boolean that tells the app if the file
    has been successfully imported, and a boolean that manages
    warning pops.
    """
    upload_folder_path = get_upload_folder_path()

    # If a file has been uploaded
    if uploaded_file_name:
        uploaded_expectation_suite_path = join_paths(
            [upload_folder_path, uploaded_file_name]
        )

        # If the name is not valid
        if not is_expectation_suite_name_valid(uploaded_file_name, extension=True):
            remove_file(uploaded_expectation_suite_path)
            return to_json(False), True
        imported_expectation_suite_path = (
            move_uploaded_expectation_suite_to_expectations_suite_folder(
                uploaded_expectation_suite_path
            )
        )
        expectation_suite_name = get_expectation_suite_name_from_path(
            imported_expectation_suite_path
        )

        # If it is not an expectation suite
        if not is_expectation_suite(context, expectation_suite_name.name):
            remove_file(imported_expectation_suite_path)
            return to_json(False), True
    return to_json(True), False


def create_new_expectation_suite_to_be_filled(
    context,
    dataset_columns_storage: str,
    expectation_suite_name: str,
    dataset_file_name: str,
) -> (bool, str, None, str, str):
    """
    This function creates a new blank Expectation Suite, and it
    updates app warnings, states and storages.
    :param context: great_expectations object.
    :param dataset_columns_storage: JSON file that contains all
    expectations, the columns where they have to be applied and the
    required parameters (if any).
    :param expectation_suite_name: String with the name of the
    Expectation Suite
    :param dataset_file_name: String with the name of the dataset
    that will be validated.
    :return: Boolean that manages appearance of a warning, string
    with its message, list with all dataset columns, JSON file with
    all dataset columns and JSON file to control when expectation
    wizard is shown.
    """
    display_warning, message = check_expectation_suite_and_dataset_names_validity(
        expectation_suite_name, dataset_file_name
    )
    if display_warning:
        return True, message, None, to_json({}), to_json(False), False, False

    expectation_suite_name_object = get_expectation_suite_name_object(
        expectation_suite_name
    )

    # If the expectation suite already exists
    if does_expectation_suite_already_exist(expectation_suite_name_object):
        message = "Failed to create Expectation Suite. '" + expectation_suite_name
        message += "' already exists."
        return (
            True,
            message,
            None,
            dataset_columns_storage,
            to_json(False),
            False,
            False,
        )
    create_expectation_suite(context, expectation_suite_name_object)
    dataset = load_dataset(dataset_file_name, n_rows=5)
    dataset_columns = return_dataset_columns(dataset)
    dataset_columns_dictionary = list_to_dictionary(dataset_columns)
    return (
        False,
        defaults.WARNING_MESSAGES["empty_message"],
        dataset_columns,
        to_json(dataset_columns_dictionary),
        to_json(True),
        True,
        True,
    )


def check_expectation_suite_and_dataset_names_validity(
    expectation_suite_name: str, dataset_file_name: str
) -> (bool, str):
    """
    Checks the name of Expectation Suite and dataset are valid.
    :param expectation_suite_name: String with the name of the
    Expectation Suite.
    :param dataset_file_name: String with the name of the dataset.
    :return: Boolean and string that manage warning appearance.
    """
    # In case Expectation Suite name is not valid
    if not is_expectation_suite_name_valid(expectation_suite_name):
        return (
            True,
            defaults.WARNING_MESSAGES["expectation_suite_warning"]["invalid_name"],
        )

    # In case there is not a dataset name
    if not dataset_file_name:
        return (
            True,
            defaults.WARNING_MESSAGES["expectation_suite_warning"][
                "no_dataset_selected"
            ],
        )
    return False, defaults.WARNING_MESSAGES["empty_message"]


def warn_expectation_suite_is_empty(
    ctx,
    creation_expectations: list,
    edition_expectations: list,
    editor_expectation_suite_name: str,
) -> str:
    """
    Returns a message that tells the app if a warning has to be shown
    or not. This warning reminds the user the Expectation Suite is
    empty.
    :param ctx: Dash context object.
    :param creation_expectations: List with expectations present in
    Expectation Suite creator menu.
    :param edition_expectations: List with expectations present in
    Expectation Suite editor menu.
    :param editor_expectation_suite_name: String with the name of the
    Expectation Suite that is being edited.
    :return: String with an error message, or empty string if it is
    not empty.
    """
    message = defaults.WARNING_MESSAGES["empty_message"]
    error_message = defaults.WARNING_MESSAGES["expectation_suite_definition_warning"][
        "empty"
    ]
    if is_trigger(ctx, "create_expectation_suite_button"):
        if not creation_expectations:
            message = error_message

    if is_trigger(ctx, "apply_changes_to_expectation_suite_button") or is_trigger(
        ctx, "close_expectation_suite_editor_button"
    ):
        if not edition_expectations:
            message = error_message
            expectation_suite_name_object = get_expectation_suite_name_object(
                editor_expectation_suite_name
            )
            remove_expectation_suite(expectation_suite_name_object)
    return message


def is_expectation_suite_ready(
    context,
    expectation_suite_name: str,
    editor_expectation_suite_name: str,
) -> str:
    """
    Checks if the expectation suite is ready to be filled with
    expectations.
    :param context: great_expectations object.
    :param expectation_suite_name: String with the name of the
    Expectation Suite in creator.
    :param editor_expectation_suite_name: String with the name of the
    Expectation Suite in editor.
    :return: String with error message or empty string if everything
    is correct.
    """
    message = defaults.WARNING_MESSAGES["empty_message"]
    try:
        if expectation_suite_name:
            creator_name = get_expectation_suite_name_object(expectation_suite_name)
            get_expectation_suite(context, creator_name)
        else:
            editor_name = get_expectation_suite_name_object(
                editor_expectation_suite_name
            )
            get_expectation_suite(context, editor_name)
    except:
        message = defaults.WARNING_MESSAGES["expectation_suite_definition_warning"][
            "too_quick"
        ]
    return message


def get_expectation_suite(context, name: ExpectationSuiteName):
    """
    Loads Expectation Suite object from file.
    :param context: great_expectations object.
    :param name: String with its name.
    :return: great_expectations Expectation Suite object.
    """
    return context.get_expectation_suite(name.ge_name)


def get_expectation_suite_name_object(name: str) -> ExpectationSuiteName:
    """
    Returns Expectation Suite name object from a name.
    :param name: String with the name set by the user.
    :return: ExpectationSuiteName object.
    """
    return ExpectationSuiteName(name)


def list_expectation_suites() -> list:
    """
    Returns a list of all available expectation suites in the
    specified directory at the yaml file.
    :return: List with all Expectation Suite names.
    """
    return [
        get_expectation_suite_name_from_file_name(x)
        for x in get_elements_inside_directory(get_expectation_suite_folder_path())
    ]


def is_expectation_suite(context, name: str) -> bool:
    """
    Returns if the passed name belongs to any valid Expectation
    Suite.
    :param context: great_expectations object.
    :param name: ExpectationSuiteName object.
    :return: Boolean that tells the app whether it is a
    great_expectations readable Expectation Suite or not.
    """
    try:
        expectation_suite_name_object = get_expectation_suite_name_object(name)
        get_expectation_suite(context, expectation_suite_name_object)
    except:
        return False
    return True


def create_auto_expectation_suite_if_parameters_match(
    context, dataset_name: str, expectation_suite_name: str, selected_columns: list
) -> str:
    """
    Creates an automatic Expectation Suite if its name and dataset to
    be used are filled.
    :param context: great_expectations context object.
    :param expectation_suite_name: String with the name of the
    Expectation Suite.
    :param dataset_name: String with dataset name.
    :param selected_columns: List with selected columns.
    :return: JSON file that tells the app there is a new
    automatically created Expectation Suite in the file system.
    """
    if selected_columns:
        if is_expectation_suite_name_valid(expectation_suite_name):
            if dataset_name:
                create_auto_expectation_suite(
                    context, dataset_name, expectation_suite_name, selected_columns
                )
    return to_json(True)


def is_expectation_suite_name_valid(name: str, extension=False) -> bool:
    """
    Checks if input Expectation Suite name is valid.
    :param name: String with a name.
    :param extension: Bool that tells the function if the given name
    contains the JSON extension.
    :return: Boolean that tells the app if it has to pop a warning
    for the user or not.
    """
    if name:
        if not extension:
            if "." not in name:
                if len(name):
                    return True
            return False
        else:
            if len(split(name, ".")) == 2:
                name, extension = split(name, ".")
                if len(name) and extension == "json":
                    return True
    return False


def does_expectation_suite_already_exist(name: ExpectationSuiteName) -> bool:
    """
    Tells the app if the Expectation Suite already exists.
    :param name: String with the name of an Expectation Suite.
    :return: Boolean that tells if it already exists or not.
    """
    return name.name in list_expectation_suites()


def is_expectation_suite_empty(expectation_suite: dict) -> bool:  #
    """
    Returns if the Expectation Suite is empty.
    :param expectation_suite: great_expectations object.
    :return: Boolean that tells the app if it is empty.
    """
    return not get_expectation_suite_expectations(expectation_suite)


def is_expectation_suite_already_imported(expectation_suite_name: str) -> bool:  #
    """
    Can be used to tell if there is already another Expectation Suite
    with the same name as the one that is being imported.
    :param expectation_suite_name: String with Expectation Suite
    name.
    :return: Boolean that tells the app if it already exists.
    """
    return expectation_suite_name in list_expectation_suites()
