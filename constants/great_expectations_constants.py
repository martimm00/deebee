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
    "Value lengths to equal",
]
EXPECTATION_INTERFACE_SEPARATOR_STRING = "over"
EXPECTATION_PARAMS = {

    # Single column expectations
    "expect_column_values_to_be_unique": {},
    "expect_column_values_to_not_be_null": {},
    "expect_column_values_to_be_in_set": {
        "value_set": "list"
    },
    "expect_column_value_lengths_to_equal": {
        "value": "int"
    },
    "expect_column_values_to_be_of_type": {
        "type_": "str"
    },
    "expect_column_values_to_be_between": {
        "min_value": "int",
        "max_value": "int"
    },

    # Multicolumn expectations
    "expect_multicolumn_values_to_be_unique": {
        "column_list": "list"
    },
    "expect_column_pair_values_A_to_be_greater_than_B": {
        "column_A": "str",
        "column_B": "str",
        "or_equal": "bool"
    },
    "expect_column_pair_values_to_be_in_set": {
        "column_A": "str",
        "column_B": "str",
        "value_pairs_set": "list"
    }
}
SUPPORTED_GE_EXP_TYPES = [
    "int",
    "bool",
    "float",
    "str",
]
EXPECTATION_CONJUNCTION = "over"

# Expectation parameter constants
TYPE = "type_"
VALUE_SET = "value_set"
LENGTH = "value"
MIN_VALUE = "min_value"
MAX_VALUE = "max_value"

# validation_operations::save_validation constants
BATCH_KWARGS = "batch_kwargs"
EXPECTATION_SUITE_NAMES = "expectation_suite_names"
