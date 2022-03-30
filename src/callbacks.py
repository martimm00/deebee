import dash
from dash import Output, Input, State

from src.utils import get_value, is_list_empty
from src.front_end_operations import (
    is_trigger,
    hide_component,
    display_component,
    get_checklist_components,
)
from src.low_level_operations import (
    move,
    delete_file,
    get_imported_dataset_path,
    get_uploaded_dataset_names,
    get_uploaded_dataset_path,
)


def set_callbacks(app) -> dash.Dash:

    @app.callback(
        [
            Output("dataset_checklist_div", "style"),
            Output("no_imported_dataset_div", "style"),
        ],
        Input("imported_datasets_checklist", "options"),
        [
            State("dataset_checklist_div", "style"),
            State("no_imported_dataset_div", "style"),
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

    @app.callback(
        [
            Output("imported_datasets_checklist", "options"),
            Output("imported_datasets_checklist", "value"),
        ],
        [
            Input("dataset_uploader", "isCompleted"),
            Input("delete_dataset_button", "n_clicks"),
        ],
        [
            State("imported_datasets_checklist", "options"),
            State("dataset_uploader", "fileNames"),
            State("imported_datasets_checklist", "value"),
        ]
    )
    def update_dataset_listing(
        new_upload,
        delete: int,
        available_options: list,
        uploaded_file_name: list,
        selected_datasets: list
    ) -> (list, list):
        """
        Updates imported datasets listing.

        :param new_upload: A new import has been performed.
        :param delete: Delete button has been clicked.
        :param available_options: List with current checklist options.
        :param uploaded_file_name: List containing the name of the imported dataset.
        :param selected_datasets: List with names of datasets selected by the user.

        :return: List with updated checklist options, and empty list.
        """
        # If a dataset has been uploaded
        if is_trigger("dataset_uploader"):

            # Get dataset name and path
            dataset_name = get_value(uploaded_file_name)
            print("Dataset name is", dataset_name)
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
            if not is_list_empty(selected_datasets):
                delete_datasets(selected_datasets)
        available_options = refresh_imported_dataset_listing()
        return available_options, list()

    return app
