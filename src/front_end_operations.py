import os
import dash
import webbrowser

from constants.great_expectations_constants import (
    EXPECTATION_CONJUNCTION,
    MULTICOLUMN_EXPECTATIONS_MAP,
    SINGLE_COLUMN_EXPECTATIONS_MAP
)

from src.dataset_operations import get_imported_dataset_names


def open_in_browser(url: os.path) -> None:
    """
    Opens an URL in a new browser tab.

    :param url: Path with a URL to a local HTML file.
    """
    webbrowser.open(url)


def open_file_in_browser(path: os.path) -> None:
    """
    Opens an HTML file in a new browser tab given its path.

    :param path: Path where the file is allocated.
    """
    real_path = os.path.realpath(path)
    path_to_open = "file:" + os.path.sep * 2 + real_path
    open_in_browser(path_to_open)


def get_callback_context():
    """
    Provides callback context for the Dash app.

    :return: Dash object.
    """
    return dash.callback_context


def is_trigger(component_name) -> bool:
    """
    Returns if the given component has been (one of) the trigger(s).

    :param component_name: String with the name of a component.

    :return: Bool.
    """
    # Getting callback context
    ctx = get_callback_context()
    return component_name in [tc["prop_id"].split(".")[0] for tc in ctx.triggered]


def get_checklist_component(item_name: str) -> dict:
    """
    Returns a dcc.Checklist component.

    :param item_name: String with the name of the item.

    :return: Dictionary.
    """
    return {"label": item_name, "value": item_name}


def get_checklist_components(item_names: list) -> list:
    """
    Returns checklist components given the name of some items.

    :param item_names: List with item names.
    """
    return [get_checklist_component(item_name) for item_name in item_names]


def hide_component(current_style: dict) -> dict:
    """
    Allows a component to be hidden in the interface.

    :param current_style: Dictionary with the current style of the component.

    :return: Updated style.
    """
    current_style["display"] = "none"
    return current_style


def display_component(current_style: dict) -> dict:
    """
    Allows a component to be displayed in the interface.

    :param current_style: Dictionary with the current style of the component.

    :return: Updated style.
    """
    current_style["display"] = "block"
    return current_style


def refresh_imported_dataset_listing() -> (list, list):
    """
    Returns a list of dcc.Checklist components, based on imported datasets.

    :return: List of checklist components.
    """
    imported_datasets = get_imported_dataset_names()
    return get_checklist_components(imported_datasets)


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
