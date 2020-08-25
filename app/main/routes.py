from app.main import bp
from app.main import queries
from app import db
from flask import Flask, render_template, redirect, request, jsonify

# --- get list of countries ---
countries = queries.list_countries()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~ Index ~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bp.route('/')
def index():
    return render_template('methodology.html')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~ Country Rankings ~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bp.route('/country_rankings', methods=['GET','POST'])
def country_rankings():
    emission='co2_lbs'
    country_map = queries.create_plant_map(emission)
    country_table = queries.create_country_table(emission)
    return render_template('country_rankings.html',
                            plot=country_map,
                            table=country_table.to_html(table_id='emission-table',
                                                    classes='table table-striped',
                                                    justify='center',
                                                    border=False, index=False))

@bp.route('/map_update', methods=['GET', 'POST'])
def map_update():
    emission = request.args['selected']
    graphJSON = queries.create_plant_map(emission)
    return graphJSON

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~ Plant Rankings ~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bp.route('/plant_rankings')
def plant_rankings():
    selected_country = 'World'
    emission='co2_lbs'
    plants = queries.query_dirtiest_plants(emission, selected_country)
    return render_template('plant_rankings.html', countries=countries, plants=plants)

@bp.route('/plant_update', methods=['GET','POST'])
def plant_update():
    emission = 'co2_lbs'
    selected_country = request.args['selected']
    plants = queries.query_dirtiest_plants(emission, selected_country)
    plantsJSON = jsonify({'data': render_template('_plant_loop.html', plants=plants)})
    return plantsJSON

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ Explore ~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bp.route('/explore_the_data')
def explore_the_data():

    # --- Initialize switches ---
    switches_init = {'emission':'co2_lbs', 'country_long':'World', 'emission_label':'CO2'}

    dirtiest_spline = queries.spline_dirtiest_plants(switches_init)
    plant_bubble = queries.bubble_plant_capacity(switches_init)
    return render_template('explore_the_data.html',
                            countries=countries,
                            dirtiest_spline=dirtiest_spline,
                            plant_bubble=plant_bubble)


@bp.route('/dirtiest_spline_update', methods=['GET', 'POST'])
def dirtiest_spline_update():
    switches = dict(request.args)
    switches['emission_label'] = switches['emission'].replace('_lbs','').upper()
    graphJSON = queries.spline_dirtiest_plants(switches)
    return graphJSON

@bp.route('/plant_bubble_update', methods=['GET', 'POST'])
def plant_bubble_update():
    switches = dict(request.args)
    switches['emission_label'] = switches['emission'].replace('_lbs','').upper()
    graphJSON = queries.bubble_plant_capacity(switches)
    return graphJSON

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~ Methodology ~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bp.route('/methodology')
def methodology():
    return render_template('methodology.html')
   
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~ Contact ~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bp.route('/contact')
def contact():
    return render_template('contact.html')

