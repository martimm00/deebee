import os

LOCALHOST = r"http://127.0.0.1:8050"
DATA_DIRECTORY = r"data"
IMPORT_DIRECTORY = r"imports"
UPLOAD_DIRECTORY = r"temp"
IMPORT_DIRECTORY_PATH = os.path.join(DATA_DIRECTORY, IMPORT_DIRECTORY)
UPLOAD_DIRECTORY_PATH = os.path.join(DATA_DIRECTORY, UPLOAD_DIRECTORY)
PROFILE_REPORTS_PATH = r"profile_reports"
HIDE_COMPONENT = {"display": "none"}
GREAT_EXPECTATIONS_DIR = r"great_expectations"
GREAT_EXPECTATIONS_PATH = os.path.join(DATA_DIRECTORY, GREAT_EXPECTATIONS_DIR)
EXPECTATION_SUITES_PATH = r"data/great_expectations/expectations"
EXPECTATION_SETS_PATH = r"expectation_sets"
VALIDATION_RESULTS_PATH = r"validation_results"
GE_VALIDATIONS_PATH = os.path.join(
    *[
        DATA_DIRECTORY,
        "great_expectations",
        "uncommitted",
        "data_docs",
        "local_site",
        "validations",
    ]
)