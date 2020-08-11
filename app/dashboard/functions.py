
# --- Python Batteries ---
import os
import json

# --- External libraries ---
import dash
import dash_table
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
import pandas as pd
import plotly.tools as tls
import plotly.io as pio
import json as json_func
import plotly.express as px
import pycountry_convert as pcc
from datetime import datetime as dt

# --- Module Imports ---
import app.dashboard.resources as resources
import app.dashboard.layout as layout
from app import db

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~ Set up server ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# --- Theming ---
pio.templates.default = 'seaborn'


def init_callbacks(dash_app):
    
    @dash_app.callback(
    Output('selected_switches', 'data'),
    [Input('button', 'n_clicks')],
    state=[
        State('selected_variable', 'value'),
        State('selected_daterange', 'start_date'),
        State('selected_daterange', 'end_date'),
        ])
    def package_selections(n_clicks, variable, startdate, enddate):
        dict_out = {'variable':variable, 
                    'startdate':startdate,
                    'enddate':enddate,
                    'variable_label':resources.variable_lookup[variable],
                    }
        
        return json.dumps(dict_out)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~ Plots ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @dash_app.callback(
        Output('line_graph', 'figure'),
    [Input('selected_switches', 'data')])
    def spline_dirtiest_plants(switches):

        # --- read in switches ---
        switches = json.loads(switches)
        switches['startdate'] = dt.strptime(switches['startdate'], '%Y-%m-%dT%H:%M:%S').strftime("%Y-%m-%d")
        switches['enddate'] = dt.strptime(switches['enddate'], '%Y-%m-%dT%H:%M:%S').strftime("%Y-%m-%d")

        # --- query sql ---
        query = f"""
                WITH dirtiest_world AS (
                    SELECT *
                    FROM {config.SCHEMA}.plant
                    ORDER BY cum_{switches['variable'].replace('_lbs','')} DESC
                    LIMIT 20
                )

                SELECT
                    a.plant_id_wri,
                    b.datetime_utc,
                    a.country, 
                    a.primary_fuel,
                    b.pred_{switches['variable']} as {switches['variable']}
                FROM dirtiest_world a
                LEFT JOIN predictions b
                    ON a.plant_id_wri = b.plant_id_wri
                WHERE datetime_utc BETWEEN '{str(switches['startdate'])}' AND '{str(switches['enddate'])}' 
                """
        df = pd.read_sql(query, db.engine)

        # -- set datetime ---
        df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])

        fig = px.line(df, x="datetime_utc", y=switches['variable'], render_mode='svg',
                    color='primary_fuel', line_group='plant_id_wri',
                    title=f"{switches['variable_label']} Emissions for 20 Dirtiest Plants in the World")
        
        fig.update_traces(mode='lines', line_shape='spline', opacity=0.5)
        fig.update_layout(xaxis_title='Date', yaxis_title=switches['variable_label'])
        return fig

    @dash_app.callback(
        Output('scatter_graph', 'figure'),
    [Input('selected_switches', 'data')])
    def bubble_plant_capacity(switches):

        # --- read in switches ---
        switches = json.loads(switches)
        switches['startdate'] = dt.strptime(switches['startdate'], '%Y-%m-%dT%H:%M:%S').strftime("%Y-%m-%d")
        switches['enddate'] = dt.strptime(switches['enddate'], '%Y-%m-%dT%H:%M:%S').strftime("%Y-%m-%d")

        # --- query sql ---
        query = f"""
                SELECT
                    a.plant_id_wri,
                    b.country, 
                    b.primary_fuel,
                    SUM(a.pred_{switches['variable']}) as {switches['variable']},
                    SUM(b.capacity_mw) as capacity_mw
                FROM predictions a
                LEFT JOIN plant b
                    ON a.plant_id_wri = b.plant_id_wri
                WHERE datetime_utc BETWEEN '{str(switches['startdate'])}' AND '{str(switches['enddate'])}'
                GROUP BY a.plant_id_wri
                """
        df = pd.read_sql(query, db.engine)

        fig = px.scatter(df, x='capacity_mw', y=switches['variable'],
                        color='primary_fuel', size=switches['variable'], opacity=0.5,
                        marginal_x='histogram', marginal_y='histogram',
                        title=f"Sum of Plant Level Capacity against Emissions of {switches['variable_label']}")

        fig.update_layout(xaxis_title='Capacity (MW)', yaxis_title=switches['variable_label'])
        return fig
