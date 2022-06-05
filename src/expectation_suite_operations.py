from objects.expectation_suite_name import ExpectationSuiteName


def create_ge_expectation_suite(context, name: ExpectationSuiteName) -> None:
    context.create_expectation_suite(name.ge_name, overwrite_existing=True)


def get_expectation_suite_name_object(name: str) -> ExpectationSuiteName:
    return ExpectationSuiteName(name)
