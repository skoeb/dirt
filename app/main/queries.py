import plotly
import plotly.graph_objs as go

from flask import jsonify

# from models import Plant, Country, Predictions, Dirtiest
from flask import current_app, url_for
from app import db
from config import Config

import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import json
from datetime import datetime as dt

primary_fuel_cmap={
        "Coal": '#636EFA',
        "Oil": '#EF553B',
        "Gas": '#00CC96',
        "Petcoke": '#AB63FA'
}

def list_countries():
    query = f"""
            SELECT DISTINCT country_long
            FROM {Config.SCHEMA}.country
            """
    df = pd.read_sql(query, db.engine)

    countries = list(df['country_long'])
    countries.insert(0,'World')
    return countries

def create_plant_map(emission):
    """Create bubble map of worlds power plants by emission source."""

    emission_col = f"cum_{emission}"
    emission_label = f"Cumulative {emission.upper()} Tons"

    query = f"""
            SELECT 
                plant_id_wri,
                country,
                longitude,
                latitude,
                {emission_col},
                capacity_mw,
                primary_fuel
            FROM {Config.SCHEMA}.plant
            ORDER BY {emission_col} DESC
            """

    # --- Read data from SQL ---
    map_df = pd.read_sql(query, db.engine)

    # --- Downcast ---
    map_df['capacity_mw'] = map_df['capacity_mw'].astype(int)
    map_df[emission_col] /= 2000
    map_df[emission_col] = map_df[emission_col].astype(int)

    # --- Rename Columns ---
    map_df.rename({'primary_fuel':'Primary Fuel',
                   'capacity_mw':'Capacity MW',
                    emission_col:emission_label,
                    'plant_id_wri':'Plant ID',
                    "longitude":"Longitude",
                    "latitude":'Latitude',
                    }, axis='columns', inplace=True)

    # --- Plot --- 
    fig = px.scatter_mapbox(map_df, lat='Latitude', lon='Longitude', color='Primary Fuel',
                    size=emission_label, hover_name='Plant ID', mapbox_style='stamen-toner',
                    hover_data=['Primary Fuel','Capacity MW', emission_label],
                    color_discrete_map=primary_fuel_cmap,
                    height=700, zoom=1)

    # --- automatically set bounds ---
    fig.update_geos(showcountries=True, countrycolor="Black", countrywidth=0.5,
                    resolution=110) #fitbounds="locations", 

    graphJSON = fig.to_json()

    return graphJSON

def create_country_table(emission):
    """Create table of countries by emission."""

    query = f"""
            SELECT
                country_long,
                cum_co2,
                cum_nox,
                cum_so2,
                n_plants
            FROM {Config.SCHEMA}.country
            ORDER BY cum_co2 DESC
            """

    table_df = pd.read_sql(query, db.engine)

    # --- unit conversion ---
    table_df['cum_co2'] /= 2000000000
    table_df['cum_so2'] /= 1000000
    table_df['cum_nox'] /= 1000000

    # --- downcasting ---
    table_df['cum_co2'] = table_df['cum_co2'].astype(int)
    table_df['cum_so2'] = table_df['cum_so2'].astype(int)
    table_df['cum_nox'] = table_df['cum_nox'].astype(int)

    table_df.columns = ['Country', 'CO2 Mil. Tons', 'SO2 Mil. lbs', 'NOX Mil. lbs', 'Number of Plants in Country']

    return table_df.sort_values('CO2 Mil. Tons', ascending=False)

def query_dirtiest_plants(emission, country_long, n=10):

    if country_long == 'World':
        # --- grab country objects ---
        query = f"""
                WITH dirtiest_plants AS(
                    SELECT
                        plant_id_wri,
                        pct_country_co2,
                        pct_country_so2,
                        pct_country_nox
                    FROM {Config.SCHEMA}.dirtiest
                    ORDER BY cum_co2 DESC
                    LIMIT {n}
                )

                SELECT *
                FROM dirtiest_plants as dp
                LEFT JOIN {Config.SCHEMA}.plant p
                    ON p.plant_id_wri = dp.plant_id_wri
                """
    
    else:
        # --- grab country objects ---
        query = f"""
                WITH dirtiest_plants AS(
                    SELECT
                        plant_id_wri,
                        pct_country_co2,
                        pct_country_so2,
                        pct_country_nox
                    FROM {Config.SCHEMA}.dirtiest
                    WHERE country_long = {country_long}
                    ORDER BY cum_co2 DESC
                    LIMIT {n}
                )

                SELECT *
                FROM dirtiest_plants as dp
                LEFT JOIN {Config.SCHEMA}.plant p
                    ON p.plant_id_wri = dp.plant_id_wri
                """
    
    df = pd.read_sql(query, db.engine)
    return df

def spline_dirtiest_plants(switches):

    # --- query sql ---
    query = f"""
            SELECT
                a.plant_id_wri,
                a.country_long, 
                c.primary_fuel,
                b.datetime_utc,
                b.pred_{switches['emission']} as {switches['emission']}
            FROM {Config.SCHEMA}.dirtiest a
            LEFT JOIN {Config.SCHEMA}.predictions b
                ON a.plant_id_wri = b.plant_id_wri
            LEFT JOIN {Config.SCHEMA}.plant c
                ON a.plant_id_wri = c.plant_id_wri
            WHERE a.country_long = '{switches['country_long']}'
                AND a.co2_rank < 10
            """
    df = pd.read_sql(query, db.engine)

    # -- set datetime ---
    df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])

    fig = px.line(df, x="datetime_utc", y=switches['emission'], render_mode='svg',
                color='primary_fuel', line_group='plant_id_wri', color_discrete_map=primary_fuel_cmap,
                title=f"{switches['emission_label']} Emissions for 10 Dirtiest Plants in the {switches['country_long']}")
    
    fig.update_traces(mode='lines', line_shape='spline', opacity=0.5)
    fig.update_layout(xaxis_title='Date', yaxis_title=switches['emission_label'])
    return fig.to_json()

def bubble_plant_capacity(switches):

    # --- query sql ---
    query = f"""
            SELECT
                a.plant_id_wri,
                b.country_long, 
                b.primary_fuel,
                SUM(a.pred_{switches['emission']}) as {switches['emission']},
                SUM(b.capacity_mw) as capacity_mw
            FROM {Config.SCHEMA}.predictions a
            LEFT JOIN {Config.SCHEMA}.plant b
                ON a.plant_id_wri = b.plant_id_wri
            WHERE b.country_long = '{switches['country_long']}'
            GROUP BY a.plant_id_wri
            """
    df = pd.read_sql(query, db.engine)

    fig = px.scatter(df, x='capacity_mw', y=switches['emission'],
                    color='primary_fuel', size=switches['emission'], opacity=0.5,
                    marginal_x='histogram', marginal_y='histogram', color_discrete_map=primary_fuel_cmap,
                    title=f"Sum of Plant Level Capacity against Emissions of {switches['emission_label']}")

    fig.update_layout(xaxis_title='Capacity (MW)', yaxis_title=switches['emission_label'])
    return fig.to_json()
