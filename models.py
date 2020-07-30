from flask import current_app, url_for
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from app import db

class Country(db.Model):
    __table__ = db.Model.metadata.tables['country']
    __mapper_args__ = {'primary_key': [__table__.c.country]} 

class Plant(db.Model):
    __table__ = db.Model.metadata.tables['plant']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 

class Predictions(db.Model):
    __table__ = db.Model.metadata.tables['predictions']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 

class WRI(db.Model):
    __table__ = db.Model.metadata.tables['wri']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 

class Dirtiest(db.Model):
    __table__ = db.Model.metadata.tables['dirtiest']
    __mapper_args__ = {'primary_key': [__table__.c.plant_id_wri]} 