import os
import dash
import webbrowser
import dash_bootstrap_components as dbc

from constants.great_expectations_constants import EXPECTATION_INTERFACE_SEPARATOR_STRING


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


def get_callback_context() -> dash._callback_context.CallbackContext:
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


def build_list_group_item(
    item_id: dict, text: str, item_color=None, item_href=None
) -> dbc.ListGroupItem:
    """
    Builds ListGroupItems from the Dash Bootstrap Components library.
    :param item_id: Dictionary that contains item id.
    :param text: String that contains item text.
    :param item_color: String that tells which color the item has to
    be.
    :param item_href: String with item href, which points to the HTML
    validation summary file.
    :return: dbc.ListGroupItem object to be added to a dbc.ListGroup
    object.
    """
    return dbc.ListGroupItem(
        text,
        color=item_color,
        id=item_id,
        href=item_href,
    )


def get_checklist_components(item_names: list) -> list:
    """
    Returns checklist components given the name of some items.

    :param item_names: List with item names.
    """
    return [get_checklist_component(item_name) for item_name in item_names]


def get_checklist_component_value(component: dict) -> any:
    """
    Returns the value of a Dash dcc.Checklist component.

    :param component: Dictionary.

    :return: Any value contained in this field.
    """
    return component["value"]


def get_checklist_component_by_value(
    list_of_components: list, value: str
) -> dict or None:
    """
    Returns the checklist component according to a given value.

    :param list_of_components: List of checklist components.
    :param value: String with the value to be looked for.

    :return: Dictionary with the component or None, in case it is not inside the given
    list.
    """
    for component in list_of_components:
        if get_checklist_component_value(component) == value:
            return component

    # Returning None if the value is not part of any component in the list
    return None


def display_component(current_style: dict) -> dict:
    """
    Allows a component to be displayed in the interface.

    :param current_style: Dictionary with the current style of the component.

    :return: Updated style.
    """
    current_style["display"] = "block"
    return current_style


def add_option_to_checklist(options: list, new_element: str) -> None:
    """
    This function can be used to add an option to a checklist, by
    adding a checklist component to a list.
    :param options: List of current options.
    :param new_element: String with the new element to be added.
    """
    item = get_checklist_component(new_element)
    if item not in options:
        options.append(item)


def add_options_to_checklist(options: list, new_elements: list) -> list:
    """
    This function can be used to add options to a checklist, by
    adding checklist components to a list.
    :param options: List of current options.
    :param new_elements: List of new elements to add.
    :return: List of updated options.
    """
    for element in new_elements:
        add_option_to_checklist(options, element)
    return options


def hide_component(current_style: dict) -> dict:
    """
    Allows a component to be hidden in the interface.

    :param current_style: Dictionary with the current style of the component.

    :return: Updated style.
    """
    current_style["display"] = "none"
    return current_style


def get_expectation_info_from_interface_name(
    expectation_interface_name: str,
) -> (str, str):
    """
    Returns some expectation information by splitting its interface name.

    :param expectation_interface_name: String with the name.

    :return: String with the name of the expectation, string with the name of the dataset
    column where it has to be applied.
    """
    divider = EXPECTATION_INTERFACE_SEPARATOR_STRING
    expectation_name = get_expectation_name_from_interface_name(
        expectation_interface_name, divider
    )
    expectation_column = get_expectation_column_from_interface_name(
        expectation_interface_name, divider
    )
    return expectation_name, expectation_column


def get_expectation_name_from_interface_name(
    expectation_interface_name: str, divider: str
) -> str:
    """
    Returns expectation name from complete expectation name.

    :param expectation_interface_name: String with the interface expectation name.
    :param divider: String that is in between the expectation name and the dataset column
    where it has to be applied. This argument can be changed at any time in
    defaults.py.

    :return: String with the expectation name.
    """
    divider_beginning = expectation_interface_name.find(divider)
    return expectation_interface_name[: divider_beginning - 1]


def get_expectation_column_from_interface_name(
    expectation_interface_name: str, divider: str
) -> str:
    """
    Returns dataset column from complete expectation name.

    :param expectation_interface_name: String with the interface expectation name.
    :param divider: String that is in between the expectation name and the dataset column
    where it has to be applied. This argument can be changed at any time in defaults.py.

    :return: String with the dataset column.
    """
    divider_beginning = expectation_interface_name.find(divider)
    divider_ending = divider_beginning + len(divider) + 1
    expectation_column = expectation_interface_name[divider_ending:]
    expectation_column = expectation_column.strip("'")
    return expectation_column


