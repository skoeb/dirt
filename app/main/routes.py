from app.main import bp
from app.main import plots
from app import db
from models import Plant, Predictions, Country, Dirtiest
from flask import Flask, render_template, redirect, request, jsonify
from app.main.forms import EmissionForm

@bp.route('/')
def index():
    return render_template('methodology.html')

@bp.route('/country_rankings', methods=['GET','POST'])
def country_rankings():
    emission='co2'
    country_map = plots.create_map(emission)
    country_table = plots.create_table(emission)
    return render_template('country_rankings.html',
                            plot=country_map,
                            table=country_table.to_html(table_id='emission-table',
                                                    classes='table table-striped',
                                                    justify='center',
                                                    border=False, index=False))

@bp.route('/map_update', methods=['GET', 'POST'])
def map_update():
    emission = request.args['selected']
    graphJSON = plots.create_map(emission)
    return graphJSON

@bp.route('/dirtiest_spline_update', methods=['GET', 'POST'])
def dirtiest_spline_update():
    emission = request.args['selected']
    graphJSON = plots.spline_dirtiest_plants(emission)
    return graphJSON


@bp.route('/plant_rankings')
def plant_rankings():

    # --- create list of countries for dropdown ---
    countries = db.session.query(Country.country_long).distinct()
    countries = [i[0] for i in countries]
    countries.insert(0,'World')
    selected_country = 'World'

    emission='co2'
    plants = plots.create_plant_text(emission, selected_country)
    return render_template('plant_rankings.html', countries=countries, plants=plants)


@bp.route('/explore_the_data')
def explore_the_data():
    return render_template('explore_the_data.html')

@bp.route('/methodology')
def methodology():
    return render_template('methodology.html')
   

@bp.route('/contact')
def contact():
    return render_template('contact.html')
