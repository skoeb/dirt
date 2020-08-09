
# --- Python batteries ---
import os
from datetime import datetime as dt

# --- External imports ---
import dash
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

# --- Module imports ---
import app.dashboard.resources as resources

html_obj = html.Div([

    # === Storage ===
    dcc.Store(id='selected_switches', storage_type='session'),
    
    # === Overview and Data Input ===
    html.Div([

        # --- Switches ---
        html.Div([


            # --- Select Variable ---
            html.Div([
                dbc.Row(
                    html.P('Select emission variable to plot:', className="row"),
                    justify="center", align="center", className="h-50"
                ),
                dcc.Dropdown(
                    id='selected_variable',
                    className="row",
                    options=[
                        {'label': 'CO2 lbs', 'value':'co2_lbs'},
                        {'label': 'NOx lbs', 'value':'nox_lbs'},
                        {'label': 'SO2 lbs', 'value':'so2_lbs'},
                    ],
                    value='nox_lbs',
                ),
            ]), 

            html.Br(),

            # --- Select Date Range ---
            html.Div([
                dbc.Row(
                    html.P('Select the date range to consider:', className="row"),
                    justify="center", align="center", className="h-50"
                ),
                dcc.DatePickerRange(
                    id='selected_daterange',
                    min_date_allowed=dt(2019,1,1),
                    max_date_allowed=dt(2019,12,31),
                    start_date=dt(2019,1,1),
                    end_date=dt(2019,12,31),
                    display_format= 'MMM, Do YYYY'
                )
            ]),

            # --- Button ---
            html.Button('Update Charts', id='button')
        ]), # end of switches
    
    ]), #end of overview and data input


    # === Line Graph ===
    html.Div([
        dcc.Graph(id="line_graph")
    ]),

    # === Scatterplot ===
    html.Div([
        dcc.Graph(id="scatter_graph")
    ]),
]) #end of html
