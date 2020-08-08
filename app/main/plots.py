import plotly
import plotly.graph_objs as go

from flask import jsonify

from models import Plant, Country, Predictions, Dirtiest
from app import db

import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import json

def create_map(emission):
    """Create bubble map of worlds power plants by emission source."""

    if emission == 'co2':
        query = db.session.query(Plant.plant_id_wri,
                                Plant.country,
                                Plant.longitude, Plant.latitude,
                                Plant.cum_co2,
                                Plant.capacity_mw,
                                Plant.primary_fuel)\
                            .order_by(db.desc(Plant.cum_co2))
    elif emission == 'so2':
        query = db.session.query(Plant.plant_id_wri,
                                Plant.country,
                                Plant.longitude, Plant.latitude,
                                Plant.cum_so2,
                                Plant.capacity_mw,
                                Plant.primary_fuel)\
                            .order_by(db.desc(Plant.cum_so2))
    if emission == 'nox':
        query = db.session.query(Plant.plant_id_wri,
                                Plant.country,
                                Plant.longitude, Plant.latitude,
                                Plant.cum_nox,
                                Plant.capacity_mw,
                                Plant.primary_fuel)\
                            .order_by(db.desc(Plant.cum_nox))

    # --- Create labels of selection from jQuery ---
    emission_col = f"cum_{emission}"
    emission_label = f"Cumulative {emission.upper()} Tons"

    # --- Read data from SQL ---
    map_df = pd.read_sql(query.statement, db.engine)

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
                    height=700, zoom=1)

    # --- automatically set bounds ---
    fig.update_geos(showcountries=True, countrycolor="Black", countrywidth=0.5,
                    resolution=110) #fitbounds="locations", 

    graphJSON = fig.to_json()

    return graphJSON

def create_table(emission):
    """Create table of countries by emission."""

    query = db.session.query(Country.country_long,
                        Country.cum_co2,
                        Country.cum_nox,
                        Country.cum_so2,
                        Country.n_plants)\
                    .order_by(db.desc(Country.cum_co2))\

    table_df = pd.read_sql(query.statement, db.engine)

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

def create_plant_text(emission, country_long, n=10):

    output = []
    if country_long == 'World':
        # --- grab country objects ---
        query = db.session.query(Plant.plant_id_wri)\
                                .order_by(db.desc(Plant.cum_co2))\
                                .limit(n)
    
    else:
        # --- grab country objects ---
        query = db.session.query(Dirtiest.plant_id_wri)\
                                .order_by(Dirtiest.co2_rank)\
                                .filter(Dirtiest.country_long == country_long)\
                                .limit(n)

    dirtiest_plants = [i[0] for i in query]
    for index, plant_id in enumerate(dirtiest_plants):
        plant_results = db.session.query(Plant).filter(Plant.plant_id_wri == plant_id)
        for plant in plant_results:
            output.append(plant)

    return output