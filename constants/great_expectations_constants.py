EXPECTATIONS_MAP = {
    "Values to be unique": "expect_column_values_to_be_unique",
    "Values to not be null": "expect_column_values_to_not_be_null",
    "Values to be in set": "expect_column_values_to_be_in_set",
    "Values to be of type": "expect_column_values_to_be_of_type",
    "Values to be between": "expect_column_values_to_be_between",
    "Value lengths to equal": "expect_column_value_lengths_to_equal"
}
NUMERIC_ONLY_EXPECTATIONS = [
    "Values to be between"
]
NON_NUMERIC_ONLY_EXPECTATIONS = [
    "Lengths to equal",
]
EXPECTATION_INTERFACE_NAME_DIVIDER = "over"
EXPECTATION_N_PARAMS = {
    "expect_column_values_to_be_unique": 0,
    "expect_column_values_to_not_be_null": 0,
    "expect_column_values_to_be_in_set": 1,
    "expect_column_value_lengths_to_equal": 1,
    "expect_column_values_to_be_of_type": 1,
    "expect_column_values_to_be_between": 2,
}
EXPECTATION_PARAMS = {
    "expect_column_values_to_be_unique": {},
    "expect_column_values_to_not_be_null": {},
    "expect_column_values_to_be_in_set": {
        "values": "list"
    },
    "expect_column_value_lengths_to_equal": {
        "length": "int"
    },
    "expect_column_values_to_be_of_type": {
        "type": "str"
    },
    "expect_column_values_to_be_between": {
        "min_value": "int",
        "max_value": "int"
    },
}
SUPPORTED_GE_EXP_TYPES = [
    "int",
    "bool",
    "float",
    "str",
]
OUTDATED = "[OUTDATED] "
