from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length

class EmissionForm(FlaskForm):
    emission = SelectField(('Emission Type to Map'),
                    choices=[('co2', 'Carbon Dioxide (CO2)'),
                             ('nox', 'Nitrogen Oxides (NOx)'),
                             ('so2', 'Sulfur Dioxide (SO2)')],
                    default='co2')
                            
