from app.main import bp
from app.main import plots
from app import db
from models import Plant, Prediction, Country
from flask import Flask, render_template, redirect, request, jsonify
from app.main.forms import EmissionForm

@bp.route('/')
def index():
    return render_template('base.html')

@bp.route('/country_rankings', methods=['GET','POST'])
def country_rankings():
    emission='co2'
    country_map = plots.create_map(emission)
    country_table = plots.create_table(emission)
    return render_template('country_rankings.html',
                            plot=country_map,
                            table=country_table.to_html(table_id='emission-table'))

@bp.route('/map_update', methods=['GET', 'POST'])
def map_update():
    emission = request.args['selected']
    graphJSON = plots.create_map(emission)
    return graphJSON

@bp.route('/plant_rankings')
def plant_rankings():

    # --- create list of countries for dropdown ---
    countries = db.session.query(Country.iso3).distinct()
    countries = [i[0] for i in countries]
    countries.insert(0,'WORLD')
    selected_country = 'WORLD'

    emission='co2'
    plants = plots.create_plant_text(emission, selected_country)
    return render_template('plant_rankings.html', countries=countries, plants=plants)

@bp.route('/plant_update', methods=['GET','POST'])
def plant_update():
    emission = 'co2'
    selected_country = request.args['selected']
    print(selected_country)
    plants = plots.create_plant_text(emission, selected_country)
    plantsJSON = jsonify({'data': render_template('_plant_loop.html', plants=plants)})
    return plantsJSON

@bp.route('/explore_the_data')
def explore_the_data():
    return render_template('explore_the_data.html')

@bp.route('/methodology')
def methodology():
    return render_template('methodology.html')
   

@bp.route('/contact')
def contact():
    return render_template('contact.html')
