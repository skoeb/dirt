import plotly
import plotly.graph_objs as go

from flask import jsonify

from models import Plant, Country, Prediction
from app import db

import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import json

def create_map(emission):
    """Create bubble map of worlds power plants by emission source."""
    
    emission_label = f"{emission}_cum"

    query = db.session.query(Plant.plant_id_wri,
                            Plant.iso3,
                            Plant.longitude, Plant.latitude,
                            Plant.emission_cum(emission=emission),
                            Plant.wri_capacity_mw,
                            Plant.primary_fuel)\
                        .filter(Plant.source == 'WRI')\
                        .order_by(db.desc(emission_label))

    map_df = pd.read_sql(query.statement, db.engine)

    fig = px.scatter_mapbox(map_df, lat='latitude', lon='longitude', color='primary_fuel',
                    size=emission_label, hover_name='iso3', mapbox_style='stamen-toner',
                    hover_data=['plant_id_wri', emission_label,'wri_capacity_mw'],
                    title=f"World Map of Power Plants by Annual {emission} Emissions",
                    height=500, zoom=1)

    # --- automatically set bounds ---
    fig.update_geos(showcountries=True, countrycolor="Black", countrywidth=0.5,
                    resolution=110) #fitbounds="locations", 

    graphJSON = fig.to_json()

    return graphJSON

def create_table(emission):
    """Create table of countries by emission."""

    query = db.session.query(Country.iso3,
                        Country.emission_cum(emission='co2'),
                        Country.emission_cum(emission='so2'),
                        Country.emission_cum(emission='nox'),
                        Country.n_plants)\
                    .order_by(db.desc('co2_cum'))\

    table_df = pd.read_sql(query.statement, db.engine)

    table_df['co2_cum'] /= 2000000000
    table_df['so2_cum'] /= 1000000
    table_df['nox_cum'] /= 1000000
    table_df.columns = ['Country', 'CO2 mil. tons', 'SO2 mil. lbs', 'NOX mil. lbs', 'Number of Plants in Country']

    return table_df

def create_plant_text(emission, country, n=10):

    output = []
    # --- grab country objects ---
    if country == 'WORLD':
        query = db.session.query(Plant.plant_id_wri)\
                                    .order_by(Plant.emission_cum(emission=emission).desc())\
                                    .limit(n)
        dirtiest_plants = [i[0] for i in query]
    else:
        output = []
        country_results = db.session.query(Country).filter(Country.iso3 == country)
        for i in country_results:
            dirtiest_plants = i.dirtiest_plants(emission='co2', iso3=country, n=n)
    
    for index, plant_id in enumerate(dirtiest_plants):
        plant_results = db.session.query(Plant).filter(Plant.plant_id_wri == plant_id)
        for plant in plant_results:
            output.append(plant)

    return output