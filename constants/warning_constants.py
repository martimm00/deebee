WARNING_MESSAGES = {
    "empty_message": "",
    "upload_dataset_warning": "Failed to upload the file. The file is not actually CSV or EXCEL.",
    "upload_excel_file_warning": {
        "first_sheet_only": "You have uploaded an EXCEL file. Only the first sheet will be loaded as a dataset.",
        "wrong_table_format": "Some columns are called 'Unnamed', and that is a sign that the dataset is not correctly "
        "arranged in the excel sheet. Please import a dataset with a correct table.",
    },
    "auto_expectations_warning": "Please, first enter a valid expectation suite name and select a dataset.",
    "open_rename_modal_warning": {
        "no_dataset_selected": "Please, select one dataset.",
        "invalid_name": "Invalid dataset name. Please try another name.",
        "already_in_use": "Dataset name is already in use. Please try another name.",
    },
    "expectation_suite_definition_warning": {
        "empty": "Empty expectation suites have no sense!",
        "too_quick": "Didn't have enough time to update the expectation suite.",
        "wrong_expectations": "Unexpected error happened when applying expectations to dataset. Some defined "
        "expectations could be damaged or non-existent.",
    },
    "expectation_suite_warning": {
        "invalid_name": "Failed to define expectation suite because input name is not valid. The name cannot contain "
        "dots.",
        "no_dataset_selected": "Failed to define expectation suite. Please, select a dataset to work on.",
    },
    "edit_expectation_suite_warning": {
        "no_expectation_suite_selected": "One expectation suite has to be selected.",
        "select_only_one": "Only one expectation suite can be edited at a time.",
        "no_datasets_compatible": "No compatible datasets are uploaded. Upload a compatible dataset first.",
    },
    "import_expectation_suite_warning": "Failed to import the expectation suite. Please try another file.",
    "export_expectation_suite_warning": {
        "no_expectation_suite_selected": "No expectation suite was selected.",
        "select_only_one": "Only one expectation suite can be exported at a time.",
    },
    "validation_warning": {
        "select_expectation_suite_and_file": "Please, select an expectation suite and a file.",
        "only_one_expectation_suite": "One single expectation suite can be used to validate at a time.",
        "select_a_dataset": "No dataset was selected.",
        "select_only_one_dataset": "One single dataset can be validated at a time.",
        "dataset_not_compatible": "Columns found in expectations do not match dataset columns. Please, try validating "
        "another dataset.",
        # The following warning message could be also shown when creating an Expectation Suite.
        "wrong_expectations": "An error happened when applying expectations to the dataset. It seems the selected "
        "dataset has the same columns as the one that was used to create the expectation suite. "
        "However, the columns of the two datasets do not follow the same data pattern or do not "
        "have the same type.",
    },
    "remove_validation_warning": "Click on the validations you want to remove, then tap the button again.",
    "export_validation_result_warning": "Click on one validation that you want to export, then tap the button again. "
    "Only one validation can be exported at a time.",
}
