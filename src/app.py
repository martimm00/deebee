import os
import dash
import dash_uploader as du
import dash_bootstrap_components as dbc

from src.layout import create_layout
from src.callbacks import set_callbacks


def configure_dash_uploader(app: dash.Dash, upload_dir_path: os.path) -> dash.Dash:
    """
    Configure a Dash uploader component in a Dash app.

    :param app: The target app.
    :param upload_dir_path: Where the uploaded files will be written.

    :return: The app itself.
    """
    du.configure_upload(app, upload_dir_path)
    return app


def create_app(upload_dir_path: os.path) -> dash.Dash:
    """
    Prepare a Dash app and return.

    :param upload_dir_path: The path where data will be stored.

    :return: The Dash app, ready to run.
    """
    app = dash.Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=False,
    )

    app = configure_dash_uploader(app, upload_dir_path)
    app = create_layout(app)
    app = set_callbacks(app)

    return app
