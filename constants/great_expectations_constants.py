SINGLE_COLUMN_EXPECTATIONS_MAP = {
    "Values to be unique": "expect_column_values_to_be_unique",
    "Values to not be null": "expect_column_values_to_not_be_null",
    "Values to be in set": "expect_column_values_to_be_in_set",
    "Values to be of type": "expect_column_values_to_be_of_type",
    "Values to be between": "expect_column_values_to_be_between",
    "Value lengths to equal": "expect_column_value_lengths_to_equal"
}
MULTICOLUMN_EXPECTATIONS_MAP = {
    "Values from columns to be unique": "expect_multicolumn_values_to_be_unique",
    "Values in first to be greater than in second": "expect_column_pair_values_A_to_be_greater_than_B",
    "Values from columns to be in set": "expect_column_pair_values_to_be_in_set"
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
MULTICOLUMN_EXPECTATIONS_N_COLUMNS = {
    "expect_column_pair_values_A_to_be_greater_than_B": 2,
    "expect_column_pair_values_to_be_in_set": 2,
    "expect_multicolumn_values_to_be_unique": None
}
MULTICOLUMN_EXP_NEEDS_GE_NAME = "expect_column_pair_values_A_to_be_greater_than_B"
SUPPORTED_GE_EXP_TYPES = [
    "int",
    "bool",
    "float",
    "str",
]
EXPECTATION_CONJUNCTION = "over"

# Expectation parameter constants
# Single column expectations
TYPE = "type_"
VALUE_SET_SINGLE = "value_set"
LENGTH = "value"
MIN_VALUE = "min_value"
MAX_VALUE = "max_value"

# Multicolumn expectations
COLUMN_A = "column_A"
COLUMN_B = "column_B"
COLUMN_LIST = "column_list"
OR_EQUAL = "or_equal"
VALUE_SET_MULTI = "value_pairs_set"

# validation_operations::save_validation constants
BATCH_KWARGS = "batch_kwargs"
EXPECTATION_SUITE_NAMES = "expectation_suite_names"
