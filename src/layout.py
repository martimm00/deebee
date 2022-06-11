import dash
from dash import dcc
from dash import html
import dash_uploader as du
import dash_bootstrap_components as dbc

from constants.defaults import EMPTY_LIST, EMPTY_STRING
from constants.layout_shortcut_constants import (
    INPUT_STYLE,
    MAIN_COL_STYLE,
    CHECKLIST_DIV_STYLE
)
from constants.great_expectations_constants import (
    SUPPORTED_GE_EXP_TYPES,
    MULTICOLUMN_EXPECTATIONS_MAP,
    SINGLE_COLUMN_EXPECTATIONS_MAP
)


def create_layout(app: dash.Dash) -> dash.Dash:
    """
    Defines the layout of the tool.

    :param app: Dash.Dash object, the app itself.

    :return: The same Dash.Dash object, with a configured layout.
    """
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.H1(
                        "deebee",
                        style={
                            "fontSize": "60px",
                            "fontFamily": "Argent Demi Bold Font",
                            "color": "#ffd25d"
                        }
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H1(
                                        "Import"
                                    ),
                                    html.Div(
                                        [
                                            du.Upload(
                                                id="dataset_uploader",
                                                text="Drag and drop or browse files",
                                                text_completed=EMPTY_STRING,
                                                pause_button=False,
                                                cancel_button=False,
                                                filetypes=["csv", "xlsx"],
                                                max_files=1,
                                                upload_id="temp",
                                                default_style={
                                                    "height": "100px",
                                                    "border": "0px black solid",
                                                    "borderRadius": "20px"
                                                }
                                            )
                                        ],
                                        style={
                                            "width": "100%",
                                            "display": "inline-block",
                                            "marginTop": "15px",
                                            "marginBottom": "20px",
                                            "border": "3px black solid",
                                            "borderRadius": "20px",
                                            "backgroundColor": "#fff"
                                        }
                                    ),
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dcc.Input(
                                                                id="rename_dataset_input",
                                                                value=EMPTY_STRING,
                                                                type="text",
                                                                placeholder="New name",
                                                                style={
                                                                    "height": "38px",
                                                                    "width": "103%",
                                                                    "border": "3px black solid",
                                                                    "borderRadius": "20px",
                                                                    "paddingLeft": "10px",
                                                                    "paddingRight": "10px"
                                                                }
                                                            )
                                                        ]
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Button(
                                                                "Rename",
                                                                id="rename_dataset_button",
                                                                color="secondary"
                                                            )
                                                        ],
                                                        width=3,
                                                        style={
                                                            "textAlign": "right"
                                                        }
                                                    )
                                                ],
                                                justify="between"
                                            )
                                        ],
                                        id="rename_dataset_div",
                                        style={
                                            "width": "100%",
                                            "marginBottom": "20px",
                                            "height": "40px"
                                        }
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H3("Uploaded datasets")
                                                ],
                                                width=9
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                "Delete",
                                                                id="delete_dataset_button",
                                                                color="danger"
                                                            )
                                                        ],
                                                        id="delete_dataset_div",
                                                        style={"textAlign": "right"}
                                                    )
                                                ],
                                                width=3
                                            )
                                        ],
                                        justify="between"
                                    ),
                                    html.Div(
                                        [
                                            dcc.Checklist(
                                                id="imported_datasets_checklist",
                                                options=EMPTY_LIST,
                                                value=EMPTY_LIST,
                                                labelStyle={"display": "block"},
                                                inputStyle={"marginRight": "15px"}
                                            )
                                        ],
                                        id="imported_datasets_checklist_div",
                                        style=CHECKLIST_DIV_STYLE
                                    ),
                                    html.Div(
                                        [
                                            "There are no imported files."
                                        ],
                                        id="no_imported_datasets_div",
                                        style={
                                            "marginTop": "20px",
                                            "marginBottom": "20px",
                                            "padding": "25px",
                                            "paddingTop": "14vh",
                                            "width": "100%",
                                            "height": "30vh",
                                            "backgroundColor": "#fff",
                                            "border": "3px black solid",
                                            "borderRadius": "20px",
                                            "overflow": "scroll",
                                            "textAlign": "center",
                                            "display": "none"
                                        }
                                    ),
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Button(
                                                                "Preview table",
                                                                id="open_preview_table_button",
                                                                color="secondary"
                                                            )
                                                        ]
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Button(
                                                                "Insights",
                                                                id="open_insights_button",
                                                                color="secondary"
                                                            )
                                                        ]
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Button(
                                                                "Clear all insights",
                                                                id="clear_insights_button",
                                                                color="danger"
                                                            )
                                                        ],
                                                        id="clear_insights_div",
                                                        style={"display": "none"}
                                                    )
                                                ],
                                                justify="between"
                                            )
                                        ],
                                        style={"textAlign": "center"}
                                    )
                                ],
                                style=MAIN_COL_STYLE
                            ),
                            dbc.Col(
                                [
                                    html.H1(
                                        "Define"
                                    ),
                                    html.Div(
                                        [
                                            dcc.Checklist(
                                                id="expectation_sets_checklist",
                                                options=EMPTY_LIST,
                                                value=EMPTY_LIST,
                                                labelStyle={"display": "block"},
                                                inputStyle={"marginRight": "15px"}
                                            )
                                        ],
                                        id="expectation_sets_checklist_div",
                                        style=CHECKLIST_DIV_STYLE
                                    ),
                                    html.Div(
                                        [
                                            "There are no expectation sets."
                                        ],
                                        id="no_expectation_sets_div",
                                        style={
                                            "marginTop": "20px",
                                            "marginBottom": "20px",
                                            "padding": "25px",
                                            "paddingTop": "14vh",
                                            "width": "100%",
                                            "height": "30vh",
                                            "backgroundColor": "#fff",
                                            "border": "3px black solid",
                                            "borderRadius": "20px",
                                            "overflow": "scroll",
                                            "textAlign": "center",
                                            "display": "none"
                                        }
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Button(
                                                        "Define expectations",
                                                        id="open_expectation_set_definer_button",
                                                        color="secondary"
                                                    )
                                                ]
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                "Delete expectations",
                                                                id="delete_expectation_set_button",
                                                                color="danger"
                                                            ),
                                                        ],
                                                        id="delete_expectation_set_div",
                                                        style={
                                                            "display": "none",
                                                            "textAlign": "right"
                                                        }
                                                    )
                                                ]
                                            )
                                        ],
                                        justify="between"
                                    )
                                ],
                                style=MAIN_COL_STYLE
                            ),
                            dbc.Col(
                                [
                                    html.H1(
                                        "Validate"
                                    ),
                                    dcc.Dropdown(
                                        EMPTY_LIST,
                                        id="validation_dropdown",
                                        style={
                                            "marginTop": "20px",
                                            "marginBottom": "20px"
                                        }
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Button(
                                                        "Validate",
                                                        id="validate_dataset_button",
                                                        color="secondary"
                                                    )
                                                ]
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                "Delete all validations",
                                                                id="delete_validations_button",
                                                                color="danger"
                                                            ),
                                                        ],
                                                        id="delete_validations_div",
                                                        style={
                                                            "display": "none",
                                                            "textAlign": "right"
                                                        }
                                                    )
                                                ]
                                            )
                                        ],
                                        justify="between"
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H6(
                                                        "Confidence (%):",
                                                        style={"marginTop": "10px"}
                                                    )
                                                ],
                                                width=4
                                            ),
                                            dbc.Col(
                                                [
                                                    dcc.Input(
                                                        id="validation_confidence_input",
                                                        value=100,
                                                        style={
                                                            "height": "38px",
                                                            "width": "55px",
                                                            "border": "3px black solid",
                                                            "borderRadius": "20px",
                                                            "paddingLeft": "10px",
                                                            "paddingRight": "10px",
                                                            "marginBottom": "15px"
                                                        }
                                                    )
                                                ],
                                                width=2
                                            ),
                                        ],
                                        justify="start",
                                        style={"marginTop": "20px"},
                                    ),
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Button(
                                                                "Open result",
                                                                id="open_validation_result_button",
                                                                color="secondary"
                                                            )
                                                        ],
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Button(
                                                                "Export",
                                                                id="export_validation_result_button",
                                                                color="secondary"
                                                            )
                                                        ],
                                                    ),
                                                ],
                                                justify="between"
                                            )
                                        ],
                                        id="validation_operations_div",
                                        style={"display": "none"}
                                    )
                                ],
                                style=MAIN_COL_STYLE
                            )
                        ],
                        justify="evenly"
                    )
                ]
            ),

            # Modals
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(id="preview_table_modal_header_title")
                    ),
                    dbc.ModalBody(
                        [
                            html.Div(
                                id="preview_table_modal_body",
                                style={
                                    "width": "1500px"
                                }
                            )
                        ],
                        style={
                            "overflow": "scroll"
                        }
                    )
                ],
                id="preview_table_modal",
                autofocus=True,
                centered=True,
                fullscreen=True,
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        html.H1("Define expectations")
                    ),
                    dbc.ModalBody(
                        [
                            html.H5("Name:"),
                            dcc.Input(
                                id="expectation_set_name_input",
                                style=INPUT_STYLE
                            ),
                            html.H5("Table:"),
                            dcc.Dropdown(
                                id="imported_datasets_dropdown",
                                options=EMPTY_LIST,
                                style={
                                    "marginBottom": "20px"
                                }
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                "New single column",
                                                id="new_single_column_expectation_button",
                                                color="secondary"
                                            )
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                "New multicolumn",
                                                id="new_multicolumn_expectation_button",
                                                color="secondary"
                                            )
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    dbc.Button(
                                                        "Delete",
                                                        id="delete_expectation_button",
                                                        color="danger"
                                                    )
                                                ],
                                                id="delete_expectation_button_div",
                                                style={"display": "none"}
                                            )
                                        ]
                                    )
                                ],
                                justify="between"
                            ),
                            html.Div(
                                [
                                    dcc.Checklist(
                                        id="expectations_checklist",
                                        options=EMPTY_LIST,
                                        value=EMPTY_LIST,
                                        labelStyle={"display": "block"},
                                        inputStyle={"marginRight": "15px"}
                                    )
                                ],
                                id="expectations_checklist_div",
                                style={
                                    "marginTop": "20px",
                                    "padding": "25px",
                                    "paddingTop": "23px",
                                    "width": "100%",
                                    "height": "20vh",
                                    "backgroundColor": "#fff",
                                    "border": "3px black solid",
                                    "borderRadius": "20px",
                                    "overflow": "scroll",
                                    "display": "none"
                                }
                            ),
                            html.Div(
                                [
                                    "Defined expectations will appear here."
                                ],
                                id="no_expectations_div",
                                style={
                                    "marginTop": "20px",
                                    "textAlign": "center",
                                    "marginBottom": "20px"
                                }
                            )
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel",
                                id="cancel_expectation_set_definition_button",
                                color="secondary"
                            ),
                            dbc.Button(
                                "Confirm",
                                id="confirm_expectation_set_definition_button",
                                color="secondary"
                            )
                        ]
                    )
                ],
                id="expectation_set_definer_modal",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        html.H1("Set an expectation")
                    ),
                    dbc.ModalBody(
                        [
                            html.H5("Select a column:"),
                            dcc.Dropdown(
                                id="table_columns_dropdown",
                                options=EMPTY_LIST,
                                style={"marginBottom": "20px"}
                            ),
                            html.H5("Select an expectation:"),
                            dcc.Dropdown(
                                id="compatible_single_column_expectations_dropdown",
                                options=sorted(list(SINGLE_COLUMN_EXPECTATIONS_MAP.keys())),
                                style={"marginBottom": "20px"}
                            ),
                            html.Div(
                                [
                                    html.H5("Type"),
                                    dcc.Dropdown(
                                        id="type_exp_param_input",
                                        options=SUPPORTED_GE_EXP_TYPES,
                                        style={"marginBottom": "20px"}
                                    )
                                ],
                                id="type_exp_param_div",
                                style={"display": "none"}
                            ),
                            html.Div(
                                [
                                    html.H5("Length"),
                                    dcc.Input(
                                        id="length_exp_param_input",
                                        style=INPUT_STYLE
                                    )
                                ],
                                id="length_exp_param_div",
                                style={"display": "none"}
                            ),
                            html.Div(
                                [
                                    html.H5("Values (v1,v2,...)"),
                                    dcc.Input(
                                        id="values_single_column_exp_param_input",
                                        style=INPUT_STYLE
                                    )
                                ],
                                id="values_single_column_exp_param_div",
                                style={"display": "none"}
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    html.H5("Minimum value"),
                                                    dcc.Input(
                                                        id="min_value_exp_param_input",
                                                        style=INPUT_STYLE
                                                    )
                                                ],
                                                id="min_value_exp_param_div",
                                                style={
                                                    "display": "none",
                                                    "textAlign": "center"
                                                }
                                            ),
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            html.Div(
                                                [
                                                    html.H5("Maximum value"),
                                                    dcc.Input(
                                                        id="max_value_exp_param_input",
                                                        style=INPUT_STYLE
                                                    )
                                                ],
                                                id="max_value_exp_param_div",
                                                style={
                                                    "display": "none",
                                                    "textAlign": "center"
                                                }
                                            ),
                                        ]
                                    )
                                ],
                                justify="between",
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Add",
                                id="add_single_column_expectation_button",
                                color="secondary"
                            ),
                            dbc.Button(
                                "Close",
                                id="close_single_column_expectation_definer_button",
                                color="secondary"
                            )
                        ]
                    )
                ],
                id="single_column_expectation_definer_modal",
                style={
                    "padding": "30px"
                }
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        html.H1("Set an expectation")
                    ),
                    dbc.ModalBody(
                        [
                            html.H5("Select an expectation:"),
                            dcc.Dropdown(
                                id="compatible_multicolumn_expectations_dropdown",
                                options=sorted(list(MULTICOLUMN_EXPECTATIONS_MAP.keys())),
                                style={"marginBottom": "20px"}
                            ),
                            html.Div(
                                [
                                    html.H5("Select columns:")
                                ],
                                id="select_columns_text_div",
                                style={"display": "none"}
                            ),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="table_column_a",
                                        options=EMPTY_LIST,
                                        value=EMPTY_STRING
                                    ),
                                    dcc.Dropdown(
                                        id="table_column_b",
                                        options=EMPTY_LIST,
                                        value=EMPTY_STRING
                                    )
                                ],
                                id="table_a_and_b_columns_div",
                                style={"display": "none"}
                            ),
                            html.Div(
                                [
                                    dcc.Checklist(
                                        value=EMPTY_LIST,
                                        options=["Greater or equal"],
                                        id="greater_or_equal_checklist"
                                    )
                                ],
                                id="greater_or_equal_div",
                                style={"display": "none"}
                            ),
                            html.Div(
                                [
                                    dcc.Checklist(
                                        value=EMPTY_LIST,
                                        options=EMPTY_LIST,
                                        id="table_columns_checklist"
                                    ),
                                ],
                                id="table_columns_checklist_div",
                                style={"display": "none"}
                            ),
                            html.Div(
                                [
                                    html.H5("Values (v1,v2),(v3,v4)...)"),
                                    dcc.Input(
                                        id="values_multicolumn_exp_param_input",
                                        style=INPUT_STYLE
                                    )
                                ],
                                id="values_multicolumn_exp_param_div",
                                style={"display": "none"}
                            )
                        ]
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Add",
                                id="add_multicolumn_expectation_button",
                                color="secondary"
                            ),
                            dbc.Button(
                                "Close",
                                id="close_multicolumn_expectation_definer_button",
                                color="secondary"
                            )
                        ]
                    )
                ],
                id="multicolumn_expectation_definer_modal",
                style={
                    "padding": "30px"
                }
            ),

            # Auxiliary Divs
            html.Div(id="profile_report_output_div", style={"display": "none"}),
            html.Div(id="open_validation_result_output_div", style={"display": "none"}),
            dcc.Download(id="validation_result_downloader")
        ],
        style={
            "padding": "30px",
            "paddingTop": "15px",
            "width": "100%",
            "height": "100%"
        }
    )
    return app
