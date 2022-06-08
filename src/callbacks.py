import dash
import json
import great_expectations as ge
from dash import Output, Input, State
import dash_bootstrap_components as dbc

from constants.path_constants import GREAT_EXPECTATIONS_PATH
from constants.defaults import EMPTY_LIST, EMPTY_DICT, EMPTY_STRING
from constants.great_expectations_constants import (
    EXPECTATIONS_MAP,
    EXPECTATION_PARAMS,
    SUPPORTED_GE_EXP_TYPES,
    EXPECTATION_CONJUNCTION
)

from objects.expectation_suite_name import ExpectationSuiteName

from src.expectation_operations import is_expectation_set_name_valid
from src.expectation_suite_operations import create_ge_expectation_suite
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
from src.low_level_operations import (
    move,
    rename,
    join_paths,
    exists_path,
    delete_file,
    has_extension,
    is_dataset_name,
    get_import_dir_path,
    get_validations_path,
    is_profile_report_name,
    get_profile_report_path,
    get_profile_reports_path,
    get_imported_dataset_path,
    get_validation_file_names,
    get_uploaded_dataset_path,
    get_imported_dataset_names,
    is_profile_report_available,
    get_elements_inside_directory,
    get_available_expectation_sets,
    get_expectation_set_path,
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

    def check_all_expectation_sets_are_not_empty() -> None:
        """
        This function checks that no defined set is empty. If it is, it will be removed.
        """
        # Getting the name of all sets
        expectation_sets = get_available_expectation_sets()
        for set_name in expectation_sets:

            # Getting the path of each set
            expectation_set_path = get_expectation_set_path(set_name)
            with open(expectation_set_path, "r") as fp:
                content = json.load(fp)

            # If there is no content, then that is an empty expectation set. Let's delete
            # it
            if not content:
                delete_file(expectation_set_path)

    def check_existing_expectation_sets_integrity() -> None:
        """
        Responsible for checking all listed expectation sets are valid.
        """
        # Check they are not empty
        check_all_expectation_sets_are_not_empty()

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
        return [n[:-5] for n in get_available_expectation_sets()], EMPTY_LIST

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
        Output("expectation_definer_modal", "is_open"),
        [
            Input("new_expectation_button", "n_clicks"),
            Input("add_expectation_button", "n_clicks"),
            Input("close_expectation_definer_button", "n_clicks")
        ],
        [
            State("expectation_set_name_input", "value"),
            State("imported_datasets_dropdown", "value"),
            State("expectations_checklist", "options"),
            State("expectation_definer_modal", "is_open")
        ],
        prevent_initial_call=True
    )
    def toggle_expectation_definer(
        new_expectation: int,
        add_expectation: int,
        close_definer: int,
        set_name: str,
        dataset_name: str,
        current_expectations: list,
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
        :param modal_state: Current modal state.

        :return: Bool.
        """
        if is_trigger("new_expectation_button"):
            if is_expectation_set_name_valid(set_name):
                if (not is_expectation_set_name_in_use(set_name) or current_expectations) and dataset_name:
                    modal_state = True
        else:
            modal_state = False
        return modal_state

    @app.callback(
        [
            Output("supported_expectations_dropdown", "value"),
            Output("table_columns_dropdown", "value"),
            Output("type_exp_param_input", "value"),
            Output("length_exp_param_input", "value"),
            Output("values_exp_param_input", "value"),
            Output("min_value_exp_param_input", "value"),
            Output("max_value_exp_param_input", "value")
        ],
        [
            Input("new_expectation_button", "n_clicks")
        ]
    )
    def clear_values_at_expectation_definer(new_expectation: int) -> (str, str):
        """
        Returns two empty strings to clear dropdown selections.
        """
        return [EMPTY_STRING] * 7

    @app.callback(
        Output("table_columns_dropdown", "options"),
        Input("imported_datasets_dropdown", "value")
    )
    def find_available_table_columns(dataset_name: str) -> list:
        """
        Finds table columns once the user selects one dataset to create expectations on.

        :param dataset_name: String with the name of the selected dataset.

        :return: List with dataset columns, but in case there is no selected dataset, it
        returns an empty list.
        """
        table_columns = EMPTY_LIST
        if dataset_name:
            dataset_path = get_imported_dataset_path(dataset_name)
            sep = infer_csv_separator(dataset_path)
            table = read_dataset(dataset_path, n_rows=2, sep=sep)
            table_columns = table.columns.tolist()
        return table_columns

    @app.callback(
        [
            Output("expectations_checklist_div", "style"),
            Output("no_expectations_div", "style"),
            Output("delete_expectation_button_div", "style"),
            Output("expectation_set_name_input", "disabled")
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
            disabled_input = False

        # In case there are, hide the message and show the checklist
        else:
            checklist_div_style = display_component(checklist_div_style)
            no_expectations_div_style = hide_component(no_expectations_div_style)
            delete_expectations_div_style = display_component(
                delete_expectations_div_style
            )
            disabled_input = True

        # Returning updated styles
        return (
            checklist_div_style,
            no_expectations_div_style,
            delete_expectations_div_style,
            disabled_input
        )

    @app.callback(
        [
            Output("type_exp_param_div", "style"),
            Output("length_exp_param_div", "style"),
            Output("values_exp_param_div", "style"),
            Output("min_value_exp_param_div", "style"),
            Output("max_value_exp_param_div", "style")
        ],
        [
            Input("new_expectation_button", "n_clicks"),
            Input("supported_expectations_dropdown", "value")
        ],
        [
            State("type_exp_param_div", "style"),
            State("length_exp_param_div", "style"),
            State("values_exp_param_div", "style"),
            State("min_value_exp_param_div", "style"),
            State("max_value_exp_param_div", "style")
        ],
        prevent_initial_call=True
    )
    def show_expectation_parameter_inputs(
        new_expectation: int,
        selected_expectation: str,
        type_div_style: dict,
        length_div_style: dict,
        values_div_style: dict,
        min_value_div_style: dict,
        max_value_div_style: dict,
    ) -> (dict, dict, dict, dict):
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
            "type": type_div_style,
            "length": length_div_style,
            "values": values_div_style,
            "min_value": min_value_div_style,
            "max_value": max_value_div_style
        }

        if is_trigger("new_expectation_button") or not selected_expectation:
            expectation_params = EMPTY_LIST

        else:
            expectation_id = EXPECTATIONS_MAP[selected_expectation]
            expectation_params = EXPECTATION_PARAMS[expectation_id]

        for param in params_div_map:
            if param in expectation_params:
                params_div_map[param] = display_component(params_div_map[param])
            else:
                params_div_map[param] = hide_component(params_div_map[param])

        return list(params_div_map.values())

    def parse_parameter(param_name: str, value: str) -> any or None:
        """
        Returns a parsed parameter in case it is correct. If not, it returns None.

        :param param_name: String with the name of the parameter.
        :param value: String with non-parsed value given to the parameter.
        """
        parsed_param = None
        if param_name == "type":
            if value in SUPPORTED_GE_EXP_TYPES:
                parsed_param = value
        elif param_name == "length":
            if value.isnumeric():
                parsed_param = value
        elif param_name == "values":
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
        elif param_name == "min_value" or param_name == "max_value":
            value = value.replace(",", ".")
            try:
                parsed_param = float(value)
            except ValueError:
                pass
        return parsed_param

    def write_expectation_in_config(
        expectation_set_name: str, expectation_id: str, parameters_dict: dict
    ) -> None:
        """
        This function creates a new file to write down a configuration for an expectation
        set, or opens a created file to append new expectations and their parameters.

        :param expectation_set_name: String with the name of the expectation set.
        :param expectation_id: String with the name of the new expectation to be added.
        :param parameters_dict: Dictionary with parameters of this new expectation.
        """
        expectation_set_path = get_expectation_set_path(expectation_set_name)
        if not exists_path(expectation_set_path):
            with open(expectation_set_path, "w") as fp:
                json.dump(EMPTY_DICT, fp)
        with open(expectation_set_path, "r") as fp:
            config_dict = json.load(fp)

        config_dict[expectation_id] = parameters_dict

        with open(expectation_set_path, "w") as fp:
            json.dump(config_dict, fp)

    def delete_expectation_in_config(
        expectation_set_name: str, expectation_ids: list
    ) -> None:
        """
        This function creates a new file to write down a configuration for an expectation
        set, or opens a created file to append new expectations and their parameters.

        :param expectation_set_name: String with the name of the expectation set.
        :param expectation_ids: List with names of expectations to be deleted.
        """
        expectation_set_config_path = get_expectation_set_path(expectation_set_name)
        with open(expectation_set_config_path, "r") as fp:
            config_dict = json.load(fp)

        for expectation_id in expectation_ids:
            del config_dict[expectation_id]

        with open(expectation_set_config_path, "w") as fp:
            json.dump(config_dict, fp)

    def build_expectation_interface_name(expectation_name: str, column_name: str) -> str:
        """
        Builds expectation interface name from expectation name and column name.

        :param expectation_name: String with expectation name.
        :param column_name: String with column name.

        :return: String with interface name.
        """
        spacer = " " if EXPECTATION_CONJUNCTION else ""
        return expectation_name + spacer + EXPECTATION_CONJUNCTION + spacer + column_name

    @app.callback(
        Output("expectations_checklist", "options"),
        [
            Input("open_expectation_set_definer_button", "n_clicks"),
            Input("add_expectation_button", "n_clicks"),
            Input("delete_expectation_button", "n_clicks")
        ],
        [
            State("supported_expectations_dropdown", "value"),
            State("expectation_set_name_input", "value"),
            State("table_columns_dropdown", "value"),
            State("expectations_checklist", "options"),
            State("expectations_checklist", "value"),
            State("type_exp_param_input", "value"),
            State("length_exp_param_input", "value"),
            State("values_exp_param_input", "value"),
            State("min_value_exp_param_input", "value"),
            State("max_value_exp_param_input", "value"),

        ]
    )
    def add_new_expectation(
        open_set_definer: int,
        add_expectation: int,
        delete_expectation: int,
        selected_expectation_name: str,
        expectation_set_name: str,
        selected_table_column: str,
        current_expectations: list,
        selected_expectations: list,
        type_input: str,
        length_input: str,
        values_input: str,
        min_value_input: str,
        max_value_input: str,
    ) -> (list, dict):
        if is_trigger("open_expectation_set_definer_button"):
            current_expectations = EMPTY_LIST
        elif is_trigger("add_expectation_button"):
            params_map = {
                "type": type_input,
                "length": length_input,
                "values": values_input,
                "min_value": min_value_input,
                "max_value": max_value_input
            }
            all_params_are_set = True

            expectation_id = EXPECTATIONS_MAP[selected_expectation_name]
            expectation_params = EXPECTATION_PARAMS[expectation_id]

            params_of_interest = dict()
            for param in expectation_params:
                parsed_param = parse_parameter(param, params_map[param])
                params_of_interest[param] = parsed_param
                if parsed_param is None:
                    all_params_are_set = False

                # Expectation will not be added if min value is greater than max
                # value
                if "min_value" in params_of_interest and "max_value" in params_of_interest:
                    if params_of_interest["min_value"] > params_of_interest["max_value"]:
                        all_params_are_set = False
            if all_params_are_set:
                write_expectation_in_config(
                    expectation_set_name, expectation_id, params_of_interest
                )
                expectation_interface_name = build_expectation_interface_name(
                    selected_expectation_name, selected_table_column
                )
                current_expectations.append(expectation_interface_name)

        elif is_trigger("delete_expectation_button"):
            expectation_ids = list()
            for interface_name in selected_expectations:

                # Getting the expectations to be removed
                expectation_ids.append(EXPECTATIONS_MAP[" ".join(interface_name.split(" ")[:-2])])

                # Removing the expectations from the interface
                current_expectations.remove(interface_name)

            # Finally, deleting selected expectations in configuration
            delete_expectation_in_config(expectation_set_name, expectation_ids)

        return current_expectations

    @app.callback(
        Output("validation_dropdown", "options"),
        [
            Input("validate_dataset_button", "n_clicks"),
            Input("delete_validations_button", "n_clicks")
        ],
        [
            State("imported_datasets_checklist", "value"),
            State("expectation_sets_checklist", "value")
        ]
    )
    def update_validation_listing(
        validate: int,
        delete_validations: int,
        selected_datasets: list,
        selected_expectation_sets: list
    ) -> list:
        validations_path = get_validations_path()

        if is_trigger("validate_dataset_button"):
            if list_has_one_item(selected_datasets)\
                    and list_has_one_item(selected_expectation_sets):
                dataset_name = get_value(selected_datasets)
                expectation_set_name = get_value(selected_expectation_sets)
                create_ge_expectation_suite(
                    ge_context, ExpectationSuiteName(expectation_set_name)
                )

        elif is_trigger("delete_validations_button"):
            current_validations = get_validation_file_names()
            for validation_name in current_validations:
                validation_path = join_paths(validations_path, validation_name)
                delete_file(validation_path)

        return get_validation_file_names()

    @app.callback(
        Output("delete_validations_div", "style"),
        [
            Input("validate_dataset_button", "n_clicks"),
            Input("delete_validations_button", "n_clicks")
        ],
        [
            State("delete_validations_div", "style"),
            State("validation_dropdown", "options")
        ]
    )
    def toggle_delete_validations_div(
        make_validation: int,
        delete_validations: int,
        div_style: dict,
        current_validations: list
    ) -> dict:
        """
        Displays or hides button to delete all validations, depending on whether there
        are any validations to be deleted or not.

        :param div_style: Dictionary with current style of the Div containing the delete
        button.
        :param current_validations: List with currently available validations.

        :return: Dictionary with updated style.
        """
        if is_list_empty(current_validations):
            div_style = hide_component(div_style)
        else:
            div_style = display_component(div_style)
        return div_style

    return app
