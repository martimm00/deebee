from constants.great_expectations_constants import EXPECTATION_N_PARAMS

from src.utils import is_list_empty


def get_number_of_arguments_required(expectation_name: str) -> int:
    """
    Returns the number of parameters required by a specific expectation.

    :param expectation_name: String with the name of the expectation.

    :return: Int with the number of parameters that the expectation requires.
    """
    return EXPECTATION_N_PARAMS[expectation_name]


def requires_parameters(expectation_name: str) -> bool:
    """
    Tells the app whether an expectation requires parameters or not.

    :param expectation_name: String with the name of the expectation.

    :return: Bool.
    """
    number_of_arguments_required = get_number_of_arguments_required(expectation_name)
    return bool(number_of_arguments_required)


def check_number_of_params_is_correct(expectation_name: str, parameters: list) -> bool:
    """
    Checks if the number of parameters for an expectation is correct, as the name
    suggests.

    :param expectation_name: Str that contains the expectation name.
    :param parameters: List that contains all parameters that have to be checked.

    :return: Bool that tells the app if the number of parameters for the current
    expectation is correct or not.
    """
    if requires_parameters(expectation_name):

        # In case no parameters are provided
        if is_list_empty(parameters):
            return False

        if expectation_name == "expect_column_value_lengths_to_equal":
            if len(parameters) != 1:
                return False
            if not check_params_type_is_correct(parameters):
                return False

        # For those expectations which need two parameters
        elif get_number_of_arguments_required(expectation_name) == 2:
            if len(parameters) != 2:
                return False
            if not check_params_type_is_correct(parameters):
                return False
            if not check_order_of_parameters_is_correct(parameters):
                return False
    return True


def check_order_of_parameters_is_correct(parameters: list) -> bool:
    """
    Returns if at an expectation with parameters of type Min, Max the second value is
    equal or greater than the first one.

    :param parameters: List with extracted parameters.

    :return: Bool that tells the app if this requirement is accomplished.
    """
    return parameters[0] <= parameters[1]


def check_params_type_is_correct(parameters: list) -> bool:
    """
    Checks if at an expectation with parameters of type Min, Max both values are
    integers.

    :param parameters: List of parameters to be checked.

    :return: Bool.
    """
    for param in parameters:
        if not isinstance(param, int):
            return False
    return True


def extract_parameters(parameters: str) -> list or None:
    """
    Helps to extract expectation parameters from a string.

    :param parameters: Str that contains all introduced parameters.

    :return: List of parameters with correct type or None.
    """
    if parameters:

        # Splitting string of parameters into a list
        parameters_list = parameters.split(",")

        # Converting the list into a set to avoid duplicity
        parameters_set = set(parameters_list)

        # Back to list
        parameters_list = list(parameters_set)

        # Removing empty parameters from the list
        for parameter in parameters_list:
            if not parameter:
                parameters_list.remove(parameter)
        try:

            # Converting them into int type if possible
            return [int(param) for param in parameters_list]
        except ValueError:
            return parameters_list

    # If parameters was an empty string, return None
    return None
