from objects.expectation_suite_name import ExpectationSuiteName


def create_empty_ge_expectation_suite(context, name_object: ExpectationSuiteName):
    """
    Creates a new, empty GE Expectation Suite.

    :param context: Great Expectations' context object.
    :param name_object: ExpectationSuiteName object defining the name.

    :return: GE's Expectation Suite object.
    """
    return context.create_expectation_suite(name_object.name, overwrite_existing=True)


def get_expectation_suite_name_object(name: str) -> ExpectationSuiteName:
    """
    Returns GE's Expectation Suite name object.

    :param name: String with the name of the Expectation Suite.

    :return: Expectation Suite name object.
    """
    return ExpectationSuiteName(name)
