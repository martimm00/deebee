import dash
from dash import dcc
from dash import html
import dash_uploader as du
import dash_bootstrap_components as dbc

from constants.defaults import EMPTY_LIST, EMPTY_STRING
from constants.great_expectations_constants import SUPPORTED_EXPECTATIONS
from constants.layout_shortcut_constants import MAIN_COL_STYLE, CHECKLIST_DIV_STYLE


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
                                            "marginTop": "20px",
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
                                    dbc.Button(
                                        "Define expectations",
                                        id="open_expectation_set_definer_button",
                                        color="secondary"
                                    )
                                ],
                                style=MAIN_COL_STYLE
                            ),
                            dbc.Col(
                                [
                                    html.H1(
                                        "Validate"
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
                                style={
                                    "height": "38px",
                                    "width": "100%",
                                    "border": "3px black solid",
                                    "borderRadius": "20px",
                                    "paddingLeft": "10px",
                                    "paddingRight": "10px",
                                    "marginBottom": "15px"
                                }
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
                                                "New",
                                                id="new_expectation_button",
                                                color="secondary"
                                            )
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Button(
                                                "Delete",
                                                id="delete_expectation_button",
                                                color="danger"
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
                                    "marginBottom": "20px",
                                    "padding": "25px",
                                    "paddingTop": "23px",
                                    "width": "100%",
                                    "height": "30vh",
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
                                style={"marginTop": "20px", "textAlign": "center"}
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
                            html.H3("Select an expectation:"),
                            dcc.Dropdown(
                                id="supported_expectations_dropdown",
                                options=SUPPORTED_EXPECTATIONS
                            ),
                            html.H3("Select a column:"),
                            dcc.Dropdown(
                                id="table_columns_dropdown",
                                options=EMPTY_LIST
                            ),
                            dbc.ModalFooter(
                                [
                                    dbc.Button(
                                        "Add",
                                        id="add_expectation_button"
                                    ),
                                    dbc.Button(
                                        "Close",
                                        id="close_expectation_definer_button",
                                        color="secondary"
                                    )
                                ]
                            )
                        ]
                    ),
                ],
                id="expectation_definer_modal",
                style={
                    "padding": "30px"
                }
            ),

            # Auxiliary Divs
            html.Div(id="profile_report_output_div", style={"display": "none"}),

            # Stores
            dcc.Store("imported_datasets_store")
        ],
        style={
            "padding": "30px",
            "paddingTop": "15px",
            "width": "100%",
            "height": "100%"
        }
    )
    return app
