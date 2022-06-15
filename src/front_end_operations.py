import os
import dash
import webbrowser


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
