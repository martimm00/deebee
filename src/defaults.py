import os

LOCALHOST = r"http://127.0.0.1:8050"
DATA_DIRECTORY = r"data"
IMPORT_DIRECTORY = r"imports"
UPLOAD_DIRECTORY = r"temp"
IMPORT_DIRECTORY_PATH = os.path.join(DATA_DIRECTORY, IMPORT_DIRECTORY)
UPLOAD_DIRECTORY_PATH = os.path.join(DATA_DIRECTORY, UPLOAD_DIRECTORY)
PROFILE_REPORTS_PATH = r"profile_reports"
EMPTY_STRING = ""
EMPTY_LIST = list()
HIDE_COMPONENT = {"display": "none"}
GREAT_EXPECTATIONS_DIR = r"great_expectations"
GREAT_EXPECTATIONS_PATH = os.path.join(DATA_DIRECTORY, GREAT_EXPECTATIONS_DIR)
EXPECTATION_SUITES_PATH = r"expectation_suites"
VALIDATION_RESULTS_PATH = r"validation_results"
LOCAL_SITE = os.path.join(
    *[
        DATA_DIRECTORY,
        "great_expectations",
        "uncommitted",
        "data_docs",
        "local_site",
        "validations",
    ]
)
SUPPORTED_DATASET_TYPES = ["csv", "xlsx"]
SUPPORTED_VALIDATION_DATA_TYPES = [
    "int",
    "int32",
    "int64",
    "uint",
    "uint32",
    "uint64",
    "bool",
    "float",
    "float32",
    "float64",
    "str",
]
MAIN_COL_STYLE={
    "padding": "30px",
    "height": "80vh",
    "border": "3px black solid",
    "borderRadius": "20px",
    "margin": "10px",
    "backgroundColor": "#e3e3e3",
}
CHECKLIST_DIV_STYLE = {
    "marginTop": "20px",
    "marginBottom": "20px",
    "padding": "25px",
    "paddingTop": "23px",
    "width": "100%",
    "height": "30vh",
    "backgroundColor": "#fff",
    "border": "3px black solid",
    "borderRadius": "20px",
    "overflow": "scroll",
}
