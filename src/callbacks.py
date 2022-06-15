import dash
from dash import dcc
import great_expectations as ge
from dash import Output, Input, State
import dash_bootstrap_components as dbc
from pandas.core.dtypes.common import is_string_dtype, is_numeric_dtype

from constants.defaults import EMPTY_LIST, EMPTY_STRING
from constants.path_constants import GREAT_EXPECTATIONS_PATH
from constants.great_expectations_constants import (
    TYPE,
    LENGTH,
    OR_EQUAL,
    COLUMN_A,
    COLUMN_B,
    MIN_VALUE,
    MAX_VALUE,
    COLUMN_LIST,
    VALUE_SET_MULTI,
    VALUE_SET_SINGLE,
    EXPECTATION_PARAMS,
    SUPPORTED_GE_EXP_TYPES,
    EXPECTATION_CONJUNCTION,
    MULTICOLUMN_EXPECTATIONS_MAP,
    SINGLE_COLUMN_EXPECTATIONS_MAP,
)

from src.expectation_suite_operations import get_expectation_suite_name_object
from src.validation_operations import validate_dataset, move_validation_to_app_system
from src.front_end_operations import (
    is_trigger,
    hide_component,
    display_component,
    open_file_in_browser,
    get_checklist_components,
)
from src.utils import (
    get_value,
    read_dataset,
    is_list_empty,
    list_has_one_item,
    infer_csv_separator,
    build_profile_report
)
from src.expectation_set_operations import (
    is_numeric_expectation,
    is_non_numeric_expectation,
    get_two_columns_expectations,
    is_expectation_set_name_valid,
    delete_expectations_in_config,
    get_any_column_count_expectations,
    write_multicolumn_expectation_in_config,
    write_single_column_expectation_in_config,
    check_existing_expectation_sets_integrity
)
from src.low_level_operations import (
    move,
    rename,
    join_paths,
    delete_file,
    has_extension,
    is_dataset_name,
    get_validation_path,
    get_import_dir_path,
    get_validations_path,
    is_profile_report_name,
    get_profile_report_path,
    get_profile_reports_path,
    get_expectation_set_path,
    get_imported_dataset_path,
    get_validation_file_names,
    get_uploaded_dataset_path,
    get_imported_dataset_names,
    is_profile_report_available,
    get_elements_inside_directory,
    get_available_expectation_sets,
)


def set_callbacks(app) -> dash.Dash:
    """
    Defines all callback functions for the app.

    :param app: Dash object whose callbacks need to be configured.

    :return: Dash object with configured callbacks.
    """

    ge_context = ge.data_context.DataContext(
        context_root_dir=GREAT_EXPECTATIONS_PATH
    )

    @app.callback(
        [
            Output("imported_datasets_checklist_div", "style"),
            Output("no_imported_datasets_div", "style")
        ],
        Input("imported_datasets_checklist", "options"),
        [
            State("imported_datasets_checklist_div", "style"),
            State("no_imported_datasets_div", "style")
        ]
    )
    def switch_dataset_listing_styles(
        available_options: list,
        checklist_div_style: dict,
        no_imports_div_style: dict
    ) -> (dict, dict):
        """
        Switches between two Div components, depending on whether there are imported
        datasets or not.

        :param available_options: List with the current dcc.Checklist options.
        :param checklist_div_style: Dictionary with the current style.
        :param no_imports_div_style: Dictionary with the current style.

        :return: Dictionaries with updated styles
        """
        # In case there are no imported datasets, hide the checklist and show the message
        if is_list_empty(available_options):
            checklist_div_style = hide_component(checklist_div_style)
            no_imports_div_style = display_component(no_imports_div_style)

        # In case there are, hide the message and show the checklist
        else:
            checklist_div_style = display_component(checklist_div_style)
            no_imports_div_style = hide_component(no_imports_div_style)

        # Returning updated styles
        return checklist_div_style, no_imports_div_style

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

        return

    def refresh_imported_dataset_listing() -> (list, list):
        """
        Returns a list of dcc.Checklist components, based on imported datasets.

        :return: List of checklist components.
        """
        imported_datasets = get_imported_dataset_names()
        return get_checklist_components(imported_datasets)

    def dataset_name_is_already_in_use(dataset_name: str) -> bool:
        """
        Returns if the name of a recently imported dataset is already in use.

        :param dataset_name: String with the name of the dataset.

        :return: Bool.
        """
        return dataset_name in get_imported_dataset_names()

    def dataset_can_be_imported(dataset_name: str) -> bool:
        """
        Returns if a dataset can be imported or not.

        :param dataset_name: String with the name of the dataset.

        :return: Bool
        """
        return not dataset_name_is_already_in_use(dataset_name)

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

        return

    @app.callback(
        [
            Output("imported_datasets_checklist", "options"),
            Output("imported_datasets_checklist", "value"),
            Output("rename_dataset_input", "value"),
            Output("imported_datasets_dropdown", "options"),
        ],
        [
            Input("dataset_uploader", "isCompleted"),
            Input("delete_dataset_button", "n_clicks"),
            Input("rename_dataset_button", "n_clicks"),
        ],
        [
            State("imported_datasets_checklist", "options"),
            State("imported_datasets_checklist", "value"),
            State("dataset_uploader", "fileNames"),
            State("rename_dataset_input", "value"),
        ]
    )
    def update_dataset_listing(
        new_upload,
        delete: int,
        rename_dataset: int,
        available_options: list,
        selected_datasets: list,
        uploaded_file_names: list,
        new_dataset_name: str,
    ) -> (list, list):
        """
        Updates imported datasets listing.

        :param new_upload: A new import has been performed.
        :param delete: Delete button has been clicked.
        :param rename_dataset: Rename button has been clicked.
        :param available_options: List with current checklist options.
        :param uploaded_file_names: List containing the name of the imported dataset.
        :param selected_datasets: List with names of datasets selected by the user.
        :param new_dataset_name: String with a new name for a dataset.

        :return: List with updated checklist options, and empty list.
        """
        # If a dataset has been uploaded
        if is_trigger("dataset_uploader"):
            if list_has_one_item(uploaded_file_names):

                # Get dataset name and path
                dataset_name = get_value(uploaded_file_names)
                dataset_path = get_uploaded_dataset_path(dataset_name)

                # If it can be imported, then move it from upload to import directory
                if dataset_can_be_imported(dataset_name):
                    new_dataset_path = get_imported_dataset_path(dataset_name)
                    move(dataset_path, new_dataset_path)

                # If it cannot be imported, delete it
                else:
                    delete_file(dataset_path)

        # If delete button has been clicked
        elif is_trigger("delete_dataset_button"):

            # If there are selected datasets, delete them
            if not is_list_empty(selected_datasets):
                delete_datasets(selected_datasets)

        # If rename button has been used
        elif is_trigger("rename_dataset_button"):

            # If there is only one selected dataset and the new name is valid
            if list_has_one_item(selected_datasets):
                current_name = get_value(selected_datasets)
                current_extension = current_name.split(".")[-1]

                # If it has no extension, add it
                if not has_extension(new_dataset_name):
                    new_dataset_name += "." + current_extension

                # Comparing extensions
                new_extension = new_dataset_name.split(".")[-1]
                if new_extension == current_extension:
                    if is_new_dataset_name_valid(available_options, new_dataset_name):
                        directory_path = get_import_dir_path()

                        # Rename the selected dataset
                        rename(directory_path, current_name, new_dataset_name)

        # Getting current file names in the directory
        available_options = refresh_imported_dataset_listing()
        return available_options, EMPTY_LIST, EMPTY_STRING, available_options

    @app.callback(
        [
            Output("preview_table_modal", "is_open"),
            Output("preview_table_modal_body", "children"),
            Output("preview_table_modal_header_title", "children")
        ],
        Input("open_preview_table_button", "n_clicks"),
        [
            State("imported_datasets_checklist", "value"),
            State("preview_table_modal", "is_open")
        ]
    )
    def show_table_preview(
        open_preview: int, selected_datasets: list, modal_state
    ) -> (bool, list):
        """
        Displays the table preview of the selected imported dataset.

        :param open_preview: Open preview button has been clicked.
        :param selected_datasets: List with selected datasets.
        :param modal_state: Current state of the modal.

        :return: Style for the preview modal, as well as table content for its body.
        """
        body_content = None
        modal_title = EMPTY_STRING
        if is_trigger("open_preview_table_button"):
            if list_has_one_item(selected_datasets):
                dataset_name = get_value(selected_datasets)
                dataset_path = get_imported_dataset_path(dataset_name)
                separator = infer_csv_separator(dataset_path)
                dataset = read_dataset(dataset_path, sep=separator, n_rows=20)
                body_content = dbc.Table.from_dataframe(
                    dataset, striped=True, bordered=True, hover=True
                )
                modal_state = True
                modal_title = f"{dataset_name} preview"
        return modal_state, body_content, modal_title

    @app.callback(
        Output("profile_report_output_div", "children"),
        Input("open_insights_button", "n_clicks"),
        State("imported_datasets_checklist", "value")
    )
    def see_dataset_insights(open_insights: int, selected_datasets: list) -> None:
        """
        Launches modal to see a preview of the dataset.

        :param open_insights: Number of clicks.
        :param selected_datasets: List with selected datasets.
        """
        if is_trigger("open_insights_button"):
            if list_has_one_item(selected_datasets):
                dataset_name = get_value(selected_datasets)
                if not is_profile_report_available(dataset_name):
                    build_profile_report(dataset_name)
                file_path = get_profile_report_path(dataset_name)
                open_file_in_browser(file_path)

        return

    @app.callback(
        Output("clear_insights_div", "style"),
        [
            Input("clear_insights_button", "n_clicks"),
            Input("profile_report_output_div", "children"),
        ],
        State("clear_insights_div", "style")
    )
    def clear_profile_reports_or_toggle_components(
        change: list or None, clear_profile_reports: int, current_style: dict
    ) -> dict:
        profile_reports_dir = get_profile_reports_path()
        profile_reports = [
            pr
            for pr in get_elements_inside_directory(profile_reports_dir)
            if is_profile_report_name(pr)
        ]

        # If all profile reports have to be deleted
        if is_trigger("clear_insights_button"):
            for pr in profile_reports:
                pr_path = join_paths(profile_reports_dir, pr)
                delete_file(pr_path)
            style = hide_component(current_style)

        else:

            # If there are no profile reports, hide the components
            if is_list_empty(profile_reports):
                style = hide_component(current_style)

            # If there are, then display them
            else:
                style = display_component(current_style)
        return style

    @app.callback(
        [
            Output("expectation_set_definer_modal", "is_open"),
            Output("expectation_set_name_input", "value"),
            Output("imported_datasets_dropdown", "value"),
        ],
        [
            Input("open_expectation_set_definer_button", "n_clicks"),
            Input("confirm_expectation_set_definition_button", "n_clicks"),
            Input("cancel_expectation_set_definition_button", "n_clicks")
        ],
        [
            State("expectation_set_name_input", "value"),
            State("imported_datasets_dropdown", "value"),
        ],
        prevent_initial_call=True
    )
    def toggle_expectation_set_definer(
        open_modal: int, define_set: int, cancel_definition: int, set_name, dataset_name
    ) -> (bool, str, str):
        """
        Opens the expectation set definer when the button is clicked.

        :param open_modal: Number of clicks.
        :param define_set: Number of clicks.
        :param cancel_definition: Number of clicks.
        :param set_name: String with current expectation set name.
        :param dataset_name: String with the name of the dataset the user is applying
        expectations to.

        :return: Bool.
        """
        is_open = False

        # If the modal has to be opened, then change the output
        if is_trigger("open_expectation_set_definer_button"):
            is_open, set_name, dataset_name = True, EMPTY_STRING, EMPTY_STRING
        return is_open, set_name, dataset_name

    @app.callback(
        [
            Output("expectation_sets_checklist_div", "style"),
            Output("no_expectation_sets_div", "style"),
            Output("delete_expectation_set_div", "style")
        ],
        Input("expectation_sets_checklist", "options"),
        [
            State("expectation_sets_checklist_div", "style"),
            State("no_expectation_sets_div", "style"),
            State("delete_expectation_set_div", "style")
        ]
    )
    def switch_expectation_sets_listing_styles(
        available_options: list,
        checklist_div_style: dict,
        no_sets_div_style: dict,
        display_delete_button: dict
    ) -> (dict, dict):
        """
        Switches between two Div components, depending on whether there are imported
        datasets or not.

        :param available_options: List with the current dcc.Checklist options.
        :param checklist_div_style: Dictionary with the current style.
        :param no_sets_div_style: Dictionary with the current style.
        :param display_delete_button: Dictionary with style of the Div containing delete
        button.

        :return: Dictionaries with updated styles
        """
        # In case there are no imported datasets, hide the checklist and show the message
        if is_list_empty(available_options):
            checklist_div_style = hide_component(checklist_div_style)
            no_sets_div_style = display_component(no_sets_div_style)
            display_delete_button = hide_component(display_delete_button)

        # In case there are, hide the message and show the checklist
        else:
            checklist_div_style = display_component(checklist_div_style)
            no_sets_div_style = hide_component(no_sets_div_style)
            display_delete_button = display_component(display_delete_button)

        # Returning updated styles
        return checklist_div_style, no_sets_div_style, display_delete_button

    def get_expectation_set_name_from_filename(filename: str) -> str:
        """
        Returns the expectation set name given its filename, in other words, it removes
        the JSON extension.

        :param filename: String with the filename.

        :return: Expectation set name, without the extension.
        """
        return filename.split(".")[0]

    @app.callback(
        [
            Output("expectation_sets_checklist", "options"),
            Output("expectation_sets_checklist", "value")
        ],
        [
            Input("confirm_expectation_set_definition_button", "n_clicks"),
            Input("delete_expectation_set_button", "n_clicks")
        ],
        State("expectation_sets_checklist", "value")
    )
    def update_expectation_set_checklist_listing(
        new_set: int, delete_set: int, selected_sets: list
    ) -> (list, list):
        if is_trigger("confirm_expectation_set_definition_button"):
            check_existing_expectation_sets_integrity()
        elif is_trigger("delete_expectation_set_button"):
            for set_name in selected_sets:
                set_path = get_expectation_set_path(set_name)
                delete_file(set_path)
        return (
            sorted(
                [
                    get_expectation_set_name_from_filename(fn)
                    for fn in get_available_expectation_sets()
                ]
            ),
            EMPTY_LIST
        )

    def is_expectation_set_name_in_use(set_name: str) -> bool:
        """
        Returns if the expectation set name is already in use. In that case, the name
        will not be available.

        :param set_name: String with the name introduced by the user.

        :return: Bool.
        """
        expectation_set_names_in_use = get_available_expectation_sets()
        return set_name + ".json" in expectation_set_names_in_use

    @app.callback(
        Output("single_column_expectation_definer_modal", "is_open"),
        [
            Input("new_single_column_expectation_button", "n_clicks"),
            Input("add_single_column_expectation_button", "n_clicks"),
            Input("close_single_column_expectation_definer_button", "n_clicks")
        ],
        [
            State("expectation_set_name_input", "value"),
            State("imported_datasets_dropdown", "value"),
            State("expectations_checklist", "options"),
            State("expectation_sets_checklist", "options"),
            State("single_column_expectation_definer_modal", "is_open")
        ],
        prevent_initial_call=True
    )
    def toggle_single_column_expectation_definer(
        new_expectation: int,
        add_expectation: int,
        close_definer: int,
        set_name: str,
        dataset_name: str,
        current_expectations: list,
        sets_in_checklist: list,
        modal_state
    ) -> bool:
        """
        Opens the expectation definer when the button is clicked, only if conditions
        match.

        :param new_expectation: Number of clicks.
        :param add_expectation: Number of clicks.
        :param close_definer: Number of clicks.
        :param set_name: Current name typed by the user.
        :param dataset_name: Currently selected dataset or table.
        :param current_expectations: List with current expectations.
        :param sets_in_checklist: List with current expectation set names in expectation
        sets checklist.
        :param modal_state: Current modal state.

        :return: Bool.
        """
        if is_trigger("new_single_column_expectation_button"):
            if is_expectation_set_name_valid(set_name):
                if (set_name not in sets_in_checklist or current_expectations) \
                        and dataset_name:
                    modal_state = True
        else:
            modal_state = False
        return modal_state

    @app.callback(
        Output("multicolumn_expectation_definer_modal", "is_open"),
        [
            Input("new_multicolumn_expectation_button", "n_clicks"),
            Input("add_multicolumn_expectation_button", "n_clicks"),
            Input("close_multicolumn_expectation_definer_button", "n_clicks")
        ],
        [
            State("expectation_set_name_input", "value"),
            State("imported_datasets_dropdown", "value"),
            State("expectations_checklist", "options"),
            State("expectation_sets_checklist", "options"),
            State("multicolumn_expectation_definer_modal", "is_open")
        ],
        prevent_initial_call=True
    )
    def toggle_multicolumn_expectation_definer(
        new_expectation: int,
        add_expectation: int,
        close_definer: int,
        set_name: str,
        dataset_name: str,
        current_expectations: list,
        sets_in_checklist: list,
        modal_state
    ) -> bool:
        """
        Opens the expectation definer when the button is clicked, only if conditions
        match.

        :param new_expectation: Number of clicks.
        :param add_expectation: Number of clicks.
        :param close_definer: Number of clicks.
        :param set_name: Current name typed by the user.
        :param dataset_name: Currently selected dataset or table.
        :param current_expectations: List with current expectations.
        :param sets_in_checklist: List with current expectation set names in expectation
        sets checklist.
        :param modal_state: Current modal state.

        :return: Bool.
        """
        if is_trigger("new_multicolumn_expectation_button"):
            if is_expectation_set_name_valid(set_name):
                if (set_name not in sets_in_checklist or current_expectations) and dataset_name:
                    modal_state = True
        else:
            modal_state = False
        return modal_state

    @app.callback(
        Output("select_columns_text_div", "style"),
        Input("compatible_multicolumn_expectations_dropdown", "value"),
        State("select_columns_text_div", "style")
    )
    def display_or_hide_text(selected_expectation: str, div_style: dict) -> dict:
        if is_trigger("compatible_multicolumn_expectations_dropdown"):
            if selected_expectation:
                div_style = display_component(div_style)
            else:
                div_style = hide_component(div_style)
        return div_style

    def get_two_column_expectation_interface_names() -> list:
        """
        Returns a list with interface names of those expectations that work with two
        table columns.

        :return: List with interface names.
        """
        names = list()
        for interface_name in SINGLE_COLUMN_EXPECTATIONS_MAP:
            if SINGLE_COLUMN_EXPECTATIONS_MAP[interface_name] in get_two_columns_expectations():
                names.append(interface_name)
        return names

    def get_any_column_count_expectation_interface_names() -> list:
        """
        Returns a list with interface names of those expectations that work with any
        table column count.

        :return: List with interface names.
        """
        names = list()
        for interface_name in SINGLE_COLUMN_EXPECTATIONS_MAP:
            if SINGLE_COLUMN_EXPECTATIONS_MAP[interface_name] in get_any_column_count_expectations():
                names.append(interface_name)
        return names

    @app.callback(
        [
            Output("compatible_single_column_expectations_dropdown", "value"),
            Output("compatible_multicolumn_expectations_dropdown", "value"),
            Output("table_columns_dropdown", "value"),
            Output("type_exp_param_input", "value"),
            Output("length_exp_param_input", "value"),
            Output("values_single_column_exp_param_input", "value"),
            Output("min_value_exp_param_input", "value"),
            Output("max_value_exp_param_input", "value"),
            Output("table_column_a", "value"),
            Output("table_column_b", "value"),
            Output("values_multicolumn_exp_param_input", "value"),
            Output("or_equal_checklist", "value"),
            Output("table_columns_checklist", "value")
        ],
        [
            Input("new_single_column_expectation_button", "n_clicks"),
            Input("new_multicolumn_expectation_button", "n_clicks")
        ]
    )
    def clear_values_at_expectation_definer(
        new_single: int, new_multi: int
    ) -> (str, str):
        """
        Returns two empty strings to clear dropdown selections.

        :param new_single: Number of clicks.
        :param new_multi: Number of clicks.

        :return: Empty elements to clear all inputs.
        """
        return [EMPTY_STRING] * 11 + [EMPTY_LIST] * 2

    @app.callback(
        [
            Output("table_columns_dropdown", "options"),
            Output("table_columns_checklist", "options"),
            Output("table_column_a", "options"),
            Output("table_column_b", "options")
        ],
        [
            Input("imported_datasets_dropdown", "value"),
            Input("table_column_a", "value"),
            Input("table_column_b", "value")
        ]
    )
    def find_available_table_columns(
        dataset_name: str, selected_a_column: str, selected_b_column: str
    ) -> (list, list, list, list):
        """
        Finds table columns once the user selects one dataset to create expectations on.

        :param dataset_name: String with the name of the selected dataset.
        :param selected_a_column: String with the name of selected A table column.
        :param selected_b_column: String with the name of selected B table column.

        :return: Lists with dataset columns, but in case there is no selected dataset, it
        returns empty lists.
        """
        table_columns = EMPTY_LIST
        if dataset_name:
            dataset_path = get_imported_dataset_path(dataset_name)
            sep = infer_csv_separator(dataset_path)
            table = read_dataset(dataset_path, n_rows=2, sep=sep)
            table_columns = table.columns.tolist()

        table_column_a_options = [tc for tc in table_columns if tc != selected_b_column]
        table_column_b_options = [tc for tc in table_columns if tc != selected_a_column]
        return (
            table_columns, table_columns, table_column_a_options, table_column_b_options
        )

    @app.callback(
        [
            Output("expectations_checklist_div", "style"),
            Output("no_expectations_div", "style"),
            Output("delete_expectation_button_div", "style"),
            Output("expectation_set_name_input", "disabled"),
            Output("imported_datasets_dropdown", "disabled")
        ],
        Input("expectations_checklist", "options"),
        [
            State("expectations_checklist_div", "style"),
            State("no_expectations_div", "style"),
            State("delete_expectation_button_div", "style"),
        ]
    )
    def switch_expectations_listing_styles(
        current_expectations: list,
        checklist_div_style: dict,
        no_expectations_div_style: dict,
        delete_expectations_div_style: dict
    ) -> (dict, dict, bool):
        """
        Switches between two Div components, depending on whether there are imported
        datasets or not.

        :param current_expectations: List with the current dcc.Checklist options.
        :param checklist_div_style: Dictionary with the current style.
        :param no_expectations_div_style: Dictionary with the current style.
        :param delete_expectations_div_style: Dictionary with the current style.

        :return: Dictionaries with updated styles
        """
        # In case there are no expectations, hide the checklist and show the message
        if is_list_empty(current_expectations):
            checklist_div_style = hide_component(checklist_div_style)
            no_expectations_div_style = display_component(no_expectations_div_style)
            delete_expectations_div_style = hide_component(delete_expectations_div_style)
            disabled_parameter = False

        # In case there are, hide the message and show the checklist
        else:
            checklist_div_style = display_component(checklist_div_style)
            no_expectations_div_style = hide_component(no_expectations_div_style)
            delete_expectations_div_style = display_component(
                delete_expectations_div_style
            )
            disabled_parameter = True

        # Returning updated styles
        return (
            checklist_div_style,
            no_expectations_div_style,
            delete_expectations_div_style,
            disabled_parameter,
            disabled_parameter
        )

    @app.callback(
        [
            Output("type_exp_param_div", "style"),
            Output("length_exp_param_div", "style"),
            Output("values_single_column_exp_param_div", "style"),
            Output("min_value_exp_param_div", "style"),
            Output("max_value_exp_param_div", "style")
        ],
        [
            Input("new_single_column_expectation_button", "n_clicks"),
            Input("compatible_single_column_expectations_dropdown", "value")
        ],
        [
            State("type_exp_param_div", "style"),
            State("length_exp_param_div", "style"),
            State("values_single_column_exp_param_div", "style"),
            State("min_value_exp_param_div", "style"),
            State("max_value_exp_param_div", "style")
        ],
        prevent_initial_call=True
    )
    def show_single_column_expectation_parameter_inputs(
        new_expectation: int,
        selected_expectation: str,
        type_div_style: dict,
        length_div_style: dict,
        values_div_style: dict,
        min_value_div_style: dict,
        max_value_div_style: dict,
    ) -> (dict, dict, dict, dict, dict):
        """
        Shows or hides Divs that are meant to be the input for expectation parameters.

        :param new_expectation: Number of clicks.
        :param selected_expectation: String with the expectation that the user selected.
        :param type_div_style: Component style.
        :param length_div_style: Component style.
        :param values_div_style: Component style.
        :param min_value_div_style: Component style.
        :param max_value_div_style: Component style.

        :return: Dictionaries with styles for the mentioned Divs.
        """
        params_div_map = {
            TYPE: type_div_style,
            LENGTH: length_div_style,
            VALUE_SET_SINGLE: values_div_style,
            MIN_VALUE: min_value_div_style,
            MAX_VALUE: max_value_div_style
        }

        if is_trigger("new_single_column_expectation_button") or not selected_expectation:
            expectation_params = EMPTY_LIST

        else:
            expectation_id = SINGLE_COLUMN_EXPECTATIONS_MAP[selected_expectation]
            expectation_params = EXPECTATION_PARAMS[expectation_id]

        for param in params_div_map:
            if param in expectation_params:
                params_div_map[param] = display_component(params_div_map[param])
            else:
                params_div_map[param] = hide_component(params_div_map[param])

        return list(params_div_map.values())

    @app.callback(
        [
            Output("table_a_column_div", "style"),
            Output("table_b_column_div", "style"),
            Output("or_equal_div", "style"),
            Output("table_columns_checklist_div", "style"),
            Output("values_multicolumn_exp_param_div", "style"),
        ],
        [
            Input("new_multicolumn_expectation_button", "n_clicks"),
            Input("compatible_multicolumn_expectations_dropdown", "value")
        ],
        [
            State("table_a_column_div", "style"),
            State("table_b_column_div", "style"),
            State("or_equal_div", "style"),
            State("table_columns_checklist_div", "style"),
            State("values_multicolumn_exp_param_div", "style"),
        ],
        prevent_initial_call=True
    )
    def show_multicolumn_expectation_parameter_inputs(
        new_expectation: int,
        selected_expectation: str,
        column_a_style: dict,
        column_b_style: dict,
        or_equal_style: dict,
        columns_checklist_style: dict,
        values_div_style: dict,
    ) -> (dict, dict, dict, dict, dict):
        """
        Shows or hides Divs that are meant to be the input for expectation parameters.

        :param new_expectation: Number of clicks.
        :param selected_expectation: String with the expectation that the user selected.
        :param column_a_style: Component style.
        :param column_b_style: Component style.
        :param or_equal_style: Component style.
        :param columns_checklist_style: Component style.
        :param values_div_style: Component style.

        :return: Dictionaries with styles for the mentioned Divs.
        """
        params_div_map = {
            COLUMN_A: column_a_style,
            COLUMN_B: column_b_style,
            OR_EQUAL: or_equal_style,
            COLUMN_LIST: columns_checklist_style,
            VALUE_SET_MULTI: values_div_style,
        }
        if is_trigger("new_multicolumn_expectation_button") or not selected_expectation:
            expectation_params = EMPTY_LIST

        else:
            expectation_id = MULTICOLUMN_EXPECTATIONS_MAP[selected_expectation]
            expectation_params = EXPECTATION_PARAMS[expectation_id]

        for param in params_div_map:
            if param in expectation_params:
                params_div_map[param] = display_component(params_div_map[param])
            else:
                params_div_map[param] = hide_component(params_div_map[param])

        return list(params_div_map.values())

    def multicolumn_value_set_matches_expression(value: str) -> bool:
        """
        Returns if the value set of a multicolumn expectation matches the required
        format.

        :param value: String with value set.

        :return: Bool.
        """
        matches_format = True

        opening_clause_count = value.count("[")
        closing_clause_count = value.count("]")
        if (opening_clause_count + closing_clause_count) % 2 != 0:
            matches_format = False

        if opening_clause_count != closing_clause_count:
            matches_format = False

        if matches_format:
            value_count = 0
            comma_count = 1
            for character in value:
                if character == "[":
                    if comma_count != 1:
                        matches_format = False
                    value_count = comma_count = 0
                elif character == "]":
                    if value_count < 2 or comma_count != 1:
                        matches_format = False
                    comma_count = 0
                elif character == ",":
                    comma_count += 1
                else:
                    value_count += 1


        return matches_format

    def parse_parameter(param_name: str, value) -> any or None:
        """
        Returns a parsed parameter in case it is correct. If not, it returns None.

        :param param_name: String with the name of the parameter.
        :param value: Non-parsed value given to the parameter.
        """
        parsed_param = None
        if param_name == TYPE:
            if value in SUPPORTED_GE_EXP_TYPES:
                parsed_param = value
        elif param_name == LENGTH:
            if value.isnumeric():
                parsed_param = value
        elif param_name == VALUE_SET_SINGLE:
            value = value.replace(" ", "")
            parsed_param = value.split(",")
            for i in range(len(parsed_param)):
                if parsed_param[i].isnumeric():
                    parsed_param[i] = int(parsed_param[i])
                else:
                    try:
                        parsed_param[i] = float(parsed_param[i])
                    except ValueError:
                        pass
        elif param_name == MIN_VALUE or param_name == MAX_VALUE:
            value = value.replace(",", ".")
            try:
                parsed_param = float(value)
            except ValueError:
                pass
        elif param_name == VALUE_SET_MULTI:
            value = value.replace(" ", "").strip(",")
            if multicolumn_value_set_matches_expression(value):
                value = value.split("],")
                value = [
                    pair.replace("[", "").replace("]", "") for pair in value
                ]
                value = [pair.split(",") for pair in value]
                if not is_list_empty(value):
                    if all([len(pair) == 2 for pair in value]):
                        parsed_param = value
                        for i in range(len(value)):
                            for j in range(2):
                                parsed_param[i][j] = parsed_param[i][j].replace("'", "")
                                if parsed_param[i][j].isnumeric():
                                    parsed_param[i][j] = int(parsed_param[i][j])
                                else:
                                    try:
                                        parsed_param[i][j] = float(parsed_param[i][j])
                                    except ValueError:
                                        pass
                        parsed_param = [tuple(pair) for pair in parsed_param]
        elif param_name == OR_EQUAL:
            parsed_param = False if is_list_empty(value) else True
        return parsed_param

    def build_expectation_interface_name(
        expectation_name: str, column_names: list
    ) -> str:
        """
        Builds expectation interface name from expectation name and column name.

        :param expectation_name: String with expectation name.
        :param column_names: List with column names.

        :return: String with interface name.
        """
        spacer = " " if EXPECTATION_CONJUNCTION else ""
        interface_name = expectation_name + spacer + EXPECTATION_CONJUNCTION + spacer

        interface_name += column_names[0]
        for i in range(1, len(column_names)):
            interface_name += ", " + column_names[i]

        return interface_name

    def get_expectation_id_and_column_name_from_interface_name(interface_name: str) -> (str, list):
        """
        Returns GE's expectation ID given an expectation interface name.

        :param interface_name: String with expectation interface name.

        :return: String with GE's expectation ID.
        """
        expectation_name, column_name = interface_name.split(" " + EXPECTATION_CONJUNCTION + " ")
        if ", " not in column_name:
            expectation_id = SINGLE_COLUMN_EXPECTATIONS_MAP[expectation_name]
        else:
            expectation_id = MULTICOLUMN_EXPECTATIONS_MAP[expectation_name]
        return expectation_id, column_name.split(", ")

    @app.callback(
        Output("expectations_checklist", "value"),
        [
            Input("open_expectation_set_definer_button", "n_clicks"),
            Input("delete_expectation_button", "n_clicks")
        ]
    )
    def reset_selected_expectations(open_definer: int, delete_expectation: int) -> list:
        """
        Resets the selection of expectations in expectations checklist.

        :param open_definer: Number of clicks.
        :param delete_expectation: Number of clicks.

        :return: Empty list to clear checklist selection.
        """
        return EMPTY_LIST

    def expectation_is_already_in_checklist(
        new_interface_name: str, current_expectations: list
    ) -> bool:
        """
        Returns if an expectation interface name, for a multicolumn expectation, does
        already exist.

        :param new_interface_name: String with the interface name of the new expectation.
        :param current_expectations: List with existing expectation interface names.

        :return Bool.
        """
        exists = False
        (
            new_expectation_id,
            new_column_name
        ) = get_expectation_id_and_column_name_from_interface_name(new_interface_name)
        for interface_name in current_expectations:
            (
                expectation_id,
                column_name
            ) = get_expectation_id_and_column_name_from_interface_name(interface_name)
            if new_expectation_id == expectation_id:
                if set(new_column_name) == set(column_name):
                    exists = True
        return exists

    @app.callback(
        Output("expectations_checklist", "options"),
        [
            Input("open_expectation_set_definer_button", "n_clicks"),
            Input("add_single_column_expectation_button", "n_clicks"),
            Input("add_multicolumn_expectation_button", "n_clicks"),
            Input("delete_expectation_button", "n_clicks")
        ],
        [
            State("compatible_single_column_expectations_dropdown", "value"),
            State("compatible_multicolumn_expectations_dropdown", "value"),
            State("expectation_set_name_input", "value"),
            State("table_columns_dropdown", "value"),
            State("expectations_checklist", "options"),
            State("expectations_checklist", "value"),
            State("type_exp_param_input", "value"),
            State("length_exp_param_input", "value"),
            State("values_single_column_exp_param_input", "value"),
            State("min_value_exp_param_input", "value"),
            State("max_value_exp_param_input", "value"),
            State("table_column_a", "value"),
            State("table_column_b", "value"),
            State("or_equal_checklist", "value"),
            State("table_columns_checklist", "value"),
            State("values_multicolumn_exp_param_input", "value")
        ]
    )
    def add_new_expectation(
        open_set_definer: int,
        add_single_column_expectation: int,
        add_multicolumn_expectation: int,
        delete_expectation: int,
        selected_single_column_expectation_name: str,
        selected_multicolumn_expectation_name: str,
        expectation_set_name: str,
        selected_table_column: str,
        current_expectations: list,
        selected_expectations: list,
        type_input: str,
        length_input: str,
        values_single_input: str,
        min_value_input: str,
        max_value_input: str,
        table_column_a: str,
        table_column_b: str,
        or_equal: list,
        selected_table_columns: list,
        values_multi_input: str
    ) -> (list, dict):
        if is_trigger("open_expectation_set_definer_button"):
            current_expectations = list()
        elif is_trigger("add_single_column_expectation_button"):
            params_map = {
                TYPE: type_input,
                LENGTH: length_input,
                VALUE_SET_SINGLE: values_single_input,
                MIN_VALUE: min_value_input,
                MAX_VALUE: max_value_input
            }
            all_params_are_set = True

            expectation_id = SINGLE_COLUMN_EXPECTATIONS_MAP[selected_single_column_expectation_name]
            expectation_params = EXPECTATION_PARAMS[expectation_id]

            params_of_interest = dict()
            for param in expectation_params:
                parsed_param = parse_parameter(param, params_map[param])
                params_of_interest[param] = parsed_param
                if parsed_param is None:
                    all_params_are_set = False

                # Expectation will not be added if min value is greater than max
                # value
                if MIN_VALUE in params_of_interest and MAX_VALUE in params_of_interest:
                    if params_of_interest[MIN_VALUE] > params_of_interest[MAX_VALUE]:
                        all_params_are_set = False
            if all_params_are_set:
                write_single_column_expectation_in_config(
                    expectation_set_name, selected_table_column, expectation_id, params_of_interest
                )
                expectation_interface_name = build_expectation_interface_name(
                    selected_single_column_expectation_name, [selected_table_column]
                )
                if not expectation_is_already_in_checklist(
                        expectation_interface_name, current_expectations
                ):
                    current_expectations.append(expectation_interface_name)

        elif is_trigger("add_multicolumn_expectation_button"):
            params_map = {
                COLUMN_A: table_column_a,
                COLUMN_B: table_column_b,
                OR_EQUAL: or_equal,
                COLUMN_LIST: selected_table_columns,
                VALUE_SET_MULTI: values_multi_input,
            }
            all_params_are_set = True

            expectation_id = MULTICOLUMN_EXPECTATIONS_MAP[
                selected_multicolumn_expectation_name
            ]
            expectation_params = EXPECTATION_PARAMS[expectation_id]

            params_of_interest = dict()
            for param in expectation_params:
                if "column" not in param:
                    parsed_param = parse_parameter(param, params_map[param])
                    params_of_interest[param] = parsed_param
                    if parsed_param is None:
                        all_params_are_set = False

            if COLUMN_A in expectation_params and COLUMN_B in expectation_params:
                if not params_map[COLUMN_A] or not params_map[COLUMN_B]:
                    all_params_are_set = False

            if COLUMN_LIST in expectation_params:
                if is_list_empty(params_map[COLUMN_LIST]):
                    all_params_are_set = False

            if all_params_are_set:
                if not is_list_empty(selected_table_columns):
                    table_columns = selected_table_columns
                else:
                    table_columns = [table_column_a, table_column_b]
                write_multicolumn_expectation_in_config(
                    expectation_set_name, table_columns, expectation_id, params_of_interest
                )
                expectation_interface_name = build_expectation_interface_name(
                    selected_multicolumn_expectation_name, list(table_columns)
                )
                if not expectation_is_already_in_checklist(
                        expectation_interface_name, current_expectations
                ):
                    current_expectations.append(expectation_interface_name)

        elif is_trigger("delete_expectation_button"):
            column_names = list()
            expectation_ids = list()
            for interface_name in selected_expectations:
                (
                    expectation_id,
                    column_name
                ) = get_expectation_id_and_column_name_from_interface_name(interface_name)

                # Getting the expectations to be removed
                expectation_ids.append(expectation_id)

                # Getting column names where expectations are set at
                column_names.append(column_name)

                # Removing the expectations from the interface
                current_expectations.remove(interface_name)

            # Finally, deleting selected expectations in configuration
            delete_expectations_in_config(expectation_set_name, column_names, expectation_ids)

        return current_expectations

    @app.callback(
        Output("compatible_single_column_expectations_dropdown", "options"),
        [
            Input("table_columns_dropdown", "value"),
            Input("new_single_column_expectation_button", "n_clicks")
        ],
        State("imported_datasets_dropdown", "value"),
    )
    def get_compatible_expectations(
        selected_column: str, new_expectation: int, dataset_name: str
    ) -> list:
        """
        Returns only those expectations compatible with the dataset column type.

        :param selected_column: String with the selected dataset column.
        :param new_expectation: Number of clicks.
        :param dataset_name: String with dataset name.

        :return: List with compatible expectations.
        """
        # Getting all supported expectations
        compatible_expectations = sorted(list(SINGLE_COLUMN_EXPECTATIONS_MAP.keys()))

        # If any dataset column is selected, then get compatible expectations
        if is_trigger("table_columns_dropdown") and selected_column:
            dataset_path = get_imported_dataset_path(dataset_name)
            separator = infer_csv_separator(dataset_path)
            dataset = read_dataset(dataset_path, sep=separator, n_rows=5)
            if is_numeric_dtype(dataset[selected_column]):
                compatible_expectations = [
                    e for e in compatible_expectations if is_numeric_expectation(e)
                ]
            elif is_string_dtype(dataset[selected_column]):
                compatible_expectations = [
                    e for e in compatible_expectations if is_non_numeric_expectation(e)
                ]
        return compatible_expectations

    @app.callback(
        [
            Output("validation_dropdown", "options"),
            Output("validation_dropdown", "value"),
        ],
        [
            Input("validate_dataset_button", "n_clicks"),
            Input("delete_validations_button", "n_clicks")
        ],
        [
            State("imported_datasets_checklist", "value"),
            State("expectation_sets_checklist", "value"),
            State("validation_confidence_input", "value")
        ]
    )
    def update_validation_listing(
        validate: int,
        delete_validations: int,
        selected_datasets: list,
        selected_expectation_sets: list,
        confidence: str
    ) -> (list, str):
        validations_path = get_validations_path()

        dataset_name = EMPTY_STRING
        if is_trigger("validate_dataset_button"):
            if list_has_one_item(selected_datasets)\
                    and list_has_one_item(selected_expectation_sets):
                if not confidence:
                    confidence = "100"
                if confidence.isnumeric():
                    dataset_name = get_value(selected_datasets)
                    expectation_set_name = get_value(selected_expectation_sets)
                    expectation_name_object = get_expectation_suite_name_object(
                        expectation_set_name
                    )
                    validate_dataset(
                        ge_context,
                        dataset_name,
                        expectation_name_object,
                        int(confidence)
                    )

        elif is_trigger("delete_validations_button"):
            current_validations = get_validation_file_names()
            for validation_name in current_validations:
                validation_path = join_paths(validations_path, validation_name)
                delete_file(validation_path)

        move_validation_to_app_system(dataset_name, confidence)

        available_validations = sorted(get_validation_file_names())
        selected_by_default = ""
        if not is_list_empty(available_validations):
            selected_by_default = available_validations[0]
        return available_validations, selected_by_default

    @app.callback(
        [
            Output("delete_validations_div", "style"),
            Output("validation_operations_div", "style")
        ],
        [
            Input("validation_dropdown", "options"),
            Input("delete_validations_button", "n_clicks")
        ],
        [
            State("delete_validations_div", "style"),
        ]
    )
    def toggle_delete_validations_div(
        make_validation: int,
        delete_validations: int,
        div_style: dict,
    ) -> (dict, dict):
        """
        Displays or hides button to delete all validations, depending on whether there
        are any validations to be deleted or not.

        :param make_validation: Number of clicks.
        :param delete_validations: Number of clicks.
        :param div_style: Dictionary with current style of the Div containing the delete
        button.

        :return: Dictionary with updated style.
        """
        available_validations = get_validation_file_names()
        if is_list_empty(available_validations)\
                or is_trigger("delete_validations_button"):
            div_style = hide_component(div_style)
        else:
            div_style = display_component(div_style)
        return div_style, div_style

    @app.callback(
        Output("validation_confidence_input", "value"),
        Input("validation_dropdown", "options")
    )
    def clear_validation_confidence(change_in_validation_options: list) -> str:
        """
        Clears validation confidence.

        :param change_in_validation_options: List with updated options.

        :return: Empty string.
        """
        return "100"

    @app.callback(
        Output("open_validation_result_output_div", "children"),
        Input("open_validation_result_button", "n_clicks"),
        State("validation_dropdown", "value"),
        prevent_initial_call=True
    )
    def open_validation_result(open_validation: int, selected_validation: str) -> None:
        """
        Opens validation result in a new browser tab.

        :param open_validation: Number of clicks.
        :param selected_validation: String with selected result to be opened.
        """
        validation_path = get_validation_path(selected_validation)
        open_file_in_browser(validation_path)

    @app.callback(
        Output("validation_result_downloader", "data"),
        Input("export_validation_result_button", "n_clicks"),
        State("validation_dropdown", "value"),
        prevent_initial_call=True
    )
    def download_validation_result(download: int, selected_validation: str):
        """
        Downloads a validation result.

        :param download: Number of clicks.
        :param selected_validation: String with selected result to be downloaded.

        :return: Downloader data object.
        """
        validation_path = get_validation_path(selected_validation)
        return dcc.send_file(validation_path)

    return app
