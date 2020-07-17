from flask import current_app, url_for
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from app import db

class Prediction(db.Model):
    """SQLAlchemy ORM Wrapper to individual predictions."""

    __tablename__ = 'prediction'

    pred_id = db.Column(db.Integer, primary_key=True)
    plant_id_wri = db.Column(db.String(12), db.ForeignKey('plant.plant_id_wri'))
    timestamp = db.Column(db.DateTime)
    timestamp_year = db.Column(db.Integer)
    timestamp_month = db.Column(db.Integer)
    gross_load_mw = db.Column(db.Float)
    so2_lbs = db.Column(db.Float)
    nox_lbs = db.Column(db.Float)
    co2_lbs = db.Column(db.Float)

    def __repr__(self):
        return f"<Prediction {self.plant_id_wri}, {self.timestamp}, LOAD: {round(self.gross_load_mw,1)}, SO2: {round(self.so2_lbs,0)}, NOX: {round(self.nox_lbs, 1)}, CO2: {round(self.co2_lbs, 1)}>"


class Plant(db.Model):
    """SQLAlchemy ORM Wrapper to Plants."""

    __tablename__ = 'plant'

    plant_id_wri = db.Column(db.String(12), primary_key=True)
    iso3 = db.Column(db.String(3), db.ForeignKey('country.iso3'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    primary_fuel = db.Column(db.String(8))
    estimated_generation_gwh = db.Column(db.Float)
    wri_capacity_mw = db.Column(db.Float)

    source = db.column_property(db.func.substr(plant_id_wri, 1, 3).label('source'))

    co2_cum = db.column_property(db.select([db.func.sum(Prediction.co2_lbs)]).where(Prediction.plant_id_wri==plant_id_wri).label('co2_cum'))
    nox_cum = db.column_property(db.select([db.func.sum(Prediction.nox_lbs)]).where(Prediction.plant_id_wri==plant_id_wri).label('nox_cum'))
    so2_cum = db.column_property(db.select([db.func.sum(Prediction.so2_lbs)]).where(Prediction.plant_id_wri==plant_id_wri).label('so2_cum'))

    @hybrid_method
    def emission_cum(self, emission):
        """Wrapper around co2_cum, nox_cum, and so2_cum to provide generalized function accepting name of emission as str."""
        if emission == 'co2': return self.co2_cum
        elif emission == 'nox': return self.nox_cum
        elif emission == 'so2': return self.so2_cum
    
    co2_avg = db.column_property(db.select([db.func.avg(Prediction.co2_lbs)]).where(Prediction.plant_id_wri==plant_id_wri).label('co2_avg'))
    nox_avg = db.column_property(db.select([db.func.avg(Prediction.nox_lbs)]).where(Prediction.plant_id_wri==plant_id_wri).label('nox_avg'))
    so2_avg = db.column_property(db.select([db.func.avg(Prediction.so2_lbs)]).where(Prediction.plant_id_wri==plant_id_wri).label('so2_avg'))

    @hybrid_method
    def emission_avg(self, emission):
        """Wrapper around co2_avg, nox_avg, and so2_avg to provide generalized function accepting name of emission as str."""
        if emission == 'co2': return self.co2_avg
        elif emission == 'nox': return self.nox_avg
        elif emission == 'so2': return self.so2_avg
    
    @hybrid_property
    def cf(self):
        return (self.estimated_generation_gwh * 1000) / (self.wri_capacity_mw * 8760)

    def __repr__(self):
        return f'<Plant {self.plant_id_wri}, {self.iso3}, {self.primary_fuel} {self.wri_capacity_mw} MW>'


class Country(db.Model):

    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True)
    iso3 = db.Column(db.String(3))
    plants = db.relationship('Plant', backref='country_name', lazy='joined')
    
    @hybrid_property
    def plant_ids(self):
        return [i[0] for i in db.session.query(Plant.plant_id_wri).filter(Plant.iso3 == iso3).all()]

    n_plants = db.column_property(db.select([db.func.count(Plant.plant_id_wri)]).where(Plant.iso3 == iso3).label('n_plants'))

    # @hybrid_method
    def dirtiest_plants(self, emission, iso3, n=10):
        query = db.session.query(Plant.plant_id_wri)\
                      .filter(Plant.iso3 == iso3)\
                      .order_by(Plant.emission_cum(emission=emission).desc())\
                      .limit(n)
        return [i[0] for i in query.all()]
 
    co2_cum = db.column_property(db.select([db.func.sum(Plant.co2_cum)]).where(Plant.iso3==iso3).where(Plant.source == 'WRI').label('co2_cum'))
    nox_cum = db.column_property(db.select([db.func.sum(Plant.nox_cum)]).where(Plant.iso3==iso3).where(Plant.source == 'WRI').label('nox_cum'))
    so2_cum = db.column_property(db.select([db.func.sum(Plant.so2_cum)]).where(Plant.iso3==iso3).where(Plant.source == 'WRI').label('so2_cum'))

    @hybrid_method
    def emission_cum(self, emission):
        """Wrapper around co2_cum, nox_cum, and so2_cum to provide generalized function accepting name of emission as str."""
        if emission == 'co2': return self.co2_cum
        elif emission == 'nox': return self.nox_cum
        elif emission == 'so2': return self.so2_cum

    co2_avg = db.column_property(db.select([db.func.avg(Plant.co2_cum)]).where(Plant.iso3==iso3).where(Plant.source == 'WRI').label('co2_avg'))
    nox_avg = db.column_property(db.select([db.func.avg(Plant.nox_cum)]).where(Plant.iso3==iso3).where(Plant.source == 'WRI').label('nox_avg'))
    so2_avg = db.column_property(db.select([db.func.avg(Plant.so2_cum)]).where(Plant.iso3==iso3).where(Plant.source == 'WRI').label('so2_avg'))

    @hybrid_method
    def emission_avg(self, emission):
        """Wrapper around co2_avg, nox_avg, and so2_avg to provide generalized function accepting name of emission as str."""
        if emission == 'co2': return self.co2_avg
        elif emission == 'nox': return self.nox_avg
        elif emission == 'so2': return self.so2_avg


    def __repr__(self):
        return f"<Country: {self.iso3}, # Plants: {len(self.n_plants)}>"