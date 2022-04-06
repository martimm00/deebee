import dash
from dash import dcc
from dash import html
import dash_uploader as du
import dash_bootstrap_components as dbc

from src.defaults import EMPTY_LIST, EMPTY_STRING, MAIN_COL_STYLE, CHECKLIST_DIV_STYLE


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
                                                        style={
                                                            "textAlign": "right"
                                                        }
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
                                        id="dataset_checklist_div",
                                        style=CHECKLIST_DIV_STYLE
                                    ),
                                    html.Div(
                                        [
                                            "There are no imported files."
                                        ],
                                        id="no_imported_dataset_div",
                                        style={
                                            "marginTop": "20px",
                                            "marginBottom": "20px",
                                            "padding": "25px",
                                            "paddingTop": "13vh",
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
                                            dbc.Button(
                                                "Preview table",
                                                id="open_preview_table_button",
                                                color="secondary"
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
                                                options=EMPTY_LIST,
                                                value=EMPTY_LIST,
                                                labelStyle={"display": "block"},
                                                inputStyle={"marginRight": "15px"}
                                            )
                                        ],
                                        style=CHECKLIST_DIV_STYLE
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
                    dbc.ModalHeader(dbc.ModalTitle("Header")),
                    dbc.ModalBody(id="preview_table_modal_body"),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close", className="ms-auto", n_clicks=0
                        )
                    )
                ],
                id="preview_table_modal",
            )
        ],
        style={
            "padding": "30px",
            "paddingTop": "15px",
            "width": "100%",
            "height": "100%"
        }
    )
    return app
