import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

from flask import Flask, request, current_app
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_humanize import Humanize

from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()
humanize = Humanize()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- push app context ---
    app.app_context().push()

    # --- register extensions ---
    humanize.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    
    # --- register blueprints ---
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # --- logging ---
    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/dirt.log',
                                            maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Dirtiest Power Plants Startup')

    return app