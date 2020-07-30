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

    emission_label = f"cum_{emission}"

    map_df = pd.read_sql(query.statement, db.engine)

    fig = px.scatter_mapbox(map_df, lat='latitude', lon='longitude', color='primary_fuel',
                    size=emission_label, hover_name='country', mapbox_style='stamen-toner',
                    hover_data=['plant_id_wri', emission_label,'capacity_mw'],
                    title=f"World Map of Power Plants by Annual {emission} Emissions",
                    height=500, zoom=1)

    # --- automatically set bounds ---
    fig.update_geos(showcountries=True, countrycolor="Black", countrywidth=0.5,
                    resolution=110) #fitbounds="locations", 

    graphJSON = fig.to_json()

    return graphJSON

def create_table(emission):
    """Create table of countries by emission."""

    query = db.session.query(Country.country,
                        Country.cum_co2,
                        Country.cum_nox,
                        Country.cum_so2,
                        Country.n_plants)\
                    .order_by(db.desc(Country.cum_co2))\

    table_df = pd.read_sql(query.statement, db.engine)

    table_df['cum_co2'] /= 2000000000
    table_df['cum_so2'] /= 1000000
    table_df['cum_nox'] /= 1000000
    table_df.columns = ['Country', 'CO2 mil. tons', 'SO2 mil. lbs', 'NOX mil. lbs', 'Number of Plants in Country']

    return table_df

def create_plant_text(emission, country, n=10):

    output = []
    # --- grab country objects ---
    query = db.session.query(Dirtiest.plant_id_wri)\
                                .order_by(Dirtiest.co2_rank)\
                                .limit(n)
    dirtiest_plants = [i[0] for i in query]
    
    for index, plant_id in enumerate(dirtiest_plants):
        plant_results = db.session.query(Plant).filter(Plant.plant_id_wri == plant_id)
        for plant in plant_results:
            output.append(plant)

    return output