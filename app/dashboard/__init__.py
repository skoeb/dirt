
# --- External libraries ---
import dash
import pandas as pd
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html



def create_dashboard(server):
    """Create the plotly Dash dashboard."""

    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            '/app/static/assets/base.css'
        ]
    )
    
    # --- set layout ---
    import app.dashboard.layout as layout
    dash_app.layout = layout.html_obj

    # --- initialize callbacks ---
    from app.dashboard.functions import init_callbacks
    init_callbacks(dash_app)

    return dash_app.server
