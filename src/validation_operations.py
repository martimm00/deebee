from src.expectation_parameters import requires_parameters, get_number_of_arguments_required


def compute_results(
    expectations_ids: dict, expectation_and_columns: dict, batch
) -> None:
    """
    This function is used to compute validation results when applying
    an Expectation Suite to a dataset.
    :param expectations_ids: String with great_expectations
    expectation names.
    :param expectation_and_columns: Dictionary that contains all
    currently defined expectations, the columns where they have to
    be applied and their params (if any).
    :param batch: great_expectations data batch object.
    :return: String with warning message.
    """
    compute_results_by_expectation_type(
        expectation_and_columns, expectations_ids
    )

    # Saving Expectation Suite to JSON file
    batch.save_expectation_suite(discard_failed_expectations=False)


def compute_results_by_expectation_type(
    expectation_and_columns: dict, expectations_ids: dict
) -> None:
    """
    This function is used to compute validation results when applying
    an Expectation Suite to a dataset, by expectation type.
    :param expectation_and_columns: Dictionary that contains all
    currently defined expectations, the columns where they have to
    be applied and their params (if any).
    :param expectations_ids: String with great_expectations
    expectation names.
    :return: String with warning message.
    """
    for expectation_name in expectation_and_columns:
        compute_result_for_each_expectation(
            expectation_and_columns[expectation_name],
            expectation_name,
            expectations_ids,
        )


def compute_result_for_each_expectation(
    expectation_type_dict: dict,
    expectation_name: str,
    expectations_ids: dict,
) -> None:
    """
    This function is used to compute validation results when applying
    an Expectation Suite to a dataset, one expectation at a time.
    :param expectation_type_dict: Dictionary that contains all
    currently defined expectations, the columns where they have to be
    applied and their params (if any).
    :param expectation_name: String with expectation name.
    :param expectations_ids: String with great_expectations
    expectation names.
    :return: String with warning message.
    """
    for column in expectation_type_dict:
        parameters = expectation_type_dict[column]

        # If the expectation requires any parameters
        if requires_parameters(expectation_name):

            # Getting the number of parameters to be read
            required_argument_count = get_number_of_arguments_required(expectation_name)
            if required_argument_count == 1:
                expectations_ids[expectation_name](column, parameters)
            elif required_argument_count == 2:
                value1, value2 = parameters
                expectations_ids[expectation_name](column, value1, value2)
        else:
            getattr(batch, expectation_id)
            expectations_ids[expectation_name](column)
