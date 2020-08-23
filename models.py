from flask import current_app, url_for
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, Table
from app import db

from config import Config

# db.Model.metadata.schema = Config.SCHEMA

class Country(db.Model):
    # __mapper_args__ = {'primary_key': [__table__.c.country]} 

    print('SCHEMA', db.Model.metadata.schema)
    print('TABLES', db.Model.metadata.tables.keys())
    breakpoint()
    __table__ = db.Model.metadata.tables['production.country']

class Plant(db.Model):
    __table__ = db.Model.metadata.tables['plant']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 

    @hybrid_property
    def pct_of_country_co2(self):
        country_co2 = db.session.query(Country.cum_co2).filter(Country.country == self.country)[0][0]
        return self.cum_co2 / country_co2


class Predictions(db.Model):
    __table__ = db.Model.metadata.tables['predictions']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 

class WRI(db.Model):
    __table__ = db.Model.metadata.tables['wri']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 

class Dirtiest(db.Model):
    __table__ = db.Model.metadata.tables['dirtiest']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 