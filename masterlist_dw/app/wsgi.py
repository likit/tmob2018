from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
import os
from app.config import *

if os.environ.get('FLASK_ENV', 'production') == 'development':
    DEV_DATABASE = os.environ.get('DEV_DATABASE')
    if DEV_DATABASE is None:
        raise ValueError('Development database must be specified for the development mode.')
    config = DevelopmentConfig
else:
    DATABASE = os.environ.get('DATABASE')
    if DATABASE is None:
        raise ValueError('Production database must be specified for the production mode.')
    config = ProductionConfig

db = SQLAlchemy()
migrate = Migrate()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app

app = create_app(config)

