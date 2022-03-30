def is_list_empty(list_to_be_checked: list) -> bool:
    """
    Returns if a list is empty or not.

    :param list_to_be_checked: List to be checked.

    :return: Bool.
    """
    return not bool(list_to_be_checked)


def get_value(something: any) -> any:
    if something:
        if len(something) == 1:
            return something[0]
    return None
