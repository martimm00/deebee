import os
import dash
import webbrowser


def open_in_browser(url: os.path) -> None:
    """
    Opens an URL in a new browser tab.

    :param url: Path with a URL to a local HTML file.
    """
    webbrowser.open(url)


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


def get_checklist_components(item_names: list) -> list:
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


def hide_component(current_style: dict) -> dict:
    """
    Allows a component to be hidden in the interface.

    :param current_style: Dictionary with the current style of the component.

    :return: Updated style.
    """
    current_style["display"] = "none"
    return current_style
