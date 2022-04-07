import dash
from dash import Output, Input, State
import dash_bootstrap_components as dbc

from src.defaults import EMPTY_LIST, EMPTY_STRING

from src.utils import (
    get_value,
    read_dataset,
    is_list_empty,
    list_has_one_item,
    infer_csv_separator,
    build_profile_report
)
from src.front_end_operations import (
    is_trigger,
    hide_component,
    display_component,
    open_file_in_browser,
    get_checklist_components,
)
from src.low_level_operations import (
    move,
    rename,
    join_paths,
    delete_file,
    has_extension,
    is_dataset_name,
    is_csv_file_by_name,
    get_import_dir_path,
    get_profile_report_path,
    get_imported_dataset_path,
    get_uploaded_dataset_path,
    get_uploaded_dataset_names,
    is_profile_report_available,
    get_profile_report_title_from_dataset_name
)


def set_callbacks(app) -> dash.Dash:

    @app.callback(
        [
            Output("dataset_checklist_div", "style"),
            Output("no_imported_dataset_div", "style")
        ],
        Input("imported_datasets_checklist", "options"),
        [
            State("dataset_checklist_div", "style"),
            State("no_imported_dataset_div", "style")
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

    def refresh_imported_dataset_listing() -> list:
        """
        Returns a list of dcc.Checklist components, based on imported datasets.

        :return: List of checklist components.
        """
        imported_datasets = get_uploaded_dataset_names()
        return get_checklist_components(imported_datasets)

    def dataset_name_is_already_in_use(dataset_name: str) -> bool:
        """
        Returns if the name of a recently imported dataset is already in use.

        :param dataset_name: String with the name of the dataset.

        :return: Bool.
        """
        return dataset_name in get_uploaded_dataset_names()

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
            Output("rename_dataset_input", "value")
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
            State("rename_dataset_input", "value")
        ]
    )
    def update_dataset_listing(
        new_upload,
        delete: int,
        rename_dataset: int,
        available_options: list,
        selected_datasets: list,
        uploaded_file_names: list,
        new_dataset_name: str
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
        return available_options, EMPTY_LIST, EMPTY_STRING

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
        :param close_preview: Close preview button has been clicked.
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
        State("imported_datasets_checklist", "value"),
    )
    def see_dataset_insights(open_insights: int, selected_datasets: list) -> None:
        if is_trigger("open_insights_button"):
            if list_has_one_item(selected_datasets):
                dataset_name = get_value(selected_datasets)
                if not is_profile_report_available(dataset_name):
                    build_profile_report(dataset_name)
                file_path = get_profile_report_path(dataset_name)
                print("opening file in browser...")
                open_file_in_browser(file_path)

        return

    return app
